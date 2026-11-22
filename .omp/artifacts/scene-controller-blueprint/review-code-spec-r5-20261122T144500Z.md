## Code Review Summary

**Subject:** SPEC-SCENE-01 r5 — specification mode, repair pass 4. Candidate `.omp/artifacts/scene-controller-blueprint/spec-canonical-r5.md` (sha as dispatched; not recomputed — no shell). Read: candidate whole, r4 review, reviewHistory (F1-F8/H1-H5/K1-K2), ticket 01, ticket 02 cb4, CONTEXT.md, README.md, plan-dir copy. `spec:NN` = candidate lines.

### Closure
- **K1 CLOSED.** A9(b3)(ii) spec:62 defines an edge-bounded token scan (`[a-z0-9_]+` object; neighbours absent or not `[A-Za-z0-9_]`) over non-Jinja `name`/`description` values, keeping Jinja/`!input`/wildcard exemptions. Isolation fixture spec:77 hits `event.hallway_scene_controller_button_1_event`; `hallway` is not one of A9(a)'s enumerated rooms and a sentence cannot fullmatch, so a9 is first after a1-a8 pass. AC10 spec:106 and AC11 spec:107 agree; positive fixture spec:67 is satisfiable only because spec:47 pins dot-free prose.
- **K2 CLOSED.** `hubitat` in `blueprint.description` (spec:77) passes a2-a8 and fails a9(a)'s outside-header rule. `not_from` inside `button_1_entity.selector.entity` (spec:78) lies outside A6's trigger scope and outside a9's scans, and A4 spec:57 is a domain-presence check (spec:78 states the non-exactness normatively), so a10(i) is first. AC10 spec:106, AC11 spec:107, T2 spec:122 name both relocated positions.
- **No regression:** F1-F8, G1-G5, H1-H4 anchors intact (spec:48,57-63,92, §8 STEP 0, §9 tables). R1-R9 → AC1-AC11 complete; ticket-01 only; no vendor/room/node/entity id in executable configuration; D4 triggers/choose statically coherent with HA state-trigger and `event_type`-attribute semantics.

### Issues
1. [LOW][traceability] spec:195 heads “K1-K2 RESOLUTION LEDGER (revision 5)”, but only K1 (spec:197) exists and the file ends there. Contradicts spec:5 (“the K1-K2 resolution ledger is new in this revision”) and spec:92 (“finding -> invariant -> oracle tables … in the resolution ledgers”). No AC/oracle is affected; K2’s substance is at spec:78,87,106,107,122,176. Fix: append the K2 row (root invariant; clauses spec:59/77/78; oracle = both relocated fixtures → exit 1 at a9/a10; unknowns: none).
2. [LOW][documentation-overclaim] spec:35’s closing clause “a sentence carrying a slug is banned, not only a value that IS a slug” exceeds b3(ii)’s `name`/`description` scope; a `label:` sentence is declared residual (ii) at spec:174. A9 spec:62 itself is precise. Fix: qualify with “in `name`/`description` prose”.

### Open Questions (low-confidence)
- A4 spec:57 states only the domain restriction; the non-exactness three a10 fixtures depend on appears only at spec:78 — adding it to A4 would remove a T1 a4-first-failure risk.
- A7 spec:48/60 accept `conditions` as a bare string or one-element list; HA validity of the bare-string branch form is unverified (U1) and undistinguished by fixtures. Pre-existing since r3.

### Positive Observations
Repairs are oracle-only: no AC weakened, no fixture silently reclassified; residuals (i)-(iii) are now disclosed at spec:174.

### Limits
No shell/git/LSP/HA: candidate sha, `git status`, validator and tests unrun; plan-dir verified by content only (r3 header + rev3 A9, matching §3); HA semantics static; byte equality deferred to STEP 0.

### Recommendation
APPROVE
