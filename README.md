# Agent Handoff Lab

**Evaluate the handoff, not just the final outcome.**

A small, inspectable team-evaluation workbench built on the real [AgentWorld](https://github.com/openagents-org/agentworld) game engine. Five roles exchange resources and produce a pickaxe, an axe, and a heavy sword. A separate verifier checks inventory changes, and a dashboard lets you replay every action.

![Recorded evidence dashboard](videos/handoff-eval/assets/dashboard.png)

**v0.1 contains a scripted baseline running on the actual engine. No LLM experiments have been run.** An OpenAI-compatible tool-calling adapter is included, but requires your own model and local credentials. This is a Task 46 inspired fixture, not a reproduction of the full AgentWorld benchmark or its CCE metric.

## What is here

- A working five-role production chain using the engine's crafting API.
- Three conditions: normal delivery, partial coal delivery, and partial delivery with delayed coordination messages.
- Actual before/after inventory snapshots, replay controls, error inspection, downloadable JSON, and comparison of repeated runs.
- A verifier that requires newly crafted outputs **and** corresponding material consumption; initial inventory and agent self-reports cannot pass it.
- Bilingual HyperFrames videos with continuous AI narration and matching subtitles: 56 seconds English / 58 seconds Mandarin, including about 47 / 50 seconds of edited real gameplay with trace overlays.
- [Experimental method and limits](docs/METHODS.md), [LinkedIn draft](docs/LINKEDIN.md), and [中文上手说明](docs/QUICKSTART.zh-CN.md).

## Run locally

Requirements: Node.js 22, Git, Python 3.10+, and a Chromium-based browser. The lab runner uses the Python standard library only. Setup downloads the pinned upstream engine and its dependencies; allow several minutes and a few GB of disk space. The engine's bundled Yarn is used automatically.

```sh
git clone https://github.com/GuilinDev/agent-handoff-lab.git
cd agent-handoff-lab
npm run setup
npm run dev
```

Open **http://127.0.0.1:7331**. Wait for “Engine connected”, then choose a condition and click **Run experiment**. The separate game client is at **http://127.0.0.1:7032**. On first startup world-cache generation may take about a minute; startup logs are in `.runtime/logs/`.

In another terminal:

```sh
npm run demo
npm run experiment
npm test
```

The experiment command runs five repetitions of all three conditions. Run one experiment at a time: the runner holds an OS-backed lock because fixture users are shared. Ctrl+C in the development terminal stops the launched process trees. If port 7030, 7031, 7032, or 7331 is already occupied, stop the previous lab instance first.

### Watch the actual game

Log in at port 7032 as `lab_viewer`, password `local-lab-only`. While that browser is connected, run:

```sh
curl -X POST http://127.0.0.1:7031/lab/observer
python -m lab.run --mode scripted --condition delayed-request --pace 0.45
```

In Windows PowerShell use `curl.exe`, or `Invoke-RestMethod -Method Post -Uri http://127.0.0.1:7031/lab/observer`. The observer endpoint is enabled only by the local development launcher. Five fixture characters appear nearby during a run, then log out. The observer is not part of the evaluated team.

### Optional LLM mode

Edit the ignored local `.env` created by setup:

```dotenv
LLM_PROVIDER=openai-compatible
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=your-tool-calling-model
LLM_API_KEY=your-local-key
```

Then restart the dashboard and select LLM mode, or run:

```sh
python -m lab.run --mode llm --condition partial-delivery --max-rounds 12
```

This makes paid calls to the configured provider: at most five decisions per round. Each role sees its own inventory, delivered messages, and prior results. It does not receive other roles' private inventories. Model credentials are never included in the run artifacts. The adapter currently supports `/chat/completions` tool calling; native Anthropic APIs are not implemented. Live provider integration remains unverified in v0.1 because no API key was available.

## Recorded baseline

Actual runs from 2026-09-29 UTC; see [`artifacts/suite.json`](artifacts/suite.json) and its referenced trajectories.

| Condition | Completed | Mean rounds | Range | Mean actions |
|---|---:|---:|---:|---:|
| Normal delivery | 5/5 | 5.0 | 5–5 | 25 |
| Partial first coal delivery | 5/5 | 7.2 | 7–8 | 36 |
| Partial delivery + delayed request | 5/5 | 9.0 | 9–9 | 45 |

One partial-delivery run hit an additional engine crafting cooldown. All failures remain in the trajectories. These fixed-policy repetitions validate the instrumentation and illustrate a blind spot in outcome-only reporting; they do not estimate LLM competence or establish general causal effects.

## Video

Source: [`videos/handoff-eval/`](videos/handoff-eval/). Local footage, item sprites, screenshots, and synthetic English/Chinese narration are included. Both editions use soft licensed Pixabay music; download the track as described in [audio sources](videos/handoff-eval/assets/audio/LICENSE-SOURCE.md) before rendering a fresh clone. The stock MP3 is not redistributed in Git. FFmpeg and HyperFrames' browser dependencies are also needed.

```sh
cd videos/handoff-eval
npm ci
npm run check
npx --yes hyperframes@0.8.94 preview --background
npm run render -- --quality delivery --fps 30 --strict-all --output ../../artifacts/agent-handoff-lab-v3-en.mp4
npx --yes hyperframes@0.8.94 render -c variants/index-zh.html --quality delivery --fps 30 --strict-all --output ../../artifacts/agent-handoff-lab-v3-zh-yunyang.mp4
```

Current local delivery files are `artifacts/agent-handoff-lab-v3-en.mp4` (56.000 seconds) and `artifacts/agent-handoff-lab-v3-zh-yunyang.mp4` (58.133 seconds). English uses local Kokoro `am_michael`; Mandarin uses Edge TTS 云扬 (`zh-CN-YunyangNeural`) at normal speech rate. Each is a continuous read with its own scene timing and complete matching subtitles; evidence labels remain English. The v1/v2 files are preserved locally. Encoded deliverables are not tracked in Git. All onscreen results explicitly say scripted baseline. Scripts, SRT captions and measured timings are in [NARRATION.md](videos/handoff-eval/NARRATION.md) and its `narration/` folder.

The moving resource icons, inventory panels, and focus boxes are **editorial trace overlays**, generated from the saved run; they are not native game trading animations or a recording of LLM reasoning. This fixture prepositions the characters and supplies materials. No new navigation or gathering capability is implied by the edit.

Normal re-renders of the checked-in compositions need no rebuilding or TTS runtime. To revise v3, use `python scripts/generate-v3-narration.py en` or `zh` from the repository root, then `python scripts/build-v3-video.py`. The generation environment needs HyperFrames' Kokoro dependencies plus `faster-whisper==1.2.1` for English, or `edge-tts==7.2.8` for Mandarin. Mandarin requires the online Edge service; initial English model/tool downloads also require network access. English alignment uses local `base.en` ASR; Mandarin uses provider word boundaries. The builder reads saved evidence, generates both picture edits and captions, and resets audio processing to its base settings.

After rebuilding, re-run the HyperFrames voiceover carve separately for each language, then check and render. The carve helper resolves media relative to its HTML file: for Chinese, copy `variants/index-zh.html` to a temporary HTML file in the project root, run the helper on that copy, then move it back to `variants/index-zh.html` before checking. HyperFrames render resolves the variant's assets from the project root. Keep only one root entrypoint so preview does not discover duplicate audio. The older `build-gameplay-video.py`, `generate-chinese-voiceover.py`, and `build-chinese-voiceover.py` describe v2 and should not be used to rebuild v3.

## Project boundaries

Original code lives in `lab/`, `scripts/`, `web/`, and `tests/`. Upstream is downloaded into ignored `.runtime/agentworld`, pinned by [`upstream.lock.json`](upstream.lock.json). A checked-in Yarn lock pins the resolved dependency graph. Our small local patches add an observer camera and bind services to loopback; they do not modify recipes or outcomes.

Resource transfer uses verified, serialized inventory updates with compensation, because the local fixture does not use an atomic in-game trade API. Navigation and gathering are outside this version. Keep the admin-capable game API local; this is a development fixture, not a hosted multi-tenant service.

See [credits and licenses](THIRD_PARTY.md). Our additions are MIT; upstream and third-party assets retain their own licenses.
