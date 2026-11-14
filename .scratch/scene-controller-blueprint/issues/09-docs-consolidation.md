# 09 — Usage docs, example instances, and consolidation checklist

**What to build:** Make the blueprint consumable and close the migration: README
usage section (import, inputs, per-feature opt-ins, troubleshooting), example
automation YAML for the Game Room paired controllers (two `event.*` entities on
buttons 1-4), and a consolidation checklist mapping each of the ~13 legacy
`domain: hubitat` automations to a blueprint instance or an explicit deletion —
including the duplicate Master Bedroom button 1 binding. Document what is
intentionally out of scope (LED sync, time/sun conditions).

**Blocked by:** 03 — Multi-entity button slots with centralized trigger
normalization; 04 — Restart guard. Feature tickets 05-08 are not blockers:
documentation is written for whichever of them is implemented.

**Status:** ready-for-agent

- [ ] README covers import steps, all inputs, defaults, and the four event types
- [ ] README states LED sync parameters are unsupported (read-only in Hubitat
      MQTT Export) and per-button time/sun conditions are excluded by design
- [ ] Example instance YAML for the Game Room pair (buttons 1-4, both
      controllers in one automation) is included and valid
- [ ] Migration checklist enumerates every legacy automation to replace or
      delete, with the target blueprint instance and the duplicate Master
      Bedroom button 1 binding resolved
- [ ] README presents the blueprint as **generic** for any multi-button
      `event.*` controller (pushed/held/doubleTapped/released), with the
      Hubitat/MQTT ZEN32/ZEN35 deployment shown as one reference instance
- [ ] Documentation is per-feature sectioned so any selected subset of tickets
      05-08 can be documented and shipped without the others
- [ ] Validation command passes on the blueprint and the example YAML
- [ ] No dead triggers or legacy `domain: hubitat` device ids remain in the
      documented end state