"""Bake the v2 editorial replay from recorded, verified engine events.

Run after the six demo-voice WAVs have been generated. This builds HyperFrames
source, not synthetic gameplay. Picture cuts and event overlays are editorial;
the source run, event ids and inventory evidence are saved alongside the film.
"""
from pathlib import Path
import html
import json
import re
import wave

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / 'videos/handoff-eval'
RUN_ID = '20260929T031527021009Z-scripted-delayed-request'
run = json.loads((ROOT / 'artifacts/runs' / (RUN_ID + '.json')).read_text())
events = {e['id']: e for e in run['events']}
assert events[2]['result']['verified_count'] == 5
assert events[14]['result']['missingMaterials'][0]['missing'] == 5
assert events[32]['result']['verified_count'] == 5
assert all(events[i]['verified_crafted'] == 1 for i in (10, 40, 45))

def esc(value):
    return html.escape(str(value), quote=True)

def attr(value):
    return esc(json.dumps(value, separators=(',', ':')))

def item(key, label, count=None):
    amount = '' if count is None else f'<b>{count}</b>'
    return f'<div class="item-row"><img src="assets/items/{key}.png" alt="">{amount}<span>{label}</span></div>'

def panel(title, body, cls=''):
    return f'<div class="readout {cls}"><div class="eyebrow">{title}</div>{body}</div>'

def note(text, tag='', cls=''):
    return f'<div class="note {cls}"><div class="eyebrow">{tag}</div><div>{text}</div></div>'

css = '''
*{box-sizing:border-box}.demo{position:relative;width:100%;height:100%;overflow:hidden;background:#183d34;color:#f5f5eb;font-family:'Montserrat',sans-serif}
.world{position:absolute;inset:0;width:1920px;height:1080px;transform-origin:1000px 540px;will-change:transform}
.capture{position:absolute;left:-320px;top:-360px;width:2560px;height:1800px;max-width:none;object-fit:fill;image-rendering:pixelated}
.topbar{position:absolute;inset:0 0 auto;height:122px;background:#183d34;display:flex;align-items:center;justify-content:space-between;padding:0 112px;font:25px 'IBM Plex Mono',monospace;letter-spacing:1px}
.stage-number{color:#f7d59a}.headbox{position:absolute;left:112px;top:175px;width:510px;background:#183d34;padding:30px 32px 34px;border:2px solid #a8c39b}
.eyebrow{font:23px 'IBM Plex Mono',monospace;line-height:1.4;color:#d7e4c2;margin-bottom:15px}.headline{font-size:63px;line-height:1.09;font-weight:900;letter-spacing:-2px;margin:0}.subline{font-size:27px;line-height:1.45;margin:22px 0 0}
.note{position:absolute;left:112px;top:565px;width:510px;padding:26px 30px;background:#f5f5eb;color:#183d34;font-size:33px;line-height:1.3;border:3px solid #183d34;transform-origin:50% 50%}
.note .eyebrow{color:#476458;font-size:22px}.note strong{font-size:54px;font-weight:900}.note.amber{background:#f7d59a}.note.dark{background:#183d34;color:#f5f5eb;border-color:#d7e4c2}.note.dark .eyebrow{color:#d7e4c2}
.readout{position:absolute;left:1410px;top:228px;width:398px;padding:28px;background:#183d34;border:2px solid #d7e4c2;font-size:27px;line-height:1.4}.readout .large{font-size:60px;line-height:1.1;font-weight:900;margin:8px 0 15px}.item-row{display:flex;align-items:center;gap:14px;min-height:75px;font:25px 'IBM Plex Mono',monospace}.item-row img{width:57px;height:57px;object-fit:contain;image-rendering:pixelated}.item-row b{font:900 41px 'Montserrat',sans-serif;min-width:45px}.readout .rule{height:2px;background:#668378;margin:20px 0}.readout .small{font:23px/1.5 'IBM Plex Mono',monospace}
.pin{position:absolute;padding:8px 15px;background:#183d34;border:2px solid #d7e4c2;color:#f5f5eb;font:24px 'IBM Plex Mono',monospace;white-space:nowrap}.pin.iron{left:697px;top:283px}.pin.coal{left:1090px;top:283px}.pin.smelter{left:653px;top:813px}.pin.wood{left:931px;top:813px}.pin.smith{left:1140px;top:813px}
.focus{position:absolute;border:4px solid #f7d59a;width:162px;height:190px;left:705px;top:584px;box-shadow:0 0 0 3px #183d34;pointer-events:none}.focus.coal{left:1090px;top:305px}.focus.smith{left:1090px;top:584px}.focus .focus-caption{position:absolute;left:-8px;top:-58px;background:#f7d59a;color:#183d34;padding:8px 14px;white-space:nowrap;font:900 26px 'Montserrat',sans-serif}
.cargo-flight{position:absolute;width:92px;height:92px;left:1124px;top:440px}.cargo{position:relative;width:92px;height:92px;background:#f5f5eb;border:4px solid #183d34;border-radius:18px;display:grid;place-items:center;box-shadow:0 7px 0 #183d34}.cargo img{width:65px;height:65px;image-rendering:pixelated}.cargo span{position:absolute;right:-18px;top:-20px;background:#f7d59a;color:#183d34;font:900 30px 'Montserrat',sans-serif;padding:2px 9px;border:3px solid #183d34}
.bottom{position:absolute;left:0;right:0;bottom:0;height:130px;background:#183d34;padding:22px 112px;display:flex;align-items:center;justify-content:space-between}.source{font:22px/1.5 'IBM Plex Mono',monospace;max-width:1060px;color:#d7e4c2}.goal{display:flex;gap:16px;align-items:center;font:27px 'IBM Plex Mono',monospace}.goal-icon{width:65px;height:65px;border:2px solid #d7e4c2;display:grid;place-items:center;background:#284e40}.goal-icon img{width:48px;height:48px;image-rendering:pixelated}.goal.done{color:#f7d59a}
.tools{display:flex;gap:14px;justify-content:space-between;margin-top:20px}.tool{width:100px;text-align:center}.tool img{width:94px;height:94px;image-rendering:pixelated}.tool span{display:block;font:20px 'IBM Plex Mono',monospace;margin-top:8px}
.rounds{display:flex;gap:10px;margin:23px 0}.round{font:900 36px 'Montserrat',sans-serif;padding:10px 15px;border:2px solid #a8c39b}.quote{font-size:30px;line-height:1.5}.credits{font:23px/1.5 'IBM Plex Mono',monospace;color:#d7e4c2}
.ending{padding:175px 112px 145px}.ending h1{font-size:83px;line-height:1.1;max-width:1350px;margin:0 0 25px;font-weight:900;letter-spacing:-3px}.ending .lead{font:31px 'IBM Plex Mono',monospace}.chart{position:absolute;left:112px;top:424px;width:970px;height:455px;display:flex;align-items:flex-end;gap:58px;border-bottom:3px solid #d7e4c2}.bar-wrap{width:250px;position:relative}.bar{width:250px;transform-origin:bottom;background:#b6cc9a}.bar-wrap:nth-child(2) .bar{background:#e6bd79}.bar-wrap:nth-child(3) .bar{background:#f7d59a}.bar-value{font-size:65px;font-weight:900;margin-bottom:13px}.bar-label{position:absolute;top:100%;padding-top:17px;font:22px/1.4 'IBM Plex Mono',monospace;white-space:nowrap}.takeaway{position:absolute;left:1200px;top:440px;width:580px;font-size:58px;line-height:1.1;font-weight:900}.takeaway p{font:27px/1.5 'IBM Plex Mono',monospace;margin-top:30px}.under{position:absolute;bottom:57px;left:112px;font:22px 'IBM Plex Mono',monospace;color:#d7e4c2}
'''
(PROJECT / 'assets/demo.css').write_text(css, encoding='utf-8')

shots = [
    ('demo-hook', 0, 6, 12, 'WATCH THE HANDOFF', 'One handoff.<br>Team stalled.', 'Five agents. Three tools. A missing delivery.'),
    ('demo-party', 6, 8, 2, 'MEET THE TEAM', 'Make three<br>new tools.', 'Suppliers → smelter → smith'),
    ('demo-coal', 14, 9, 2, 'THE SHORT DELIVERY', 'Only half<br>the coal.', 'Requested: 10. Delivered: 5.'),
    ('demo-recovery', 23, 11, 12, 'THE COORDINATION DELAY', 'Ask for coal.<br>Then wait.', 'A delayed request becomes a dependency test.'),
    ('demo-finish', 34, 8, 28, 'BACK TO WORK', 'Watch the<br>inventory.', 'Three new outputs. Verified against materials.'),
    ('demo-result', 42, 8, None, 'THE EVAL QUESTION', '', ''),
]

def make_scene(ident, start, duration, media, label, title, sub):
    parts=[]; tweens=[]
    def reveal(cls, at=0, end=None, pop=True):
        selector = f'#{ident} {cls}'
        tweens.append(f'tl.fromTo({json.dumps(selector)},{{opacity:0,scale:{0.88 if pop else 1},y:{12 if pop else 0}}},{{opacity:1,scale:1,y:0,duration:.35,ease:"power3.out"}},{at});')
        if end is not None:
            tweens.append(f'tl.to({json.dumps(selector)},{{opacity:0,duration:.12}},{end-.12});')
    def add(html_text, cls, at=0, end=None):
        parts.append(html_text.replace('class="', f'class="{cls} ', 1)); reveal('.'+cls,at,end)
    if media is not None:
        parts.append(f'<div class="world"><video id="{ident}-video" class="clip capture" src="assets/game-session.mp4" data-start="0" data-duration="{duration}" data-media-start="{media}" data-track-index="1" muted playsinline></video>')
        if ident=='demo-party':
            for role in ('iron','coal','smelter','wood','smith'):
                parts.append(f'<div class="pin {role}">{role.upper()}</div>')
            reveal('.pin',.2)
        parts.append('</div>')
        parts.append(f'<div class="headbox"><div class="eyebrow">{label}</div><h1 class="headline">{title}</h1><p class="subline">{sub}</p></div>')
        reveal('.headbox',.05)
        tweens.append(f'tl.fromTo("#{ident} .world",{{scale:1}},{{scale:1.035,duration:{duration},ease:"none"}},0);')
    parts.append(f'<div class="topbar"><span>AGENT HANDOFF LAB / SCRIPTED BASELINE</span><span class="stage-number">{start:02d}–{start+duration:02d}s / REAL ENGINE</span></div>')
    if ident=='demo-hook':
        add(note('<strong>5 coal missing.</strong>','ACTUAL ERROR / EVENT 14','amber'),'hook-error',.3)
        add(panel('SMELTER / EVENT 14',item('ironore','Iron ore',5)+item('coal','Coal',0)+'<div class="rule"></div><div class="large">BLOCKED</div><div class="small">“Missing required materials”</div>'),'hook-inventory',.7)
        add('<div class="focus"><span class="focus-caption">NEEDS COAL</span></div>','hook-focus',.45)
        bottom='Cold open from event 14. Rewind next to the first handoff.'
    elif ident=='demo-party':
        add(note(item('ironore','Iron ore',10)+item('coal','Coal',10)+item('logs','Logs',2),'STARTING MATERIALS'),'party-materials',.3)
        add(panel('THE QUEST','<div class="large">0 / 3</div><div>Newly crafted tools</div><div class="tools">'+''.join(f'<div class="tool"><img src="assets/items/{k}.png" alt=""><span>{n}</span></div>' for k,n in [('pickaxe','Pickaxe'),('axe','Axe'),('sword2','Sword')])+'</div>'),'party-quest',.7)
        bottom='Materials supplied · characters prepositioned · five fixed policies'
    elif ident=='demo-coal':
        add(note(item('coal','Delivered',5)+'<div>5 remain with the supplier.</div>','VERIFIED TRANSFER / EVENT 2','amber'),'coal-transfer',.25,3.1)
        add(note(item('ironbar','New bars',5),'FIRST BATCH / EVENT 4'),'coal-batch',3.2,6.05)
        add(note('<strong>Next batch fails.</strong><div>Required: 5 coal. Available: 0.</div>','ACTUAL ERROR / EVENT 14','amber'),'coal-failure',6.15)
        add(panel('AFTER HANDOFF',item('ironore','Iron ore',10)+item('coal','Coal',5)),'coal-state-a',.3,3.05)
        add(panel('AFTER FIRST BATCH',item('ironore','Iron ore',5)+item('coal','Coal',0)+item('ironbar','New bars',5)),'coal-state-b',3.15,6.05)
        add(panel('FIRST TOOL / EVENT 10',item('pickaxe','Verified',1)+'<div class="rule"></div><div class="large">1 / 3</div><div>But the smelter is out of coal.</div>'),'coal-state-c',6.15)
        add('<div class="focus coal"><span class="focus-caption">ONLY FIVE</span></div>','coal-focus',.4,2.9)
        add('<div class="focus"><span class="focus-caption">NO COAL LEFT</span></div>','coal-focus-b',6.2)
        parts.append('<div class="cargo-flight"><div class="cargo"><img src="assets/items/coal.png" alt=""><span>5</span></div></div>')
        reveal('.cargo',.5,2.5)
        tweens.append(f'tl.fromTo("#{ident} .cargo-flight",{{x:0,y:0}},{{x:-380,y:235,duration:1.25,ease:"power2.inOut"}},.7);')
        bottom='Events 2 → 4 → 10 → 14 · transfers and crafting checked against inventory'
    elif ident=='demo-recovery':
        message=events[19]['args']['message'].split('.')[0]+'.'
        add(note(esc(message),'SMELTER → COAL / EVENT 19','amber'),'recovery-message',.2,5.35)
        add(panel('MESSAGE DELAY','<div class="large">3 rounds</div><div class="rounds"><span class="round r5">R5</span><span class="round r6">R6</span><span class="round r7">R7</span></div><div class="small">Sent in round 4.<br>Delivered in round 7.</div>'),'recovery-delay',.6,5.35)
        reveal('.r5',1.8);reveal('.r6',3.1);reveal('.r7',4.5)
        add('<div class="focus"><span class="focus-caption">WAITING</span></div>','recovery-focus',.4,5.35)
        add(note(item('coal','Delivered',5),'REQUEST RECEIVED / EVENT 32'),'recovery-delivery',5.45)
        add(panel('PRODUCTION RESUMES',item('ironbar','New bars',5)+'<div class="rule"></div><div class="small">EVENT 34<br>Materials consumed.<br>Output verified.</div>'),'recovery-success',7)
        parts.append('<div class="cargo-flight"><div class="cargo"><img src="assets/items/coal.png" alt=""><span>5</span></div></div>')
        reveal('.cargo',5.4,7.7)
        tweens.append(f'tl.fromTo("#{ident} .cargo-flight",{{x:0,y:0}},{{x:-380,y:235,duration:1.1,ease:"power2.inOut"}},5.6);')
        bottom='Message timing is the intervention. The recorded policy waits for delivery.'
    elif ident=='demo-finish':
        add(note(item('ironbar','To the smith',5),'VERIFIED HANDOFF / EVENT 39'),'finish-bars',.15,2.3)
        add(note(item('axe','Newly crafted',1),'MATERIALS CONSUMED / EVENT 40'),'finish-axe',2.4,5.05)
        add(note(item('sword2','Newly crafted',1),'FINAL RECIPE / EVENT 45'),'finish-sword',5.15)
        add(panel('SMITH INVENTORY',item('pickaxe','Pickaxe',1)+'<div class="rule"></div><div class="large">1 / 3</div>'),'finish-state-a',.2,2.3)
        add(panel('SMITH INVENTORY',item('pickaxe','Pickaxe',1)+item('axe','Axe',1)+'<div class="large">2 / 3</div>'),'finish-state-b',2.4,5.05)
        add(panel('ALL OUTPUTS VERIFIED',item('pickaxe','Pickaxe',1)+item('axe','Axe',1)+item('sword2','Heavy sword',1)+'<div class="large">3 / 3 ✓</div>'),'finish-state-c',5.15)
        add('<div class="focus smith"><span class="focus-caption">CRAFTING</span></div>','finish-focus',.4,5.05)
        add('<div class="focus smith"><span class="focus-caption">QUEST COMPLETE</span></div>','finish-focus-done',5.15)
        bottom='This recorded run completes in 9 rounds. No LLM results are claimed.'
    else:
        suite=json.loads((ROOT/'artifacts/suite.json').read_text())
        conditions=[('normal','Normal'),('partial-delivery','Partial delivery'),('delayed-request','+ Delayed request')]
        bars=[]
        for condition,name in conditions:
            rows=[r for r in suite['runs'] if r['condition']==condition]
            avg=sum(r['rounds'] for r in rows)/len(rows)
            bars.append(f'<div class="bar-wrap"><div class="bar-value">{avg:.1f}</div><div class="bar" style="height:{avg*33}px"></div><div class="bar-label">{name}<br>n = {len(rows)}</div></div>')
        parts.append('<div class="ending"><h1>Same success. Different cost.</h1><div class="lead">15 / 15 runs succeed. Mean rounds to completion:</div></div><div class="chart">'+''.join(bars)+'</div><div class="takeaway">Trace the handoff.<br>Test the dependency.<p>Next: compare LLM policies under the same interventions.</p></div><div class="under">Fixed-policy baseline · includes cooldown effects · behavior traces ≠ internal reasoning</div>')
        reveal('.ending',.1);reveal('.takeaway',1.4)
        tweens.append(f'tl.fromTo("#{ident} .bar",{{scaleY:0}},{{scaleY:1,duration:.7,ease:"power3.out",stagger:.12}},.35);')
        bottom=None
    if bottom:
        parts.append(f'<div class="bottom"><div class="source">{bottom}<br>AgentWorld / Kaetram · Edited recording + trace overlays</div><div class="goal"><div class="goal-icon"><img src="assets/items/pickaxe.png" alt=""></div><div class="goal-icon"><img src="assets/items/axe.png" alt=""></div><div class="goal-icon"><img src="assets/items/sword2.png" alt=""></div></div></div>')
    content=''.join(parts)
    # Repeated UI icons are CSS sprites, not independent timed image clips.
    content=re.sub(r'<img src="([^"]+)" alt="">', lambda m: f'<i class="sprite" style="background-image:url(\'{m[1]}\')" aria-hidden="true"></i>', content)
    scene_css=css.replace(' img', ' .sprite')+'#root{position:relative;width:100%;height:100%}.sprite{display:block;flex-shrink:0;background-size:contain;background-position:center;background-repeat:no-repeat;image-rendering:pixelated}'
    doc=f'<!DOCTYPE html><html><head></head><body><template><style>{scene_css}</style><div id="root" data-composition-id="{ident}" data-duration="{duration}" data-width="1920" data-height="1080"><div id="{ident}" class="demo">'+content+f'</div></div><script>const tl=gsap.timeline({{paused:true}});'+''.join(tweens)+f'window.__timelines["{ident}"]=tl;</script></template></body></html>'
    (PROJECT/'compositions'/f'{ident}.html').write_text(doc,encoding='utf-8')

for shot in shots:
    make_scene(*shot)

hosts='\n'.join(f'<div id="{ident}-host" class="clip scene" data-composition-id="{ident}" data-composition-src="compositions/{ident}.html" data-start="{start}" data-duration="{duration}" data-track-index="0" data-track-kind="graphics" data-width="1920" data-height="1080"></div>' for ident,start,duration,*_ in shots)
voices=[];timing=[]
for i,(ident,start,duration,*_) in enumerate(shots,1):
    relative=f'assets/audio/demo-voice-{i:02d}.wav'
    with wave.open(str(PROJECT/relative)) as wav:
        length=wav.getnframes()/wav.getframerate()
    assert length+.3<duration, (ident,length,duration)
    voices.append(f'<audio id="demo-narration-{i}" class="clip" src="{relative}" data-start="{start+.2}" data-duration="{length:.6f}" data-track-index="10" data-audio-group="voiceover" data-volume="1"></audio>')
    timing.append({'scene':ident,'start':start+.2,'duration':length,'text':(PROJECT/f'assets/audio/demo-script-{i:02d}.txt').read_text().strip()})
fx={'version':1,'nodes':[{'type':'compressor','id':'voice-evenness','label':'Voice levelling','params':{'threshold':-18,'ratio':3,'attack':8,'release':120,'knee':2.83,'makeup':8,'mix':1}},{'type':'limiter','id':'voice-ceiling','label':'Voice peak ceiling','params':{'limit':-2,'attack':5,'release':50,'level_out':0}}]}
automation={'version':1,'lanes':[{'target':'volume','points':[{'t':0,'v':0},{'t':1.5,'v':.5},{'t':47.5,'v':.5},{'t':50,'v':0}]}]}
index='''<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=1920,height=1080"><script src="assets/gsap.min.js"></script><style>*{box-sizing:border-box}html,body{margin:0;width:1920px;height:1080px;overflow:hidden;background:#183d34}#root{width:100%;height:100%;position:relative}.scene{position:absolute;inset:0;width:100%;height:100%}</style></head><body><div id="root" data-composition-id="main" data-start="0" data-duration="50" data-width="1920" data-height="1080">'''+hosts+f'<hf-audio-group id="voiceover" data-label="English narration" data-volume="1" data-fx-chain="{attr(fx)}"></hf-audio-group>'+''.join(voices)+f'<audio id="music-bed" class="clip" src="assets/audio/pixabay-554832.mp3" data-start="0" data-duration="50" data-track-index="11" data-volume="0.5" data-automation="{attr(automation)}"></audio>'+'''</div><script>const tl=gsap.timeline({paused:true});window.__timelines.main=tl;</script></body></html>'''
index=index.replace('#root{', "body{font-family:'IBM Plex Mono',monospace}#root{", 1)
(PROJECT/'index.html').write_text(index,encoding='utf-8')
(PROJECT/'assets/demo-evidence.json').write_text(json.dumps({'source_run':RUN_ID,'editing':'Editorial cuts and trace overlays; not synchronized raw UI telemetry. No simulated gameplay or model reasoning.','events':[events[i] for i in (2,4,10,14,19,32,34,39,40,45)],'narration':timing},indent=2),encoding='utf-8')
print(json.dumps({'scenes':len(shots),'duration':50,'gameplay_seconds':42,'narration':timing},indent=2))
