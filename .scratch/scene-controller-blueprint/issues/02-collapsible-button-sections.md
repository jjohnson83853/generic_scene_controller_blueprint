# 02 — Collapsible per-button sections with all four action slots

**What to build:** Replace the flat input list with one collapsible `input:`
section per button — collapsed by default, titled Button 1…Button 5 with icons
`mdi:numeric-1-box-outline` … `mdi:numeric-5-box-outline` — each holding the
button's event entity and four action slots: `pushed`, `held`, `doubleTapped`,
`released`. The `choose` branches on the trigger's `event_type`, and the
automation runs `mode: parallel` so a held-then-released pair or two near-
simultaneous presses cannot abort each other. Empty slots are no-ops.

**Blocked by:** 01 — Importable blueprint skeleton.

**Status:** ready-for-agent

- [ ] Five inputs marked `collapsed: true`, one per button, each with the
      numbered `mdi:numeric-N-box-outline` icon
- [ ] Each section contains the entity input plus four optional `action`
      selectors named `pushed`, `held`, `doubleTapped`, `released`
- [ ] The four event types each dispatch to their own slot; an empty slot
      produces no action and no error
- [ ] Automation `mode: parallel`; two overlapping button presses both run
- [ ] UI check in HA: default view shows only five collapsed section headers,
      not ~15-20 loose fields
- [ ] Only the numbering and icons are fixed UI; no device-specific labels,
      defaults, or entity ids are baked in (generic for any event-entity
      controller)
- [ ] Validation command still passes