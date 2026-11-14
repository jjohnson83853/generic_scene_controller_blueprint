# 05 — Smart toggle and scene cycling for a button slot

**What to build:** An optional per-button "smart toggle" mode so a press acts on
room state instead of firing a blind `turn_on`: if any configured target light
is on, the press turns the room off; if all are off, it activates the default
scene (or, when a cycle helper is configured, advances an `input_select`
through Off → Dim → Bright by moving to its next option). Each of the five
button slots can opt in independently; leaving it off keeps the plain action
slots unchanged.

**Blocked by:** 02 — Collapsible per-button sections with all four action
slots.

**Status:** ready-for-agent

- [ ] Per-button (or per-slot) opt-in toggle exposes: target light entities,
      a default scene, and an optional `input_select` cycle helper
- [ ] Opt-in off: existing action slots behave exactly as before, no state
      reads performed
- [ ] All targets off → default scene activates (or cycle helper selects its
      first/second option when cycling is configured)
- [ ] Any target on → all targets turn off (or cycle helper advances)
- [ ] Cycle helper advances in order and wraps; helper with a single option
      does not error
- [ ] Missing default scene with cycling disabled falls back to turning the
      targets on rather than raising a template error (documented fallback)
- [ ] Button slot fires on `pushed` only; other event types unchanged
- [ ] All room-specific entities (targets, scene, cycle helper) are inputs;
      none are hardcoded
- [ ] Independently selectable: shipping 05 alone leaves base dispatch and all
      other slots functional
- [ ] Validation command passes