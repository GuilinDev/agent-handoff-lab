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
