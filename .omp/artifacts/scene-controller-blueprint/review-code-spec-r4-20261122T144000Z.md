## Code Review Summary

**Subject:** SPEC-SCENE-01 r4 - specification mode, repair pass 3. Candidate sha256 52bf3f97... (dispatch; not recomputed). Read candidate whole, r3 review, T01, T02 cb4, CONTEXT, README, plan-dir, review-sequence. `spec:NN` = candidate lines.

**Closure (text-verified):** H1 CLOSED: A7 spec:59 asserts `{{`/`}}` before stripping; bare-expression fixture spec:74 and AC6 spec:99. H2 CLOSED: A6 spec:58 exact `{platform,entity_id,id}`; `to` fixture spec:73 (but see F2). H3 CLOSED: A10(ii) spec:62 root keys `{blueprint,trigger,action}`; root-sun fixture spec:77; AC11 spec:104 enumerates a3/a6/a7/a9(b3)/a10 and matches implementation. H4 CLOSED: spec:23 plan-dir observed = rev3 header + rev3 A9 (plan copy line 58); byte equality deferred to STEP 0 spec:133 recorded sha/cmp. H5 NOT CLOSED (F1). F1-F8/G1-G5 intact; R1-R9 -> AC1-AC11 complete; ticket-01 only; config free of vendor/room/node/entity ids; HA wiring statically valid; positive fixture passes.

### Issues

1. [HIGH][oracle-gap] H5 prose rule is not the stated oracle. Confidence: HIGH.
   spec:61 b3 fires only on values that FULLMATCH `<domain>.<object_id>`, yet spec:76 and AC10 spec:103 require description `controls event.hallway_scene_controller_button_1_event` to fail b3 ALONE. A sentence does not fullmatch (`hallway` is not an A9(a) token), so the isolation fixture returns 0: T1 GREEN is unreachable and spec:34/187's "curated-domain slugs banned in prose" claim is false for embedded slugs.
   Fix: make b3 scan non-Jinja prose for entity-id tokens (boundary regex; keep wildcard/Jinja exemptions), OR keep fullmatch and use an exact-value description plus disclose the embedded-slug residual; update spec:76/103/187.

2. [MEDIUM][oracle-gap, repair-induced] A6 exact trigger keys preempt two later fixtures. Confidence: HIGH.
   A6 spec:58 (order spec:51; first-failure contract spec:65) rejects extra trigger keys, so `hubitat: true` in trigger 1 (spec:76, listed under a9) and `not_from` in trigger 1 (spec:77, claimed "-> exit 1 at a10") now first-fail a6. The a9 header-boundary leg and the a10 `not_from` leg are unproven; if tests assert the named assertion (natural reading of spec:65), both fail.
   Fix: move both mutations where A6 does not govern (`hubitat` in `blueprint.description`; `not_from` inside `button_1_entity.selector.entity`), or reclassify them as a6 fixtures and add fresh a9/a10 fixtures; update AC10/AC11/T2.

### Open Questions (low-confidence)

- spec:59 A7 internal-whitespace normalization latitude (flagged item 7); no false accept found for the mandated bytes.
- A curated-domain slug in a header comment escapes b3 (comments unparsed) and A9(a) unless a room token is present; no such position in the mandated file, but H5's unknowns omit it.

### Positive Observations
H1/H2/H3 oracles are falsifiable and do not reject the mandated delimited/three-key/root-key-set design; H4 provenance is now observational; AC11 no longer overstates; F/G repairs intact.

### Limits
No shell/git/LSP/HA; sha not recomputed; validator/tests unrun; HA semantics static; plan-dir compared by content (header + rev3 A9), not bytes.

### Recommendation
REQUEST CHANGES
