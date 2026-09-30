# Audio sources

## Background music

- Track: **Ambient Piano Ambient Technology**
- Creator: **AudioDollar / Vladislav Litvinenko**
- Track page: https://pixabay.com/music/ambient-ambient-piano-ambient-technology-554832/
- License summary: https://pixabay.com/service/license-summary/
- Full terms: https://pixabay.com/service/terms/
- Retrieved: 2026-09-29, using the track page's Free download button.
- Local filename: `pixabay-554832.mp3`; source duration: 124.029375 seconds.
- SHA-256: `f11e32751aac09841a3df2c9634a7b631235c28c22d9b087422ee66edc914f84`
- Used: first 50 seconds beneath original video and narration, with fades, reduced gain, and voice-aware equalization/ducking.

The page identifies the track as free for use under the Pixabay Content License. This is licensed music, not public-domain or copyright-free music. The license permits free use and adaptation without required attribution, subject to its restrictions. Standalone redistribution of the stock track is prohibited, so the MP3 is ignored by Git. Our project's MIT license does not apply to this track.

To render a fresh clone, download this track from the page above, then save it here as `pixabay-554832.mp3`. Retain the source record and check the applicable terms. No account or paid subscription was used for this download. This record is not a promise that automated copyright systems can never flag the music.

Suggested credit: Music: “Ambient Piano Ambient Technology” by AudioDollar, via Pixabay.

## Narration

The four `voice-*.wav` files were generated locally with HyperFrames 0.8.91 using Kokoro-82M, voice `am_michael`, English, speed 0.9. The original scripts are included alongside them. These are synthetic speech; no person's voice was cloned.

The composition applies a shared gentle compressor and peak ceiling to the narration, and carves the music against the `voiceover` group. All processing remains editable in HyperFrames.

## Gameplay edition v2

The six `demo-voice-*.wav` files use local Kokoro-82M `am_michael`, English, speed 1.0, via HyperFrames 0.8.91 / kokoro-onnx 0.6.1.

The six current `zh-voice-*.wav` files use Microsoft Edge's online TTS service, accessed with edge-tts 7.2.8, stock Mandarin voice `zh-CN-YunyangNeural` (云扬), normal rate `+0%`. The user requested this replacement after rejecting the initial Kokoro Chinese voice. They were generated from the included scripts on 2026-09-29; MP3 responses were decoded to mono 24 kHz PCM WAV without changing speed. No voice model is redistributed and no voice cloning is used. The project's MIT license does not relicense Microsoft's service or voice technology.

The Chinese version keeps the English on-screen labels. Both edits use the same licensed Pixabay track, separately carved against their narration. Exact placement and durations are recorded in `../../NARRATION.md` and `../zh-voice-source.json`.

## Continuous narration edition v3

`v3-en-voice.wav` is local Kokoro-82M `am_michael`, en-us, speed 1.0, through HyperFrames 0.8.94 / kokoro-onnx 0.6.1. `v3-zh-voice.wav` is Edge TTS `zh-CN-YunyangNeural`, edge-tts 7.2.8, normal rate `+0%`. Each is a single continuous read from the approved v3 script, without inserted paragraph padding or time stretching. Durations are 54.181 and 56.304 seconds. Provider/model ownership and the no-voice-cloning statement above still apply.

The 56.000-second English and 58.133-second Mandarin films reuse the first corresponding portion of the same licensed Pixabay track. Each music bed has its own voice-aware carve and fade. The original stock track remains ignored by Git. Caption alignment uses local faster-whisper `base.en` for English and Edge word boundaries for Mandarin. See `../../narration/v3-audio-source.json` for generation settings and hashes, and the repository's `docs/VALIDATION.md` for encoded signal measurements.
