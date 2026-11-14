# 07 — Bounded hold-to-dim loop on held + released

**What to build:** Native-feeling dimming over MQTT for HA-managed lights (Govee
etc.): when a button slot opts in, `held` starts stepping the target
brightness every 250-400 ms and `released` (or a `pushed` arriving on the same
button) stops the loop. The loop is a `repeat: until:` with a safety cap of
~15-20 iterations, so a dropped `released` packet can never dim forever. Step
size, delay, and iteration cap are inputs with sane defaults; direction can be
inverted for brighten-on-hold.

**Blocked by:** 02 — Collapsible per-button sections with all four action
slots.

**Status:** ready-for-agent

- [ ] Per-button opt-in exposes: target lights, `brightness_step_pct` (default
      in the 5-15% range), delay (default 250-400 ms), and iteration cap
      (default ~15-20)
- [ ] `held` starts the loop; `released` stops it within one step delay
- [ ] Loop terminates on the cap even if `released` never arrives
- [ ] Loop stops when the automation's `released` trigger arrives on any
      entity configured in that button slot (multi-controller safe)
- [ ] Opt-in off: `held`/`released` slots behave exactly as plain action slots
- [ ] Letting go restores nothing implicitly; brightness is left at the final
      stepped value (documented)
- [ ] Targets that are off are not turned on by dimming (state-guarded,
      documented)
- [ ] Targets and timing are inputs; no vendor or model assumptions (works on
      any `event.*` controller exposing `held`/`released`)
- [ ] Independently selectable: shipping 07 alone leaves base dispatch and all
      other slots functional
- [ ] Validation command passes