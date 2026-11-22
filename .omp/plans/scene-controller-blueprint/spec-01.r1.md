SPEC-SCENE-01 — revision 1 — STATUS: DRAFT
Objective: specify the importable generic five-button Home Assistant automation blueprint skeleton for ticket 01, plus its one-command repo-local mechanical validation.

== 1. STATUS ==
Spec ID SPEC-SCENE-01, revision 1. DRAFT. One-sentence objective: ship one generic HA automation blueprint file (five event-entity buttons, push-only dispatch) plus a python3/PyYAML structural validator and README validation docs, all machine-checkable in this repo.

== 2. REQUIREMENTS ==
Stable IDs map 1:1 to ticket 01 checkboxes (issues/01-blueprint-skeleton.md):
R1 (checkbox 1): The repo ships one HA blueprint file whose `blueprint:` block declares `name`, `description`, `domain: automation`, and an `input:` map with, for each button N in 1..5, exactly one event-entity input and one action input (ten inputs total).
R2 (checkbox 2): Entity inputs accept only `event.*` entities (`entity` selector restricted to `domain: event`) and are required; action inputs use the `action` selector, are optional, and default to an empty action sequence.
R3 (checkbox 3): The blueprint loads in Home Assistant (Settings -> Automations -> Blueprints) with no import error.
R4 (checkbox 4): A `pushed` event on configured button N runs button N's action input; an unconfigured (default-empty) action input is a no-op, not an error.
R5 (checkbox 5): `held`, `doubleTapped`, `released` events on any configured button run nothing.
R6 (checkbox 6): A one-command repo-local validation runs on python3+PyYAML, is documented in README, and passes on the blueprint file.
R7 (checkbox 7): The blueprint's leading header comment documents the four supported event types (`pushed`, `held`, `doubleTapped`, `released`) and the MQTT/Hubitat origin of the event-entity pattern, per CONTEXT.md.
R8 (checkbox 8): No vendor, model, node id, room name, or concrete entity id is hardcoded; all five controller entities come from the input map (generic by design; CONTEXT.md "Generic by design" rules).
R9 (scope fence / non-goals): No per-button collapsible sections or icons (ticket 02); no `multiple: true` entity selectors or central `variables:` (ticket 03); no `not_from: [unavailable, unknown]` restart guard (ticket 04); no held/doubleTapped/released action slots; no LED sync inputs (CONTEXT.md: read-only on hub side — never in scope); no per-button time/sun conditions; no shared action scripts; nothing from tickets 05-09. The chosen structure must remain ADDITIVE for tickets 02-04.

== 3. EVIDENCE AND UNCERTAINTY ==
VERIFIED (evidence): repo root contains only README.md (36 bytes, single heading), LICENSE, .git/, .scratch/ (directory read, 2026-11-22); working tree clean at 4ff9f85 on main; no blueprint or validation file exists. `python3` 3.13.5 with PyYAML 6.0.2 importable (`python3 -c 'import yaml'` exit 0). No Home Assistant instance reachable from this workstation. Origin remote git@github.com:johnson83853/generic_scene_controller_blueprint.git, branch main.
[AUTO-DECISION] D1 (file layout): blueprint at `blueprints/automation/generic_scene_controller.yaml` — the community-repo convention path for HA blueprint imports. Consequence: README import instructions cite this exact path; validator default target is this path.
[AUTO-DECISION] D2 (conflict, reported not narrowed): ticket checkbox 7 requires the header comment to document "the MQTT/Hubitat origin", while CONTEXT.md's generic-by-design rule bans vendor names in repo artifacts. These conflict on the literal string "Hubitat". Resolution: the four event types plus ONE provenance sentence naming MQTT discovery and the Hubitat Elevation hub may appear ONLY inside the leading comment block (documentation prose); every machine-executed configuration byte (selectors, triggers, conditions, actions) stays vendor-free. Validator assertion A9 enforces this: the genericity denylist scans the ENTIRE file for Zooz/model numbers (`zooz`, `zen3[0-9]+`), IPv4 literals, the reference room-name denylist, concrete-entity-id pattern `event\.[a-z0-9_]+`, and `hubitat` OUTSIDE the leading comment block. Consequence: a reviewer may overturn this by choosing the stricter reading, but that reading weakens a binding ticket AC, which the planner may not do.
[AUTO-DECISION] D3 (optional actions): each action input carries `default: []`; HA substitutes an empty action sequence, so an unconfigured action renders as a no-op (R4's second clause) rather than an input-required error.
[AUTO-DECISION] D4 (dispatch wiring): five state triggers, each `{platform: state, entity_id: !input button_N_entity, id: button_N}`; choose branch N condition template: `trigger.id == 'button_N' and trigger.to_state is not none and trigger.to_state.attributes.get('event_type') == 'pushed'`; branch N sequence: `!input button_N_action`; no `default:` on choose. Rationale: `attributes.get()` avoids undefined-attribute render errors when HA restart/restore updates state without `event_type` (lifecycle counterexample below); `trigger.id` matching keeps dispatch independent of concrete entity ids and stays additive for ticket 03 (`multiple: true` — same trigger id dispatches any merged entity) and ticket 04 (`not_from` guard added to the same triggers).
[AUTO-DECISION] D5: automation `mode: parallel` now — listed under CONTEXT.md's agreed "include" decisions and assigned to NO later ticket (02=sections, 03=multi-entity+variables, 04=restart guard); physical five-button controllers can push concurrently. No R9 conflict.
[AUTO-DECISION] D6 (validator extensibility): validator asserts REQUIRED PRESENCE of the ten ticket-01 input keys and their per-key constraints — not an exact key set — so tickets 02-04 can add inputs/branches without editing the validator's shape contract. It DOES assert exact structural wiring for what ticket 01 builds (five triggers, five pushed branches, one action input per branch).
[AUTO-DECISION] D7 (test framework): stdlib `unittest` in `tests/test_validate_blueprint.py`, run via `python3 -m unittest discover -s tests` — pytest availability is UNVERIFIED on this workstation; python3+PyYAML are the only verified runtime dependencies, and the validator/tests use only those. If the verifier confirms pytest exists, switching runner is a same-envelope implementation detail, not an AC change.
UNKNOWN / UNVERIFIABLE (recorded limits, not blockers):
U1: live HA import (R3) and runtime `pushed` dispatch (R4) cannot be executed locally — no HA instance reachable. Verification method: the owner imports the file in a real HA instance and watches the blueprint-created automation trace. The local oracle proves static YAML validity + structural wiring ONLY; nothing in this repo's artifacts may claim runtime proof.
U2: exact HA UI rendering of `default: []` on an `action` selector input is assumed to follow the standard community-blueprint pattern; only U1's live import closes this.

== 4. DESIGN ==
Selected approach: one declarative blueprint file + one structural validator script + README docs + validator-behavior tests. No services, no dependencies beyond PyYAML.
Blueprint contract (structure, not source text):
- File `blueprints/automation/generic_scene_controller.yaml` (D1).
- `blueprint.name`: "Generic Multi-Button Scene Controller"; `blueprint.description`: generic one-liner naming event-entity scene controllers and push-only dispatch; no vendor/room/entity ids in these strings.
- `blueprint.domain`: `automation`; `blueprint.input`: for N in 1..5: `button_N_entity` = {name, description, selector: {entity: {domain: event}}} (required, no default); `button_N_action` = {name, description, selector: {action: {}}, default: []}.
- Top-level `mode: parallel` (D5); `trigger`: five entries per D4; `action`: `choose` with five branches per D4; no `default:` on choose (non-matching triggers — held/doubleTapped/released — fall through doing nothing, R5).
- Leading comment block (before the first `---`): the four event types, the event-entity-via-MQTT-discovery provenance sentence (D2), and a push-only note.
Validator contract — `scripts/validate_blueprint.py`, python3, stdlib+PyYAML only:
- Invocation: `python3 scripts/validate_blueprint.py <blueprint.yaml>` (README documents it with the D1 path).
- Exit codes: 0 = all assertions pass (pass list printed); 1 = an assertion failed (assertion name + reason on stderr); 2 = usage error / file not found. Deterministic, no network.
- Assertions (distinct, each AC-mapped):
  A1 parse_yaml (yaml.safe_load or equivalent succeeds).
  A2 blueprint_metadata (name, description non-empty; domain == automation; input is a mapping).
  A3 button_inputs_required (all ten keys button_{1..5}_{entity,action} PRESENT per D6; each has non-empty name+description).
  A4 entity_selectors_domain_event (each `button_N_entity` selector is an entity selector restricted to domain event).
  A5 action_selectors_optional (each `button_N_action` uses the action selector and carries default []).
  A6 state_triggers (five state triggers; trigger N has entity_id bound to the `!input button_N_entity` tag and id `button_N`).
  A7 choose_dispatch_pushed (five choose branches; branch N condition references trigger.id 'button_N' AND 'pushed'; branch N sequence bound to `!input button_N_action`; no branch dispatches any event type other than 'pushed').
  A8 header_comment (leading comment block contains all four event type strings and the MQTT/Hubitat provenance wording).
  A9 generic_denylist (D2 rule: scan entire file for zooz/zen3x/IPv4/room-name/entity-slug patterns — banned everywhere including header; `hubitat` allowed only inside the leading comment block).
- `!input` tag checks: PyYAML drops custom tags by default; the engineer reconstructs tags (e.g. a custom Constructor registering `!input`) within this contract — mechanism is an implementation detail owned by the engineer, semantics fixed by A6/A7. No source-text trivia assertions.
README.md additions (edit existing 36-byte file): one-paragraph purpose (generic event-entity scene-controller blueprint); repo layout; HA import instructions (Settings -> Automations -> Blueprints, URL/raw-path import of the D1 file); Validation section with the exact command and the python3+PyYAML requirement; a one-line note that live import is performed by the user in HA (not machine-verified in-repo).
Tests `tests/test_validate_blueprint.py` (stdlib unittest): test_validate__real_blueprint_passes (subprocess validator on the real file, exit 0); one negative fixture per assertion written under a tempfile dir — wrong/missing entity selector domain, action input missing `default: []`, missing input key, bad trigger id, choose branch wired to the wrong action input, a `held` branch added, header missing `doubleTapped`, denylist hits (zooz, room name, `event.<slug>`, `hubitat` in configuration) — each expects exit 1 with the assertion name in stderr; usage error expects exit 2. No network, no HA, no fixtures committed as repo artifacts (temp dirs only).
W09E risk evidence (matrix, shared packet = this spec + ticket + CONTEXT):
- Lifecycle (producer: repo file; consumer: HA blueprint import; invalidation: blueprint edits require re-import; restart: HA reload may restore event-entity state without event_type attributes): counterexample — a state trigger firing during restart-restore with missing `attributes.event_type` would make a Jinja direct-attribute access raise inside the condition; mitigated NOW by D4 (`to_state is not none` + `attributes.get(...)`); the full `not_from: [unavailable, unknown]` guard stays ticket 04 (R9 fence) and is an accepted residual until 04 ships. Import counterexample: a file with an invalid input-selector shape fails only at UI import — A2-A5 pre-empt the shape classes the validator can see.
- Shared state: NOT APPLICABLE — reason: one declarative YAML file with no concurrent writers; repo writes flow through git on main; HA-side instances are per-user copies frozen at import time. Consequence: no locking/transaction design; the validator is idempotent and read-only.
- Contract: counterexample — an entity input WITHOUT `domain: event` restriction would accept `light.*`, whose state changes carry no `event_type`, so every choose branch silently never matches (buttons appear dead); hence A4 pins selector domain (AC3) and A6 pins trigger-to-input wiring so no trigger can reference a non-input entity.
- Authority: ticket ACs binding and unweakened; R9 fence excludes 02-09; implementation permission belongs to the coordinator's dispatch, not this spec; [AUTO-DECISION]s are coordinator-persisted to the decision log.
- Observability: section 7 (loaded skill://observability-contract).
- Repair closure: N/A for this initial plan — no findings supplied; taxonomy classes reserved for revision rounds.

== 5. ACCEPTANCE CRITERIA ==
Primary command (all structural ACs): `python3 scripts/validate_blueprint.py blueprints/automation/generic_scene_controller.yaml` -> exit 0 with the named assertion in the pass list. Negative oracle: the matching unittest fixture -> exit 1.
AC1 -> R1: assertion A2 passes (primary command); test_blueprint_metadata_negative proves A2 falsifiable.
AC2 -> R1: assertion A3 passes (primary command); fixture deleting `button_3_action` -> exit 1.
AC3 -> R2: assertion A4 passes (primary command); fixture with unrestricted entity selector -> exit 1.
AC4 -> R2: assertion A5 passes (primary command); fixture action input without `default: []` -> exit 1.
AC5 -> R3: LOCAL LIMIT (U1): primary command exit 0 is NECESSARY static evidence (valid YAML + blueprint schema shape); the observable "loads in HA with no error" is verified only by the owner importing the file in a live HA instance. Recorded UNVERIFIED locally; never inferred from validator output.
AC6 -> R4: assertions A6+A7 pass (primary command); fixtures — trigger id `button_2` on trigger 1; branch 1 sequence wired to `!input button_2_action` -> exit 1 each. Runtime execution of the configured action is U1-unverifiable locally; structural wiring is the local oracle.
AC7 -> R5: A7's no-other-event-types leg passes (primary command); fixture adding a `held` branch -> exit 1.
AC8 -> R6: (a) `grep -n "python3 scripts/validate_blueprint.py blueprints/automation/generic_scene_controller.yaml" README.md` matches the documented command verbatim; (b) that command exits 0; (c) `python3 -m unittest discover -s tests -v` exits 0.
AC9 -> R7: assertion A8 passes (primary command); fixture header missing `doubleTapped` -> exit 1.
AC10 -> R8: assertion A9 passes (primary command); fixtures — `zooz` anywhere, `event.living_room_scene_controller_button_1_event` slug, `hubitat` in configuration (outside leading comment) -> exit 1 each. The leading-comment Hubitat provenance sentence is the documented D2 exception.
Oracle separation (shared-oracle guard): AC1<->A2, AC2<->A3, AC3<->A4, AC4<->A5, AC6<->A6+A7, AC7<->A7-dispatch-leg, AC9<->A8, AC10<->A9 are distinct assertions/tests; AC5 and AC8 have non-overlapping oracles by construction (U1 limit statement; README grep + command execution).

== 6. TASK LEDGER ==
T1 (engineer; owns production code + permanent tests; blockedBy: none):
- Objective: implement blueprint, validator, README, tests to this spec, RED -> GREEN.
- Required inputs/evidence: `.scratch/scene-controller-blueprint/issues/01-blueprint-skeleton.md`, `.scratch/scene-controller-blueprint/CONTEXT.md`, this spec; verified env facts (python3 3.13.5, PyYAML 6.0.2, no HA).
- Expected files (all new except README edit): `blueprints/automation/generic_scene_controller.yaml`, `scripts/validate_blueprint.py`, `tests/test_validate_blueprint.py`, `README.md`.
- RED step (run first, expected failure): `python3 -m unittest discover -s tests` -> non-zero (ModuleNotFoundError: scripts.validate_blueprint / FileNotFoundError: blueprint file), exit != 0.
- GREEN: `python3 -m unittest discover -s tests -v` -> exit 0 AND `python3 scripts/validate_blueprint.py blueprints/automation/generic_scene_controller.yaml` -> exit 0.
- Allowed scope: exactly the four files above; stdlib + PyYAML only; generic wording throughout. Prohibited: any ticket 02-09 feature (collapsible sections/icons, `multiple: true`, central variables, `not_from` guard, held/doubleTapped/released slots), LED inputs, vendor/model/node/room/concrete-entity ids, new dependencies, edits to LICENSE/.git/.scratch or any file outside the four, fabricated HA runtime results.
- Decision log: spec [AUTO-DECISION]s D1-D7, persisted by the coordinator; task receipt at `.omp/artifacts/receipt_<task_id>.json`.
- Blocked/failed reporting: any assertion unimplementable as specified, or a PyYAML tag-handling constraint forcing a different `!input` verification mechanism, is reported BLOCKED with the exact constraint — no scope cut, no weakened AC. Successful termination requires every required verification command passing with exit code 0; a blocked task is reported unsuccessful, never conversationally waved through.
T2 (independent verifier; blockedBy: T1):
- Objective: re-run every AC command from a clean shell WITHOUT editing any file; record command + exit code for: primary validator command (expect 0, assertions A1-A9 in pass list), `python3 -m unittest discover -s tests -v` (expect 0), README grep (expect match); confirm no ticket 02-09 artifact exists (grep blueprint for `multiple`, `not_from`, `collapsible`, section markers — expect none); report the AC1-AC10 table with observed outputs, marking AC5's runtime leg UNVERIFIED locally per U1.
- Read-only; no writes. Failure = report command + exit code as verification failure (fix loops back to T1 under a new round).

== 7. OBSERVABILITY ==
(skill://observability-contract loaded before planning this section.)
- Component `scripts/validate_blueprint.py` (T1): signal = plain-text stdout/stderr carrying assertion name + reason; operational contract = exit codes 0/1/2. Verification tied to AC8 and T2 (unit tests prove the 1/2 paths; T2 records the observed 0). Structured JSON logs: JUSTIFIED EXCEPTION — this is a one-shot CLI dev tool invoked per change, not a long-running service; consequence: no aggregation pipeline, failures are consumed directly from terminal/CI output; adding a logging stack would violate the no-new-stack rule for a static repo.
- Loki: JUSTIFIED EXCEPTION — no log shipping path exists in this repo (static YAML + dev script emit nothing persistent); consequence: none, nothing to ship.
- Prometheus/metrics: JUSTIFIED EXCEPTION — repo artifacts emit no persistent runtime signals and latency is irrelevant (single small-file parse); consequence: none; no unbounded-label risk because no metrics exist.
- Operations: no dashboards/alerts warranted. Failure visibility = validator exit 1 names the failing assertion (A1-A9, AC-bound); T2 (ledger) records observed outputs; the validator never logs file contents beyond assertion names/reasons, so no sensitive-payload risk.
- HA-side runtime observability: the automation created from the blueprint is observable through HA automation traces (Settings -> Automations -> trace). This is the ONLY runtime surface and is U1-unverifiable locally. JUSTIFIED EXCEPTION — reason: no HA instance reachable from this workstation; consequence: runtime dispatch correctness (AC5/AC6 runtime legs) stays owner-verified via HA import + trace, never machine-claimed from this repo.

== 8. RELEASE AND RECOVERY ==
Deployment order: T1 -> staged independent review (W09: code-reviewer stage 1, critic stage 2) -> T2 verification -> git-master commits and pushes straight to origin main (W10), reporting the full pushed SHA. No data migrations; no irreversible steps (two new files, one new test file, one README edit on a clean tree at 4ff9f85).
Per-task failure modes & rollback:
- T1: RED observed but GREEN unreachable within the four allowed files -> stop at MAX_FAILURES=2 (record-failure via execution-state), preserve evidence, report BLOCKED with the exact assertion/constraint. Rollback: `git checkout -- README.md` and removal of the three new files, restoring the clean 4ff9f85 tree.
- T2: any command exits non-zero -> record command + exit code, report as verification failure; read-only, so no repo rollback needed; repair re-enters T1 as a new round.
- Post-push rollback: `git revert <sha>` on main. HA-side instances are user copies frozen at import; repo rollback does not touch them until the owner re-imports — README import section notes this.
Irreversible steps: none.

== 9. CRITIC HANDOFF ==
Highest-risk assumptions/decisions for staged review:
1. D2 conflict resolution (ticket checkbox 7 "MQTT/Hubitat origin" vs genericity ban): review whether restricting the provenance mention to the leading comment block is the right reading; the alternative (ban "Hubitat" everywhere) weakens a binding ticket AC and is out of planner bounds.
2. U1 honesty: AC5/AC6 runtime legs must never be claimed from validator results; reject any prose equating exit 0 with "loads in HA".
3. D5 `mode: parallel` shipped in ticket 01: confirm it is not 02-09 scope creep (CONTEXT.md agreed-include list, assigned to no later ticket).
4. D7 unittest over pytest: availability-driven choice; if pytest is verified present, the runner swap is a same-envelope implementation detail, not an AC change.
5. `!input` tag reconstruction: PyYAML drops custom tags by default; review that the engineer's tag mechanism implements A6/A7 semantics (wiring correctness) without source-text/wiring-trivia assertions.
6. D6 extensibility: validator asserts required-key PRESENCE, not exact key set, keeping tickets 02-04 additive; R9 fence intact.
Review targets: validator assertion fidelity vs AC text; A9 denylist coverage vs R8/D2; README command byte-accuracy vs AC8; blueprint trigger/choose wiring vs D4.
Coverage check: all eight ticket checkboxes map R1-R8 -> AC1-AC10 -> T1/T2; every R has >=1 AC; every AC cites an R; no ticket 02-09 feature appears in any R/AC/T; no vendor/model/node/room/entity id prescribed anywhere in configuration.