#!/usr/bin/env python3
"""Validate the generic five-button Home Assistant blueprint structure."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any, Callable, NoReturn

from yaml.nodes import ScalarNode

import yaml


BUTTON_NUMBERS = range(1, 6)
EVENT_TYPES = ("pushed", "held", "doubleTapped", "released")
ROOT_KEYS = {"blueprint", "trigger", "action", "mode"}
SECTION_KEYS = {f"button_{number}" for number in BUTTON_NUMBERS}
SECTION_FIELDS = {"name", "description", "collapsed", "icon", "input"}
SECTION_INPUT_KEYS = {
    f"button_{number}_{event}"
    for number in BUTTON_NUMBERS
    for event in ("entity", *EVENT_TYPES)
}
TRIGGER_KEYS = {"platform", "entity_id", "id"}
BRANCH_KEYS = {"conditions", "sequence"}
BANNED_SCOPE_KEYS = {"variables", "multiple", "not_from", "mdi"}
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
    homeassistant = blueprint.get("homeassistant")
    if not isinstance(homeassistant, dict) or homeassistant.get("min_version") != "2024.6.0":
        fail('blueprint.homeassistant.min_version must be the string "2024.6.0"')


def check_sections(document: dict) -> None:
    inputs = document["blueprint"]["input"]
    if set(inputs) != SECTION_KEYS:
        fail("blueprint.input must contain exactly button_1 through button_5")
    for number in BUTTON_NUMBERS:
        if not isinstance(inputs[f"button_{number}"], dict):
            fail(f"button_{number} must be a mapping")


def check_section_appearance(document: dict) -> None:
    inputs = document["blueprint"]["input"]
    for number in BUTTON_NUMBERS:
        key = f"button_{number}"
        section = inputs[key]
        if set(section) != SECTION_FIELDS:
            fail(f"{key} must contain exactly name, description, collapsed, icon, and input")
        if section.get("name") != f"Button {number}":
            fail(f"{key}.name must be Button {number}")
        if not nonempty_text(section.get("description")):
            fail(f"{key}.description must be non-empty")
        if section.get("collapsed") is not True:
            fail(f"{key}.collapsed must be the boolean true")
        if section.get("icon") != f"mdi:numeric-{number}-box-outline":
            fail(f"{key}.icon must be mdi:numeric-{number}-box-outline")


def expected_section_input_keys(number: int) -> set[str]:
    return {f"button_{number}_{event}" for event in ("entity", *EVENT_TYPES)}


def check_section_inputs(document: dict) -> None:
    sections = document["blueprint"]["input"]
    for number in BUTTON_NUMBERS:
        key = f"button_{number}"
        entries = sections[key]["input"]
        if not isinstance(entries, dict) or set(entries) != expected_section_input_keys(number):
            fail(f"{key}.input must contain its event entity and four action slots")
        for entry_name, entry in entries.items():
            if not isinstance(entry, dict):
                fail(f"{entry_name} must be a mapping")
            if not nonempty_text(entry.get("name")) or not nonempty_text(entry.get("description")):
                fail(f"{entry_name} must have non-empty name and description")
        entity_key = f"button_{number}_entity"
        if entries[entity_key].get("default") != "":
            fail(f"{entity_key} must default to the empty string")


def check_entity_selectors(document: dict) -> None:
    sections = document["blueprint"]["input"]
    for number in BUTTON_NUMBERS:
        entry = sections[f"button_{number}"]["input"][f"button_{number}_entity"]
        selector = as_mapping(entry.get("selector"))
        entity_selector = as_mapping(selector.get("entity"))
        if entity_selector.get("domain") != "event":
            fail(f"button_{number}_entity selector must restrict entity domain to event")


def check_action_slots(document: dict) -> None:
    sections = document["blueprint"]["input"]
    for number in BUTTON_NUMBERS:
        entries = sections[f"button_{number}"]["input"]
        for event in EVENT_TYPES:
            key = f"button_{number}_{event}"
            entry = entries[key]
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


def canonical_condition(number: int, event: str) -> str:
    return (
        f"trigger.id == 'button_{number}' and trigger.to_state is not none and "
        f"trigger.to_state.attributes.get('event_type') == '{event}'"
    )


def check_dispatch(document: dict) -> None:
    actions = document.get("action")
    if not isinstance(actions, list) or len(actions) != 1:
        fail("action must contain exactly one choose step")
    action_step = actions[0]
    if not isinstance(action_step, dict) or set(action_step) != {"choose"}:
        fail("the sole action step must contain only choose")
    branches = action_step["choose"]
    expected_branches = [(number, event) for number in BUTTON_NUMBERS for event in EVENT_TYPES]
    if not isinstance(branches, list) or len(branches) != len(expected_branches):
        fail("choose must be a list of exactly twenty branches")

    for index, (number, event) in enumerate(expected_branches, start=1):
        branch = branches[index - 1]
        if not isinstance(branch, dict) or set(branch) != BRANCH_KEYS:
            fail(f"branch {index} must contain exactly conditions and sequence")
        conditions = branch["conditions"]
        if isinstance(conditions, list):
            if len(conditions) != 1:
                fail(f"branch {index} conditions must be one canonical template")
            conditions = conditions[0]
        expected_condition = "{{ " + canonical_condition(number, event) + " }}"
        if not isinstance(conditions, str) or conditions != expected_condition:
            fail(f"branch {index} conditions must equal the canonical {event} template")
        expected_input = f"button_{number}_{event}"
        sequence = branch["sequence"]
        if not isinstance(sequence, InputReference) or sequence.name != expected_input:
            fail(f"branch {index} sequence must reference !input {expected_input}")


def leading_header(lines: list[str]) -> tuple[str, int | None]:
    document_start = next((index for index, line in enumerate(lines) if line.strip() == "---"), None)
    header_lines = []
    for line in lines:
        if line.strip() and not line.lstrip().startswith("#"):
            break
        header_lines.append(line)
    return "\n".join(header_lines), document_start


def check_header(text: str) -> None:
    header, document_start = leading_header(text.splitlines())
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


def scope_violation(value: object, path: tuple[str, ...] = ()) -> str | None:
    if isinstance(value, dict):
        for key, child in value.items():
            key_name = key.casefold() if isinstance(key, str) else ""
            if key_name in BANNED_SCOPE_KEYS:
                return f"configuration key {key!r} is not allowed"
            if key_name == "mode" and path:
                return "mode is allowed only at the automation root"
            if key_name in {"collapsed", "icon"}:
                section_path = (
                    len(path) == 3
                    and path[:2] == ("blueprint", "input")
                    and path[2] in SECTION_KEYS
                )
                if not section_path:
                    return f"configuration key {key!r} is allowed only on a button section"
            reason = scope_violation(child, path + (key,)) if isinstance(key, str) else scope_violation(child, path)
            if reason is not None:
                return reason
    elif isinstance(value, list):
        for child in value:
            reason = scope_violation(child, path)
            if reason is not None:
                return reason
    return None


def check_root_mode(document: object) -> None:
    if not isinstance(document, dict) or set(document) != ROOT_KEYS:
        actual = sorted(document, key=str) if isinstance(document, dict) else type(document).__name__
        fail(f"root keys must be exactly {sorted(ROOT_KEYS)} (found {actual})")
    if document.get("mode") != "parallel":
        fail("root mode must be parallel")


def check_scope_fence(document: dict) -> None:
    reason = scope_violation(document)
    if reason is not None:
        fail(reason)


def validate(text: str, document: Any) -> None:
    checks: tuple[tuple[int, str, Callable[[], None]], ...] = (
        (2, "blueprint_metadata", lambda: check_metadata(document)),
        (3, "button_sections_exact", lambda: check_sections(document)),
        (4, "section_collapsed_icon", lambda: check_section_appearance(document)),
        (5, "section_input_slots", lambda: check_section_inputs(document)),
        (6, "entity_selectors_domain_event", lambda: check_entity_selectors(document)),
        (7, "action_slots_optional", lambda: check_action_slots(document)),
        (8, "state_triggers", lambda: check_triggers(document)),
        (9, "four_event_dispatch", lambda: check_dispatch(document)),
        (10, "header_comment", lambda: check_header(text)),
        (11, "generic_denylist", lambda: check_genericity(text, document)),
        (12, "root_mode_parallel", lambda: check_root_mode(document)),
        (13, "scope_fence_keys", lambda: check_scope_fence(document)),
    )
    for assertion_number, assertion_name, check in checks:
        try:
            check()
        except ValidationFailure as error:
            raise ValidationFailure(f"assertion_number={assertion_number} {error}") from error
        print(f"PASS A{assertion_number} {assertion_name}")


def main(arguments: list[str]) -> int:
    if len(arguments) != 1:
        print("usage: validate_blueprint.py <blueprint.yaml>", file=sys.stderr)
        return 2

    blueprint_path = Path(arguments[0])
    try:
        text = blueprint_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        print(f"blueprint file not found or unreadable: {blueprint_path} ({error})", file=sys.stderr)
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
        prefix, separator, reason = str(error).partition(" ")
        if separator and prefix.startswith("assertion_number="):
            assertion_number = prefix.removeprefix("assertion_number=")
            print(f"a{assertion_number}: {reason}", file=sys.stderr)
        else:
            print(f"validation failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
