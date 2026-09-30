"""Create the Chinese audio entrypoint while preserving the English picture edit."""
from pathlib import Path
import json
import re
import wave

project = Path(__file__).resolve().parents[1] / 'videos/handoff-eval'
source = (project / 'index.html').read_text(encoding='utf-8')
starts = [0, 6, 14, 23, 34, 42]
slots = [6, 8, 9, 11, 8, 8]
timings = []
voices = json.loads((project/'assets/zh-voice-source.json').read_text(encoding='utf-8'))['clips']

def replace_voice(match):
    tag = match[0]
    number = int(re.search(r'id="demo-narration-(\d+)"', tag)[1])
    relative = f'assets/audio/zh-voice-{number:02d}.wav'
    with wave.open(str(project / relative)) as wav:
        duration = wav.getnframes() / wav.getframerate()
    assert duration + .1 < slots[number-1], (number, duration)
    start = starts[number-1] + .1
    tag = re.sub(r'\bsrc="[^"]+"', f'src="{relative}"', tag)
    tag = re.sub(r'\bdata-start="[^"]+"', f'data-start="{start}"', tag)
    tag = re.sub(r'\bdata-duration="[^"]+"', f'data-duration="{duration:.6f}"', tag)
    tag = tag.replace(f'id="demo-narration-{number}"', f'id="zh-narration-{number}"')
    timings.append({**voices[number-1], 'start':start, 'duration':duration})
    return tag

source, count = re.subn(r'<audio\b[^>]*\bid="demo-narration-\d+"[^>]*>', replace_voice, source)
assert count == 6, count
source = source.replace('<html lang="en">','<html lang="zh-CN">').replace('data-label="English narration"','data-label="中文 AI 旁白"')
(project/'variants').mkdir(exist_ok=True)
(project/'variants/index-zh.html').write_text(source,encoding='utf-8')
(project/'assets/zh-narration-timing.json').write_text(json.dumps(timings,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'clips':count,'last_voice_ends':timings[-1]['start']+timings[-1]['duration']},ensure_ascii=False))
