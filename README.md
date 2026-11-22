# Generic Scene Controller Blueprint

A generic Home Assistant automation blueprint accepts five event-entity inputs in independently collapsible button sections. Each button has four separate action slots for `pushed`, `held`, `doubleTapped`, and `released` events.

## Repository layout

- `blueprints/automation/generic_scene_controller.yaml` — importable automation blueprint.
- `scripts/validate_blueprint.py` — structural validation using Python 3 and PyYAML.
- `tests/test_validate_blueprint.py` — validator regression tests.

## Minimum Home Assistant version

Input sections require Home Assistant 2024.6.0 or later. The blueprint declares `blueprint.homeassistant.min_version: "2024.6.0"`.

## Import into Home Assistant

In Home Assistant, open **Settings → Automations & Scenes → Blueprints** and choose **Import Blueprint**. Provide the raw file URL or local path for `blueprints/automation/generic_scene_controller.yaml`, then create an automation from the imported blueprint and configure the five collapsed button sections. Select a valid event entity for every button before saving; Home Assistant rejects the save while any entity input is still blank. The live import and automation trace are verified in Home Assistant by the user; they are not checked by the local validator.

## Validation

Install Python 3 and PyYAML, then run:

```sh
python3 scripts/validate_blueprint.py blueprints/automation/generic_scene_controller.yaml
```

Expected output is the pass list from `PASS A1 parse_yaml` through `PASS A13 scope_fence_keys`, followed by exit status `0`. Run the offline regression suite with `python3 -m unittest discover -s tests -v`.