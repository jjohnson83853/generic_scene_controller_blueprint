import contextlib
import dis
import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BLUEPRINT = ROOT / "blueprints" / "automation" / "generic_scene_controller.yaml"
VALIDATOR = ROOT / "scripts" / "validate_blueprint.py"
EVENTS = ("pushed", "held", "doubleTapped", "released")
BLUEPRINT_DESCRIPTION = (
    "  description: Generic event-entity scene controllers with four per-button action slots.\n"
)


def run_validator(*arguments):
    return subprocess.run(
        [sys.executable, str(VALIDATOR), *(str(argument) for argument in arguments)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def replace_once(source, old, new):
    if source.count(old) != 1:
        raise AssertionError(f"Expected exactly one fixture anchor, found {source.count(old)}: {old!r}")
    return source.replace(old, new, 1)


def append_root_key(source, text):
    return source.rstrip() + "\n" + text + "\n"


def input_entry(number, event):
    if event == "entity":
        return (
            f"        button_{number}_entity:\n"
            f"          name: Button {number} event entity\n"
            f"          description: Event entity for button {number}.\n"
            '          default: ""\n'
            "          selector:\n"
            "            entity:\n"
            "              domain: event\n"
        )
    return (
        f"        button_{number}_{event}:\n"
        f"          name: Button {number} {event} action\n"
        f"          description: Action to run when button {number} is {event}.\n"
        "          default: []\n"
        "          selector:\n"
        "            action: {}\n"
    )


def section_block(source, number):
    marker = f"    button_{number}:\n"
    start = source.index(marker)
    next_marker = f"    button_{number + 1}:\n" if number < 5 else "trigger:\n"
    end = source.index(next_marker, start)
    return source[start:end]


def mutate_section(source, number, mutation):
    block = section_block(source, number)
    return replace_once(source, block, mutation(block))


def mutate_entry(source, number, entry_name, mutation):
    old = input_entry(number, entry_name)
    return mutate_section(source, number, lambda block: replace_once(block, old, mutation(old)))


def event_condition(number, event):
    return (
        "{{ trigger.id == 'button_"
        f"{number}' and trigger.to_state is not none and "
        f"trigger.to_state.attributes.get('event_type') == '{event}'"
        " }}"
    )


def branch_block(number, event):
    return (
        f'      - conditions: "{event_condition(number, event)}"\n'
        f"        sequence: !input button_{number}_{event}\n"
    )


def mutate_branch(source, number, event, mutation):
    old = branch_block(number, event)
    return replace_once(source, old, mutation(old))


def wrap_choose_with_branches(source):
    start = source.index("  - choose:\n")
    end = source.index("\nmode: parallel\n", start)
    block = source[start:end]
    lines = block.splitlines()
    wrapped = (
        "  - choose:\n"
        "      branches:\n"
        + "\n".join(f"  {line}" for line in lines[1:])
        + "\n      default: []"
    )
    return replace_once(source, block, wrapped)


def mutate_section_selector(source, number, extra_line):
    selector = (
        "          selector:\n"
        "            entity:\n"
        "              domain: event\n"
    )
    return mutate_section(
        source,
        number,
        lambda block: replace_once(block, selector, selector + extra_line),
    )


NEGATIVE_FIXTURES = (
    ("a1_unclosed_quote", "a1", lambda s: replace_once(
        s, BLUEPRINT_DESCRIPTION, '  description: "Unclosed description\n'
    )),
    ("a2_empty_name", "a2", lambda s: replace_once(
        s, "  name: Generic Multi-Button Scene Controller\n", '  name: ""\n'
    )),
    ("a2_wrong_domain", "a2", lambda s: replace_once(
        s, "  domain: automation\n", "  domain: script\n"
    )),
    ("a2_missing_homeassistant", "a2", lambda s: replace_once(
        s, '  homeassistant:\n    min_version: "2024.6.0"\n', ""
    )),
    ("a2_old_min_version", "a2", lambda s: replace_once(
        s, '    min_version: "2024.6.0"\n', '    min_version: "2024.5.0"\n'
    )),
    ("a3_missing_section", "a3", lambda s: replace_once(s, section_block(s, 3), "")),
    ("a3_extra_section", "a3", lambda s: replace_once(
        s, "trigger:\n", "    button_6: {}\ntrigger:\n"
    )),
    ("a3_renamed_section", "a3", lambda s: replace_once(s, "    button_2:\n", "    btn_2:\n")),
    ("a4_not_collapsed", "a4", lambda s: mutate_section(
        s, 1, lambda b: replace_once(b, "      collapsed: true\n", "      collapsed: false\n")
    )),
    ("a4_wrong_icon", "a4", lambda s: mutate_section(
        s, 2, lambda b: replace_once(b, "      icon: mdi:numeric-2-box-outline\n",
                                     "      icon: mdi:lightbulb\n")
    )),
    ("a4_missing_icon", "a4", lambda s: mutate_section(
        s, 3, lambda b: replace_once(b, "      icon: mdi:numeric-3-box-outline\n", "")
    )),
    ("a4_wrong_name", "a4", lambda s: mutate_section(
        s, 4, lambda b: replace_once(b, "      name: Button 4\n", "      name: Button Four\n")
    )),
    ("a4_missing_collapsed", "a4", lambda s: mutate_section(
        s, 5, lambda b: replace_once(b, "      collapsed: true\n", "")
    )),
    ("a4_string_collapsed", "a4", lambda s: mutate_section(
        s, 1, lambda b: replace_once(b, "      collapsed: true\n", '      collapsed: "true"\n')
    )),
    ("a4_wrong_section_icon", "a4", lambda s: mutate_section(
        s, 2, lambda b: replace_once(b, "      icon: mdi:numeric-2-box-outline\n",
                                     "      icon: mdi:numeric-3-box-outline\n")
    )),
    ("a5_missing_slot", "a5", lambda s: mutate_entry(s, 2, "held", lambda _: "")),
    ("a5_extra_slot", "a5", lambda s: mutate_section(
        s, 1, lambda b: replace_once(
            b, "        button_1_released:\n",
            "        button_1_longpress: {}\n        button_1_released:\n"
        )
    )),
    ("a5_missing_entity_default", "a5", lambda s: mutate_entry(
        s, 3, "entity", lambda entry: replace_once(entry, '          default: ""\n', "")
    )),
    ("a5_concrete_entity_default", "a5", lambda s: mutate_entry(
        s, 3, "entity", lambda entry: replace_once(
            entry, '          default: ""\n', "          default: event.any_controller\n"
        )
    )),
    ("a6_wrong_entity_domain", "a6", lambda s: mutate_section(
        s, 1, lambda b: replace_once(b, "              domain: event\n", "              domain: light\n")
    )),
    ("a7_missing_slot_default", "a7", lambda s: mutate_entry(
        s, 1, "released", lambda entry: replace_once(entry, "          default: []\n", "")
    )),
    ("a7_null_slot_default", "a7", lambda s: mutate_entry(
        s, 2, "pushed", lambda entry: replace_once(entry, "          default: []\n",
                                                   "          default: null\n")
    )),
    ("a7_wrong_slot_selector", "a7", lambda s: mutate_entry(
        s, 3, "held", lambda entry: replace_once(entry, "            action: {}\n",
                                                 "            entity: {}\n")
    )),
    ("a8_wrong_trigger_id", "a8", lambda s: replace_once(
        s, "    id: button_1\n", "    id: button_2\n"
    )),
    ("a8_extra_trigger_key", "a8", lambda s: replace_once(
        s, "    id: button_1\n", "    id: button_1\n    to: unavailable\n"
    )),
    ("a8_literal_trigger_entity", "a8", lambda s: replace_once(
        s, "    entity_id: !input button_1_entity\n", "    entity_id: some_button_1\n"
    )),
    ("a8_extra_trigger", "a8", lambda s: replace_once(
        s, "action:\n", "  - platform: state\n    entity_id: !input button_1_entity\n"
        "    id: button_6\naction:\n"
    )),
    ("a8_missing_trigger", "a8", lambda s: replace_once(
        s,
        "  - platform: state\n    entity_id: !input button_5_entity\n    id: button_5\n",
        ""
    )),
    ("a9_bare_condition", "a9", lambda s: mutate_branch(
        s, 1, "held",
        lambda b: replace_once(b, f'conditions: "{event_condition(1, "held")}"',
                               f"conditions: {event_condition(1, 'held')[3:-3]}"),
    )),
    ("a9_noncanonical_list_condition", "a9", lambda s: mutate_branch(
        s, 1, "held",
        lambda b: replace_once(
            b,
            f'      - conditions: "{event_condition(1, "held")}"\n',
            '      - conditions:\n'
            '          - "{{ trigger.id in [\'button_1\', \'button_2\'] and trigger.to_state is not none and trigger.to_state.attributes.get(\'event_type\') == \'held\' }}"\n',
        ),
    )),
    ("a9_wrong_input_ref", "a9", lambda s: mutate_branch(
        s, 2, "pushed",
        lambda b: replace_once(b, "!input button_2_pushed", "!input button_2_entity"),
    )),
    ("a9_literal_sequence", "a9", lambda s: mutate_branch(
        s, 3, "released", lambda b: replace_once(b, "!input button_3_released", "[]")
    )),
    ("a9_sibling_action", "a9", lambda s: mutate_branch(
        s, 1, "pushed",
        lambda b: replace_once(
            b,
            "        sequence: !input button_1_pushed\n",
            "        sequence:\n          - !input button_1_pushed\n          - service: noop\n",
        ),
    )),
    ("a9_sibling_step", "a9", lambda s: replace_once(
        s, "\nmode: parallel\n", "\n  - service: noop\nmode: parallel\n"
    )),
    ("a9_choose_default_sibling", "a9", lambda s: replace_once(
        s, "\nmode: parallel\n", "\n    default: []\nmode: parallel\n"
    )),
    ("a9_branches_wrapper", "a9", wrap_choose_with_branches),
    ("a9_missing_branch", "a9", lambda s: mutate_branch(s, 5, "doubleTapped", lambda _: "")),
    ("a9_duplicate_branch", "a9", lambda s: replace_once(
        s, "\nmode: parallel\n", "\n" + branch_block(1, "pushed") + "\nmode: parallel\n"
    )),
    ("a9_unsupported_event", "a9", lambda s: mutate_branch(
        s, 4, "pushed",
        lambda b: replace_once(b, "== 'pushed'", "== 'pressed'"),
    )),
    ("a10_missing_event_header", "a10", lambda s: replace_once(
        s, "# Supported event types: pushed, held, doubleTapped, released.\n",
        "# Supported event types: pushed, held, released.\n"
    )),
    ("a10_missing_provenance", "a10", lambda s: replace_once(
        s, "# MQTT discovery through the Hubitat Elevation hub exposes these event entities.\n",
        "# MQTT discovery through the event integration.\n"
    )),
    ("a10_missing_document_start", "a10", lambda s: replace_once(s, "---\n", "")),
    ("a11_vendor_prose", "a11", lambda s: replace_once(
        s, BLUEPRINT_DESCRIPTION, "  description: Zooz generic event-entity scene controllers.\n"
    )),
    ("a11_room_input_prose", "a11", lambda s: mutate_entry(
        s, 1, "entity", lambda entry: replace_once(
            entry, "          name: Button 1 event entity\n",
            "          name: Game room button 1 event entity\n"
        )
    )),
    ("a11_hubitat_outside_header", "a11", lambda s: replace_once(
        s, BLUEPRINT_DESCRIPTION, "  description: Hubitat generic event-entity controllers.\n"
    )),
    ("a11_node_id", "a11", lambda s: append_root_key(s, "node_id: 484")),
    ("a11_literal_entity_id", "a11", lambda s: append_root_key(
        s, "entity_id: light.hallway_light"
    )),
    ("a11_room_entity_id", "a11", lambda s: append_root_key(
        s, "entity_id: event.living_room_scene_controller_button_1_event"
    )),
    ("a11_curated_domain_value", "a11", lambda s: append_root_key(s, "label: scene.movie_night")),
    ("a11_shared_script_call", "a11", lambda s: append_root_key(s, "service: script.shared_on")),
    ("a11_curated_slug_prose", "a11", lambda s: replace_once(
        s, BLUEPRINT_DESCRIPTION,
        "  description: Controls event.living_room_scene_controller_button_1_event.\n"
    )),
    ("a11_isolated_curated_slug", "a11", lambda s: replace_once(
        s, BLUEPRINT_DESCRIPTION,
        "  description: Controls event.hallway_scene_controller_button_1_event.\n"
    )),
    ("a12_wrong_mode", "a12", lambda s: replace_once(
        s, "mode: parallel\n", "mode: single\n"
    )),
    ("a12_restart_mode", "a12", lambda s: replace_once(
        s, "mode: parallel\n", "mode: restart\n"
    )),
    ("a12_extra_alias", "a12", lambda s: append_root_key(s, "alias: test")),
    ("a12_extra_condition", "a12", lambda s: append_root_key(
        s, "condition:\n  - condition: sun\n    after: sunset"
    )),
    ("a12_root_icon", "a12", lambda s: append_root_key(s, "icon: mdi:lightbulb")),
    ("a12_root_collapsed", "a12", lambda s: append_root_key(s, "collapsed: true")),
    ("a12_missing_mode", "a12", lambda s: replace_once(s, "mode: parallel\n", "")),
    ("a13_multiple_key", "a13", lambda s: mutate_section_selector(
        s, 1, "              multiple: true\n"
    )),
    ("a13_not_from_key", "a13", lambda s: mutate_section_selector(
        s, 1, "              not_from: [unavailable, unknown]\n"
    )),
    ("a13_variables_key", "a13", lambda s: mutate_section_selector(
        s, 1, "              variables: {}\n"
    )),
    ("a13_mdi_key", "a13", lambda s: mutate_section_selector(
        s, 2, "              mdi: lightbulb\n"
    )),
    ("a13_nested_mode_key", "a13", lambda s: mutate_section_selector(
        s, 2, "              mode: parallel\n"
    )),
    ("a13_slot_icon_key", "a13", lambda s: mutate_entry(
        s, 1, "pushed", lambda entry: entry.replace(
            "        button_1_pushed:\n", "        button_1_pushed:\n          icon: mdi:lightbulb\n", 1
        )
    )),
    ("a13_selector_icon_key", "a13", lambda s: mutate_section_selector(
        s, 1, "              icon: mdi:numeric-1-box-outline\n"
    )),
    ("a13_slot_collapsed_key", "a13", lambda s: mutate_entry(
        s, 2, "held", lambda entry: entry.replace(
            "        button_2_held:\n", "        button_2_held:\n          collapsed: true\n", 1
        )
    )),
)


def build_cases(directory):
    source = BLUEPRINT.read_text(encoding="utf-8")
    cases = [
        ("real_blueprint", [str(BLUEPRINT)], 0, "PASS A13"),
        ("usage_error", [], 2, "usage:"),
        ("missing_file", [str(directory / "missing.yaml")], 2, "not found or unreadable"),
    ]
    for name, assertion, mutation in NEGATIVE_FIXTURES:
        fixture = directory / f"{name}.yaml"
        fixture.write_text(mutation(source), encoding="utf-8")
        cases.append((name, [str(fixture)], 1, f"a{assertion[1:]}:"))
    return cases


def executable_lines(code):
    lines = set()
    pending = [code]
    while pending:
        current = pending.pop()
        lines.update(line for _, line in dis.findlinestarts(current) if line is not None)
        pending.extend(item for item in current.co_consts if isinstance(item, type(code)))
    return lines


class BlueprintValidatorTests(unittest.TestCase):
    def test_real_blueprint_passes_all_assertions(self):
        result = run_validator(BLUEPRINT)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        for assertion in range(1, 14):
            self.assertIn(f"PASS A{assertion}", result.stdout)

    def test_usage_error(self):
        result = run_validator()
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("usage:", result.stderr.lower())

    def test_missing_file_is_a_usage_error(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            result = run_validator(Path(temporary_directory) / "missing.yaml")
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("not found or unreadable", result.stderr)

    def test_each_negative_fixture_fails_at_its_named_first_assertion(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            cases = build_cases(Path(temporary_directory))
            for name, arguments, expected, marker in cases[3:]:
                with self.subTest(fixture=name):
                    result = run_validator(*arguments)
                    self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
                    self.assertIn(marker, result.stderr)

    def test_coverage__in_process_line_coverage(self):
        temporary_directory = Path(tempfile.mkdtemp())
        cases = build_cases(temporary_directory)
        code = compile(VALIDATOR.read_text(encoding="utf-8"), str(VALIDATOR.resolve()), "exec")
        measurable_lines = executable_lines(code)
        covered_lines = set()
        validator_path = str(VALIDATOR.resolve())

        def tracer(frame, event, _argument):
            if event == "line" and frame.f_code.co_filename == validator_path:
                covered_lines.add(frame.f_lineno)
            return tracer

        spec = importlib.util.spec_from_file_location(
            "validate_blueprint_in_process_coverage", VALIDATOR
        )
        module = importlib.util.module_from_spec(spec)
        previous_trace = sys.gettrace()
        try:
            sys.settrace(tracer)
            spec.loader.exec_module(module)
            for name, arguments, expected, marker in cases:
                with self.subTest(case=name):
                    stdout = io.StringIO()
                    stderr = io.StringIO()
                    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                        result = module.main(arguments)
                    output = stdout.getvalue() + stderr.getvalue()
                    self.assertEqual(result, expected, output)
                    self.assertIn(marker, output)
        finally:
            sys.settrace(previous_trace)

        measurable = len(measurable_lines)
        covered = len(measurable_lines & covered_lines)
        percentage = 100.0 * covered / measurable if measurable else 0.0
        evidence = {
            "production_file": "scripts/validate_blueprint.py",
            "measurable": measurable,
            "covered": covered,
            "percentage": round(percentage, 2),
            "cases": [
                {"name": name, "expected_returncode": expected}
                for name, _arguments, expected, _marker in cases
            ],
        }
        evidence_path = temporary_directory / "coverage-evidence-t02.json"
        evidence_path.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
        print(f"coverage evidence: {evidence_path.resolve()}")
        self.assertGreater(measurable, 0, evidence)
        self.assertGreaterEqual(percentage, 90.0, evidence)


if __name__ == "__main__":
    unittest.main()
