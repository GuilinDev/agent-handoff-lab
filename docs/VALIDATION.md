# v0.1 validation

Validated locally on Windows with Node.js 22.22.3, Python, Microsoft Edge, FFmpeg, the pinned AgentWorld source, and HyperFrames 0.8.90.

- `npm run setup`: completed from the pinned source and checked-in dependency lock. Upstream dependency warnings remain; no install failure.
- `npm test`: 7 tests pass. The outcome checks reject initial outputs, unverified API success, material-free creation, and mismatched transfers. Archived suite scores are recomputed from all 15 raw trajectories.
- Real engine suite: 15/15 completed, with mean rounds 5.0 / 7.2 / 9.0. Additional paced recording run completed at 9 rounds. See METHODS for the observed cooldown failure and exclusions.
- Browser checks: dashboard loads without JavaScript errors or broken images; recorded failure evidence, next-event stepping, and playback controls verified. Desktop and 390-pixel mobile layout checked; no horizontal document overflow after responsive fix.
- HyperFrames `check --snapshots`: no lint, runtime, layout, or contrast errors/warnings. A brief intentional text crossfade is reported as informational overlap. Actual scene PNGs were visually inspected.
- Final video: H.264, 1920 × 1080, 30 fps, 50.000 seconds, 11,637,584 bytes; silent by design. Extracted frames from the encoded MP4 confirm real game footage and the measured results scene.
- Studio background preview verified running at port 3004. Dashboard runs at port 7331; game client at 7032.

Final video SHA-256: `a230e65e81495080c1e881c2e023ad4ca5f38fd05bac6d72bed4e520fe3262b9`.

Not validated: live LLM provider calls (no configured key), other operating systems, production deployment, navigation/gathering tasks, or benchmark-wide performance. The model adapter is optional and remains experimental.

## Audio edition — 2026-09-29

- HyperFrames upgraded from 0.8.90 to 0.8.91; the existing picture edit passed the upgrade check. Four local Kokoro narration clips fit their scenes and finish at 47.342 seconds. The last 2.658 seconds leave room for the final slide and music fade.
- Pixabay music source, license links, retrieval date, and SHA-256 are recorded in `videos/handoff-eval/assets/audio/LICENSE-SOURCE.md`. The original stock MP3 is ignored by Git; generated narration WAVs and scripts are included.
- HyperFrames check passed with zero lint/runtime/layout/contrast errors or warnings. The existing brief evidence-text crossfade remains informational. Scene snapshots and a frame extracted from the final MP4 were visually inspected.
- Delivery render passed with `--strict-all`. Render used hardware GPU / drawElement capture and completed in 45.1 seconds. Narration uses a shared levelling/peak-ceiling bus; music uses fades and a carve against the complete voiceover group.
- `artifacts/agent-handoff-lab-v1-audio.mp4`: H.264, 1920 × 1080, 30 fps; AAC stereo, 48 kHz. Both streams and the container are exactly 50.000 seconds; file size is 14,616,506 bytes.
- Encoded audio measurement: integrated loudness **−19.6 LUFS**, loudness range **4.3 LU**, true peak **−1.6 dBFS**. The measured peak is below full scale. These are signal checks, not a claim of human listening review.
- Original silent video remains unchanged, verified against its SHA-256 above. Updated Studio preview at `http://localhost:3004/#project/handoff-eval` returned HTTP 200.

Audio-edition SHA-256: `feb3c4dd6f392868a7276a8c774efae7da3eceeb0b5f57d59d5a4aea09142946`.

## Gameplay edition v2 — English and Chinese, 2026-09-29

- Same 50-second picture edit for both languages, with 42 seconds of enlarged real game capture and editorial trace overlays. Source event IDs and narration timing are baked into `assets/demo-evidence.json`. Chinese narration timing is separately recorded in `assets/zh-narration-timing.json`. This remains a scripted baseline; no new LLM experiments, navigation, or gathering are claimed.
- HyperFrames full picture check sampled 2.5, 9, 16, 21, 27, 32, 38, 40, and 46 seconds: zero lint/runtime/layout/contrast errors or warnings. Sixteen informational layout findings concern intentional fades and chart-label bounding boxes; sampled images were reviewed. After shortening the coal title, targeted checks at 16 and 21 seconds again passed with zero errors/warnings and four informational fade-related findings.
- Animation diagnostics reviewed: no degenerate or off-screen tweens. Slow footage push-ins and the final reading hold are deliberate. The original source was re-encoded with one-second keyframes for reliable preview seeking; renders extract source frames before composition.
- English and Chinese delivery renders passed `--strict-all`, with hardware GPU / drawElement capture, at 30 fps. Final encoded frames were visually inspected, including the corrected coal panel and three verified outputs. Chinese uses an alternate entry under `variants/`, leaving only one root entry for preview.
- Each video is H.264, 1920 × 1080, 30 fps, with AAC stereo at 48 kHz. Both video/audio streams and the container are exactly 50.000 seconds. English narration ends at 48.685 seconds; Chinese ends at 49.865 seconds, without truncation.
- Audio signal measurements are below full scale. These are automated signal checks; no human listening review or pronunciation-quality claim is implied.

| Edition | File bytes | Integrated LUFS | LRA (LU) | True peak (dBFS) |
|---|---:|---:|---:|---:|
| EN | 54,395,273 | -19.9 | 6.2 | -1.6 |
| ZH (initial, superseded) | 54,395,829 | -13.7 | 3.8 | -1.5 |

EN SHA-256: `4c55c4cece72092aa216bd5a5f1f90067180f42d4bfd6204c56f84a5321f3590`.


Initial, superseded ZH SHA-256: `b031356662baf6cebbf27be51915f09e3b0de5497300218a079e07599dc6a26d`.

The v1 silent and English-audio MP4s retain their previously recorded hashes. The GitHub repository is public and the LinkedIn draft includes its URL; nothing has been posted to LinkedIn.

## Mandarin replacement — Yunyang

The current Chinese deliverable is `artifacts/agent-handoff-lab-v2-zh-yunyang.mp4`. It supersedes the initial Kokoro Chinese file above, which the user rejected for intelligibility.

- Voice catalog confirmed `zh-CN-YunyangNeural` (male, zh-CN); generated all six clips with edge-tts 7.2.8 at normal rate `+0%`. No speed adjustment was needed. Scripts and provider settings are included in `assets/zh-voice-source.json`.
- Measured clip durations: 4.752 / 6.384 / 6.384 / 7.392 / 6.840 / 6.600 seconds. Final voice ends at 48.700 seconds. The music carve was recomputed against these clips.
- HyperFrames check passed with zero lint/runtime/layout/contrast errors or warnings; reviewed informational transitions remain. Delivery render with `--strict-all` succeeded. English picture edit and narration remain unchanged.
- H.264, 1920 × 1080, 30 fps; AAC stereo at 48 kHz. Video/audio/container duration: 50.000 seconds. File size: 54,403,368 bytes.
- Encoded signal: −23.7 LUFS integrated, 5.5 LU range, −1.6 dBFS true peak. The voice identity and duration are verified; no human listening review is claimed.
- Background Studio preview returned HTTP 200 at `http://localhost:3004`.

Yunyang video SHA-256: `dce34dac1c44a5ee00d0e45d623e8e849f07caef86722b9472bc8be562434405`.
