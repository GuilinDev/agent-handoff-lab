"""Build the bilingual v3 edit from continuous narration and observed word timings.

Source text is approved copy; timing is Edge WordBoundary (Mandarin) or a checked
faster-whisper transcription (English). No model decisions or game events are invented.
"""
from pathlib import Path
import difflib
import html
import json
import math
import re
import wave

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / 'videos/handoff-eval'
VO_START = .4
RUN = '20260929T031527021009Z-scripted-delayed-request'
events = {e['id']: e for e in json.loads((ROOT/f'artifacts/runs/{RUN}.json').read_text())['events']}
assert events[2]['result']['verified_count'] == 5
assert events[32]['result']['verified_count'] == 5
assert all(events[e]['verified_crafted'] == 1 for e in (10,40,45))
suite = json.loads((ROOT/'artifacts/suite.json').read_text())
means = []
for condition in ['normal','partial-delivery','delayed-request']:
    runs = [r for r in suite['runs'] if r['condition'] == condition]
    assert len(runs) == 5
    means.append(sum(r['rounds'] for r in runs)/len(runs))

def esc(s): return html.escape(str(s), quote=True)
def js(v): return json.dumps(v, ensure_ascii=False, separators=(',',':'))
def norm(s): return ''.join(c.lower() for c in s if c.isalnum())

CSS = '''
*{box-sizing:border-box}#root{position:relative;width:100%;height:100%}
.frame{position:relative;width:1920px;height:1080px;overflow:hidden;background:#183d34;color:#f5f5eb;font-family:'Montserrat',sans-serif}
.world{position:absolute;inset:0}.capture{position:absolute;left:-320px;top:-360px;width:2560px;height:1800px;max-width:none;image-rendering:pixelated}
.top{position:absolute;left:0;top:0;width:1920px;height:110px;background:#183d34;padding:35px 112px;display:flex;justify-content:space-between;font:24px 'IBM Plex Mono',monospace}
.top em{font-style:normal;color:#f7d59a}
.left,.right,.note,.wide{position:absolute;background:#183d34;border:2px solid #aac19b;padding:28px 30px}
.left{left:112px;top:168px;width:510px}.right{left:1390px;top:200px;width:418px}.note{left:112px;top:605px;width:510px;background:#f7d59a;color:#183d34;border-color:#183d34}
.eyebrow{font:22px/1.4 'IBM Plex Mono',monospace;color:#d7e4c2;margin:0 0 18px}.note .eyebrow{color:#183d34}
h1{font-size:55px;line-height:1.08;letter-spacing:-1.8px;margin:0 0 24px;font-weight:900}h2{font-size:39px;line-height:1.16;margin:0 0 16px;font-weight:900}p{font-size:26px;line-height:1.45;margin:0}.big{font-size:72px;font-weight:900;line-height:1.1;margin:14px 0}
.small{font:22px/1.5 'IBM Plex Mono',monospace}.row{display:flex;gap:16px;align-items:center;margin:20px 0;font-size:25px}.sprite{display:block;width:54px;height:54px;flex-shrink:0;background-size:contain;background-position:center;background-repeat:no-repeat;image-rendering:pixelated}.row b{font-size:36px}.divider{height:2px;background:#789878;margin:22px 0}
.footer{position:absolute;left:0;bottom:0;width:1920px;height:216px;background:#183d34}.source{position:absolute;left:112px;bottom:60px;right:112px;color:#d7e4c2;font:19px/1.2 'IBM Plex Mono',monospace}
.focus{position:absolute;left:705px;top:584px;width:165px;height:195px;border:4px solid #f7d59a;box-shadow:0 0 0 3px #183d34}.focus.smith{left:1090px}.focus.coal{left:1090px;top:305px}.focus span{position:absolute;bottom:100%;left:-4px;padding:9px 12px;margin-bottom:8px;background:#f7d59a;color:#183d34;white-space:nowrap;font-size:25px;font-weight:900}
.pill{display:inline-block;background:#f7d59a;color:#183d34;padding:9px 14px;font:25px 'IBM Plex Mono',monospace;margin:12px 0}
.condition{margin-top:14px;border-left:5px solid #f7d59a;padding:12px 16px;font-size:25px;line-height:1.4}.condition b{display:block;font-size:20px;color:#d7e4c2;margin-bottom:5px}
.chart-title{position:absolute;left:112px;top:170px;width:1350px}.chart-title h1{font-size:70px}.chart{position:absolute;left:112px;top:365px;width:1000px;height:440px;display:flex;align-items:flex-end;gap:70px;border-bottom:3px solid #aac19b}.bar-wrap{position:relative;width:240px}.bar{width:240px;transform-origin:bottom;background:#b6cc9a}.bar-wrap:nth-child(2) .bar{background:#e6bd79}.bar-wrap:nth-child(3) .bar{background:#f7d59a}.value{font-weight:900;font-size:55px;margin-bottom:12px}.bar-label{position:absolute;top:100%;left:0;margin-top:14px;font:21px/1.3 'IBM Plex Mono',monospace}.chart-note{position:absolute;left:1230px;top:395px;width:550px}.chart-note h2{font-size:52px}.chart-note p{font-size:29px;margin-top:24px}
.wide{left:112px;top:170px;width:1020px}.wide h1{font-size:62px}.repo{position:absolute;left:112px;top:604px;width:1160px;padding:27px 32px;background:#f7d59a;color:#183d34}.repo .eyebrow{color:#183d34}.repo p{font:34px/1.4 'IBM Plex Mono',monospace}.right .step{padding:18px 0;border-bottom:1px solid #aac19b;font-size:26px;line-height:1.4}
'''

def sprite(key): return f'<i class="sprite" style="background-image:url(\'assets/items/{key}.png\')" aria-hidden="true"></i>'
def row(key, count, name): return f'<div class="row">{sprite(key)}<b>{count}</b><span>{esc(name)}</span></div>'
def box(cls,label,title,body): return f'<div class="{cls}"><div class="eyebrow">{label}</div><h2>{title}</h2>{body}</div>'
def title(label,headline,sub=''): return f'<div class="left"><div class="eyebrow">{label}</div><h1>{headline}</h1><p>{sub}</p></div>'

def alignment(lang):
    text=(P/f'narration/v3-{lang}.txt').read_text(encoding='utf-8').strip()
    words=json.loads((P/f'narration/v3-{lang}-words.json').read_text(encoding='utf-8'))
    ref=norm(text); actual=''; starts=[]; ends=[]
    for w in words:
        n=norm(w['text']); actual+=n
        starts.extend([w['start']+VO_START]*len(n));ends.extend([w['end']+VO_START]*len(n))
    mapping={}
    matcher=difflib.SequenceMatcher(None,ref,actual,autojunk=False)
    for a,b,size in matcher.get_matching_blocks():
        for k in range(size):mapping[a+k]=b+k
    assert len(mapping)/len(ref)>.93, (lang,len(mapping)/len(ref))
    def span(offset,length):
        match=[mapping[k] for k in range(offset,offset+length) if k in mapping]
        assert match, (lang,offset,length)
        return starts[min(match)],ends[max(match)]
    def at(phrase):
        needle=norm(phrase);idx=ref.index(needle)
        return span(idx,len(needle))[0]
    fragments=re.findall(r'[^.!?。！？;；,:，：\n]+[.!?。！？;；,:，：]?',text)
    pieces=[]
    for fragment in fragments:
        fragment=fragment.strip()
        if not fragment: continue
        spacer=' ' if lang=='en' else ''
        if pieces and not re.search(r'[.!?。！？]$',pieces[-1]) and len(pieces[-1]+spacer+fragment)<=(86 if lang=='en' else 32):
            pieces[-1]+=spacer+fragment
        else: pieces.append(fragment)
    cues=[];cursor=0
    for piece in pieces:
        piece=piece.strip()
        if not piece:continue
        # Soft line wrapping handles remaining long clauses; keep punctuation natural.
        start,end=span(cursor,len(norm(piece)));cursor+=len(norm(piece))
        cues.append({'text':piece,'start':round(start,3),'end':round(end,3)})
    assert cursor==len(ref)
    # Adjacent clauses may share a provider word. Split the display at the next start.
    for i,c in enumerate(cues):
        nxt=cues[i+1]['start'] if i+1<len(cues) else c['end']+.25
        c['end']=round(min(max(c['end']+.15,c['start']+.18),nxt-.01),3)
        assert c['end']>c['start'], c
    return text,at,cues,round(len(mapping)/len(ref),4)

def document(ident,duration,body,tweens,extra=''):
    return f'<!DOCTYPE html><html><head></head><body><template><style>{CSS}{extra}</style><div id="root" data-composition-id="{ident}" data-duration="{duration:.6f}" data-width="1920" data-height="1080"><div id="{ident}" class="frame">{body}</div></div><script>const tl=gsap.timeline({{paused:true}});'+''.join(tweens)+f'window.__timelines["{ident}"]=tl;</script></template></body></html>'

def build(lang):
    text,at,cues,coverage=alignment(lang)
    with wave.open(str(P/f'assets/audio/v3-{lang}-voice.wav')) as wav:voice_duration=wav.getnframes()/wav.getframerate()
    total=math.ceil((voice_duration+VO_START+1.4)*30)/30
    phrases= {
        'en':['I tested','Here\'s the third','Five runs','My takeaway','This scripted baseline'],
        'zh':['我比较了','来看第三种','每种情况','我的体会是','这版先验证']
    }
    boundaries=[0]+[at(s) for s in phrases[lang]]+[total]
    names=['team','conditions','replay','results','insight','close']
    media_offsets=[0,4,10,None,12,20]
    hosts=[];scenes=[]
    for n,name in enumerate(names):
        start,end=boundaries[n:n+2];duration=end-start;ident=f'v3-{lang}-{name}'
        body=[];tweens=[]
        def pop(selector,when=.05):
            tweens.append(f'tl.fromTo("#{ident} {selector}",{{opacity:0,scale:.93,y:8}},{{opacity:1,scale:1,y:0,duration:.35,ease:"power3.out"}},{when:.4f});')
        def state(classname,markup,when,until=None):
            body.append(f'<div class="{classname}">{markup}</div>');pop('.'+classname,when)
            if until is not None:tweens.append(f'tl.to("#{ident} .{classname}",{{opacity:0,duration:.09}},{max(when+.36,until-.10):.4f});')
        media=media_offsets[n]
        if media is not None:
            assert media+duration<=38,(lang,name,duration)
            body.append(f'<div class="world"><video id="{ident}-game" class="clip capture" src="assets/game-session.mp4" data-start="0" data-duration="{duration:.6f}" data-media-start="{media}" data-track-index="1" muted playsinline></video></div>')
        body.append(f'<div class="top"><span>AGENT HANDOFF LAB / SCRIPTED BASELINE</span><em>{n+1:02d} / {name.upper()}</em></div>')
        if name=='team':
            body.append(title('THE QUESTION','Does success<br>mean good<br>teamwork?','A small experiment in AgentWorld.'))
            body.append(box('right','THE TASK','Five roles. Three tools.',row('pickaxe',1,'Pickaxe')+row('axe',1,'Axe')+row('sword2',1,'Sword')))
            body.append(box('note','THE SETUP','Fixed policies','<p>Suppliers → smelter → smith</p><p class="small">Materials supplied. Characters prepositioned.</p>'))
            pop('.left');pop('.right',.3);pop('.note',min(2.7,duration/2))
        elif name=='conditions':
            body.append(title('THE COMPARISON','Change the<br>handoff.','Same task, same scripted policies.'))
            conditions=[('01','Normal delivery','10 coal, request arrives on time'),('02','Half the coal','First delivery capped at 5'),('03','Half + delayed request','Same cap; request held 3 rounds')]
            cards=''.join(f'<div class="condition"><b>{a} / {b}</b>{c}</div>' for a,b,c in conditions)
            body.append(f'<div class="right">{cards}</div>')
            body.append(box('note','CONTROLLED INTERVENTIONS','Five runs each','<p>15 recorded runs in total.</p>'))
            pop('.left');pop('.right',.25);pop('.note',.5)
        elif name=='replay':
            runout=at('The smelter runs out' if lang=='en' else '冶炼者用完后')-start
            wait=at('I delay that message' if lang=='en' else '我让消息晚到')-start
            refill=at('Once it arrives' if lang=='en' else '供应者收到请求')-start
            resumed=at('work resumes' if lang=='en' else '生产才恢复')-start
            cuts=[0,runout,wait,refill,min(resumed,duration-.7),duration]
            state('transfer',title('1 / SHORT DELIVERY','Ten requested.<br>Five delivered.','I cap the first handoff at five.')+box('right','EVENT 2 / VERIFIED','Only half arrives',row('coal',5,'Delivered')+'<p class="small">5 remain with supplier.</p>')+box('note','FIRST TOOL / EVENT 10','First tool complete.',row('pickaxe',1,'Pickaxe')),.03,cuts[1])
            state('empty',title('2 / MATERIALS RUN OUT','The next batch<br>cannot start.','Required: 5 coal. Available: 0.')+box('right','EVENT 14 / ACTUAL ERROR','Missing materials',row('ironore',5,'Iron ore')+row('coal',0,'Coal'))+'<div class="focus"><span>NEEDS COAL</span></div>',cuts[1],cuts[2])
            state('held',title('3 / DELAYED REQUEST','The request<br>has to wait.','I hold this message for three rounds.')+box('right','EVENT 19 / MESSAGE','Need 5 more coal','<div class="big">3 rounds</div><p class="small">Sent: round 4</p><p class="small">Delivered: round 7</p>')+'<div class="focus"><span>WAITING</span></div>',cuts[2],cuts[3])
            state('refill',title('4 / SUPPLIER RESPONDS','Request arrives.<br>Coal follows.','The supplier sends the remaining five.')+box('right','EVENT 32 / VERIFIED','Replenished',row('coal',5,'Delivered'))+'<div class="focus coal"><span>REFILL SENT</span></div>',cuts[3],cuts[4])
            state('resume',title('5 / PRODUCTION RECOVERS','Back to work.','Materials consumed. Outputs verified.')+box('right','EVENTS 10 / 40 / 45','All three tools',row('pickaxe',1,'Pickaxe')+row('axe',1,'Axe')+row('sword2',1,'Sword'))+'<div class="focus smith"><span>3 / 3 VERIFIED</span></div>',cuts[4])
            scenes.append({'language':lang,'scene':'replay-states','times':[round(start+c,3) for c in cuts]})
        elif name=='results':
            body.append('<div class="chart-title"><div class="eyebrow">FIVE RUNS PER CONDITION</div><h1>15 / 15 succeed.</h1><p>Mean rounds to verified completion</p></div>')
            labels=['Normal','Half the coal','Half + delay']
            bars=''.join(f'<div class="bar-wrap"><div class="value">{m:.1f}</div><div class="bar" style="height:{m*29}px"></div><div class="bar-label">{label}</div></div>' for m,label in zip(means,labels))
            body.append('<div class="chart">'+bars+'</div><div class="chart-note"><h2>Completion took more rounds.</h2><p>Same fixed-policy task.<br>Different disruptions.</p><p class="small">One partial-delivery run also hit an engine cooldown.</p></div>')
            pop('.chart-title');pop('.chart-note',.45)
            tweens.append(f'tl.fromTo("#{ident} .bar",{{scaleY:0}},{{scaleY:1,duration:.7,ease:"power3.out",stagger:.12}},.3);')
        elif name=='insight':
            trace=at('Traces show' if lang=='en' else '轨迹能告诉我们')-start
            state('eval',title('MY TAKEAWAY','Evaluate<br>the handoff.','Measure recovery alongside success.')+box('right','WHAT TO INSPECT','Beyond the result','<div class="step">Verified transfers</div><div class="step">Failed actions</div><div class="step">Waits and recovery</div>'),.03,trace)
            state('trace',title('EXPLAINABILITY / SCOPE','Evidence of<br>behavior.','Inventory deltas and delivered messages.')+box('right','WHAT A TRACE CAN SHOW','What happened','<p>Who sent what, what failed, and when work resumed.</p><div class="divider"></div><p>It does not expose a model’s internal reasoning.</p>'),trace)
        else:
            body.append('<div class="wide"><div class="eyebrow">WHAT COMES NEXT</div><h1>Same experiment.<br>LLM policies next.</h1><p>This scripted baseline checks the measurement setup.</p></div>')
            body.append('<div class="repo"><div class="eyebrow">CODE + TRACES + REPRODUCTION STEPS</div><p>github.com/GuilinDev/agent-handoff-lab</p><p class="small">Public repository · Link in the post</p></div>')
            pop('.wide');pop('.repo',min(2.5,duration/3))
        body.append('<div class="footer"></div><div class="source">AgentWorld / Kaetram · Edited real gameplay + trace overlays · Fixed policies; no LLM results claimed</div>')
        (P/f'compositions/{ident}.html').write_text(document(ident,duration,''.join(body),tweens),encoding='utf-8')
        hosts.append(f'<div id="{ident}" class="clip scene" data-composition-id="{ident}" data-composition-src="compositions/{ident}.html" data-start="{start:.6f}" data-duration="{duration:.6f}" data-track-index="0" data-track-kind="graphics" data-width="1920" data-height="1080"></div>')
        scenes.append({'language':lang,'scene':name,'start':round(start,3),'end':round(end,3),'duration':round(duration,3)})
    caption_id=f'v3-{lang}-captions'
    caption_css='''@font-face{font-family:'Noto SC Local';src:url('assets/fonts/noto-sans-sc-v3.ttf') format('truetype');font-weight:500;font-style:normal}#root{position:relative;width:100%;height:100%}.cue{position:absolute;left:192px;top:874px;width:1536px;height:96px;display:flex;align-items:center;justify-content:center;text-align:center;color:#fff;background:#183d34}.cue p{font-family:'Noto SC Local','Montserrat',sans-serif;font-size:36px;font-weight:500;line-height:1.3;margin:0;max-width:1470px}'''
    if lang=='en':caption_css=caption_css.replace("'Noto SC Local','Montserrat'","'Montserrat'")
    captions=''.join(f'<div id="{caption_id}-{i}" class="clip cue" data-start="{c["start"]:.3f}" data-duration="{c["end"]-c["start"]:.3f}"><p>{esc(c["text"])}</p></div>' for i,c in enumerate(cues))
    (P/f'compositions/{caption_id}.html').write_text(f'<!DOCTYPE html><html><body><template><style>{caption_css}</style><div id="root" data-composition-id="{caption_id}" data-duration="{total}" data-width="1920" data-height="1080">{captions}</div><script>window.__timelines["{caption_id}"]=gsap.timeline({{paused:true}});</script></template></body></html>',encoding='utf-8')
    hosts.append(f'<div id="{caption_id}" class="clip scene captions" data-composition-id="{caption_id}" data-composition-src="compositions/{caption_id}.html" data-start="0" data-duration="{total}" data-track-index="20" data-track-kind="captions" data-width="1920" data-height="1080"></div>')
    fx={'version':1,'nodes':[{'type':'gain','id':'voice-gain','label':'Measured voice gain','params':{'gain':9 if lang=='en' else 10.2}},{'type':'compressor','id':'voice-level','label':'Peak control','params':{'threshold':-12,'ratio':4,'attack':5,'release':100,'knee':2.83,'makeup':0,'mix':1}},{'type':'limiter','id':'voice-ceiling','params':{'limit':-1.5,'attack':5,'release':50,'level_out':0}}]}
    automation={'version':1,'lanes':[{'target':'volume','points':[{'t':0,'v':0},{'t':1.2,'v':.22},{'t':total-2,'v':.22},{'t':total,'v':0}]}]}
    audio=f'<audio id="v3-{lang}-voice" class="clip" src="assets/audio/v3-{lang}-voice.wav" data-start="{VO_START}" data-duration="{voice_duration:.6f}" data-track-index="10" data-audio-group="voiceover" data-volume="1"></audio><hf-audio-group id="voiceover" data-volume="1" data-fx-chain="{esc(js(fx))}"></hf-audio-group><audio id="music-bed" class="clip" src="assets/audio/pixabay-554832.mp3" data-start="0" data-duration="{total}" data-track-index="11" data-volume="0.22" data-automation="{esc(js(automation))}"></audio>'
    doc=f'<!DOCTYPE html><html lang="{lang}"><head><meta charset="UTF-8"><script src="assets/gsap.min.js"></script><style>*{{box-sizing:border-box}}html,body{{margin:0;width:1920px;height:1080px;overflow:hidden;background:#183d34}}body{{font-family:"Montserrat",sans-serif}}#root{{position:relative;width:100%;height:100%}}.scene{{position:absolute;inset:0;width:100%;height:100%}}.captions{{z-index:50;pointer-events:none}}</style></head><body><div id="root" data-composition-id="main" data-start="0" data-duration="{total}" data-width="1920" data-height="1080">'+''.join(hosts)+audio+'</div><script>window.__timelines.main=gsap.timeline({paused:true});</script></body></html>'
    doc=doc.replace('body{font-family:"Montserrat",sans-serif}', 'body{font-family:"IBM Plex Mono",monospace}.scene{font-family:"Montserrat",sans-serif}')
    path=P/('index.html' if lang=='en' else 'variants/index-zh.html')
    path.write_text(doc,encoding='utf-8')
    (P/f'narration/v3-{lang}-captions.json').write_text(json.dumps(cues,ensure_ascii=False,indent=2),encoding='utf-8')
    def srt_time(seconds):
        ms=round(seconds*1000)
        hours,ms=divmod(ms,3600000);minutes,ms=divmod(ms,60000);seconds,ms=divmod(ms,1000)
        return f'{hours:02d}:{minutes:02d}:{seconds:02d},{ms:03d}'
    srt='\n\n'.join(f"{i}\n{srt_time(c['start'])} --> {srt_time(c['end'])}\n{c['text']}" for i,c in enumerate(cues,1))+'\n'
    (P/f'narration/v3-{lang}.srt').write_text(srt,encoding='utf-8')
    return {'language':lang,'duration':total,'voice_start':VO_START,'voice_duration':voice_duration,'voice_end':VO_START+voice_duration,'alignment_coverage':coverage,'scene_cuts':boundaries,'scenes':scenes,'caption_count':len(cues),'gameplay_seconds':round(total-(boundaries[4]-boundaries[3]),3)}

result=[build(lang) for lang in ['en','zh']]
(P/'narration/v3-timing.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
