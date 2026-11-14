# 03 — Multi-entity button slots with centralized trigger normalization

**What to build:** Each button slot accepts *multiple* `event.*` entities
(`multiple: true`, `domain: event`), so one automation instance serves paired or
mirrored controllers — the Game Room case where "Game Room Scene Controller"
and "Theater Computer Scene Controller" fire identical actions on buttons 1-4.
Matching a trigger back to its button slot is done once in a top-level
`variables:` block (`triggered_entity`, `event_type`, `button_index`), and every
`choose` branch reads those variables instead of repeating Jinja templates.
The blueprint tolerates empty slots and entity lists of different lengths.

**Blocked by:** 02 — Collapsible per-button sections with all four action slots.

**Status:** ready-for-agent

- [ ] Every per-button entity input uses `multiple: true` and accepts only
      `domain: event`
- [ ] Top-level `variables:` exposes `triggered_entity` (`trigger.entity_id`),
      `event_type` (`trigger.to_state.attributes.event_type`) and `button_index`
- [ ] `button_index` is resolved by membership of the triggered entity in that
      button's configured entity list; an entity configured under two buttons
      resolves deterministically (first matching button, documented)
- [ ] No `choose` branch re-derives the entity or event type inline
- [ ] Demo: two entities in button 1's slot both fire button 1's `pushed` action
- [ ] Unconfigured (empty) button slots do not error and do not capture events
- [ ] Pairing is generic: any two or more controllers exposing the same event
      types can share a slot; no Hubitat/Zooz-specific attributes are assumed
- [ ] Validation command passes