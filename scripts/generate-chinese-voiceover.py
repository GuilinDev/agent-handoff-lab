"""Generate Mandarin narration with Edge TTS Yunyang (requires network access)."""
import asyncio
import json
from pathlib import Path
import subprocess
import wave

import edge_tts

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / 'videos/handoff-eval'
VOICE = 'zh-CN-YunyangNeural'
SLOTS = [6, 8, 9, 11, 8, 8]


async def main():
    temporary = ROOT / '.runtime/yunyang'
    temporary.mkdir(parents=True, exist_ok=True)
    records = []
    for number, slot in enumerate(SLOTS, 1):
        script = PROJECT / f'assets/audio/zh-script-{number:02d}.txt'
        text = script.read_text(encoding='utf-8').strip()
        mp3 = temporary / f'{number:02d}.mp3'
        wav = temporary / f'{number:02d}.wav'
        rate = 0
        for attempt in range(3):
            await edge_tts.Communicate(text, VOICE, rate=f'+{rate}%').save(str(mp3))
            subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y',
                            '-i', str(mp3), '-ar', '24000', '-ac', '1',
                            '-c:a', 'pcm_s16le', str(wav)], check=True)
            with wave.open(str(wav)) as audio:
                duration = audio.getnframes() / audio.getframerate()
            if duration < slot - .3:
                break
            rate += 5
        else:
            raise RuntimeError(f'Clip {number} exceeds its scene; shorten the script.')
        destination = PROJECT / f'assets/audio/zh-voice-{number:02d}.wav'
        destination.write_bytes(wav.read_bytes())
        records.append({'clip': number, 'voice': VOICE, 'provider': 'Edge TTS',
                        'locale': 'zh-CN', 'rate': f'+{rate}%',
                        'duration': duration, 'text': text})
        print(f'Clip {number}: {duration:.3f}s, rate +{rate}%', flush=True)
    (PROJECT / 'assets/zh-voice-source.json').write_text(
        json.dumps({'edge_tts_version': edge_tts.__version__, 'clips': records},
                   ensure_ascii=False, indent=2), encoding='utf-8')


if __name__ == '__main__':
    asyncio.run(main())
