"""Presentation-only Item Space AI Operations Campus.

Contains no worker, database, network, or approval side effects. All status
labels are projections of persisted task records rather than invented agent
activity. Deliberately separate from the automation engine.
"""
from __future__ import annotations

from html import escape
from pathlib import Path


CAMPUS_CSS = r"""
:root{
  --bg:#080e1b;--panel:#111d31;--edge:rgba(140,173,213,.18);
  --cyan:#6fe8eb;--violet:#adacff;--light:#f0f5fb;--soft:#9dacc4;
  --green:#70d9b6;--gold:#ffc788;
}
body{background:radial-gradient(ellipse at 74% 8%,rgba(55,97,137,.24),transparent 39%),radial-gradient(ellipse at 4% 78%,rgba(70,65,124,.19),transparent 40%),#080e1b}
body:before{opacity:.11;mask-image:linear-gradient(180deg,black,transparent 95%)}
body:after{display:none}
.shell{max-width:1450px;padding-inline:34px}
.topbar{min-height:86px;position:relative}
.brand-text strong{letter-spacing:1.3px}
.brand-text small{letter-spacing:2px}
.topnav{display:flex;align-items:center;gap:6px;margin-inline:auto}
.topnav a{font-size:12px;color:#adbcd3;padding:10px 14px;border:1px solid transparent;border-radius:10px;font-weight:700}
.topnav a:hover,.topnav a:focus-visible{background:rgba(112,225,241,.1);border-color:rgba(112,225,241,.22);color:white}
.topnav .nav-approval{border-color:rgba(255,199,136,.29);color:#ffe1b5;background:rgba(156,100,46,.1)}
.pill{letter-spacing:0;background:rgba(32,50,75,.7)}
.hero.campus-hero{min-height:405px;padding:38px 0 22px;grid-template-columns:minmax(0,.86fr) minmax(380px,1.14fr);gap:33px}
.campus-copy{padding-block:20px}
.campus-hero h1{font-size:clamp(34px,4.3vw,59px);line-height:1.28;max-width:620px;letter-spacing:-1.7px}
.campus-hero h1 em{background:linear-gradient(100deg,#89e9e2,#bbb4ff);-webkit-background-clip:text;background-clip:text}
.campus-hero .lead{font-size:14px;line-height:2;max-width:590px}
.campus-kicker{display:inline-flex;align-items:center;gap:8px;color:#99dadc;border:1px solid #376179;border-radius:99px;padding:7px 13px;font-size:11px;font-weight:700;margin-bottom:20px}
.campus-kicker:before{content:"";width:7px;height:7px;background:#7deec7;border-radius:50%;box-shadow:0 0 0 4px rgba(125,238,199,.1)}
.hero-links{display:flex;gap:11px;flex-wrap:wrap;margin-top:25px}
.hero-links a{display:inline-flex;align-items:center;justify-content:center;padding:11px 18px;border-radius:11px;font-weight:750;font-size:13px;background:#182b43;border:1px solid #33526d;color:#e1faff}
.hero-links a.primary-link{background:linear-gradient(108deg,#68e6e5,#9ba9ff);color:#081427;border:0}
.campus-visual{min-width:0;position:relative;overflow:hidden;min-height:325px;background:linear-gradient(152deg,rgba(23,43,70,.98),rgba(12,22,40,.98));border:1px solid rgba(115,177,208,.27);border-radius:27px;box-shadow:0 24px 70px rgba(2,8,18,.31),inset 0 1px rgba(198,242,250,.1)}
.campus-visual svg{display:block;width:100%;height:100%;min-height:325px}
.scene-caption{position:absolute;top:15px;right:18px;color:#a5bdd1;font-size:10px;letter-spacing:1.4px;font-weight:800;z-index:1}
.scene-disclaimer{position:absolute;bottom:13px;left:16px;color:#8bacc2;font-size:10px;z-index:1}
.agent-monitor{animation:monitor-glow 3s ease-in-out infinite alternate;transform-origin:center}
.scene-activity{animation:scene-drift 4s ease-in-out infinite alternate}
.scene-activity.two{animation-delay:-2s}
@keyframes monitor-glow{to{opacity:.58}}
@keyframes scene-drift{to{transform:translateY(-5px)}}
.campus-visual .meeting-glow{animation:scene-drift 3s ease-in-out infinite alternate}
.stats{grid-template-columns:repeat(3,minmax(0,1fr));margin:20px 0 27px;gap:12px}
.stat{background:#121f32;border-color:rgba(152,185,212,.16);border-radius:15px;box-shadow:none}
.stat .num{text-align:right;color:#eff8fd}
.stat .desc{letter-spacing:1px}
.approval-hub{scroll-margin-top:20px;margin:4px 0 25px;padding:24px;border:1px solid rgba(251,196,135,.4);border-radius:19px;background:linear-gradient(120deg,rgba(71,48,43,.5),rgba(31,37,56,.76) 52%,rgba(15,29,49,.98));box-shadow:0 12px 50px rgba(0,0,0,.13)}
.approval-header{display:flex;justify-content:space-between;align-items:center;gap:18px;margin-bottom:14px}
.approval-title{margin:0;font-size:19px;color:#fff2e0}
.approval-sub{color:#c6bac0;font-size:12px;margin:4px 0 0}
.approval-count{display:flex;flex-direction:column;align-items:center;justify-content:center;min-width:72px;padding:10px 18px;border-radius:15px;background:rgba(255,197,136,.1);border:1px solid rgba(255,197,136,.32);color:#ffd7a7;font-size:27px;font-weight:850;line-height:1.2}
.approval-count small{font-size:10px;font-weight:600;white-space:nowrap}
.approval-list{display:grid;gap:10px}
.approval-entry{display:flex;align-items:center;justify-content:space-between;gap:14px;padding:14px 17px;background:rgba(12,22,37,.7);border:1px solid rgba(238,199,151,.24);border-radius:12px}
.approval-entry strong{display:block;font-size:14px;color:#fff;overflow-wrap:anywhere}
.approval-entry p{font-size:12px;color:#c3b9b9;margin:5px 0 0}
.review-link{display:inline-flex;align-items:center;justify-content:center;flex:none;border-radius:10px;padding:10px 15px;background:#ffd09b;color:#251b19;font-size:12px;font-weight:900}
.review-link:hover{color:#16121d;background:#ffe3bc}
.approval-clear{display:flex;align-items:center;gap:10px;background:rgba(16,30,44,.6);border-radius:12px;padding:15px;color:#c8d4e2;font-size:13px}
.approval-clear strong{color:#9de5d0;font-size:19px}
.grid .panel{background:linear-gradient(152deg,#142238,#0d1829);border-radius:18px}
.panel{box-shadow:0 10px 38px rgba(0,0,0,.13)}
.section-band{margin:27px 0 16px;display:flex;align-items:end;justify-content:space-between;gap:10px}
.section-band h2{margin:0;font-size:20px}
.section-band p{margin:5px 0 0;color:var(--soft);font-size:12px}
.departments{scroll-margin-top:30px;margin-bottom:30px}
.dept-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}
.dept-card{min-height:168px;padding:17px;border-radius:16px;background:linear-gradient(150deg,#182a40,#101c30);border:1px solid rgba(129,177,217,.19);position:relative;overflow:hidden}
.dept-card:after{content:"";position:absolute;width:100px;height:100px;left:-40px;bottom:-44px;border-radius:50%;border:1px solid rgba(107,198,217,.1);box-shadow:0 0 0 26px rgba(94,187,210,.025)}
.dept-icon{width:40px;height:40px;display:grid;place-items:center;border:1px solid rgba(123,190,212,.29);border-radius:12px;font-size:20px;background:#18374a;margin-bottom:17px}
.dept-card h3{font-size:14px;margin:0 0 5px}
.dept-card p{font-size:11px;color:#a5b4ca;margin:0}
.dept-card .dept-value{margin-top:11px;font-size:11px;color:#a5e3db;font-weight:750}
.dept-card .dept-value strong{font-size:15px}
.mission-grid{margin-top:18px}
#mission-intake,#missions{scroll-margin-top:25px}
.task{background:#101f33;border:1px solid rgba(133,184,210,.18)}
.task-title{color:#e1f6ff}
.action{background:linear-gradient(95deg,#69e5e0,#a0b4ff);box-shadow:none}
.approval-detail{scroll-margin-top:20px;margin:22px 0;padding:24px;border-radius:18px;border:1px solid rgba(250,205,150,.42);background:linear-gradient(110deg,rgba(66,51,51,.8),#16263c)}
.approval-detail h2{font-size:21px;color:#ffe5c3;margin:0 0 8px}
.approval-detail p{color:#d5c8bf;font-size:13px;max-width:830px}
.approval-actions{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin-top:16px}
.approval-actions form{margin:0}
.approval-submit{background:linear-gradient(110deg,#ffd399,#f6ad74);color:#1b1924;border:none;border-radius:12px;padding:13px 22px;font-weight:900;font-family:inherit;font-size:13px;cursor:pointer}
.approval-submit:hover{filter:brightness(1.07)}
.report-link{padding:12px 16px;border:1px solid rgba(204,216,236,.4);border-radius:11px;color:#e6f1ff;font-size:13px;font-weight:750}
.approval-quiet{border-color:#2b4c57;background:#122a36}
.approval-quiet h2{color:#b6eed9}
.stage-section{border:1px solid var(--edge);border-radius:16px;background:#101c2d;margin:20px 0;padding:20px}
.stage-section h2{font-size:15px;margin:0 0 14px}
.stage-track{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px}
.stage-cell{border:1px solid rgba(158,188,211,.16);background:#17253a;border-radius:10px;padding:11px 10px;font-size:11px;color:#8394af}
.stage-cell span{display:block;font-size:9px;color:#7388a5;letter-spacing:1px}
.stage-cell.current{border-color:#74ddd9;background:#1c414d;color:#ebffff;font-weight:850}
.stage-cell.done{border-color:rgba(117,203,164,.27);color:#9fdfc7}
.stage-cell.current span,.stage-cell.done span{color:inherit}
.task-headline{padding-top:20px}
.task-headline h1{font-size:clamp(27px,3vw,42px);margin-bottom:8px}
.task-subline{display:flex;align-items:center;gap:8px;flex-wrap:wrap;color:#b5c7d9;font-size:12px}
#reports{scroll-margin-top:15px;font-size:18px;margin:34px 0 10px}
@media(max-width:1100px){.topnav{display:none}.dept-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:900px){.hero.campus-hero{grid-template-columns:1fr}.campus-visual{min-height:280px}.campus-visual svg{max-height:350px}.campus-copy{padding:0}}
@media(max-width:600px){.shell{padding-inline:15px}.hero.campus-hero{padding-top:25px}.campus-hero h1{font-size:32px}.approval-hub{padding:16px}.approval-entry{align-items:stretch;flex-direction:column}.review-link{width:100%}.approval-count{min-width:60px;padding:8px}.dept-grid{grid-template-columns:1fr 1fr}.dept-card{padding:13px;min-height:170px}.stage-track{grid-template-columns:repeat(2,minmax(0,1fr))}.hero-links a{flex:1}.approval-detail{padding:18px}}
@media(prefers-reduced-motion:reduce){.agent-monitor,.scene-activity,.campus-visual .meeting-glow{animation:none!important}*,*:before,*:after{scroll-behavior:auto!important}}
"""


CAMPUS_SCENE = r"""
<div class="campus-visual" role="img" aria-label="رسم توضيحي لمكتب شركة برمجيات ذكية؛ وكلاء على حواسيب ومساحة اجتماع">
  <span class="scene-caption">AI OPERATIONS CAMPUS / CONCEPT VIEW</span>
  <svg viewBox="0 0 660 360" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
    <defs>
      <linearGradient id="wall" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#233a59"/><stop offset="1" stop-color="#101d31"/></linearGradient>
      <linearGradient id="screen" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#255d78"/><stop offset="1" stop-color="#294b76"/></linearGradient>
      <linearGradient id="floor" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#2d455f"/><stop offset="1" stop-color="#142338"/></linearGradient>
    </defs>
    <rect width="660" height="360" fill="url(#wall)"/>
    <path d="M0 235H660V360H0Z" fill="url(#floor)"/>
    <path d="M0 235H660M0 297H660M0 344H660" stroke="#405d76" opacity=".32"/>
    <path d="M160 235 80 360M340 235 320 360M530 235 620 360" stroke="#405d76" opacity=".2"/>
    <rect x="26" y="48" width="365" height="158" rx="14" fill="#10263d" stroke="#456d85"/>
    <rect x="39" y="61" width="339" height="132" rx="7" fill="#152b44"/>
    <path d="M55 100H363M55 137H363" stroke="#244561" stroke-width="1"/>
    <g opacity=".75">
      <rect x="58" y="79" width="70" height="9" rx="4" fill="#3a6d7b"/>
      <rect x="142" y="79" width="91" height="9" rx="4" fill="#355c78"/>
      <rect x="250" y="79" width="89" height="9" rx="4" fill="#244e6a"/>
      <path d="M65 167 112 150 164 157 199 118 245 144 285 109 348 128" fill="none" stroke="#72e5d1" stroke-width="3" stroke-linecap="round"/>
      <circle cx="199" cy="118" r="5" fill="#c3f6fa"/>
      <circle cx="285" cy="109" r="5" fill="#c3f6fa"/>
    </g>
    <rect x="414" y="54" width="219" height="166" rx="14" fill="#13293d" stroke="#42647f"/>
    <rect x="428" y="68" width="190" height="21" rx="6" fill="#24445b"/>
    <circle cx="442" cy="78" r="4" fill="#76ebd6"/>
    <path d="M456 78H529" stroke="#9bcbd7" stroke-width="5" stroke-linecap="round"/>
    <text x="522" y="107" fill="#9abbc9" text-anchor="middle" font-size="10" font-family="sans-serif">TEAM SYNC / REVIEW</text>
    <ellipse cx="518" cy="169" rx="71" ry="25" fill="#305773" stroke="#5790ac"/>
    <ellipse cx="518" cy="168" rx="51" ry="15" fill="#41718e" opacity=".5"/>
    <g class="meeting-glow">
      <circle cx="470" cy="134" r="12" fill="#f2bea1"/><path d="M453 154Q470 140 486 156L489 177H449Z" fill="#7d94ec"/>
      <circle cx="555" cy="126" r="12" fill="#dbab8e"/><path d="M538 148Q556 136 573 152L576 167H536Z" fill="#55c0ba"/>
      <circle cx="516" cy="201" r="11" fill="#f4cba9"/><path d="M499 220Q517 205 534 220" fill="#7eabd7"/>
    </g>
    <path d="M40 290 122 249 211 282 142 340Z" fill="#3b617a" stroke="#4f7a98"/>
    <path d="M232 285 301 245 389 281 321 330Z" fill="#365e79" stroke="#4f7a98"/>
    <g>
      <ellipse cx="117" cy="236" rx="32" ry="16" fill="#15263c"/>
      <path d="M91 252Q116 231 145 249L154 288 83 288Z" fill="#786fd0"/>
      <rect x="98" y="210" width="40" height="43" rx="17" fill="#dca881"/>
      <circle cx="117" cy="202" r="25" fill="#e8b58e"/>
      <path d="M91 198Q91 169 116 176Q140 177 144 202L130 188 106 187Z" fill="#253648"/>
      <path d="M98 210 107 214M128 214 137 211" stroke="#ad6c62" stroke-width="2" opacity=".55"/>
      <rect x="50" y="236" width="89" height="52" rx="6" fill="url(#screen)" stroke="#85d6e7"/>
      <path d="M61 249H119M61 258H107M61 268H96" stroke="#7de8e1" opacity=".67" stroke-width="4" stroke-linecap="round" class="agent-monitor"/>
      <path d="M43 288H153L141 295H49Z" fill="#7b97ad"/>
    </g>
    <g>
      <path d="M285 251Q308 233 340 250L347 285H277Z" fill="#45acae"/>
      <circle cx="312" cy="205" r="24" fill="#deb69b"/>
      <path d="M288 200Q289 175 313 178Q340 181 338 207L323 191 295 198Z" fill="#242941"/>
      <rect x="300" y="223" width="26" height="24" rx="9" fill="#deb69b"/>
      <rect x="244" y="233" width="90" height="57" rx="6" fill="url(#screen)" stroke="#8bd7e9"/>
      <path d="M256 246H317M256 256H303M256 267H310" stroke="#a7a5fd" stroke-width="4" stroke-linecap="round" class="agent-monitor"/>
      <path d="M238 290H351L339 296H247Z" fill="#849cb9"/>
    </g>
    <g class="scene-activity">
      <rect x="178" y="226" width="90" height="33" rx="9" fill="#18394f" stroke="#4d9eac"/>
      <circle cx="193" cy="242" r="5" fill="#80ebd3"/><path d="M208 238H251M208 246H238" stroke="#90bfcb" stroke-width="4" stroke-linecap="round"/>
    </g>
    <g class="scene-activity two">
      <rect x="365" y="249" width="93" height="34" rx="9" fill="#203953" stroke="#5b8dc4"/>
      <rect x="375" y="259" width="18" height="14" rx="4" fill="#a2a7ff"/><path d="M403 260H447M403 269H431" stroke="#90b4ca" stroke-width="4" stroke-linecap="round"/>
    </g>
    <path d="M379 30H610" stroke="#4a718b" stroke-width="2" opacity=".65"/>
    <circle cx="605" cy="30" r="5" fill="#7de9d2"/>
    <circle cx="383" cy="30" r="5" fill="#a2adfa"/>
  </svg>
  <span class="scene-disclaimer">Illustration only · status from real task data</span>
</div>
"""


DEPARTMENTS = (
    ("discovery", "◈", "Discovery", "فهم الفكرة وتحديد الأهداف"),
    ("requirements", "▤", "Product", "المتطلبات وقبول النتائج"),
    ("architecture", "⌘", "Architecture", "التصميم التقني والقرارات"),
    ("backlog", "☷", "Planning", "خريطة التنفيذ والأولويات"),
    ("implementation", "⌨", "Engineering", "البرمجة داخل Worktree معزول"),
    ("qa", "◉", "Quality Lab", "الاختبارات والتدقيق"),
    ("security", "◇", "Security", "المراجعة الأمنية"),
    ("release_plan", "↗", "Release Control", "تجهيز خطة الإصدار"),
)


def campus_hero() -> str:
    return (
        '<section class="hero campus-hero"><div class="campus-copy">'
        '<div class="campus-kicker">ITEM SPACE AI · OPERATIONS CAMPUS</div>'
        '<h1>شركة برمجيات ذكية.<br><em>كل قسم إله مهمة.</em></h1>'
        '<p class="lead">من الفكرة إلى التصميم والبرمجة والجودة. '
        'تابع المشروع على مراحل واضحة، وخذ قرارات الموافقة بنفسك من مركز واحد.</p>'
        '<div class="hero-links"><a class="primary-link" href="/office">◈ شاهد مكتب الـAgents</a>'
        '<a href="#approvals">مركز الموافقات</a>'
        '<a href="#mission-intake">ابدأ مشروعاً</a>'
        '<a href="#departments">أقسام العمل</a></div></div>'
        + CAMPUS_SCENE + '</section>'
    )


def approval_center(records: list[dict]) -> str:
    waiting = [r for r in records if r["status"] == "WAITING_APPROVAL"]
    result = (
        '<section class="approval-hub" id="approvals" aria-labelledby="approval-center-title">'
        '<div class="approval-header"><div><h2 id="approval-center-title" class="approval-title">'
        '◈ مركز الموافقات والقرارات</h2>'
        '<p class="approval-sub">هذه القائمة تعرض قرارات المهام الحقيقية فقط، '
        'ولا تمنح موافقة تلقائياً.</p></div>'
        '<div class="approval-count">' + str(len(waiting)) + '<small>بانتظار قرارك</small></div></div>'
    )
    if not waiting:
        return result + (
            '<div class="approval-clear"><strong>✓</strong>'
            '<span>لا توجد موافقات معلّقة حالياً. ستظهر هنا عند توقف المهمة للمراجعة.</span>'
            '</div></section>'
        )
    result += '<div class="approval-list">'
    for r in waiting:
        stage = r["stage"]
        decision = ("اعتماد بدء البرمجة" if stage == "implementation"
                    else "اعتماد المراجعة النهائية" if stage == "release_gate"
                    else "مراجعة الحالة")
        result += (
            '<article class="approval-entry"><div><strong>' + escape(r["title"])
            + '</strong><p>' + escape(decision) + ' · ' + escape(r["id"])
            + ' · ' + escape(stage) + '</p></div>'
            '<a class="review-link" href="/ideas/' + escape(r["id"], quote=True)
            + '#task-approval">مراجعة القرار ←</a></article>'
        )
    return result + '</div></section>'


def department_board(records: list[dict]) -> str:
    result = (
        '<section class="departments" id="departments">'
        '<div class="section-band"><div><h2>◈ أقسام شركة الـAI</h2>'
        '<p>تمثيل لمراحل العمل الفعلية، وليس ادعاء بوجود وكلاء يعملون بشكل مباشر.</p>'
        '</div><span class="tag">8 PIPELINE STAGES</span></div>'
        '<div class="dept-grid">'
    )
    for stage, symbol, title, description in DEPARTMENTS:
        number = sum(r["stage"] == stage and
                     r["status"] in ("PENDING", "RUNNING", "INTERRUPTED", "WAITING_APPROVAL")
                     for r in records)
        result += (
            '<article class="dept-card"><div class="dept-icon" aria-hidden="true">'
            + escape(symbol) + '</div><h3>' + escape(title) + '</h3>'
            '<p>' + escape(description) + '</p>'
            '<div class="dept-value"><strong>' + str(number)
            + '</strong> مهام في المرحلة</div></article>'
        )
    return result + '</div></section>'


def task_hero(task: dict) -> str:
    project_name = Path(task["project"].replace("\\", "/")).name
    return (
        '<section class="task-headline"><p class="eyebrow">MISSION / PROJECT WAR ROOM</p>'
        '<h1>غرفة متابعة <em>المشروع</em></h1>'
        '<div class="task-subline"><strong>' + escape(project_name)
        + '</strong><span>·</span><span>' + escape(task["id"])
        + '</span><span>·</span><span class="flag '
        + escape(task["status"], quote=True) + '">'
        + escape(task["status"]) + '</span></div></section>'
    )


def stage_track(task: dict) -> str:
    labels = {
        "discovery": "اكتشاف", "requirements": "متطلبات",
        "architecture": "معمارية", "backlog": "خطة عمل",
        "implementation": "برمجة", "qa": "جودة",
        "security": "أمان", "release_plan": "إصدار",
    }
    stages = [item[0] for item in DEPARTMENTS]
    current = stages.index(task["next_stage"]) if task["next_stage"] in stages else len(stages)
    result = '<section class="stage-section"><h2>مسار التنفيذ · الحالة الفعلية للمهمة</h2><div class="stage-track">'
    for index, stage in enumerate(stages):
        state = "done" if index < current else "current" if index == current else "future"
        result += (
            '<div class="stage-cell ' + state + '"><span>0' + str(index + 1) + '</span>'
            + escape(labels[stage]) + '</div>'
        )
    return result + '</div></section>'


def approval_panel(csrf: str, task: dict) -> str:
    if task["status"] != "WAITING_APPROVAL":
        return (
            '<section class="approval-detail approval-quiet" id="task-approval">'
            '<h2>✓ مركز الموافقة</h2><p>لا يوجد قرار مطلوب منك حالياً لهذه المهمة. '
            'حالتها الحالية: ' + escape(task["status"]) + '.</p></section>'
        )
    stage = task["next_stage"]
    if stage == "implementation":
        heading = "قرار مطلوب: السماح ببدء البرمجة"
        description = ("راجع مخرجات الاكتشاف والمتطلبات والمعمارية وخطة التنفيذ. "
                       "الموافقة تسمح للعامل بالوصول إلى مرحلة تعديل الكود في Worktree معزول؛ "
                       "لا تعني النشر أو الدمج.")
        gate = "build"
        button = "أوافق على بدء البرمجة"
    elif stage == "release_gate":
        heading = "قرار مطلوب: اعتماد المراجعة النهائية"
        description = ("راجع تقارير الجودة والأمان وخطة الإصدار. هذه موافقة إدارية "
                       "ولا تنفذ نشر الإنتاج أو GitHub push.")
        gate = "release"
        button = "أعتمد المراجعة النهائية"
    else:
        return (
            '<section class="approval-detail" id="task-approval">'
            '<h2>مراجعة الحالة مطلوبة</h2><p>لا يوجد زر موافقة لهذه المرحلة. '
            'افتح مخرجات وتقارير المهمة وافحص سبب التوقف.</p></section>'
        )
    return (
        '<section class="approval-detail" id="task-approval">'
        '<h2>⚑ ' + escape(heading) + '</h2><p>' + escape(description) + '</p>'
        '<div class="approval-actions"><a class="report-link" href="#reports">'
        'استعراض تقارير المراحل أولاً</a>'
        '<form method="post" action="/ideas/' + escape(task["id"], quote=True)
        + '/approve"><input type="hidden" name="csrf" value="'
        + escape(csrf, quote=True) + '">'
        '<input type="hidden" name="gate" value="' + gate + '">'
        '<button class="approval-submit" type="submit">' + escape(button)
        + '</button></form></div>'
        '<p class="hint">الموافقة فعل حقيقي على المهمة، وتسمح بالمتابعة عند تشغيل العامل. '
        'لا تضغط إلا بعد مراجعة التقارير.</p></section>'
    )
