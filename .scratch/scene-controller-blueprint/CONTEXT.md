# Context: Home Assistant Scene Controller & Automation Consolidation

Shared background for every ticket in this backlog. Read this first.

## Current architecture & state

- Zooz ZEN32 and ZEN35 scene controllers are exposed to Home Assistant via MQTT
  discovery from a Hubitat Elevation hub, which acts as the Z-Wave mesh
  coordinator and MQTT export bridge (`appId: 646`, broker `192.168.50.72:1883`).
- The multi-button scene controllers (`484` Master Bedroom, `485` Game Room,
  `491` Living Room, `499` Theater Computer) are configured as **read-only**
  (`readableDevices`) in Hubitat MQTT Export, so their button events publish
  cleanly to MQTT without command-topic collisions. **No LED sync parameters**
  (484, 485, 491, 499) are exposed in HA; blueprints must not offer LED inputs.
- HA surfaces each button as a native `event.*` entity, e.g.
  `event.living_room_scene_controller_button_1_event`, with `event_type` values
  `pushed`, `held`, `doubleTapped`, `released`.
- Two physical controllers in the Game Room ("Game Room Scene Controller",
  "Theater Computer Scene Controller") trigger the *same* actions on buttons 1-4.

## Problem being solved

- ~13 fragmented HA automations handle button events. Many use brittle legacy
  `domain: hubitat` device IDs instead of the unified MQTT `event.*` entities;
  some slots have duplicate/conflicting bindings (e.g. Master Bedroom button 1).
- Goal: one MQTT event-entity blueprint (+ shared action scripts) that replaces
  them, with restart safety (ignore retained MQTT replays), no dead triggers,
  and room occupancy/media logic kept decoupled from wall-switch presses.

## Blueprint scope decisions (agreed)

Include:

- Collapsible per-button input sections (buttons 1-5), icons
  `mdi:numeric-1-box-outline` … `mdi:numeric-5-box-outline`.
- `multiple: true` event-entity selectors per button (merges paired
  controllers in one automation instance).
- `pushed` / `held` / `doubleTapped` / `released` action slots per button,
  automation `mode: parallel`.
- `not_from: ["unavailable", "unknown"]` restart guards.
- Central top-level `variables:` computing `triggered_entity`, `event_type`,
  `button_index` once (no repeated Jinja per branch).

Skip:

- LED sync parameters (read-only on the Hubitat side).
- Complex per-button time/sun conditions; time and occupancy logic stays in the
  dedicated occupancy automations (`turn_off_game_room_if_unoccupied`,
  `turn_off_living_room_when_not_occupied`).

## Generic by design

This repo targets **generic** multi-button scene controllers exposed to HA as
`event.*` entities emitting `pushed`, `held`, `doubleTapped`, `released` —
whatever the vendor or transport. Nothing vendor- or site-specific may be baked
into the blueprint: no Hubitat device ids, no `domain: hubitat` targets, no Zooz
model numbers, node ids, room names, or entity ids. Every controller entity,
light, scene, `input_select`, and `input_boolean` is an input. The Game Room
pair, Master Bedroom, Living Room, and Theater Computer are *reference
instances*, not assumptions the blueprint may encode.

## Selective scope

Tickets 01-03 are the irreducible core. Every feature ticket (04-08) is
independent, opt-in, and individually selectable: adopting any subset must leave
the blueprint functional, and disabling a feature must restore base dispatch
unchanged. Features are not v1-mandatory — they can be picked from the backlog
later, so no ticket may assume a sibling feature shipped.

## Borrowed patterns (source blueprints)

- Blackshome/sensor-light-add-on: collapsible sections, pre-scene snapshot.
- codingPear/vacuum-control-via-one-single-button: state-aware toggles.
- Ltek/repeating-alerts-ltek: central variables + restart guard.
- Community ZEN32/ZEN35 blueprints: bounded hold-to-dim `repeat: until:` loop.