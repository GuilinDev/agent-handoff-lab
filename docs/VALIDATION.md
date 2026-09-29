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
