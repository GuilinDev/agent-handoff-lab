# Narration — delivered v3

Status: **v3 audio and video produced from the approved bilingual scripts** on 2026-09-29. English is 56.000 seconds; Mandarin is 58.133 seconds. The v1/v2 timing records below describe the preserved older edits.

The current scripts are [English](narration/v3-en.txt) and [Mandarin](narration/v3-zh.txt). They tell one continuous story, with paragraph breaks as semantic beats, not fixed video slots. Rewrite requested on 2026-09-29 after the bilingual narration audit.

## 中文脚本

任务成功了，就代表协作得好吗？

我在 AgentWorld 里搭了个实验：让五个按固定策略行动的角色，合作做出镐、斧头和剑。

我比较了三种情况：正常交付、只交一半煤，以及在此基础上延迟补煤请求。

来看第三种：十份煤，我只让五份送到。冶炼者用完后请求补煤，我让消息晚到三个回合。供应者收到请求，补齐剩下的煤，生产才恢复。

每种情况跑五次，全部成功。但正常情况平均只需五轮，两种干预叠加后要九轮。

我的体会是，评估智能体，也要看交接和恢复成本。轨迹能告诉我们发生了什么，却不能揭示模型内部的推理。

这版先验证测量工具，下一步再比较大模型策略。代码和运行记录，都在帖子链接里。

## English script

Does task success mean good teamwork?

I built an AgentWorld experiment: five scripted roles crafting a pickaxe, an axe, and a sword.

I tested normal delivery, a coal shortage, and that shortage plus a delayed request.

Here's the third case. I deliver five coal instead of ten. The smelter runs out and requests more. I delay that message by three rounds. Once it arrives, the supplier sends the rest, and work resumes.

Five runs per condition, all successful. But average completion takes five rounds normally, versus nine with both disruptions.

My takeaway: evaluate handoffs and recovery alongside success. Traces show what happened; they don't reveal a model's internal reasoning.

This scripted baseline tests the measurement setup. Next, I'll compare LLM policies. Code and traces are linked in the post.

## v3 production and timing

- Production authorized by the user: “好的 请开始做吧”. Each language was generated as one continuous read, with no inserted inter-paragraph padding or time stretching. Scene cuts follow the measured speech, rather than the previous fixed slots.
- English: 129 words, local Kokoro-82M `am_michael`, en-us, speed 1.0, through HyperFrames 0.8.94 / kokoro-onnx 0.6.1. The WAV is 54.181 seconds, placed at 0.400 and ending at 54.581 in a 56.000-second film.
- Mandarin: 236 Han characters plus the product name, Edge TTS `zh-CN-YunyangNeural` (云扬), edge-tts 7.2.8, normal rate `+0%`. The WAV is 56.304 seconds, placed at 0.400 and ending at 56.704 in a 58.133-second film.
- Spoken spellings are “Agent World” and “L L M”; on-screen names retain AgentWorld and LLM. English word timing comes from a locally reviewed faster-whisper 1.2.1 `base.en` transcript (99.54% normalized character alignment). Mandarin timing comes from provider WordBoundary events (100% normalized alignment). These timing checks do not constitute human pronunciation review.
- Full burned-in subtitles: 16 English cues and 14 Mandarin cues. Approved copy supplies the displayed text. Caption JSON, SRT sidecars, word timings and the exact scene manifest live in `narration/`.
- English contains 46.88 seconds of edited real gameplay; Mandarin contains 49.946 seconds. Recorded footage is reused and cut editorially; the trace overlays are not frame-synchronized native telemetry.
- Each language has its own voice gain, compressor/limiter bus and music carve. Encoded signal measurements are recorded in `../../docs/VALIDATION.md`.
- Spoken results contrast the normal and combined-disruption conditions. The results visual should still show all three means (5.0 / 7.2 / 9.0), five runs each, and the observed cooldown caveat. Do not attribute every extra round solely to message latency.
- This is a fixed-policy experiment checking the evaluation instrumentation. It does not demonstrate LLM collaboration or expose model reasoning. Inventory and message traces support behavioral inspection.
- Keep actual game footage prominent. The final frame should carry the repo URL and a legible link prompt: https://github.com/GuilinDev/agent-handoff-lab . Do not read the whole URL aloud.
- The old `assets/audio/demo-script-*.txt` and `zh-script-*.txt` describe the preserved v2 WAVs. Use `scripts/generate-v3-narration.py` and `scripts/build-v3-video.py` for v3; rebuilding requires reapplying the separate music carves before rendering.

---

# Delivered narration history

# English narration — audio edition

Approved direction: restrained English AI narration with soft instrumental music. Keep the original 50-second picture edit and the silent v1 deliverable. This is a scripted baseline, not an LLM capability claim.

Voice: local Kokoro-82M, `am_michael`, American English, speed `0.9`. Local generation avoids requiring a new cloud account. Measured clip durations: 6.421, 10.837, 9.643, and 12.992 seconds. Final narration ends at 47.342 seconds, leaving 2.658 seconds for the closing question and music fade.

| Scene | Start (seconds) | Narration |
|---|---:|---|
| Opening | 0.45 | Every run succeeded. But that didn't tell the whole story. I wanted to evaluate the handoff. |
| Game | 8.35 | Five roles turn ore, coal, and wood into three tools. This first version uses scripted policies, running on the real Agent World engine. |
| Evidence | 20.4 | I capped one coal delivery, then delayed a coordination message. The trace shows exactly where work stalls: five coal are missing. |
| Results | 34.35 | All fifteen runs finish, but completion takes more rounds. A trace shows what changed. An intervention tests a dependency. Next, I'll compare L L M policies. |

“Agent World” and “L L M” are speech spellings only; onscreen product names remain AgentWorld and LLM. No voice cloning or imitation of a named person.

## Gameplay edition v2 — English and Chinese

Both editions keep the same 50-second picture edit: 42 seconds of edited real game capture, then the measured results. The Chinese edition changes the narration; on-screen labels remain English. English uses local Kokoro speech. Mandarin uses the Edge online TTS service through edge-tts, with the stock Yunyang voice. No voice cloning is used.


### English

Voice: am_michael, English, speed 1.0. Timings are measured from the generated WAV files.

| Clip | Start (s) | Duration (s) | Narration |
|---|---:|---:|---|
| 1 | 0.200 | 3.520 | Five agents. Three tools. One broken handoff. |
| 2 | 6.200 | 5.013 | Iron, coal, and wood feed the smelter and smith. The goal: three new tools. |
| 3 | 14.200 | 6.507 | Ten coal requested. Only five delivered. The first batch works. Then the smelter runs out. |
| 4 | 23.200 | 7.147 | The smelter asks for more coal. I delay that message by three rounds. When it arrives, production resumes. |
| 5 | 34.200 | 6.080 | Watch the inventory: new bars, an axe, and the final sword. Three verified outputs. |
| 6 | 42.200 | 6.485 | All fifteen runs succeeded. The handoff cost changed. That's why I evaluate the process, too. |

Last voice ends at 48.685 seconds.

### Chinese — Mandarin Yunyang

Voice: `zh-CN-YunyangNeural` (云扬), locale `zh-CN`, edge-tts 7.2.8. All six clips use normal rate `+0%`, with no time stretching. The earlier Kokoro Chinese mix was rejected for intelligibility and is superseded.

| Clip | Start (s) | Duration (s) | Narration |
|---|---:|---:|---|
| 1 | 0.100 | 4.752 | 五个智能体，三件工具。一次交接出了问题。 |
| 2 | 6.100 | 6.384 | 铁矿、煤和木材，交给冶炼者和铁匠。目标是造出三件工具。 |
| 3 | 14.100 | 6.384 | 请求十份煤，实际只交付五份。第一批成功了，下一批却缺煤了。 |
| 4 | 23.100 | 7.392 | 冶炼者请求补煤。我把消息延迟了三个回合。消息送达后，生产才继续。 |
| 5 | 34.100 | 6.840 | 看库存：新的铁锭、斧头，还有最后一把剑。三件产物，都有证据。 |
| 6 | 42.100 | 6.600 | 十五次都成功了，交接的代价却不同。所以，评估还要看完成的过程。 |

Last voice ends at 48.700 seconds, leaving 1.3 seconds for the closing frame. The music carve was recomputed against all six Yunyang clips. These timings are measured; pronunciation was not reviewed by a human. Regeneration uses `scripts/generate-chinese-voiceover.py` and requires network access.
