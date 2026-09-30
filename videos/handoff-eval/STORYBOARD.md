# Storyboard

| Time | Scene | Evidence |
|---|---|---|
| 0–8 | Evaluate the handoff | Five roles; task success is only the beginning |
| 8–20 | Five roles, one chain | Real AgentWorld local footage; preloaded materials; scripted policy |
| 20–34 | Where did it stall? | Actual events 2 and 14: partial coal transfer, then missing-coal error |
| 34–50 | Same success, different cost | 5.0 / 7.2 / 9.0 mean rounds; n=5 per condition; all 15 succeed |

Closing thought: trace the state, test the dependency. These are behavioral traces, not model reasoning. Next: compare LLM policies. One partial-delivery run includes a real engine cooldown error; disclose this in METHODS and the results scene.

## Changes from v1 — 2026-09-29

User: “我感觉游戏截图/视频太少了 趣味性不够，‘实操’的感觉不强”. Increase real game footage from 12 to 42 seconds of the same 50-second total. Enlarge the party, follow an actual recorded transfer/failure/recovery sequence, and shorten the chart to eight seconds. Keep the original delivery files. The later request adds a Chinese AI voiceover edition over the same picture, a public repository, and its link in the LinkedIn draft.

| Time | Current scene | Source / proof |
|---|---|---|
| 0–6 | Cold open: missing coal | Recorded gameplay; actual error and inventory at event 14 |
| 6–14 | Rewind: meet the five roles | Starting materials and three required tools |
| 14–23 | Short delivery, first batch, failure | Events 2, 4, 10, 14 |
| 23–34 | Delayed request, delivery, recovery | Events 19, 32, 34; sent R4, delivered R7 |
| 34–42 | Verify each finished tool | Events 39, 40, 45; three actual outputs |
| 42–50 | Evaluate the handoff | Saved 15-run comparison; 5.0 / 7.2 / 9.0 rounds |

All footage and events come from recorded local execution. The cut uses an editorial timeline, not frame-synchronized native telemetry. Animation explicitly represents trace evidence. The fixture's movement/gathering scope is unchanged.

## Frame 1
status: built
src: compositions/demo-hook.html
Rules: spring-pop-entrance; authored camera scale on the inner world wrapper.
Beat: actual missing-coal error first, then rewind.

## Frame 2
status: built
src: compositions/demo-party.html
Rules: spring-pop-entrance; authored camera scale. Telemetry HUD readout layout adapted from the installed registry reference.
Beat: five characters, starting materials, three targets.

## Frame 3
status: built
src: compositions/demo-coal.html
Rules: spring-pop-entrance; deterministic resource-icon translation.
Beat: partial handoff, verified first batch, then missing-material failure.

## Frame 4
status: built
src: compositions/demo-recovery.html
Rules: spring-pop-entrance; discrete round reveals and resource-icon translation.
Beat: message held for three rounds; recorded delivery restores production.

## Frame 5
status: built
src: compositions/demo-finish.html
Rules: spring-pop-entrance; staged inventory readouts.
Beat: bars arrive, axe is crafted, final sword completes the quest.

## Frame 6
status: built
src: compositions/demo-result.html
Rules: stat-bars-and-fills; spring-pop-entrance.
Beat: comparison and evaluation question, then hold for reading.

## Script revision plan — 2026-09-29

User: “请你审计一下中文配音和英文配音，我听起来觉得没头没尾的”, followed by “是的 先改下中英文脚本”.

The bilingual v3 scripts in `NARRATION.md` and `narration/v3-*.txt` replace the fragmented narration with a continuous argument: task success versus coordination; authorship, scripted roles and the three tools; three comparison conditions; an explicit partial delivery and delayed request; replenishment and recovery; fifteen completed runs with five versus nine mean rounds; behavioral evidence, the next LLM comparison, and the open-source link.

Status at script review: draft only, with a rough 60–70 second allowance. Production was subsequently authorized; actual timing is below.

## Delivered v3 — measured narration timing

Six built scenes per language, with a separate subtitle composition. Files are `compositions/v3-{en,zh}-{scene}.html`; `narration/v3-timing.json` contains exact timing. Main entry is English; `variants/index-zh.html` is Mandarin. Each scene uses spring-pop-entrance for evidence cards; results also use stat-bars-and-fills. Long reading holds are intentional over moving footage.

| Scene | English (s) | Mandarin (s) | Beat / source |
|---|---|---|---|
| team | 0–9.020 | 0–10.900 | Question, fixed-policy setup, pickaxe/axe/sword targets |
| conditions | 9.020–14.220 | 10.900–18.012 | Normal; half coal; half coal plus delayed request |
| replay | 14.220–27.020 | 18.012–30.887 | Short delivery → empty inventory → held request → refill → resumed work; actual saved trace |
| results | 27.020–36.140 | 30.887–39.075 | 5.0 / 7.2 / 9.0 rounds; five runs each; cooldown caveat |
| insight | 36.140–45.500 | 39.075–48.975 | Handoffs and recovery; observable behavior versus internal reasoning |
| close | 45.500–56.000 | 48.975–58.133 | Measurement baseline, next LLM policies, public repo URL |

Rules used: `hyperframes-animation/rules/spring-pop-entrance.md` and `hyperframes-animation/rules/stat-bars-and-fills.md`. Source game pixels are reused from the existing recording. The intervention replay is editorial evidence, not native live telemetry. Subtitle timing comes from the continuous reads, without new narration padding.
