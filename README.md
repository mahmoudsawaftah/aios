# AIOS — Item Space Edition

نسخة Codex-first نظيفة لتطوير Item Space داخل Antigravity، مع إجراءات وأدوار للمشروع وسجل خطة واحد. أُخذت الدروس المفيدة من AIOS الأصلي، وتوثقت حالة مصنع البرمجيات القديم وحدوده في `docs/ORIGINAL_AIOS_REFERENCE.md`. النسخة لا تنسخ النسخ الاحتياطية أو الكاش أو runtime التجريبي إلى مسار العمل النشط.

## ابدأ من هنا
1. فك النسخة في مجلد جديد وافتح جذر AIOS في Antigravity.
2. اقرأ `AGENTS.md` و`ITEM_SPACE_BRIEF.md`.
3. اكتب `/skills` داخل محادثة Codex وتأكد من ظهور مهارات `item-space-*`.
4. ابدأ بطلب جرد قراءة فقط للمجلد المستهدف وجذر Git. لا تبدأ توليد التطبيق قبل تثبيت خط الأساس وأول شريحة MVP.

## المحتويات
- `AGENTS.md`: توجيه Codex كمهندس رئيسي وحدود النطاق والأمان.
- `ITEM_SPACE_BRIEF.md`: اتجاه المنتج المعروف وما لم يُحسم بعد.
- `PLANS.md`: سجل المهمة والخطة الحالية.
- `agents/roles/`: مراحل اكتشاف ومتطلبات ومعمارية وتخطيط وتنفيذ وQA وأمن وإطلاق؛ يطبقها Codex الرئيسي ولا تعني تشغيل وكلاء مستقلين.
- `.agents/skills/`: مهارات Codex المتخصصة.
- `docs/AIOS_OPERATING_MODEL.md`: سير العمل، الأدلة، وبوابات المراجعة.
- `docs/CAPABILITIES_AND_LIMITS.md`: ما يفعله هذا الإصدار وما لا يشغله.
- `docs/ORIGINAL_AIOS_REFERENCE.md`: ملخص موثق لمحتوى AIOS الأصلي ومخاطر runtime القديم.
- `projects/Item Space/Item Space.md`: ملف فارغ كبداية.

## جذر Git
مجلد `projects/Item Space/` placeholder داخل مستودع AIOS، وليس مستودع Git مستقلًا. إذا أردت Git مستقلًا للمنتج، افتح نسخة مستودع Item Space نفسها في Antigravity أو أنشئ clone منفصلًا. لا تخلط التطبيق مع جذر AIOS.

## حدود النسخة
Codex هو الوكيل الرئيسي الذي ينفذ المهمة عند تكليفه بها. هذه الملفات لا تشغل Worker بالخلفية، ولا تضمن استئنافًا آليًا أو تشغيلًا 24/7. لا يوجد نشر أو commit أو push تلقائي. راجع `docs/CAPABILITIES_AND_LIMITS.md`.
