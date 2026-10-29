#!/bin/sh
# الاستخدام (من مجلد العمل): GODOT=/path/to/Godot_v4.7.2 sh tools/run_all.sh "/path/Nuketown for GTA V.zip"
# يتطلب xvfb-run على Linux (خطوة التحسين تحتاج مُصيِّرًا حقيقيًا: لا تستخدم --headless لـ optimize.gd لأنه لا يحفظ بيانات MultiMesh)
set -e
T="$(dirname "$0")"; G="${GODOT:-godot}"
mkdir -p out proj
cp "$T/spawns.json" out/spawns.json
python3 "$T/prepare.py" "$1"
python3 "$T/ytd.py"; python3 "$T/ymap.py"; python3 "$T/ybn.py"
python3 "$T/build.py"; python3 "$T/build_scene.py"; python3 "$T/build_vcol.py"; python3 "$T/assemble.py"
python3 "$T/sigs.py"
mkdir -p proj/tools; cp "$T/optimize.gd" proj/tools/
( cd proj && "$G" --headless --path . --import )
( cd proj && xvfb-run -a -s "-screen 0 1280x720x24" "$G" --path . --rendering-driver opengl3 --rendering-method gl_compatibility --resolution 640x360 --script tools/optimize.gd )
echo "تم. افتح المجلد proj في Godot 4.7.2 (المشهد المحسّن Nuketown.tscn، وغير المحسّن Nuketown_original.tscn)"
