"""Native, read-only Pixel Office for Item Space AI's verified task pipeline.

The characters show persisted AIOS tasks and their pipeline roles. They are not
independent Codex sessions or a second scheduling engine. Nothing runs Codex.
Artwork is original Canvas primitives (not copied sprites or third-party packs).
"""
from __future__ import annotations

from html import escape
from factory.intake import list_ideas
from factory.live_studio import worker_state

OFFICE_CSS = r"""
.office-intro{padding:22px 0 20px}
.office-intro h1{margin:3px 0 7px;font-size:clamp(30px,4vw,48px)}
.office-intro p{font-size:13px;color:#aebdd2;max-width:920px}
.office-layout{display:grid;grid-template-columns:minmax(0,1.65fr) minmax(285px,.68fr);gap:14px}
.office-panel{border:1px solid rgba(104,171,198,.28);border-radius:18px;background:#111e32;padding:19px;min-width:0}
.office-scene{position:relative;border-radius:11px;background:#0b1726;overflow:hidden;border:1px solid rgba(119,175,198,.25)}
#office-canvas{display:block;width:100%;height:auto;image-rendering:pixelated;cursor:default;touch-action:manipulation}
.office-overlay{position:absolute;right:14px;top:14px;background:rgba(6,14,26,.92);border:1px solid #38556a;border-radius:8px;padding:6px 10px;font-size:10px;font-weight:850;color:#a8e5e0}
.office-toolbar{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px;margin:0 0 13px}
.office-toolbar h2{margin:0;font-size:15px}
.office-key{font-size:11px;color:#a6bdd2}
.office-status{display:flex;gap:10px;flex-wrap:wrap;margin:12px 0 0}
.office-pill{border:1px solid #345366;background:#172d40;border-radius:8px;padding:5px 10px;color:#c1dae9;font-size:11px}
.office-pill strong{color:#a3f1dc}
.office-hint{color:#92a9c2;font-size:11px;margin:12px 0 0}
.office-list{display:grid;gap:10px;max-height:550px;overflow:auto;padding-inline-end:5px}
.office-member{display:block;background:#17283d;border:1px solid #2c4b62;border-radius:12px;padding:12px;text-decoration:none;color:#e4f4fd}
.office-member:hover{background:#1c3950;border-color:#6dbbbb;color:#fff}
.office-member strong{display:block;font-size:13px;overflow-wrap:anywhere}
.office-member .member-meta{display:flex;align-items:center;gap:7px;margin-top:6px;font-size:10px;color:#abc4d8;flex-wrap:wrap}
.office-member .member-state{font-size:10px;border:1px solid #446074;border-radius:7px;padding:2px 6px;color:#a6e0d5}
.office-member[data-status="WAITING_APPROVAL"]{border-color:#ccab75}
.office-member[data-status="WAITING_APPROVAL"] .member-state{color:#ffdea4}
.office-member[data-status="NEEDS_WORK"] .member-state,
.office-member[data-status="BLOCKED"] .member-state,
.office-member[data-status="FAILED"] .member-state{color:#ffacb5}
.office-empty{padding:24px;border:1px dashed #37516c;border-radius:12px;color:#aac1d5;font-size:12px}
.office-summary{display:flex;align-items:center;justify-content:space-between;gap:10px;margin-top:15px;padding-top:12px;border-top:1px solid #294057;color:#a8bbce;font-size:11px}
.office-summary a{color:#a4ebeb}
.office-context{padding:12px;margin:13px 0;border-radius:10px;border:1px solid #355773;background:#162a3e;color:#bbd9e9;font-size:11px;min-height:38px}
.office-legend{display:flex;gap:12px;flex-wrap:wrap;margin:13px 0 0;color:#9fb7c7;font-size:10px}
.office-legend span{display:inline-flex;align-items:center;gap:5px}
.office-legend i{display:inline-block;width:9px;height:9px;border-radius:3px;background:#78c8ad}
.office-legend .wait{background:#f5bf80}.office-legend .block{background:#d98c9e}.office-legend .idle{background:#67859c}
@media(max-width:1020px){.office-layout{grid-template-columns:1fr}.office-list{max-height:400px}}
@media(max-width:620px){.office-panel{padding:12px}.office-overlay{font-size:8px;right:6px;top:6px}.office-intro h1{font-size:30px}}
"""

OFFICE_JS = r"""'use strict';
(() => {
  const canvas = document.getElementById('office-canvas');
  if (!canvas) return;
  const parentPanel = canvas.closest('details');
  const isVisible = () => !document.hidden && (!parentPanel || parentPanel.open);
  const ctx = canvas.getContext('2d');
  if (!ctx) return;
  const W = 1100, H = 610;
  const stations = [
    {stage:'discovery',name:'DISCOVERY',x:115,y:218},
    {stage:'requirements',name:'PRODUCT',x:345,y:218},
    {stage:'architecture',name:'ARCHITECT',x:575,y:218},
    {stage:'backlog',name:'PLANNING',x:805,y:218},
    {stage:'implementation',name:'ENGINEERING',x:115,y:455},
    {stage:'qa',name:'QUALITY LAB',x:345,y:455},
    {stage:'security',name:'SECURITY',x:575,y:455},
    {stage:'release_plan',name:'RELEASE',x:805,y:455}
  ];
  const palette = ['#6fe3da','#b1a4f3','#f3bd8c','#7cafef','#b2d9aa','#dca6d2','#b1b5ef','#f2d29e'];
  const statusColors = {
    RUNNING:'#7ce0bd', PENDING:'#92b6cc', INTERRUPTED:'#f1bf80',
    WAITING_APPROVAL:'#f5bc81', NEEDS_WORK:'#f4a4aa', BLOCKED:'#f4a4aa',
    FAILED:'#f4a4aa', DONE:'#80c5b0', ACCEPTED:'#80c5b0'
  };
  const reduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  let tasks = [], dots = [], worker = 'UNKNOWN', fetchError = false, frame = 0, hovered = null;
  const byId = (id) => document.getElementById(id);
  const rect = (x,y,w,h,color) => {ctx.fillStyle=color;ctx.fillRect(Math.round(x),Math.round(y),w,h);};
  const text = (t,x,y,size,color='#dceff4',align='center') => {
    ctx.fillStyle=color; ctx.font='bold '+size+'px "Segoe UI",Arial,sans-serif';
    ctx.textAlign=align;ctx.fillText(String(t),x,y);
  };
  function plant(x,y) {
    rect(x-10,y,20,19,'#7d889d');rect(x-7,y+3,14,3,'#9eb0b8');
    rect(x-2,y-25,4,29,'#65b899');rect(x-14,y-22,10,7,'#55a68c');
    rect(x+4,y-29,11,8,'#72cbb0');rect(x-9,y-34,7,13,'#509b84');
  }
  function char(x,y,index,active,atMeeting) {
    const step = active && !reduced ? Math.sin(frame/7+index*2)*2:0;
    const clothes=palette[index % palette.length];
    const hair=['#463c48','#70524d','#b49164','#2c4658'][index % 4];
    rect(x-12,y-16,24,8,hair);
    rect(x-14,y-7,28,15,'#e6b38e');rect(x-14,y-5,5,8,hair);
    rect(x-6,y,3,3,'#263445');rect(x+5,y,3,3,'#263445');
    rect(x-17,y+10,34,22,clothes);
    rect(x-23,y+12+step,8,16,'#e3b493');rect(x+15,y+12-step,8,16,'#e3b493');
    rect(x-13,y+32,11,9,'#3c4c70');rect(x+3,y+32,11,9,'#3c4c70');
    if(!atMeeting){rect(x-18,y+39,36,6,'#15233a');}
  }
  function desk(s,i) {
    rect(s.x-91,s.y-23,182,83,'#233c52');
    rect(s.x-88,s.y-20,176,60,'#9f795f');
    rect(s.x-84,s.y-16,168,48,'#b98969');
    rect(s.x-37,s.y-29,74,49,'#202b45');
    rect(s.x-33,s.y-25,66,39,'#234f62');
    rect(s.x-27,s.y-17,51,4,'#6abbb4');
    rect(s.x-27,s.y-7,37,4,'#a1b7de');
    rect(s.x-27,s.y+3,43,3,'#5583b1');
    rect(s.x-4,s.y+20,8,10,'#677b99');
    rect(s.x-52,s.y+30,107,7,'#d8b19c');
    rect(s.x+61,s.y+18,9,12,'#536e8e');rect(s.x+63,s.y+17,5,3,'#e2cfa7');
    rect(s.x-55,s.y+45,109,5,'#6b5360');
    text(s.name,s.x,s.y-45,13,'#b3d5df');
    text((i+1).toString().padStart(2,'0'),s.x+75,s.y-45,10,'#658aa0');
  }
  function room() {
    rect(0,0,W,H,'#0b1929');
    for (let x=0;x<W;x+=30)for(let y=58;y<H;y+=30){
      rect(x+1,y+1,29,29, ((x+y)/30)%2===0?'#1b2a3d':'#1c2e43');
    }
    rect(0,0,W,66,'#22394c');rect(0,60,W,6,'#42677a');
    text('ITEM SPACE AI  /  PIXEL OFFICE',22,39,21,'#d7eef4','left');
    rect(936,13,144,39,'#183b49');rect(940,17,136,31,'#24596b');
    text('AIOS V3.2',1008,37,13,'#a5e6df');
    for(let i=0;i<stations.length;i++)desk(stations[i],i);
    rect(935,81,150,192,'#163142');
    rect(942,89,136,177,'#1e3b4e');
    rect(960,108,94,49,'#29475d');
    text('REVIEW',1007,128,11,'#b4e4eb');
    text('MEETING',1007,144,11,'#b4e4eb');
    rect(973,186,69,30,'#a47566');rect(986,177,44,51,'#bd9584');
    rect(976,221,15,22,'#4a6980');rect(1023,221,15,22,'#4a6980');
    rect(930,277,162,6,'#49627c');
    plant(32,118);plant(1082,580);plant(1028,360);plant(38,573);
    rect(928,309,140,28,'#2b4157');text('PENDING / BLOCKED',998,327,10,'#9fc4d0');
    rect(943,356,115,22,'#4a506d');rect(934,377,130,33,'#71647c');
    rect(952,412,8,15,'#59637a');rect(1040,412,8,15,'#59637a');
    rect(24,587,870,2,'#3c6275');
    text('Agents represent real task stages. Only RUNNING tasks animate as active.',40,601,12,'#9bbbd1','left');
  }
  function drawAgent(t,index,sx,sy,isMeeting) {
    const active=t.status==='RUNNING';
    const blink=active && !reduced && (frame%28<14);
    const color=statusColors[t.status]||'#92b6cc';
    const iconX = isMeeting?sx:sx, iconY=isMeeting?sy:sy+20;
    rect(iconX-26,iconY+8,52,43,'#293e58');
    char(iconX,iconY,index,active,isMeeting);
    rect(iconX-26,iconY-39,52,7,color);
    if(blink) rect(iconX+24,iconY-24,6,6,'#a0f8dc');
    dots.push({x:iconX,y:iconY,w:56,h:100,id:t.id,title:t.title,status:t.status});
  }
  function draw() {
    ++frame;dots=[];
    room();
    let meetings=0; const capacity=3;
    for(let i=0;i<tasks.length&&i<20;i++){
      const t=tasks[i];
      if(t.status==='DONE'||t.status==='ACCEPTED')continue;
      if(t.status==='WAITING_APPROVAL'&&meetings<2){
        drawAgent(t,i,969+65*meetings,173,true);meetings++;continue;
      }
      const station=stations.find(s=>s.stage===t.stage)||stations[0];
      const local=tasks.slice(0,i).filter(z=>z.stage===t.stage&&z.status!=='WAITING_APPROVAL').length;
      if(local>=capacity)continue;
      drawAgent(t,i,station.x+(local-0)*34-20,station.y+77+(local%2)*4,false);
    }
    if(meetings)text(meetings+' awaiting approval',1005,251,11,'#ffcf9b');
    if(fetchError) {rect(350,73,395,30,'#4d2d3d');text('Live link unavailable — retrying',545,93,13,'#ffe0e0');}
    if(!tasks.length&&!fetchError)text('No registered tasks. Create a mission to populate the office.',W/2,330,17,'#bbd3e7');
    if(hovered) {
      const t=tasks.find(x=>x.id===hovered);
      if(t){rect(17,80,590,48,'#102235');rect(22,85,580,38,'#264a60');
        text((t.title||'Task')+'  •  '+t.status,32,108,14,'#f1f6ff','left');}
    }
  }
  function hit(e) {
    const bounds=canvas.getBoundingClientRect();
    const x=(e.clientX-bounds.left)*W/bounds.width;
    const y=(e.clientY-bounds.top)*H/bounds.height;
    return dots.find(d=>Math.abs(x-d.x)<=d.w/2&&y>=d.y-45&&y<=d.y+d.h-45);
  }
  canvas.addEventListener('pointermove',(e)=>{const item=hit(e);hovered=item?item.id:null;canvas.style.cursor=item?'pointer':'default';});
  canvas.addEventListener('pointerleave',()=>{hovered=null;});
  canvas.addEventListener('click',(e)=>{const item=hit(e);if(item&&/^[0-9a-f]{12}$/.test(item.id))window.location.assign('/ideas/'+item.id);});
  function member(t) {
    const a=document.createElement('a');
    a.className='office-member';
    a.href='/ideas/'+t.id;
    a.dataset.status=t.status;
    const b=document.createElement('strong');b.textContent=t.title;a.appendChild(b);
    const meta=document.createElement('div');meta.className='member-meta';
    const stage=document.createElement('span');stage.textContent=t.stage;meta.appendChild(stage);
    const state=document.createElement('span');state.className='member-state';state.textContent=t.status;meta.appendChild(state);
    a.appendChild(meta);
    return a;
  }
  function updateUi() {
    byId('office-count').textContent=String(tasks.length);
    byId('office-running').textContent=String(tasks.filter(t=>t.status==='RUNNING').length);
    byId('office-approvals').textContent=String(tasks.filter(t=>t.status==='WAITING_APPROVAL').length);
    byId('office-worker').textContent=worker;
    byId('office-connection').textContent=fetchError?'غير متصل · إعادة محاولة':'متصل · تحديث كل 4 ثوانٍ';
    const list=byId('office-task-list');list.replaceChildren();
    if(!tasks.length){const e=document.createElement('div');e.className='office-empty';
      e.textContent='لا توجد مهام حالياً، أو لم تتوفر بياناتها.';list.appendChild(e);}
    else tasks.forEach(t=>list.appendChild(member(t)));
  }
  let busy=false;
  async function sync(){
    if(busy||!isVisible())return;
    busy=true;
    try {
      const r=await fetch('/office/state',{cache:'no-store'});
      if(!r.ok)throw Error('offline');
      const d=await r.json();
      if(!Array.isArray(d.tasks))throw Error('bad data');
      tasks=d.tasks.filter(t=>/^[0-9a-f]{12}$/.test(t.id));
      worker=typeof d.worker==='string'?d.worker:'UNKNOWN';
      fetchError=false;
    }catch(_){fetchError=true;}finally{busy=false;updateUi();draw();}
  }
  function loop(){if(isVisible()){draw();}if(!reduced)setTimeout(()=>requestAnimationFrame(loop),1000/12);}
  sync(); if(!reduced)requestAnimationFrame(loop);
  setInterval(sync,4000);
  if (parentPanel) parentPanel.addEventListener('toggle',()=>{
    if (parentPanel.open) { sync(); draw(); }
  });
  document.addEventListener('visibilitychange',()=>{if(isVisible()){sync();draw();}});
})();
"""


def office_snapshot() -> dict:
    """Read-only and bounded; no raw prompts, project paths, tokens or logs."""
    records = list_ideas(limit=50)
    return {
        "tasks": [
            {"id": r["id"], "title": r["title"][:100], "status": r["status"][:40],
             "stage": r["stage"][:40], "updated_at": r["updated_at"]}
            for r in records
        ],
        "worker": worker_state(),
    }


def office_html() -> str:
    return (
        '<section class="office-intro"><p class="eyebrow">OPERATIONS CAMPUS / PIXEL OFFICE</p>'
        '<h1>شوف فريق الـAI <em>وهو يشتغل.</em></h1>'
        '<p>المكتب يحوّل حالات مهام Item Space AI الفعلية إلى شخصيات صغيرة على أجهزة الكمبيوتر. '
        'اضغط على شخصية لفتح مهمة، واستعرض الموافقات من مركز القرارات.</p></section>'
        '<div class="office-layout"><section class="office-panel">'
        '<div class="office-toolbar"><h2>◈ المكتب الافتراضي</h2>'
        '<span class="office-key" id="office-connection">الاتصال جارٍ...</span></div>'
        '<div class="office-scene"><canvas id="office-canvas" width="1100" height="610" '
        'role="img" aria-label="مكتب Pixel Art متحرك، فيه أقسام البرمجة والتخطيط والجودة والاجتماعات؛ '
        'الأنشطة مأخوذة من حالة المهام الفعلية"></canvas>'
        '<div class="office-overlay">TASK-DRIVEN OFFICE · LOCAL ONLY</div></div>'
        '<div class="office-status"><span class="office-pill">المهام: <strong id="office-count">—</strong></span>'
        '<span class="office-pill">جارية: <strong id="office-running">—</strong></span>'
        '<span class="office-pill">تحتاج موافقة: <strong id="office-approvals">—</strong></span>'
        '<span class="office-pill">Worker: <strong id="office-worker">—</strong></span></div>'
        '<div class="office-legend"><span><i></i>مهمة تعمل الآن</span>'
        '<span><i class="wait"></i>بانتظار موافقتك</span>'
        '<span><i class="block"></i>بحاجة إصلاح</span>'
        '<span><i class="idle"></i>بالانتظار</span></div>'
        '<p class="office-hint">الشخصية تمثّل مهمة في مرحلة محددة، وليست عملية AI مستقلة. '
        'الحركة لا تعني أن وكلاء متعددين يعملون على نفس المشروع. '
        'لا تُنشأ مهام أو تُعدّل ملفات أو تُرسل موافقات من هذه الصفحة.</p>'
        '</section><aside class="office-panel">'
        '<div class="office-toolbar"><h2>مهام الفريق</h2>'
        '<a class="studio-open" href="/#approvals">مركز الموافقات</a></div>'
        '<div class="office-task-list" id="office-task-list" aria-live="polite"></div>'
        '<div class="office-summary"><span>مراقبة فقط، بدون تنفيذ أو موافقة</span>'
        '<a href="/#missions">كل المشاريع</a></div></aside></div>'
        '<script src="/office.js" defer></script>'
    )
