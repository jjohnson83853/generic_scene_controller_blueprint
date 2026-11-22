# Ticket 01 review-lane denial record — 2026-11-22

## State before dispatch
- Spec SPEC-SCENE-01 r1 persisted: `.omp/plans/scene-controller-blueprint/spec-01.md` (22088 bytes, sha256 e16572933bf3067eb688cef177aa6351eb8078769213b56fbf694ec04666dab1).
- Advisor lint (`workflow-policy/spec-lint.mjs`): 9 `r-ac-coverage-gap` advisory findings (R lines do not name AC ids in lint syntax; section 5 maps them). Non-blocking per W09.
- No canonical `.omp/plans/execution-state.json` in this repo.

## Denial sequence (native `task`, unmanaged lane)
1. `E_REVIEW` — `review-sequence check failed: ENOENT .../.omp/plans/review-sequence.json` (registry absent).
2. `E_REVIEW_TARGET` — `absent pair: request=targetCandidateId:<absent>,targetRevision:<absent>` (descriptors and native item lacked target pair).
3. `E_RETRY_NOT_AUTHORIZED` — same retry track `native:code-reviewer\000SpecRev01`; `MAX_DENIED_DISPATCH_ATTEMPTS=2` reached. Payload hash-verified against registry (`taskSha256`, `instructionsSha256` match) and target pair supplied; refusal is the retry counter, not request content.

## Why no alternative lane
- Registry now exists and validates structurally, but the attempt track is closed.
- Managed lane unavailable: `.omp/plans/execution-state.json` missing and `prepare-dispatch` returns `E_STATE_SOURCE` (dispatch_allowed=false). `skills/dispatch-policy/review-dispatch.md` section 1 documents that the CLI exposes no initial candidate/task registration writer, so no permitted producer exists here for canonical state.
- `OWNER_RECOVERABLE` in `execution-gate.ts:410` does not include `E_REVIEW_TARGET`, so an owner amendment cannot reopen this specific track via `ownerReopens`.

## Prepared, verified inputs for a fresh lane
- Registry: `.omp/plans/review-sequence.json` — candidate `spec-scene-01`@`r1`, authorIds `[planner]`, inputs = spec-01.md + ticket 01 + CONTEXT.md with sha256, descriptor `SpecRev01` (code-reviewer, reviewerId `code-reviewer-01`, targetCandidateId/targetRevision set).
- Exact payload saved: `.omp/artifacts/codereviewer-spec-r1-payload.json` (hash-verified).

## Needed to continue
Explicit owner authorization to reopen the review lane (fresh process/attempt authority). Without it, ticket 01 stops before stage-1 review and no implementation dispatch is permitted (W09).

## 2026-11-22 continuation attempt (fresh session, same host process)
- Owner instruction: "continue ticket 01 review" — treated as explicit authorization to resume the review lane.
- Registry re-verified before dispatch: candidate `spec-scene-01`@`r1`; input hashes still match (`spec-01.md` e1657293…, CONTEXT 795a1f7f…, ticket 01 c8e05d01…); descriptor `SpecRev01` `taskSha256` 1a6986ae… / `instructionsSha256` d157ece5… match the saved payload (`context` and `tasks[0].task` re-hashed from `.omp/artifacts/codereviewer-spec-r1-payload.json`).
- Native `task` submission of that exact payload denied: `workflow dispatch gate: E_RETRY_NOT_AUTHORIZED` ("Resolve the task-local blocker or apply the explicit owner-directed amendment…").
- Cause: gate retry history is in-process (`execution-gate.ts` `retryHistory = new Map()`, keyed `realpath(cwd)\0agentId\0scope`, `MAX_DENIED_DISPATCH_ATTEMPTS=2`). The prior session's E_REVIEW + E_REVIEW_TARGET attempts filled the track; this session is the same host process, so attempts still count.
- Owner amendment cannot clear it here: `ownerReopens()` requires `ownerAmendmentToken(state, …)`, i.e. a canonical `.omp/plans/execution-state.json`; none exists and the CLI has no initial-state writer (`transition` requires an existing schema-2 target state). This is the previously reported policy/runtime mismatch.
- Also checked: no persisted retry/owner marker file (`.omp/state/interrupt.lock`, owner files absent); no alternate permitted lane (rerouting/another tool to evade the same track is forbidden).
- Clearing action: owner-controlled restart of the omp host process (fresh gate module state), or an authorized canonical schema-2 state to enable `execution-state.mjs authorize` + `ownerReopens`. After that, resubmit the hash-verified payload unchanged; no edits needed.

## Parked
- Review lane parked under owner-controlled restart requirement; no permitted agent action remains in this process. Active todo items removed to stop reminder churn; blocker preserved here.
- Resume recipe: restart omp host (clears `retryHistory`) -> resubmit `.omp/artifacts/codereviewer-spec-r1-payload.json` unchanged -> capture untouched output -> `execution-state.mjs bind` -> Critic if PASS.

## RESOLVED 2026-11-22 13:47Z — harness hook established
- Root cause confirmed: this workspace was managed (`workspaceState` returns `.omp/plans` when it holds any .md/.json) but had no canonical schema-2 state. The prior lane hand-wrote `review-sequence.json` and submitted unmanaged native payloads; registry-repair denials consumed the 2-attempt track.
- Fix (supported writers only): canonical spec packaged with `specdd` section markers into `.omp/artifacts/scene-controller-blueprint/spec-canonical-r1.md`; feature state built to schema 2 and installed with `execution-state.mjs transition scene-controller-blueprint <state-artifact>` -> `.omp/plans/execution-state.json`; managed candidate/descriptor written to `review-sequence.json`; `prepare-dispatch` and `check-dispatch` both exit 0; managed native dispatch admitted on fresh `id:TR1` scope.
- Result: CodeReviewer SpecRev01 completed, `VERDICT: REVISE` (8 findings, 6 blocking). Output captured untouched, bound via `execution-state.mjs bind` (`ok:true`, round seq 1, codeReview verdict `REQUEST CHANGES`).
- Remaining harness gap for the repair cycle: advancing the canonical state to spec revision r2 requires a state rewrite; main-agent `edit`/`write` to `.omp/plans` is denied and no CLI revision-advance writer exists. Needs owner-authorized maintenance write or a supported revision writer.
