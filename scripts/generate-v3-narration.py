"""Generate a continuous v3 voice track and its alignment data.

Run with a Python environment containing edge-tts==7.2.8 and/or
faster-whisper==1.2.1 plus HyperFrames' local Kokoro dependencies.
Mandarin uses the Edge online service; English uses local Kokoro and local ASR.
"""
import argparse
import asyncio
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / 'videos/handoff-eval'


async def mandarin():
    import edge_tts
    text=(P/'narration/v3-zh.txt').read_text(encoding='utf-8').replace('AgentWorld','Agent World')
    (P/'narration/v3-zh-tts.txt').write_text(text,encoding='utf-8')
    temporary=ROOT/'.runtime/v3-zh.mp3'
    temporary.parent.mkdir(exist_ok=True)
    voice=edge_tts.Communicate(text,'zh-CN-YunyangNeural',rate='+0%',boundary='WordBoundary')
    words=[]
    with temporary.open('wb') as f:
        async for chunk in voice.stream():
            if chunk['type']=='audio':f.write(chunk['data'])
            elif chunk['type']=='WordBoundary':
                words.append({'text':chunk['text'],'start':chunk['offset']/1e7,
                              'end':(chunk['offset']+chunk['duration'])/1e7})
    (P/'narration/v3-zh-words.json').write_text(json.dumps(words,ensure_ascii=False,indent=2),encoding='utf-8')
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(temporary),
                    '-c:a','pcm_s16le','-ar','24000','-ac','1',str(P/'assets/audio/v3-zh-voice.wav')],check=True)


def english():
    from faster_whisper import WhisperModel
    text=(P/'narration/v3-en.txt').read_text(encoding='utf-8').replace('AgentWorld','Agent World').replace('LLM','L L M')
    script=P/'narration/v3-en-tts.txt';script.write_text(text,encoding='utf-8')
    env={**os.environ,'HYPERFRAMES_PYTHON':sys.executable}
    npx='npx.cmd' if os.name=='nt' else 'npx'
    subprocess.run([npx,'--yes','hyperframes@0.8.94','tts',str(script),'--voice','am_michael',
                    '--lang','en-us','--speed','1.0','--output',str(P/'assets/audio/v3-en-voice.wav')],
                   check=True,cwd=P,env=env)
    model=WhisperModel('base.en',device='cpu',compute_type='int8',cpu_threads=8,
                       download_root=str(ROOT/'.runtime/whisper'))
    segments,_=model.transcribe(str(P/'assets/audio/v3-en-voice.wav'),language='en',
                                word_timestamps=True,beam_size=5)
    words=[{'text':w.word.strip(),'start':w.start,'end':w.end} for segment in segments for w in segment.words]
    (P/'narration/v3-en-words.json').write_text(json.dumps(words,indent=2),encoding='utf-8')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('language',choices=['en','zh'])
    args=parser.parse_args()
    if args.language=='zh':asyncio.run(mandarin())
    else:english()
