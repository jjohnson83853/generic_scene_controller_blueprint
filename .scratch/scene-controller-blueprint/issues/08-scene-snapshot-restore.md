# 08 — Pre-scene snapshot and restore

**What to build:** Before an override scene activates (`scene.theater`,
`master_bedroom_watch_tv`), optionally snapshot the target lights' brightness
and color into a generated `scene.create` entity, so a later press (or hold) of
the same button restores the exact prior state instead of a hardcoded fallback
scene. Snapshot entities use a stable per-button id so repeated presses overwrite
rather than accumulate.

**Blocked by:** 02 — Collapsible per-button sections with all four action
slots.

**Status:** ready-for-agent

- [ ] Per-button optional snapshot toggle, list of `snapshot_entities`, and the
      override scene to activate
- [ ] With snapshot on: first press creates/overwrites a stable per-button
      snapshot scene and activates the override scene
- [ ] Subsequent press/hold with a snapshot present restores it and clears or
      marks the snapshot as consumed (documented, no stale restore)
- [ ] Snapshot entity id is deterministic per button and does not grow in count
- [ ] Snapshot off: previous behavior unchanged, no scene entities created
- [ ] Snapshot of entities that are off/unavailable does not error and is
      captured as-is / skipped (documented)
- [ ] Snapshot targets and override scene are inputs; no room-specific scene or
      entity ids are hardcoded
- [ ] Independently selectable: shipping 08 alone leaves base dispatch and all
      other slots functional
- [ ] Validation command passes