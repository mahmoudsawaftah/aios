# Item Space AI v3.1 — Engineering handoff / تسليم تشغيلي تجريبي

**Status: INTEGRATION CANDIDATE — NOT PRODUCTION-READY.**

الهدف: استقبال الفكرة أو الطلب من واجهة Item Space AI أو Codex داخل Antigravity، تسجيلها في قائمة المهام المشتركة، تشغيل مراحل تطوير v2، والاستفادة من البحث عن المشاريع المفتوحة المصدر وإعداد تسويق مبدئي ومراجعة GitHub.

## ماذا تم بناؤه فعلياً؟

| الوظيفة | التنفيذ | حدودها |
|---|---|---|
| واجهة Item Space AI | متوفرة من v3.0 مع اختصار سطح المكتب | محلية دون حسابات مستخدمين عن بُعد |
| Codex MCP Bridge | `factory/mcp_bridge.py` + `scripts/item_space_mcp.py` | يتطلب تثبيت MCP وإضافة Codex متوافقة |
| من Codex إلى Queue | submit_idea / submit_existing_project | يسجل المهمة؛ التنفيذ يتطلب Worker شغالاً |
| التخطيط والبرمجة | يستخدم محرك Factory v2 المتسلسل وCodex CLI | Codex Plus ضمن الحصة، لا يعمل إذا انتهت |
| استئناف المهام | `factory/supervisor.py` وSQLite وسجل أحداث v2 | إعادة مرحلة، ليس ضمان Exactly Once |
| البحث عن Open Source | GitHub Public Search API مع روابط وتاريخ ونوع ترخيص | نتائج أولية، بلا فحص ثغرات أو استنساخ آلي |
| التسويق | خطة إطلاق و14 مسودة نصية CSV/MD | لا ينشئ صوراً/فيديوهات ولا ينشر |
| GitHub | Preflight + private repository + review PR عبر gh | النشر معطّل افتراضياً ويتطلب سماحاً واعتماداً |
| واجهة الأدوات | 3 أزرار لكل مشروع: Research/Marketing/GitHub Check | لا يمكن النشر الإنتاجي أو تجاوز الموافقات |

## التثبيت المختصر (بضغطة واحدة بعد تنزيل الفرع)

بمجرد تبديل Git إلى هذا الفرع، أوقف أي نافذة سيرفر قديمة ثم اضغط مرتين على الملف **SETUP_ITEM_SPACE_AI_V3.cmd**. يتأكد من الاختبارات والأدوات، ويسجل Codex MCP وينشئ اختصار سطح المكتب مع Worker مفعل. إن فشل فحص، يتوقف التثبيت ولا ينفذ نشرًا خارجيًا.

## التثبيت مرة واحدة على Windows

من PowerShell، وأنت على نسخة المشروع المعتمدة:

```powershell
cd "C:\Users\ENG_Mahmoud\Documents\aios"
git fetch origin
git switch feat/item-space-ai-autonomy-v3-1
python -m unittest discover -s tests -p "test_*.py" -v
python scripts/audit_legacy_projects.py .
powershell -NoProfile -ExecutionPolicy RemoteSigned -File .\INSTALL_CODEX_BRIDGE.ps1
codex mcp list
```

**ضروري:** شغّل الاختبارات قبل تثبيت MCP، ولا تكمل إذا فشلت.

أوقف أي سيرفر قديم (Ctrl+C في نافذة تشغيله). لتعديل اختصار سطح المكتب بحيث يفتح النظام ويشغّل Worker Codex عند النقر:

```powershell
powershell -NoProfile -ExecutionPolicy RemoteSigned -File .\INSTALL_ITEM_SPACE_AI.ps1 -EnableWorker
```

بعد ذلك انقر **item space AI** على سطح المكتب. يفتح المتصفح تلقائياً عند `http://127.0.0.1:8765/`. أبقِ نافذة الـWorker مفتوحة/مصغرة. **هذا يستهلك من حدود Codex ضمن Plus**؛ لا تشغّل نسختين متزامنتين. ليس تشغيل 24 ساعة إذا الجهاز مطفأ.

### من داخل Antigravity / Codex

1. تأكد من أن إضافة Codex تعمل بالفعل وتقرأ إعدادات MCP المشتركة (راجع `codex mcp list`).
2. أعد تشغيل Codex extension بعد تثبيت MCP.
3. اكتب في محادثة Codex: **«استخدم أدوات item-space-ai MCP. سجّل الفكرة التالية كمشروع، ثم أعطني Task ID وتابع حالته: ...»**
4. لطلب داخل مستودع منتج موجود: **«استخدم submit_existing_project لهذا Git repo وهدف ...»**.
5. عند تشغيل الواجهة بالـWorker، تتقدم مراحل التخطيط والتنفيذ؛ تتوقف عند build/release approvals حتى تراجعها.

ملاحظة: لا يمكن لهذا الكود ضمان اعتراض كل رسالة تلقائياً في Antigravity؛ هو MCP tool server يستطيع Codex استخدامه إن كانت الإضافة تدعم MCP وتعمل.

### GitHub Private PR — تشغيل اختياري بعد الفحص

ثبّت GitHub CLI رسمياً، ثم سجّل دخولك بصورة تفاعلية:

```powershell
gh auth login
gh auth status
python -m factory.github_ops preflight TASK_ID
```

عندما تعود `ready_for_private_pr=true` ويكون فحص الملفات/الاختبارات والترخيص ومراجعة العميل سليماً، شغّل عن قصد:

```powershell
$env:AIOS_ALLOW_GITHUB_PR = "1"
python -m factory.github_ops publish-private-pr TASK_ID
Remove-Item Env:\AIOS_ALLOW_GITHUB_PR
```

هذا ينشئ/يستخدم مستودعاً **خاصاً** ويصنع PR للمراجعة. لا يدمج ولا ينشر. التحقق من أسماء الملفات وحده لا يعادل Secret Scanning. لا ترسل مستودعات عملاء خاصة قبل مراجعة الأمن والصلاحيات.

### تشغيل Supervisor مستقل (بديل للواجهة)

```powershell
python -m factory.supervisor --once
# أو في نافذة مستقلة:
python -m factory.supervisor --poll 20
```

لا تجمع Supervisor المستقل مع عامل الواجهة دون تخطيط منع ازدواجية التشغيل. المهام المحجوبة بالموافقة أو الفاشلة لا تُنفّذ بلا مراجعة.

### البحث والتسويق

داخل صفحة تفاصيل المشروع توجد أزرار لتشغيل الفحوص، أو من Codex MCP مباشرة، أو CLI:

```powershell
python -m factory.oss_research "salon booking open source" --limit 6
python -m factory.marketing TASK_ID
```

تقارير البحث/التسويق تحفظ محلياً تحت `.factory-runtime/` وتعرض في صفحة المهمة. GitHub Search يحتاج إنترنت وقد يحد الطلبات المجانية. نتائج الرخص لا تمثل موافقة قانونية آلية على إعادة بيع الكود.

## ما لا يزال غير مكتمل

- CI على GitHub: الفحوص السابقة لم تحصل على Runner؛ نحتاج التحقق على Windows ومعالجة سبب GitHub Actions.
- لم نختبر هذه الإضافات على جهاز Windows الخاص بالمالك بعد؛ اختبارات v3.0 السابقة لا تكفي لقبول v3.1.
- لا توجد خدمة سحابية تعمل والجهاز مطفأ؛ ولا تسجيل دخول محمي للتحكم من الإنترنت.
- لا يوجد Multi-Agent worker pool متزامن مثبت أو Crash/Restore Drill شامل.
- لا يوجد فحص ثغرات وتبعيات وتراخيص مكتمل قبل اعتماد مشروع Open Source.
- لا يوجد منشئ فيديو وصور تسويقية موثوق، ولا نشر تلقائي لحسابات السوشال ميديا، ولا إدارة إعلانات مدفوعة.
- لا توجد بوابة اشتراكات/فواتير إنتاجية أو عقود/صلاحيات حسابات العملاء.
- لا يوجد نشر إنتاجي end-to-end أو دعم SLA بدون ربط الاستضافة والدومين والدفع والنسخ الاحتياطية.

## معايير القبول قبل دمج هذا الفرع

1. نجاح اختبارات Python كافة وLegacy audit على Windows.
2. نجاح MCP handshake وtool list من Codex داخل IDE.
3. إنشاء فكرة واحدة من Codex ومن الواجهة والتحقق من Task IDs منفصلة.
4. إثبات التوقف عند build/release gate وتنفيذ اختبار استئناف بعد إيقاف Worker تجريبي.
5. التأكد أن بحث GitHub يُرجع روابط صحيحة، وأن تصنيف AGPL/UNKNOWN يطلب مراجعة.
6. التأكد أن خطة التسويق تحفظ مسودات فقط ولا تنشر.
7. اختبار GitHub preflight في وضع القراءة فقط؛ والنشر إلى مستودع تجريبي خاص فقط بعد موافقة المالك.
8. مراجعة أمان MCP والصلاحيات والسجلات والمحتوى قبل أي عميل حقيقي.

**لا تدمج في main ولا تعلن تسليماً تجارياً نهائياً قبل تحقق هذه البنود.**
