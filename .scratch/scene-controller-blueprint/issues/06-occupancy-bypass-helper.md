# 06 — Automation bypass helper for movie/scene modes

**What to build:** An optional per-button bypass: pressing a scene button (e.g.
"Watch TV", "Theater Mode") sets a chosen `input_boolean` so the separate
occupancy automations (`turn_off_game_room_if_unoccupied`,
`turn_off_living_room_when_not_occupied`) stop re-lighting or killing the room
mid-movie. The blueprint owns only the helper toggle — the occupancy
automations remain the consumers. Pressing the same button again clears the
bypass.

**Blocked by:** 02 — Collapsible per-button sections with all four action
slots.

**Status:** ready-for-agent

- [ ] Per-button optional `input_boolean` bypass target; empty means no bypass
      behavior and no helper calls
- [ ] First fire turns the helper on; second fire turns it off (documented,
      deterministic toggle via `input_boolean.toggle`)
- [ ] Bypass toggle does not replace the configured action slots — both run,
      order documented (bypass first, then actions)
- [ ] Helper state visible in HA matches the expected on/off sequence after two
      presses
- [ ] No occupancy or motion logic is implemented inside the blueprint
- [ ] The bypass helper is an input; no site-specific `input_boolean` is
      hardcoded and no occupancy automation is assumed to exist
- [ ] Independently selectable: shipping 06 alone leaves base dispatch and all
      other slots functional
- [ ] Validation command passes