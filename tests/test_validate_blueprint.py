import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BLUEPRINT = ROOT / "blueprints" / "automation" / "generic_scene_controller.yaml"
VALIDATOR = ROOT / "scripts" / "validate_blueprint.py"


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


class BlueprintValidatorTests(unittest.TestCase):
    def assert_mutation_fails_at(self, assertion, mutation):
        if not BLUEPRINT.is_file():
            result = run_validator(BLUEPRINT)
        else:
            source = BLUEPRINT.read_text(encoding="utf-8")
            mutated = mutation(source)
            with tempfile.TemporaryDirectory() as temporary_directory:
                fixture = Path(temporary_directory) / "fixture.yaml"
                fixture.write_text(mutated, encoding="utf-8")
                result = run_validator(fixture)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(assertion, result.stderr)

    def test_real_blueprint_passes_all_assertions(self):
        result = run_validator(BLUEPRINT)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        for assertion in range(1, 11):
            self.assertIn(f"A{assertion}", result.stdout)

    def test_usage_error(self):
        result = run_validator()
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("usage:", result.stderr.lower())

    def test_a1_rejects_invalid_yaml(self):
        self.assert_mutation_fails_at(
            "a1",
            lambda source: replace_once(
                source,
                "  description: Generic event-entity scene controllers with push-only action dispatch.\n",
                '  description: "Unclosed description\n',
            ),
        )

    def test_a2_rejects_invalid_blueprint_metadata(self):
        mutations = (
            lambda source: replace_once(source, "  name: Generic Multi-Button Scene Controller\n", '  name: ""\n'),
            lambda source: replace_once(source, "  domain: automation\n", "  domain: script\n"),
        )
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                self.assert_mutation_fails_at("a2", mutation)

    def test_a3_requires_exact_input_map_and_required_entities(self):
        remove_button_3_action = lambda source: replace_once(
            source,
            "    button_3_action:\n"
            "      name: Button 3 pushed action\n"
            "      description: Action to run when button 3 is pushed.\n"
            "      default: []\n"
            "      selector:\n"
            "        action: {}\n",
            "",
        )
        extra_input = lambda source: replace_once(
            source,
            "        action: {}\ntrigger:\n",
            "        action: {}\n    button_6_entity: {}\ntrigger:\n",
        )
        mutations = (
            ("missing action input", remove_button_3_action),
            ("extra input", extra_input),
            (
                "entity default",
                lambda source: replace_once(
                    source,
                    "    button_1_entity:\n"
                    "      name: Button 1 event entity\n"
                    "      description: Event entity for button 1.\n",
                    "    button_1_entity:\n"
                    "      name: Button 1 event entity\n"
                    "      description: Event entity for button 1.\n"
                    "      default: event.any_controller\n",
                ),
            ),
        )
        for label, mutation in mutations:
            with self.subTest(label=label):
                self.assert_mutation_fails_at("a3", mutation)

    def test_a4_restricts_entity_selectors_to_event(self):
        self.assert_mutation_fails_at(
            "a4",
            lambda source: replace_once(
                source,
                "    button_1_entity:\n"
                "      name: Button 1 event entity\n"
                "      description: Event entity for button 1.\n"
                "      selector:\n"
                "        entity:\n"
                "          domain: event\n",
                "    button_1_entity:\n"
                "      name: Button 1 event entity\n"
                "      description: Event entity for button 1.\n"
                "      selector:\n"
                "        entity: {}\n",
            ),
        )

    def test_a5_requires_optional_action_defaults(self):
        self.assert_mutation_fails_at(
            "a5",
            lambda source: replace_once(
                source,
                "    button_1_action:\n"
                "      name: Button 1 pushed action\n"
                "      description: Action to run when button 1 is pushed.\n"
                "      default: []\n",
                "    button_1_action:\n"
                "      name: Button 1 pushed action\n"
                "      description: Action to run when button 1 is pushed.\n",
            ),
        )

    def test_a6_requires_exact_state_triggers_and_input_bindings(self):
        mutations = (
            (
                "wrong trigger id",
                lambda source: replace_once(source, "    id: button_1\n", "    id: button_2\n"),
            ),
            (
                "literal trigger entity",
                lambda source: replace_once(
                    source,
                    "    entity_id: !input button_1_entity\n",
                    "    entity_id: some_button_1\n",
                ),
            ),
            (
                "extra trigger key",
                lambda source: replace_once(
                    source,
                    "    id: button_1\n",
                    "    id: button_1\n    to: unavailable\n",
                ),
            ),
        )
        for label, mutation in mutations:
            with self.subTest(label=label):
                self.assert_mutation_fails_at("a6", mutation)

    def test_a7_requires_exact_pushed_dispatch(self):
        condition = "{{ trigger.id == 'button_1' and trigger.to_state is not none and trigger.to_state.attributes.get('event_type') == 'pushed' }}"
        bare_condition = "trigger.id == 'button_1' and trigger.to_state is not none and trigger.to_state.attributes.get('event_type') == 'pushed'"
        mutations = (
            (
                "bare condition",
                lambda source: replace_once(
                    source,
                    f'conditions: "{condition}"',
                    f'conditions: "{bare_condition}"',
                ),
            ),
            (
                "membership dispatch",
                lambda source: replace_once(
                    source,
                    f'conditions: "{condition}"',
                    "conditions: \"{{ trigger.id in ['button_1', 'button_2'] and trigger.to_state is not none and trigger.to_state.attributes.get('event_type') == 'pushed' }}\"",
                ),
            ),
            (
                "branch sibling action",
                lambda source: replace_once(
                    source,
                    "        sequence: !input button_1_action\n",
                    "        sequence:\n"
                    "          - !input button_1_action\n"
                    "          - service: noop\n",
                ),
            ),
            (
                "action sibling step",
                lambda source: replace_once(
                    source,
                    "        sequence: !input button_5_action\n",
                    "        sequence: !input button_5_action\n  - service: noop\n",
                ),
            ),
            (
                "choose default",
                lambda source: replace_once(
                    source,
                    "        sequence: !input button_5_action\n",
                    "        sequence: !input button_5_action\n    default: []\n",
                ),
            ),
            (
                "sixth branch",
                lambda source: replace_once(
                    source,
                    "        sequence: !input button_5_action\n",
                    "        sequence: !input button_5_action\n"
                    "      - conditions: \"{{ trigger.id == 'button_1' and trigger.to_state is not none and trigger.to_state.attributes.get('event_type') == 'held' }}\"\n"
                    "        sequence: !input button_1_action\n",
                ),
            ),
        )
        for label, mutation in mutations:
            with self.subTest(label=label):
                self.assert_mutation_fails_at("a7", mutation)

    def test_a8_requires_header_and_document_start(self):
        mutations = (
            (
                "event type token",
                lambda source: replace_once(
                    source,
                    "# Supported event types: pushed, held, doubleTapped, released.\n",
                    "# Supported event types: pushed, held, released.\n",
                ),
            ),
            (
                "provenance token",
                lambda source: replace_once(
                    source,
                    "# MQTT discovery through the Hubitat Elevation hub exposes these event entities.\n",
                    "# MQTT discovery through the Elevation hub exposes these event entities.\n",
                ),
            ),
            ("document start", lambda source: replace_once(source, "---\n", "")),
        )
        for label, mutation in mutations:
            with self.subTest(label=label):
                self.assert_mutation_fails_at("a8", mutation)

    def test_a9_rejects_non_generic_configuration_and_prose(self):
        mutations = (
            (
                "vendor in prose",
                lambda source: replace_once(
                    source,
                    "  description: Generic event-entity scene controllers with push-only action dispatch.\n",
                    "  description: Zooz generic event-entity scene controllers with push-only action dispatch.\n",
                ),
            ),
            (
                "room in input prose",
                lambda source: replace_once(
                    source,
                    "      name: Button 1 event entity\n",
                    "      name: Game room button 1 event entity\n",
                ),
            ),
            (
                "Hubitat outside header",
                lambda source: replace_once(
                    source,
                    "  description: Generic event-entity scene controllers with push-only action dispatch.\n",
                    "  description: Hubitat generic event-entity scene controllers with push-only action dispatch.\n",
                ),
            ),
            ("node id key", lambda source: append_root_key(source, "node_id: 484")),
            ("literal entity id", lambda source: append_root_key(source, "entity_id: light.hallway_light")),
            (
                "room-bearing entity id",
                lambda source: append_root_key(
                    source,
                    "entity_id: event.living_room_scene_controller_button_1_event",
                ),
            ),
            ("curated dotted value", lambda source: append_root_key(source, "label: scene.movie_night")),
            ("shared script call", lambda source: append_root_key(source, "service: script.shared_on")),
            (
                "curated slug in prose",
                lambda source: replace_once(
                    source,
                    "  description: Generic event-entity scene controllers with push-only action dispatch.\n",
                    "  description: controls event.living_room_scene_controller_button_1_event\n",
                ),
            ),
            (
                "embedded curated slug in prose",
                lambda source: replace_once(
                    source,
                    "  description: Generic event-entity scene controllers with push-only action dispatch.\n",
                    "  description: controls event.hallway_scene_controller_button_1_event\n",
                ),
            ),
        )
        for label, mutation in mutations:
            with self.subTest(label=label):
                self.assert_mutation_fails_at("a9", mutation)

    def test_a10_rejects_ticket_scope_fence_keys(self):
        mutations = (
            ("mode", lambda source: append_root_key(source, "mode: parallel")),
            ("variables", lambda source: append_root_key(source, "variables: {}")),
            (
                "multiple selector",
                lambda source: replace_once(
                    source,
                    "    button_1_entity:\n"
                    "      name: Button 1 event entity\n"
                    "      description: Event entity for button 1.\n"
                    "      selector:\n"
                    "        entity:\n"
                    "          domain: event\n",
                    "    button_1_entity:\n"
                    "      name: Button 1 event entity\n"
                    "      description: Event entity for button 1.\n"
                    "      selector:\n"
                    "        entity:\n"
                    "          domain: event\n"
                    "          multiple: true\n",
                ),
            ),
            (
                "not_from selector",
                lambda source: replace_once(
                    source,
                    "    button_1_entity:\n"
                    "      name: Button 1 event entity\n"
                    "      description: Event entity for button 1.\n"
                    "      selector:\n"
                    "        entity:\n"
                    "          domain: event\n",
                    "    button_1_entity:\n"
                    "      name: Button 1 event entity\n"
                    "      description: Event entity for button 1.\n"
                    "      selector:\n"
                    "        entity:\n"
                    "          domain: event\n"
                    "          not_from: [unavailable, unknown]\n",
                ),
            ),
            (
                "collapsed action",
                lambda source: replace_once(
                    source,
                    "    button_1_action:\n"
                    "      name: Button 1 pushed action\n",
                    "    button_1_action:\n"
                    "      collapsed: true\n"
                    "      name: Button 1 pushed action\n",
                ),
            ),
            (
                "mdi icon",
                lambda source: replace_once(
                    source,
                    "    button_1_entity:\n"
                    "      name: Button 1 event entity\n",
                    "    button_1_entity:\n"
                    "      icon: mdi:lightbulb\n"
                    "      name: Button 1 event entity\n",
                ),
            ),
            (
                "root condition",
                lambda source: append_root_key(
                    source,
                    "condition:\n  - condition: sun\n    after: sunset",
                ),
            ),
        )
        for label, mutation in mutations:
            with self.subTest(label=label):
                self.assert_mutation_fails_at("a10", mutation)


if __name__ == "__main__":
    unittest.main()
