VERDICT: REQUEST CHANGES

## Code Review Summary
**Subject:** SPEC-SCENE-02 r1 — specification mode, initial pass. Candidate `.omp/artifacts/scene-controller-blueprint/spec-canonical-t02-r1.md` (sha not recomputed — no shell). Read: candidate whole, ticket 02, CONTEXT.md, r5, current blueprint/validator/tests/README, official HA blueprint-schema and choose docs. `spec:N` = candidate line. **Issues:** 8 (3 HIGH, 2 MEDIUM, 3 LOW).

### Blocking
1. [HIGH][contract] A9/design require a `branches` key under `choose` (spec:48,63,67; a9 fixture spec:81; AC8/9 spec:111-112). HA choose is `- choose: [branch...]` with an optional `default` sibling; the current blueprint/validator do this. T1 following A9 yields non-HA YAML or must deviate, and the "default added to choose" fixture cannot be a one-mutation of the real file. Fix: action-step keys EXACTLY {choose}, `choose` value = 20-element list, no `default` sibling; update A9/D5/design/AC8/AC9/T2 and the fixture.
2. [HIGH][feasibility] R1/R2 (spec:10-11) pin five `collapsed: true` sections holding a required `button_N_entity` with no default; official HA docs require all inputs in a collapsed section to have a default before they can be hidden. R6/AC11/checkbox 5 promise five collapsed headers; no decision or residual records this. Fix: resolve (generic entity default + adjusted required semantics, no-collapse/split, or owner/ticket amendment) and record the UI consequence; add `min_version`.
3. [HIGH][fence] A13 (spec:67) relies on exact-key pins for `collapsed`/`icon` outside sections, but A5 (spec:59) pins only the section's inner input-name map, not each inner input entry's keys, and A6 is presence-only. Counterexample: `button_1_pushed: {name, description, icon: mdi:x, selector: {action: {}}, default: []}` or `icon` inside `button_1_entity.selector.entity` passes A5-A13. Contradicts R10/T1, A13, and §9 item 4's "no such position / every mapping pinned". Fix: path-aware collapsed/icon ban (or exact-pin every inner entry/selector) plus AC15/T2 fixtures.
4. [MEDIUM][metadata] Input sections require HA ≥2024.6.0; docs say set `blueprint.homeassistant.min_version`. The contract/A2 omit it; R3/AC6 and the UI check depend on the owner's version. Fix: add min_version to the contract, A2 + negative fixture, README/T2, or record the owner decision.
5. [MEDIUM][regression] r5 AC7's `branch sibling action` and `action sibling step` fixtures (current tests a7) are absent from the a9 list/AC8/AC9; §9 item 3 says no oracle is lost. A9 asserts no steps outside the choose and no sibling sequence steps, but no fixture exercises them. Fix: add both fixtures, first-failure a9.

### Advisory
- [LOW] AC8 "in-list template" reads as rejecting the one-element list A9 accepts; reword to "one-element list wrapping a non-canonical template".
- [LOW] R10's supersession omits the 01-R9 held/doubleTapped/released slot fence (implicitly superseded by R4); add it.
- [LOW] §5 "every AC names its command/exit code; every oracle is structural, never source-text" overclaims: AC6/AC11 have no local command; A10 is a header-comment oracle. Qualify.

### Positive Observations
R1-R10→AC1-AC15; all seven checkboxes traceable; carried 01-R2/R3/R6/R7/R8; A11 both b3 legs with no icon exemption (a4 positive pin); a13 fixtures correctly relocated inside `selector.entity`; 20-branch four-event coverage/order; D5 empty-slot composition; T1 four-file RED/GREEN and read-only T2; flat `!input` names confirmed by HA docs; no vendor/model/node/room/entity id is prescribed in configuration or name/description prose (the header's Hubitat provenance is the carried D2/A11(a) exception).

### Limits
No shell/git/LSP/HA: candidate sha, `git status`, validator, and tests unrun; §3's clean-tree claim is [INFERENCE]. HA semantics verified from official docs only; runtime/UI remain U1.

### Recommendation
REQUEST CHANGES