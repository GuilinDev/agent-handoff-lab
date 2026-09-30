# Local media provenance

- `real-game.mp4`: 14-second excerpt from our actual local AgentWorld recording, beginning 25 seconds into the source capture. The visible roles are `lab_iron`, `lab_coal`, `lab_wood`, `lab_smelter`, `lab_smith`; `lab_viewer` is an observer. Recorded during paced scripted run `20260929T031527021009Z-scripted-delayed-request`. No simulated or composited game characters. Original recording is kept locally under ignored `artifacts/recordings/`.
- `handoff.png`: dashboard screenshot of event 2 from `20260929T030755280857Z-scripted-delayed-request`, first partial coal transfer.
- `evidence.png`: dashboard screenshot of event 14 from the same run, missing-coal error.
- `dashboard.png`: full dashboard screenshot at that event, including the three-condition comparison from `artifacts/suite.json`.
- `gsap.min.js`: unmodified GSAP 3.14.2 public distribution from jsDelivr; original license header preserved.
- `audio/voice-01.wav` through `voice-04.wav`: synthetic English narration generated locally from the adjacent script files using Kokoro via HyperFrames. Details and measured timings are in ../NARRATION.md.
- `audio/pixabay-554832.mp3`: licensed AudioDollar piano/ambient track, excluded from Git. See audio/LICENSE-SOURCE.md for the original page, license, checksum, and restoration instructions.

Game imagery belongs to the AgentWorld / Kaetram attribution chain. See the root THIRD_PARTY.md. These assets were adopted into HyperFrames' local media ledger; the ledger is a generated local file rather than the canonical attribution record.

## Gameplay edition v2

- `game-session.mp4`: 38-second excerpt, source seconds 20–58, from the same original 59.28-second local recording used for v1. Encoded from that source as H.264 / 25 fps / CRF 17, with a keyframe each second for reliable preview seeking. The edit crops and reuses selected source ranges. It does not add synthetic character actions or alter game pixels.
- `items/*.png`: unmodified item sprites from the pinned AgentWorld client `public/img/sprites/items/`. They retain upstream attribution and licensing.
- `demo-evidence.json`: selected actual events from run `20260929T031527021009Z-scripted-delayed-request`, plus narration timing. The video uses editorially timed trace overlays, not a frame-synchronized capture of native game telemetry. Resource icons moving between roles represent verified inventory changes; they are not native trade animations.
- `audio/demo-voice-*.wav`: English Kokoro `am_michael`, speed 1.0. `audio/zh-voice-*.wav`: Mandarin Edge TTS `zh-CN-YunyangNeural` (云扬), normal rate `+0%`; actual timing and synthesis settings recorded in NARRATION.md. Scripts are included.
- The registry `telemetry-hud` readout structure informed the overlay layout. Its placeholder values and scrambling effects are not used. The reference component remains in `compositions/components/`.

## Continuous narration edition v3

- `audio/v3-en-voice.wav`: one continuous local Kokoro-82M `am_michael` read, en-us, speed 1.0, HyperFrames 0.8.94 / kokoro-onnx 0.6.1. `audio/v3-zh-voice.wav`: one continuous Microsoft Edge `zh-CN-YunyangNeural` read through edge-tts 7.2.8, rate `+0%`, decoded to 24 kHz mono PCM without time stretching. Script and audio hashes are recorded in `../narration/v3-audio-source.json`.
- `../narration/v3-*-words.json`: English local faster-whisper 1.2.1 / `base.en` alignment; Mandarin provider WordBoundary timing. Captions use approved script text, not uncorrected ASR text.
- `fonts/noto-sans-sc-v3.ttf`: 41,392-byte Noto Sans SC text subset served by Google Fonts for the current Chinese copy, weight 500. `fonts/noto-sans-sc-v3.source.json` records source URLs; `fonts/NotoSansSC-OFL.txt` preserves the SIL Open Font License. Changes adding Chinese characters require a new subset or a complete font.
- `game-session.mp4` and item sprites are unchanged. Both editions reuse and crop this recorded footage; trace cards remain editorial overlays, not native telemetry. The recorded 15-run comparison is unchanged.
