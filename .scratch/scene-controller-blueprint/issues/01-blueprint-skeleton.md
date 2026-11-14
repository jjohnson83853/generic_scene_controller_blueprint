# 01 — Importable blueprint skeleton: five buttons, push actions only

**What to build:** A single Home Assistant automation blueprint that imports
into HA from the repo and drives one action per button on `pushed` events. This
is the tracer bullet: blueprint metadata, one event-entity input per button
(1-5), one action input per button, state trigger on the button entities, and a
`choose` that dispatches the matching button's action. Non-`pushed` event types
do nothing yet. Repo also gets a one-command local validation (`python` YAML
load at minimum) so every later ticket can be checked mechanically. The
blueprint is **generic**: all five buttons are configured `event.*` entities
supplied through inputs — no vendor, model, node id, room, or entity id appears
anywhere in the file (see `../CONTEXT.md`).

**Blocked by:** None — can start immediately.

**Status:** ready-for-agent

- [ ] `blueprint:` block declares `name`, `description`, `domain: automation`
      and an `input:` map covering buttons 1-5 (entity + action each)
- [ ] Entity inputs accept only `domain: event`; action inputs use the `action`
      selector and are optional
- [ ] Blueprint loads in HA (Settings → Automations → Blueprints) with no error
- [ ] A `pushed` event on a configured entity runs that button's action; no
      action configured means no-op rather than error
- [ ] `held`, `doubleTapped`, `released` events run nothing
- [ ] Repo-local validation command documented in README and passing on the
      blueprint file
- [ ] Header comment documents supported event types and the MQTT/Hubitat
      origin, per `../CONTEXT.md`
- [ ] No vendor, model, node id, room name, or concrete entity id is
      hardcoded; every controller comes from the input map (generic by design)