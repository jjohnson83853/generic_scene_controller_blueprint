# 04 — Restart guard: ignore unavailable transitions and retained replay

**What to build:** Make the button triggers immune to HA restarts and MQTT
broker reconnects. State triggers use `not_from: ["unavailable", "unknown"]`,
and dispatch is additionally gated on a real `event_type` being present so a
retained MQTT replay that merely restores state cannot fire actions. A
restart of HA or reconnect of the broker with a button scene controller
present must run zero actions even if the MQTT broker re-delivers retained
`event.*` state.

**Blocked by:** 03 — Multi-entity button slots with centralized trigger
normalization.

**Status:** ready-for-agent

- [ ] Every button state trigger carries `not_from: ["unavailable", "unknown"]`
- [ ] Dispatch requires a non-empty recognized `event_type`; a state update
      with no/unknown `event_type` is a no-op
- [ ] Restarting HA with controllers already available fires no button actions
- [ ] Simulated broker reconnect (retained state replay) fires no button actions
- [ ] Normal pushed/held/doubleTapped/released still dispatch after the guard
- [ ] The guard logic lives in the shared/central layer (variables or the
      trigger gate), not duplicated per button
- [ ] Guard relies only on standard event-entity state semantics (no MQTT- or
      vendor-specific attributes), so it holds for any transport
- [ ] Independently selectable: shipping 04 alone leaves base dispatch and all
      action slots unchanged
- [ ] Validation command passes