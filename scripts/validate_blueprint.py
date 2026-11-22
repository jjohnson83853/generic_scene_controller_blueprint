#!/usr/bin/env python3
"""Validate the generic five-button Home Assistant blueprint structure."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any, Callable, NoReturn

from yaml.nodes import ScalarNode

import yaml


EXPECTED_ROOT_KEYS = {"blueprint", "trigger", "action"}
INPUT_KEYS = {
    f"button_{number}_{kind}"
    for number in range(1, 6)
    for kind in ("entity", "action")
}
TRIGGER_KEYS = {"platform", "entity_id", "id"}
BRANCH_KEYS = {"conditions", "sequence"}
CURATED_DOMAINS = (
    "event",
    "light",
    "switch",
    "scene",
    "script",
    "input_boolean",
    "input_select",
    "automation",
    "binary_sensor",
    "sensor",
    "cover",
    "fan",
    "lock",
    "media_player",
)
CURATED_DOMAIN_PATTERN = re.compile(
    rf"(?:{'|'.join(CURATED_DOMAINS)})\.[a-z0-9_]+\Z",
    re.IGNORECASE,
)
CURATED_DOMAIN_TOKEN_PATTERN = re.compile(
    rf"(?<![A-Za-z0-9_])(?:{'|'.join(CURATED_DOMAINS)})\.[a-z0-9_]+(?![A-Za-z0-9_])",
    re.IGNORECASE,
)
IPV4_PATTERN = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
WILDCARD_PATTERN = re.compile(r"(?:[^.\s]+\.\*|\*\.[^.\s]+)\Z")
SCOPE_FENCE_KEYS = {
    "mode",
    "variables",
    "multiple",
    "not_from",
    "collapsed",
    "icon",
    "mdi",
}
BANNED_ROOM_TOKENS = (
    "master bedroom",
    "master_bedroom",
    "game room",
    "game_room",
    "living room",
    "living_room",
    "theater computer",
    "theater_computer",
)
HEADER_TOKENS = ("pushed", "held", "doubleTapped", "released", "MQTT", "Hubitat")
BANNED_RAW_TOKENS = ("zooz",) + BANNED_ROOM_TOKENS


class InputReference:
    """Opaque representation of a Home Assistant !input reference."""

    __slots__ = ("name",)

    def __init__(self, name: str) -> None:
        self.name = name


class BlueprintLoader(yaml.SafeLoader):
    """SafeLoader with a local, tag-preserving !input constructor."""

    yaml_constructors = yaml.SafeLoader.yaml_constructors.copy()
    yaml_multi_constructors = yaml.SafeLoader.yaml_multi_constructors.copy()


def construct_input_reference(loader: BlueprintLoader, node: ScalarNode) -> InputReference:
    return InputReference(loader.construct_scalar(node))


BlueprintLoader.add_constructor("!input", construct_input_reference)


class ValidationFailure(Exception):
    """A named assertion failed with a concise reason."""


def fail(reason: str) -> NoReturn:
    raise ValidationFailure(reason)


def as_mapping(value: object) -> dict:
    return value if isinstance(value, dict) else {}


def nonempty_text(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def check_metadata(document: object) -> None:
    root = as_mapping(document)
    blueprint = root.get("blueprint")
    if not isinstance(blueprint, dict):
        fail("blueprint must be a mapping")
    if not nonempty_text(blueprint.get("name")):
        fail("blueprint.name must be non-empty")
    if not nonempty_text(blueprint.get("description")):
        fail("blueprint.description must be non-empty")
    if blueprint.get("domain") != "automation":
        fail("blueprint.domain must be automation")
    if not isinstance(blueprint.get("input"), dict):
        fail("blueprint.input must be a mapping")


def check_inputs(document: dict) -> None:
    blueprint = document["blueprint"]
    inputs = blueprint["input"]
    actual_keys = set(inputs)
    if actual_keys != INPUT_KEYS:
        missing = sorted(INPUT_KEYS - actual_keys)
        extra = sorted(actual_keys - INPUT_KEYS, key=str)
        fail(f"input keys must be exactly the ten button entity/action keys (missing={missing}, extra={extra})")

    for number in range(1, 6):
        for kind in ("entity", "action"):
            key = f"button_{number}_{kind}"
            entry = inputs[key]
            if not isinstance(entry, dict):
                fail(f"{key} must be a mapping")
            if not nonempty_text(entry.get("name")) or not nonempty_text(entry.get("description")):
                fail(f"{key} must have non-empty name and description")
        if "default" in inputs[f"button_{number}_entity"]:
            fail(f"button_{number}_entity must not have a default")


def check_entity_selectors(document: dict) -> None:
    inputs = document["blueprint"]["input"]
    for number in range(1, 6):
        key = f"button_{number}_entity"
        selector = as_mapping(inputs[key].get("selector"))
        entity_selector = as_mapping(selector.get("entity"))
        if entity_selector.get("domain") != "event":
            fail(f"{key} selector must restrict entity domain to event")


def check_action_selectors(document: dict) -> None:
    inputs = document["blueprint"]["input"]
    for number in range(1, 6):
        key = f"button_{number}_action"
        entry = inputs[key]
        selector = as_mapping(entry.get("selector"))
        if selector.get("action") != {}:
            fail(f"{key} must use the action selector")
        if entry.get("default") != []:
            fail(f"{key} must default to an empty action sequence")


def check_triggers(document: dict) -> None:
    triggers = document.get("trigger")
    if not isinstance(triggers, list) or len(triggers) != 5:
        fail("trigger must contain exactly five state triggers")

    for number, trigger in enumerate(triggers, start=1):
        expected_input = f"button_{number}_entity"
        if not isinstance(trigger, dict) or set(trigger) != TRIGGER_KEYS:
            fail(f"trigger {number} must have exactly platform, entity_id, and id keys")
        if trigger.get("platform") != "state":
            fail(f"trigger {number} platform must be state")
        entity_reference = trigger.get("entity_id")
        if not isinstance(entity_reference, InputReference) or entity_reference.name != expected_input:
            fail(f"trigger {number} entity_id must reference !input {expected_input}")
        if trigger.get("id") != f"button_{number}":
            fail(f"trigger {number} id must be button_{number}")


def canonical_condition(number: int) -> str:
    return (
        f"trigger.id == 'button_{number}' and trigger.to_state is not none and "
        "trigger.to_state.attributes.get('event_type') == 'pushed'"
    )


def check_dispatch(document: dict) -> None:
    actions = document.get("action")
    if not isinstance(actions, list) or len(actions) != 1:
        fail("action must contain exactly one choose step")
    action_step = actions[0]
    if not isinstance(action_step, dict) or set(action_step) != {"choose"}:
        fail("the sole action step must be a choose mapping")

    branches = action_step["choose"]
    if not isinstance(branches, list) or len(branches) != 5:
        fail("choose must contain exactly five branches and no default")

    for number, branch in enumerate(branches, start=1):
        if not isinstance(branch, dict) or set(branch) != BRANCH_KEYS:
            fail(f"branch {number} must contain exactly conditions and sequence")
        conditions = branch["conditions"]
        if isinstance(conditions, list):
            if len(conditions) != 1:
                fail(f"branch {number} conditions must be one template string")
            conditions = conditions[0]
        if not isinstance(conditions, str):
            fail(f"branch {number} conditions must be a template string")
        raw_template = conditions.strip()
        if not raw_template.startswith("{{") or not raw_template.endswith("}}"):
            fail(f"branch {number} condition must include {{ and }} template delimiters")
        expression = " ".join(raw_template[2:-2].split())
        if expression != canonical_condition(number):
            fail(f"branch {number} condition must equal the canonical pushed-event expression")
        action_reference = branch["sequence"]
        expected_action = f"button_{number}_action"
        if not isinstance(action_reference, InputReference) or action_reference.name != expected_action:
            fail(f"branch {number} sequence must reference !input {expected_action}")


def leading_header(lines: list[str]) -> tuple[str, int | None]:
    document_start = next((index for index, line in enumerate(lines) if line.strip() == "---"), None)
    header_lines = []
    for line in lines:
        if line.strip() and not line.lstrip().startswith("#"):
            break
        header_lines.append(line)
    return "\n".join(header_lines), document_start


def check_header(text: str) -> None:
    lines = text.splitlines()
    header, document_start = leading_header(lines)
    if document_start is None:
        fail("the first YAML document-start line (---) is required")
    for token in HEADER_TOKENS:
        if token not in header:
            fail(f"leading comment block must document {token}")


def is_template(value: str) -> bool:
    return "{{" in value or "{%" in value


def is_wildcard(value: str) -> bool:
    stripped = value.strip()
    return stripped == "*" or WILDCARD_PATTERN.fullmatch(stripped) is not None


def scan_generic_configuration(value: object, prose_value: bool = False) -> str | None:
    if isinstance(value, dict):
        for key, child in value.items():
            key_name = key.casefold() if isinstance(key, str) else ""
            if key_name in {"device_id", "node_id"}:
                return f"configuration key {key!r} is not allowed"
            if key_name == "entity_id" and not isinstance(child, InputReference):
                return "every entity_id must be an !input reference"
            reason = scan_generic_configuration(
                child,
                prose_value or key_name in {"name", "description"},
            )
            if reason is not None:
                return reason
    elif isinstance(value, list):
        for child in value:
            reason = scan_generic_configuration(child, prose_value)
            if reason is not None:
                return reason
    elif isinstance(value, str) and not is_template(value) and not is_wildcard(value):
        if CURATED_DOMAIN_PATTERN.fullmatch(value):
            return "configuration contains a curated-domain entity-id value"
        if prose_value and CURATED_DOMAIN_TOKEN_PATTERN.search(value):
            return "name or description contains a curated-domain entity-id token"
    return None


def check_genericity(text: str, document: dict) -> None:
    lowered = text.casefold()
    for token in BANNED_RAW_TOKENS:
        if token in lowered:
            fail(f"raw blueprint text contains banned token {token!r}")
    if re.search(r"zen3[0-9]+", lowered):
        fail("raw blueprint text contains a banned model token")
    if IPV4_PATTERN.search(text):
        fail("raw blueprint text contains an IPv4 literal")

    lines = text.splitlines()
    header, _ = leading_header(lines)
    header_line_count = len(header.splitlines())
    outside_header = "\n".join(lines[header_line_count:])
    if "hubitat" in outside_header.casefold():
        fail("hubitat is allowed only in the leading comment block")

    reason = scan_generic_configuration(document)
    if reason is not None:
        fail(reason)


def check_scope_fence(document: dict) -> None:
    def find_banned_key(value: object) -> str | None:
        if isinstance(value, dict):
            for key, child in value.items():
                if isinstance(key, str) and key.casefold() in SCOPE_FENCE_KEYS:
                    return key
                reason = find_banned_key(child)
                if reason is not None:
                    return reason
        elif isinstance(value, list):
            for child in value:
                reason = find_banned_key(child)
                if reason is not None:
                    return reason
        return None

    banned_key = find_banned_key(document)
    if banned_key is not None:
        fail(f"configuration key {banned_key!r} is outside ticket 01 scope")
    if not isinstance(document, dict) or set(document) != EXPECTED_ROOT_KEYS:
        actual = sorted(document, key=str) if isinstance(document, dict) else type(document).__name__
        fail(f"root keys must be exactly {sorted(EXPECTED_ROOT_KEYS)} (found {actual})")

def validate(text: str, document: Any) -> None:
    checks: tuple[tuple[int, str, Callable[[], None]], ...] = (
        (2, "blueprint_metadata", lambda: check_metadata(document)),
        (3, "button_inputs_required_and_exact", lambda: check_inputs(document)),
        (4, "entity_selectors_domain_event", lambda: check_entity_selectors(document)),
        (5, "action_selectors_optional", lambda: check_action_selectors(document)),
        (6, "state_triggers", lambda: check_triggers(document)),
        (7, "action_dispatch_pushed", lambda: check_dispatch(document)),
        (8, "header_comment", lambda: check_header(text)),
        (9, "generic_denylist", lambda: check_genericity(text, document)),
        (10, "scope_fence_keys", lambda: check_scope_fence(document)),
    )
    for assertion_number, assertion_name, check in checks:
        try:
            check()
        except ValidationFailure as error:
            raise ValidationFailure(f"a{assertion_number}: {error}") from error
        print(f"PASS A{assertion_number} {assertion_name}")


def main(arguments: list[str]) -> int:
    if len(arguments) != 1:
        print("usage: validate_blueprint.py <blueprint.yaml>", file=sys.stderr)
        return 2

    blueprint_path = Path(arguments[0])
    try:
        text = blueprint_path.read_text(encoding="utf-8")
    except OSError as error:
        print(f"blueprint file not found or unreadable: {blueprint_path} ({error.strerror})", file=sys.stderr)
        return 2

    try:
        document = yaml.load(text, Loader=BlueprintLoader)
    except (yaml.YAMLError, UnicodeError) as error:
        print(f"a1: unable to parse YAML ({type(error).__name__})", file=sys.stderr)
        return 1

    print("PASS A1 parse_yaml")
    try:
        validate(text, document)
    except ValidationFailure as error:
        message = str(error)
        match = re.fullmatch(r"assertion_number=(\d+) (.*)", message, re.DOTALL)
        if match:
            assertion_number = int(match.group(1))
            reason = match.group(2)
            print(f"a{assertion_number}: {reason}", file=sys.stderr)
        else:
            print(f"validation failed: {message}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
