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
