const $ = s => document.querySelector(s);
const roles = ['iron','coal','wood','smelter','smith'];
const labels = {iron:'Iron supplier',coal:'Coal supplier',wood:'Wood courier',smelter:'Smelter',smith:'Smith'};
const icons = {iron:'⛏',coal:'◈',wood:'♧',smelter:'♨',smith:'⚒'};
const itemLabels = {ironore:'Iron ore',coal:'Coal',logs:'Logs',ironbar:'Iron bars',hilt2:'Hilt',pickaxe:'Pickaxe',axe:'Axe',sword2:'Heavy sword'};
const conditions = {normal:'Normal supply','partial-delivery':'Partial delivery','delayed-request':'Delayed request'};
let run = null, index = -1, follow = true, timer = null, running = false, allRuns = [], lastRuns = '';
const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const sprite = key => `/engine-assets/img/sprites/items/${key}.png`;
const item = (key,count) => `<span class="item" title="${esc(itemLabels[key]||key)}"><img src="${sprite(key)}" alt="">${count}<span>${esc(itemLabels[key]||key)}</span></span>`;
function note(message,error=false){$('#notice').textContent=message;$('#notice').className=error?'error':'';}
function render(){
  const events=run?.events||[], e=events[index], states=e?.after||run?.initial||{};
  const made={pickaxe:0,axe:0,sword2:0};
  events.slice(0,index+1).forEach(x=>{if(x.action==='craft'&&x.args.item in made)made[x.args.item]+=x.verified_crafted||0;});
  $('#goals').innerHTML=Object.keys(made).map(key=>`<div class="goal ${made[key]?'done':''}"><img src="${sprite(key)}" alt=""><span>${itemLabels[key]}</span><span class="check">${made[key]?'✓':'○'}</span></div>`).join('');
  for(const role of roles){
    const inv=states[role]?.inventory||{}, active=e?.actor===role, blocked=active&&e?.result?.status==='error';
    const markup=`<div class="role-card ${active?'active':''} ${blocked?'blocked':''}" data-role="${role}"><div class="role-head"><div class="role-avatar">${icons[role]}</div><div><div class="role-name">${labels[role]}</div><div class="role-id">${role.toUpperCase()} · ${states[role]?.hp>0?'ONLINE':'READY'}</div></div></div><div class="inventory">${Object.entries(inv).filter(([,n])=>n>0).map(([k,n])=>item(k,n)).join('')||'<span class="empty">No materials held</span>'}</div>${active?`<div class="role-state">${esc(describe(e))}</div>`:''}</div>`;
    if(['iron','coal','wood'].includes(role)) {let slot=$(`#slot-${role}`);if(!slot){slot=document.createElement('div');slot.id=`slot-${role}`;$('#suppliers').append(slot);}slot.innerHTML=markup;}else $(`#${role}-slot`).innerHTML=markup;
  }
  document.querySelectorAll('.connectors path').forEach(p=>p.classList.toggle('active',e?.action==='transfer'&&p.id===`edge-${e.actor}`));
  $('#round').textContent=`ROUND ${e?.round||'—'} / ${run?.fixture?.max_rounds||18}`;
  $('#mode-label').textContent=run?.mode==='llm'?`LLM · ${run.model||'AGENTS'}`:'SCRIPTED · REAL ENGINE';
  $('#event-title').textContent=e?describe(e):'Select an event to inspect the evidence';
  $('#scrubber').max=Math.max(0,events.length-1);$('#scrubber').value=Math.max(0,index);
  $('#event-counter').textContent=`${index+1} / ${events.length} events`;
  $('#run-duration').textContent=run?.duration_s?`${run.duration_s.toFixed(1)}s actual runtime · replay timing compressed`:'Evidence from the game API';
  $('#timeline').innerHTML=events.map((x,i)=>`<button class="tick ${x.action!=='wait'?'action':''} ${x.result?.status==='error'?'error':''} ${i===index?'selected':''}" data-index="${i}" title="${esc(describe(x))}">${x.action==='transfer'?'↗':x.action==='craft'?'⚒':x.action==='chat'?'◌':'·'}</button>`).join('');
  const selected=$('#timeline .selected');if(selected)$('#timeline').scrollLeft=Math.max(0,selected.offsetLeft-$('#timeline').offsetLeft-$('#timeline').clientWidth/2);
  inspect(e);
  if(run){$('#download').href=`/runs/${encodeURIComponent(run.id)}.json`;$('#download').download=run.id+'.json';}
}
function describe(e){
  if(e.action==='transfer')return `${labels[e.actor]} → ${labels[e.args.target]}: ${e.result?.verified_count||0} ${itemLabels[e.args.item]||e.args.item}`;
  if(e.action==='craft')return `${labels[e.actor]}: ${e.verified_crafted?'crafted '+e.verified_crafted:'attempted'} ${itemLabels[e.args.item]||e.args.item}`;
  if(e.action==='chat')return `${labels[e.actor]} → ${labels[e.args.target]||'team'}: message`;
  return `${labels[e.actor]}: waiting`;
}
function inspect(e){
  if(!e){$('#inspector').innerHTML='<p class="muted">A recorded run will load automatically. Select any event to see its before-and-after state.</p>';return;}
  const failed=e.result?.status==='error';
  $('#event-verdict').textContent=failed?'BLOCKED':e.action==='wait'?'WAITING':e.action==='chat'?'MESSAGE':'VERIFIED';
  $('#event-verdict').className=`verdict ${failed?'bad':e.action==='wait'?'':'ok'}`;
  let deltas='';for(const role of roles){const before=e.before?.[role]?.inventory||{},after=e.after?.[role]?.inventory||{};for(const key of new Set([...Object.keys(before),...Object.keys(after)])){const a=before[key]||0,b=after[key]||0;if(a!==b)deltas+=`<div class="delta-row"><div>${esc(labels[role])}<small>${esc(itemLabels[key]||key)}</small></div><strong class="${b>a?'positive':'negative'}">${a} → ${b}</strong></div>`;}}
  $('#inspector').innerHTML=`<div class="event-meta">EVENT ${String(e.id).padStart(3,'0')} · ROUND ${e.round} · ${e.elapsed_s.toFixed(1)}s</div><p class="event-description">${esc(describe(e))}</p>${e.intervention?`<div class="intervention">${esc(e.intervention)}</div>`:''}${e.action==='chat'?`<p class="event-description">“${esc(e.args.message)}”</p>`:''}${deltas||'<p class="muted">No inventory change in this event.</p>'}<p class="result-text" style="margin-top:15px">${esc(e.result?.message||e.args.reason||'')}</p>${e.action==='wait'?`<p class="result-text">${esc(e.args.reason)}</p>`:''}${e.result?.missingMaterials?`<div class="intervention">Missing: ${e.result.missingMaterials.map(x=>`${x.missing} ${esc(x.name)}`).join(', ')}</div>`:''}`;
}
function stop(){if(timer)clearInterval(timer);timer=null;$('#play').textContent='▶';}
function go(i){follow=false;index=Math.max(0,Math.min(i,(run?.events?.length||1)-1));render();}
$('#prev').onclick=()=>{stop();go(index-1);};$('#next').onclick=()=>{stop();go(index+1);};
$('#scrubber').oninput=e=>{stop();go(Number(e.target.value));};
$('#timeline').onclick=e=>{const b=e.target.closest('button[data-index]');if(b){stop();go(Number(b.dataset.index));}};
$('#play').onclick=()=>{if(timer)return stop();follow=false;if(index>=(run?.events?.length||0)-1)index=-1;$('#play').textContent='Ⅱ';timer=setInterval(()=>{if(index>=(run?.events?.length||0)-1)return stop();index++;render();},650);};
$('#follow').onclick=()=>{stop();follow=true;poll();};
$('#run').onclick=async()=>{stop();const response=await fetch('/api/run',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({mode:$('#mode').value,condition:$('#condition').value})});const data=await response.json();if(!response.ok)return note(data.error,true);follow=true;note('Starting a fresh fixture on the game engine…');$('#run').disabled=true;};
$('#run-select').onchange=async e=>{stop();follow=false;const response=await fetch(`/runs/${encodeURIComponent(e.target.value)}.json`);run=await response.json();index=run.events.length-1;$('#condition').value=run.condition;$('#mode').value=run.mode;render();note(`${run.mode==='scripted'?'Fixed-policy baseline':'LLM run'} · ${run.status} · ${run.evaluation?.rounds||0} rounds`);};
async function refreshRuns(){
  allRuns=await fetch('/api/runs').then(r=>r.json());
  const signature=JSON.stringify(allRuns.map(r=>r.id));if(signature!==lastRuns){lastRuns=signature;$('#run-select').innerHTML=allRuns.length?allRuns.map(r=>`<option value="${esc(r.id)}">${esc(conditions[r.condition]||r.condition)} · ${esc(r.mode)} · ${esc(r.status)} · ${r.started_at?.slice(11,19)||''}</option>`).join(''):'<option>No recordings yet</option>';if(run)$('#run-select').value=run.id;}
  const suite=await fetch('/api/suite').then(r=>r.json());
  const observations=suite?.runs?.length?suite.runs:allRuns.filter(r=>['passed','failed'].includes(r.status)&&r.mode==='scripted').map(r=>({condition:r.condition,...r.evaluation}));
  const rows=Object.keys(conditions).map(c=>{const group=observations.filter(r=>r.condition===c);return{c,n:group.length,passed:group.filter(r=>r.passed).length,rounds:group.length?group.reduce((a,r)=>a+r.rounds,0)/group.length:0};});
  const max=Math.max(1,...rows.map(r=>r.rounds));$('#comparison').innerHTML=rows.map(r=>`<div class="compare-row"><span>${conditions[r.c]}</span><div class="bar-track"><div class="bar" style="width:${r.rounds/max*100}%"></div></div><small>${r.n?`${r.rounds.toFixed(1)} rounds · ${r.passed}/${r.n}`:'Not run'}</small></div>`).join('');
}
async function poll(){try{
  const status=await fetch('/api/status').then(r=>r.json());running=status.running;$('#engine-status').textContent=status.engine?'Engine connected':'Engine starting / offline';$('#engine-status').className='status '+(status.engine?'online':'');$('#run').disabled=running||!status.engine;
  if(follow){const latest=await fetch('/api/live').then(r=>r.json());if(latest){run=latest;index=(run.events?.length||0)-1;render();$('#condition').value=run.condition;$('#mode').value=run.mode;note(run.error||`${run.mode==='scripted'?'Scripted baseline — fixed decisions, real engine execution':'LLM policy — model tool calls, real engine execution'} · ${run.status} · ${run.evaluation?.passed?'All 3 new artifacts verified':'Observe the resource handoffs below'}`,run.status==='error');}}
}catch{note('Dashboard connection unavailable. Restart npm run dev.',true);}}
render();await refreshRuns();await poll();setInterval(poll,1200);setInterval(refreshRuns,7000);
window.labReplay={load:async id=>{follow=false;run=await fetch(`/runs/${encodeURIComponent(id)}.json`).then(r=>r.json());index=run.events.length-1;render();},seek:go};
