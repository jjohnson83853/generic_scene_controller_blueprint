VERDICT: REVISE

**Mode:** specification, repair pass. Read whole: `spec-canonical-r2.md` (30,996 B; registry SHA fc0049…, not recomputable with read-only tools). Inputs: T01, T02 checkbox 4, CONTEXT.md, README, round-1 observation + review-sequence findings. Static only: no shell/HA/LSP.

**Round-1 closure (verified):** F1 CLOSED — `mode:` removed from D5/design/T1; R9:18 + AC11:81 fence it; T02 checkbox 4 cited. F2 CLOSED for top-level — A7:54 exact one `choose`, no `default`, no siblings; fixtures:59; AC7:77. F3 CLOSED — A1:49 tag-preserving `!input` constructor; A6/A7:53-54; literal-binding fixture:76; PyYAML raise corrected:22. F4 CLOSED for coverage — A9:56 enumerates rooms, node/device keys, dotted literals, header exception; AC10:80. F5 CLOSED — A3:50 no entity `default`; fixture:59/AC4:75. F6 CLOSED for recorded legs — R9→AC11, exact ten-key A3:50, additivity corrected:18/D6:28. F7 CLOSED — A8:55 tokens/boundary; fixtures:79; D2:24 corrected. F8 CLOSED in substance — tracked-tree qualification:22/:110, RED fix:89, overlap acknowledged:82.

**Findings**

1. **[MEDIUM][oracle false-positive] A9(b):56 vs D4:26.** A9 scans every parsed string value with unanchored `[a-z_]+\.[a-z0-9_]+`. D4 mandates a condition string containing `trigger.id`, `trigger.to_state`, `to_state.attributes.get(...)`; all match. A search-based validator rejects the mandated blueprint, so the primary command and AC1-AC4/AC6/AC7/AC9/AC10 (:78-82) cannot pass as written. r1's `event\.` pattern did not collide; this is a repair regression. **Fix:** full-value match (`re.fullmatch`) or restrict to `entity_id` leaves; add a positive fixture that the D4 template passes A9.

2. **[MEDIUM][oracle-gap] A7:54.** “References button_N” allows `trigger.id in ['button_1','button_2'] and ... pushed`, dispatching button 2’s event into branch 1; “sequence bound to” allows an extra `service:`/`condition: time` inside a branch. Fixtures :59/AC6:76 cover only the wrong sequence and outside-choose steps. **Fix:** assert the exact D4 condition and exactly one `!input button_N_action`; add both fixtures.

3. **[MEDIUM][traceability] R9:18 vs AC11:81.** AC11 greps only `mode|variables|multiple|not_from|collapsed|mdi|led`; R9 also fences per-button time/sun conditions and shared action scripts, which A7:54 does not catch inside a branch. **Fix:** extend the fence/structural check (`sun|time|script`, or parsed-key checks) and exclude header/description prose (a description saying “multiple buttons” would false-positive).

4. **[LOW][evidence] §3:22.** `.omp/` untracked is under VERIFIED but rests on round-1’s `[INFERENCE: no shell]`; planner did not re-run git. Mark it `[INFERENCE]` or cite `git status --porcelain`. The “36 bytes” README claim is unverified (36 chars + newline = 37 B).

5. **[LOW][packaging] `spec-01.md`:5,25,46,52.** The plan-dir spec is still revision 1 (`mode: parallel`, presence-only A3, old A9). If T1 consumes this path, F1/F4/F5/F6 regress. Replace it with the approved r2 bytes before implementation.

**Positives:** R1-R9→AC1-AC11 coverage is complete; T2 covers every AC; exact ten-key and non-additive-02 corrections are right; HA wiring (`platform: state`, `trigger.id`, `attributes.get`, `!input` in `entity_id`/sequence, choose no default, `default: []`) is valid; U1 honesty; F3/F5/F7 fixes are concrete.

**Limits:** no shell/HA/LSP; validator/tests not run, SHA not recomputed, `.git/index`/README bytes unverified; HA behavior assessed statically only.

VERDICT: REVISE
