# Credits and third-party material

- **AgentWorld**, OpenAgents contributors: https://github.com/openagents-org/agentworld . Source pinned by `upstream.lock.json`, downloaded separately by setup. The repository states that it inherits **MPL-2.0** from Kaetram. An unmodified license copy is in `engine/UPSTREAM-LICENSE`. Engine/client source is not vendored into this repo.
- **Kaetram** and its upstream game contributors provide the game engine and pixel-art world visible in our local recording and dashboard item sprites. Their material remains third-party material under the applicable upstream licenses; the MIT license of this project's original code does not relicense it. The footage is a capture of the pinned local engine, not original art created by this project. See AgentWorld's README and the Kaetram attribution chain for original credits.
- **HyperFrames**, HeyGen contributors: https://github.com/heygen-com/hyperframes . Video tooling pinned at 0.8.90. The `animated-bar-chart` catalog component was consulted and adapted for measured result bars; no catalog sample statistic is used. Its installed reference snippet is preserved under the video composition components directory.
- **GSAP 3.14.2**, GreenSock / Webflow: local `videos/handoff-eval/assets/gsap.min.js`, obtained from its public distribution. Its original header and license references are preserved. See https://gsap.com/standard-license/ .
- **Montserrat** and **IBM Plex Mono**: fonts embedded by HyperFrames at compile time. They retain their original font licenses; font source files are not separately authored by this project.

Local modifications to the downloaded engine are fully described by `scripts/patch-engine.mjs`: opt-in observer camera endpoint, loopback API and development-client bindings, and corrected client HMR port. Game recipes, skill probabilities, and crafting success logic are unchanged. Follow upstream licensing when redistributing the engine or game assets.

The attached Chinese walkthrough served as implementation inspiration. Its PDF is not redistributed. Screenshots, trajectories, and footage supplied here were generated from our own local execution.
