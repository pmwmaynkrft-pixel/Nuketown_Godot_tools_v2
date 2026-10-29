# خريطة Nuketown — مشروع اختبار Godot 4.7.2

هذه الحزمة **لا تحتوي** على أي نماذج أو خامات من GTA V أو Call of Duty. تحتوي على:

- أدوات استخراج وتحويل بلغة Python (`tools/`) تقرأ ملفك المحلي `Nuketown for GTA V.zip`.
- ملف `project.godot` ومشهد الخريطة `Nuketown.tscn` (يُولَّد بالأدوات) ومشهد نقاط الظهور.
- سكربتات اختبار GDScript (`godot_tests/`).

> **الترخيص:** منفّذ المود يذكر أن الأصول مأخوذة من Treyarch/Activision وأن الخريطة fan port غير تجاري.
> لذلك لا أُعيد توزيع الأصول. شغّل المحوّل محليًا على ملفك. النشر العلني أو التجاري يحتاج مراجعة قانونية منك.

## المتطلبات
- Python 3.10+ مع: `numpy`, `pillow`, `scipy` (الأخير اختياري).
- Godot 4.7.2 (للفتح والاختبار).

## التشغيل (من مجلد العمل الذي بجانب `tools/`)
```
GODOT=/path/to/Godot_v4.7.2-stable_linux.x86_64 sh tools/run_all.sh "/path/to/Nuketown for GTA V.zip"
```
(على Linux يلزم `xvfb-run`؛ خطوة التحسين لا تعمل بوضع `--headless` لأن المُصيِّر الوهمي لا يحفظ بيانات MultiMesh.)
الخطوات التي ينفذها السكربت:
1. `prepare.py` — يفك `dlc.rpf` (RPF7، غير مشفّر) ويستخرج 4 حزم متداخلة إلى `ex/`.
2. `ytd.py` — يحوّل 575 خامة DXT إلى PNG.
3. `ymap.py` — يقرأ 5157 كيانًا (مواضع/دوران/مقياس) من 18 ملف YMAP.
4. `ybn.py` — يقرأ تصادم 598 خلية (YBN) كمثلثات بإحداثيات عالمية.
5. `build.py` — يصدّر 1129 نموذجًا (YDR + YFT) إلى glTF مع الخامات.
6. `build_scene.py` و`build_vcol.py` و`assemble.py` — يبنون التصادم والمشهد غير المحسّن `Nuketown_original.tscn` و`project.godot`.
7. `sigs.py` ثم `optimize.gd` (داخل Godot) — يكتب `Nuketown.tscn` المحسّن (مواد مشتركة، MultiMesh، دمج، visibility_range). انظر `REPORT_PERF_AR.md`.

ثم افتح المجلد `proj/` في Godot 4.7.2 (أول فتح يستغرق وقتًا للاستيراد) وشغّل `res://maps/nuketown/Nuketown.tscn`.

## بنية المشهد
`Terrain` / `Mountains` / `Structures` / `Props` / `Foliage` / `Glass` (مجموعات حسب الاسم والحجم)،
`Collision` (تصادم YBN الأصلي)، `StructuresCollision` (تصادم بديل، انظر التقرير)،
`Environment` (سماء وشمس من تأليفي)، `SpawnPoints/TeamA` و`TeamB` (Marker3D في المجموعتين `spawn_team_a` و`spawn_team_b`).

## التحويلات
- GTA (x, y, z) ← Godot (x, z, −y)، مع طرح إزاحة (6000, 10000, 0).
- دوران YMAP المخزّن هو معكوس، ويُطبَّق معكوسًا (تم التحقق بالمقارنة مع التصادم).

## الاختبارات (GDScript، من داخل `proj/` بعد نسخ `godot_tests/` إلى `tools/`)
```
godot --headless --path . --script tools/test_map.gd
godot --headless --fixed-fps 600 --path . --script tools/test_player.gd
```

## ما لم يُنجز بعد
انظر `REPORT_AR.md` (الأداء على Android، خرائط normal، ألوان الرؤوس، الديكالات، السيارات).
