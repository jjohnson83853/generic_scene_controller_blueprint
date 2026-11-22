# Generic Scene Controller Blueprint

A generic Home Assistant automation blueprint accepts five event-entity inputs and runs a configured action only for each button's `pushed` event.

## Repository layout

- `blueprints/automation/generic_scene_controller.yaml` — importable automation blueprint.
- `scripts/validate_blueprint.py` — structural validation using Python 3 and PyYAML.
- `tests/test_validate_blueprint.py` — validator regression tests.

## Import into Home Assistant

In Home Assistant, open **Settings → Automations & Scenes → Blueprints** and choose **Import Blueprint**. Provide the raw file URL or local path for `blueprints/automation/generic_scene_controller.yaml`, then create an automation from the imported blueprint and select an event entity and optional action for each button. The live import and automation trace are verified in Home Assistant by the user; they are not checked by the local validator.

## Validation

Install Python 3 and PyYAML, then run:

```sh
python3 scripts/validate_blueprint.py blueprints/automation/generic_scene_controller.yaml
```

Expected output is the pass list from `PASS A1 parse_yaml` through `PASS A10 scope_fence_keys`, followed by exit status `0`.