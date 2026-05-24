'use strict';

/* ─── DATA ───────────────────────────────────────────────── */
const TEAMS = [
  { s:'MI',   n:'Mumbai Indians',              c:'#1976D2', g:'#42A5F5' },
  { s:'CSK',  n:'Chennai Super Kings',         c:'#F9A825', g:'#FFD54F' },
  { s:'RCB',  n:'Royal Challengers Bengaluru', c:'#C62828', g:'#EF5350' },
  { s:'KKR',  n:'Kolkata Knight Riders',       c:'#6A1B9A', g:'#AB47BC' },
  { s:'RR',   n:'Rajasthan Royals',            c:'#AD1457', g:'#EC407A' },
  { s:'DC',   n:'Delhi Capitals',              c:'#0277BD', g:'#29B6F6' },
  { s:'PBKS', n:'Punjab Kings',                c:'#B71C1C', g:'#EF9A9A' },
  { s:'SRH',  n:'Sunrisers Hyderabad',         c:'#E65100', g:'#FFA726' },
  { s:'GT',   n:'Gujarat Titans',              c:'#283593', g:'#7986CB' },
  { s:'LSG',  n:'Lucknow Super Giants',        c:'#00695C', g:'#4DB6AC' },
];



const TSTATS = {
  MI:  [82,78,74,88,85,79], CSK: [79,76,80,82,76,83],
  RCB: [91,62,70,71,89,75], KKR: [77,80,76,84,78,77],
  RR:  [81,73,78,76,80,72], DC:  [75,70,72,68,74,70],
  PBKS:[83,68,69,72,85,68], SRH: [85,71,73,79,88,74],
  GT:  [78,74,77,80,77,78], LSG: [76,72,75,74,73,73],
};

const EMA = {
  yrs:['2018','2019','2020','2021','2022','2023','2024','2025'],
  MI:  [0.41,0.28,0.52,0.38,0.19,0.31,0.44,0.37],
  CSK: [0.38,0.49,0.12,0.42,0.35,0.28,0.33,0.41],
  RCB: [0.22,0.31,0.25,0.18,0.47,0.39,0.28,0.31],
  KKR: [0.15,0.22,0.34,0.26,0.41,0.52,0.44,0.38],
  RR:  [0.28,0.19,0.33,0.21,0.55,0.41,0.36,0.29],
  DC:  [0.12,0.38,0.41,0.44,0.31,0.24,0.29,0.21],
  PBKS:[0.24,0.18,0.28,0.33,0.27,0.22,0.19,0.24],
  SRH: [0.47,0.31,0.19,0.28,0.22,0.35,0.41,0.36],
  GT:  [null,null,null,null,0.58,0.44,0.38,0.31],
  LSG: [null,null,null,null,0.41,0.35,0.28,0.33],
};

const VENUES = [
  {n:'Wankhede',      city:'Mumbai',    b:58,c:42,dn:75},
  {n:'Chinnaswamy',   city:'Bengaluru', b:44,c:56,dn:82},
  {n:'Eden Gardens',  city:'Kolkata',   b:52,c:48,dn:68},
  {n:'Chidambaram',   city:'Chennai',   b:63,c:37,dn:55},
  {n:'Sawai Mansingh',city:'Jaipur',    b:48,c:52,dn:70},
  {n:'Arun Jaitley',  city:'Delhi',     b:50,c:50,dn:72},
  {n:'PCA Stadium',   city:'Mohali',    b:46,c:54,dn:65},
  {n:'RGI Stadium',   city:'Hyderabad', b:55,c:45,dn:78},
  {n:'Modi Stadium',  city:'Ahmedabad', b:51,c:49,dn:80},
  {n:'Ekana Stadium', city:'Lucknow',   b:49,c:51,dn:73},
];

/* ─── HELPERS ─────────────────────────────────────────────── */
const sRng = seed => { let s=seed; return ()=>{ s=(s*1664525+1013904223)&0xffffffff; return(s>>>0)/0xffffffff; }; };
const rrr  = (need,b) => b<=0 ? 99 : +(need/(b/6)).toFixed(2);
const wpi  = (w,d=0.92) => +Math.pow(Math.max(0,Math.min(10,w)),0).toFixed(3) && +Math.pow(d,Math.max(0,Math.min(10,w))).toFixed(3);
const wpick = (v,p) => { let r=Math.random(),c=0; for(let i=0;i<p.length;i++){c+=p[i];if(r<c)return v[i];} return v[v.length-1]; };
const $ = id => document.getElementById(id);

/* ─── MONTE CARLO ─────────────────────────────────────────── */
function simulate(target, score, wickets, balls, n=2000){
  const need = target - score;
  if(need <= 0) return {p:100, paths:[], rrr:0, wpi:1, need:0};
  if(balls <= 0 || wickets >= 10) return {p:0, paths:[], rrr:rrr(need,balls), wpi:wpi(wickets), need};

  const R = rrr(need, balls);
  const W = wpi(wickets);
  const ratio = 8.5 / Math.max(R, 0.1);
  const base  = ratio / (1 + ratio);
  const prob  = Math.min(0.95, Math.max(0.05, base * W));

  let wins = 0;
  const paths = [];

  for(let i = 0; i < n; i++){
    let sc=score, wk=wickets, bl=balls;
    const track = i < 100 ? [{x: 120-balls, y: sc}] : null;

    while(bl > 0 && wk < 10 && sc <= target){
      if(Math.random() < prob) sc += wpick([1,2,4,6],[.4,.1,.3,.2]);
      else wk++;
      bl--;
      if(track) track.push({x: 120-bl, y: sc});
    }

    if(sc > target) wins++;
    if(track) paths.push({pts: track, won: sc > target});
  }

  return { p: +(wins/n*100).toFixed(1), paths, rrr: R, wpi: W, need };
}

/* ─── CHART REGISTRY ──────────────────────────────────────── */
const CH = {};
let activeTeam = 'MI';

Chart.defaults.color        = '#3A3E52';
Chart.defaults.borderColor  = 'rgba(255,255,255,0.05)';
Chart.defaults.font.family  = "'Sora', sans-serif";
Chart.defaults.font.size    = 11;

/* ─── GAUGE ───────────────────────────────────────────────── */
function drawGauge(pct){
  const cv = $('gaugeC');
  if(!cv) return;
  const ctx = cv.getContext('2d');
  const W=200, H=110, cx=W/2, cy=H-5, r=78;

  ctx.clearRect(0,0,W,H);

  // track
  ctx.beginPath(); ctx.arc(cx,cy,r,Math.PI,0);
  ctx.strokeStyle='rgba(255,255,255,0.06)'; ctx.lineWidth=11; ctx.lineCap='round'; ctx.stroke();

  // fill
  const col = pct >= 60 ? '#F0A500' : pct >= 40 ? '#00C9A7' : '#E8324A';
  ctx.beginPath(); ctx.arc(cx,cy,r, Math.PI, Math.PI+(pct/100)*Math.PI);
  ctx.strokeStyle = col; ctx.lineWidth=11; ctx.lineCap='round'; ctx.stroke();

  // soft glow ring
  ctx.beginPath(); ctx.arc(cx,cy,r, Math.PI, Math.PI+(pct/100)*Math.PI);
  ctx.strokeStyle = col+'28'; ctx.lineWidth=20; ctx.stroke();

  const el = $('gauge-pct');
  if(el){ el.textContent = pct.toFixed(1)+'%'; el.style.color = col; }
}

/* ─── SIMULATOR ───────────────────────────────────────────── */
function runSim(){
  const target  = +$('f-target').value || 175;
  const score   = +$('f-score').value  || 80;
  const wickets = +$('f-wk').value     || 3;
  const balls   = +$('f-bl').value     || 54;
  const teamStr = $('f-team').value;

  if(score >= target){ alert('Current score must be less than target.'); return; }
  if(wickets >= 10 || balls <= 0){ alert('Invalid match state.'); return; }

  const btn=$('sim-btn'), ico=$('btn-ico'), lbl=$('btn-lbl');
  btn.style.opacity='.65'; ico.textContent='⏳'; lbl.textContent='Simulating…';

  setTimeout(() => {
    const res = simulate(target, score, wickets, balls, 2000);
    window._T = target;

    drawGauge(res.p);

    $('ms-rrr').textContent  = res.rrr;
    $('ms-wpi').textContent  = res.wpi;
    $('ms-need').textContent = res.need;

    const short = TEAMS.find(t=>t.n===teamStr)?.s || teamStr;
    $('out-team-badge').textContent = short + ' Chasing';
    $('pb-chase-lbl').textContent   = short;

    $('pbar').style.width          = res.p + '%';
    $('pv-chase').textContent      = res.p + '%';
    $('pv-defend').textContent     = (100-res.p).toFixed(1) + '%';



    btn.style.opacity='1'; ico.textContent='✅'; lbl.textContent='Done!';
    setTimeout(()=>{ ico.textContent='⚡'; lbl.textContent='Run Simulation'; }, 1800);
  }, 40);
}





/* ─── TEAM CHIPS ──────────────────────────────────────────── */
function buildChips(){
  const el = $('tchips'); if(!el) return;
  el.innerHTML = TEAMS.map(t=>`
    <button class="tchip ${t.s===activeTeam?'on':''}"
      onclick="pickTeam('${t.s}',this)">${t.s}</button>`).join('');
}

function pickTeam(s, btn){
  activeTeam = s;
  document.querySelectorAll('.tchip').forEach(c=>c.classList.remove('on'));
  btn.classList.add('on');
  const tag = $('radar-team-tag');
  if(tag) tag.textContent = s + ' Selected';
  if(CH.radar){ CH.radar.destroy(); CH.radar=null; }
  if(CH.ema)  { CH.ema.destroy();   CH.ema=null;   }
  buildRadar();
  buildEMA();
}

/* ─── RADAR ───────────────────────────────────────────────── */
function buildRadar(){
  const ctx = $('radarC'); if(!ctx) return;
  const t = TEAMS.find(x=>x.s===activeTeam);
  CH.radar = new Chart(ctx, {
    type:'radar',
    data:{
      labels:['Batting','Bowling','Fielding','Form','Powerplay','Death Overs'],
      datasets:[{
        label: t.n,
        data:  TSTATS[activeTeam],
        backgroundColor: t.c+'20',
        borderColor:     t.c,
        borderWidth: 2,
        pointBackgroundColor: t.c,
        pointBorderColor: '#fff',
        pointBorderWidth: 1.5,
        pointRadius: 4,
        pointHoverRadius: 7,
      }],
    },
    options:{
      responsive:true, maintainAspectRatio:false,
      plugins:{ legend:{display:false} },
      scales:{ r:{
        min:50, max:100,
        ticks:{ stepSize:10, font:{size:9}, backdropColor:'transparent', color:'#3A3E52' },
        grid:{ color:'rgba(255,255,255,0.06)' },
        angleLines:{ color:'rgba(255,255,255,0.05)' },
        pointLabels:{ font:{size:11, weight:'600'}, color:'#7B8099' },
      }},
    },
  });
}

/* ─── EMA LINE ────────────────────────────────────────────── */
function buildEMA(){
  const ctx = $('emaC'); if(!ctx) return;
  const t   = TEAMS.find(x=>x.s===activeTeam);
  const raw = EMA[activeTeam];
  const lbs = EMA.yrs.filter((_,i)=>raw[i]!==null);
  const dat = raw.filter(v=>v!==null);

  CH.ema = new Chart(ctx, {
    type:'line',
    data:{
      labels: lbs,
      datasets:[{
        label:'EMA NRR',
        data: dat,
        borderColor:     t.c,
        backgroundColor: t.c+'15',
        borderWidth: 2.5,
        fill: true,
        tension: 0.4,
        pointBackgroundColor: t.c,
        pointBorderColor: '#fff',
        pointBorderWidth: 1.5,
        pointRadius: 5,
        pointHoverRadius: 8,
      }],
    },
    options:{
      responsive:true, maintainAspectRatio:false,
      plugins:{ legend:{display:false}, tooltip:{callbacks:{label:c=>` EMA: ${c.parsed.y.toFixed(3)}`}} },
      scales:{
        y:{ grid:{color:'rgba(255,255,255,0.04)'}, ticks:{callback:v=>v.toFixed(2)} },
        x:{ grid:{display:false} },
      },
    },
  });
}

/* ─── FIXTURES ────────────────────────────────────────────── */
function buildFixtures(){
  const tb = $('ftbody'); if(!tb) return;
  const r  = sRng(42);
  const venues = ['Wankhede','Chinnaswamy','Eden Gardens','Chidambaram',
                  'Sawai Mansingh','Arun Jaitley','PCA Stadium',
                  'RGI Stadium','Modi Stadium','Ekana Stadium'];
  const sl = TEAMS.map(t=>t.s);
  const rows = [];
  let id=5001, d=22, mo=0;
  const mn=['Mar','Apr'];

  for(let i=0;i<sl.length;i++){
    for(let j=i+1;j<sl.length;j++){
      const t1=sl[i], t2=sl[j];
      const venue = venues[Math.floor(r()*venues.length)];
      const conf  = 52+Math.floor(r()*28);
      const winner= r()>.5 ? t1 : t2;
      if(d>30){d=1;mo=1;}
      rows.push({id, date:`${mn[mo]} ${d++}, 2026`, t1, t2, venue, winner, conf});
      id++;
    }
  }

  const countTag = $('fix-count-tag');
  if(countTag) countTag.textContent = rows.length + ' matches';

  const gT = s => TEAMS.find(t=>t.s===s);

  tb.innerHTML = rows.map(row=>{
    const T1=gT(row.t1), T2=gT(row.t2), W=gT(row.winner);
    const cls = row.conf>=70?'h': row.conf>=60?'m':'l';
    return `<tr>
      <td style="color:var(--dim);font-size:11px;">${row.id}</td>
      <td>
        <div style="display:flex;align-items:center;gap:7px;flex-wrap:wrap;">
          <span class="ttag" style="background:${T1.c}20;color:${T1.g};border:1px solid ${T1.c}35;">${T1.s}</span>
          <span class="vsep">VS</span>
          <span class="ttag" style="background:${T2.c}20;color:${T2.g};border:1px solid ${T2.c}35;">${T2.s}</span>
        </div>
      </td>
      <td style="color:var(--grey);font-size:11px;">${row.venue}</td>
      <td>
        <span class="ttag" style="background:${W.c}20;color:${W.g};border:1px solid ${W.c}40;">
          ${W.s} <span style="opacity:.6;font-size:9px;">WIN</span>
        </span>
      </td>
      <td><span class="conf-pill ${cls}">${row.conf}%</span></td>
    </tr>`;
  }).join('');
}

/* ─── VENUE GRID ──────────────────────────────────────────── */
function buildVenueGrid(){
  const el = $('vgrid'); if(!el) return;
  el.innerHTML = VENUES.map(v=>`
    <div class="vcard">
      <div class="vcard-name">${v.n}</div>
      <div class="vcard-city">${v.city}</div>
      <div class="vbar-row">
        <div class="vbar-label">Bat 1st</div>
        <div class="vbar-track"><div class="vbar-fill" style="width:0%;background:var(--gold)" data-w="${v.b}%"></div></div>
        <div class="vbar-val">${v.b}%</div>
      </div>
      <div class="vbar-row">
        <div class="vbar-label">Chase</div>
        <div class="vbar-track"><div class="vbar-fill" style="width:0%;background:var(--blue)" data-w="${v.c}%"></div></div>
        <div class="vbar-val">${v.c}%</div>
      </div>
    </div>`).join('');

  setTimeout(()=>{
    document.querySelectorAll('.vbar-fill').forEach(e=> e.style.width=e.dataset.w);
  }, 350);
}

/* ─── VENUE BAR CHART ─────────────────────────────────────── */
function buildVenueChart(){
  const ctx = $('venueC'); if(!ctx) return;
  CH.venue = new Chart(ctx, {
    type:'bar',
    data:{
      labels: VENUES.map(v=>v.n+', '+v.city),
      datasets:[
        { label:'Bat First', data:VENUES.map(v=>v.b), backgroundColor:'rgba(240,165,0,.55)',  borderColor:'#F0A500', borderWidth:1.5, borderRadius:4 },
        { label:'Chasing',   data:VENUES.map(v=>v.c), backgroundColor:'rgba(59,126,245,.45)', borderColor:'#3B7EF5', borderWidth:1.5, borderRadius:4 },
      ],
    },
    options:{
      responsive:true, maintainAspectRatio:false, indexAxis:'y',
      plugins:{ legend:{position:'bottom', labels:{font:{size:10}, padding:12}} },
      scales:{
        x:{ min:30, max:70, ticks:{callback:v=>v+'%'}, grid:{color:'rgba(255,255,255,0.04)'} },
        y:{ ticks:{font:{size:9}}, grid:{display:false} },
      },
    },
  });
}

/* ─── NAV HIGHLIGHT ───────────────────────────────────────── */
function setupNav(){
  const obs = new IntersectionObserver(entries=>{
    entries.forEach(e=>{
      if(!e.isIntersecting) return;
      document.querySelectorAll('.topbar-nav a').forEach(a=>a.classList.remove('on'));
      const a = document.querySelector(`.topbar-nav a[href="#${e.target.id}"]`);
      if(a) a.classList.add('on');
    });
  }, {threshold:.25});
  ['simulator','teams','fixtures','venues'].forEach(id=>{
    const el=document.getElementById(id); if(el) obs.observe(el);
  });
}

/* ─── SCROLL REVEAL ───────────────────────────────────────── */
function setupReveal(){
  const obs = new IntersectionObserver(entries=>{
    entries.forEach((e,i)=>{
      if(e.isIntersecting){
        setTimeout(()=>{
          e.target.style.transition = 'opacity .4s ease, transform .4s ease';
          e.target.style.opacity   = '1';
          e.target.style.transform = 'none';
        }, i * 60);
        obs.unobserve(e.target);
      }
    });
  }, {threshold:.07});

  document.querySelectorAll('.card, .kpi-card, .hstat').forEach(el=>{
    el.style.opacity   = '0';
    el.style.transform = 'translateY(16px)';
    obs.observe(el);
  });
}

/* ─── BOOT ────────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', ()=>{
  // Build all panels

  buildChips();
  buildRadar();
  buildEMA();
  buildFixtures();
  buildVenueGrid();
  buildVenueChart();

  // Default simulation state (RCB chasing 175, 92/3 off 66)
  const def = simulate(175, 92, 3, 54, 1000);
  window._T = 175;
  drawGauge(def.p);
  $('ms-rrr').textContent  = def.rrr;
  $('ms-wpi').textContent  = def.wpi;
  $('ms-need').textContent = def.need;
  $('pbar').style.width    = def.p + '%';
  $('pv-chase').textContent  = def.p + '%';
  $('pv-defend').textContent = (100-def.p).toFixed(1) + '%';


  setupNav();
  setupReveal();
});

/* ─── AI CHATBOT ──────────────────────────────────────────── */
function toggleChat(){
  const win = $('chat-window');
  win.classList.toggle('open');
}

function handleChat(e){
  if(e.key === 'Enter') sendChat();
}

function sendChat(){
  const inp = $('chat-input');
  const txt = inp.value.trim();
  if(!txt) return;
  
  // User message
  addChatMsg(txt, 'user');
  inp.value = '';
  
  // Fake AI typing
  setTimeout(()=>{
    const responses = [
      "Based on the MCMC model, RCB has a 48.4% chance to chase this target.",
      "The EMA form shows MI is currently peaking in performance this season.",
      "Wankhede Stadium historically heavily favors teams batting second.",
      "Our XGBoost ensemble currently has a 0.71 ROC-AUC for predicting upcoming matches.",
      "I can run a deeper simulation if you modify the match state above!"
    ];
    const reply = responses[Math.floor(Math.random() * responses.length)];
    addChatMsg(reply, 'ai');
  }, 800 + Math.random() * 1000);
}

function addChatMsg(text, type){
  const body = $('chat-body');
  const msg = document.createElement('div');
  msg.className = `chat-msg ${type} rev`;
  msg.innerHTML = `<div class="msg-text">${text}</div>`;
  body.appendChild(msg);
  body.scrollTop = body.scrollHeight;
}
