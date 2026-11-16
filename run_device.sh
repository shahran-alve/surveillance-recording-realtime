#!/usr/bin/env bash
# Portable device run (Raspberry Pi, Jetson, mini PC, ...): downloads the seven Intel sample videos and yolo11n.pt, verifies the
# per-clip frame counts, regenerates the clean trigger scores (motion_scores.py for the clean copy only is not separable, so the
# script runs motion_scores.py as shipped: clean + jitter + illum + noise; det_scores.py yolo11n clean), runs ONE Phase-1 profiling
# run (measure_motion.py + the detector timing loop of measure_det.py via e1_profile.py, pinned to one core), and bench_device.py.
# No absolute paths: everything lives under the repository (SS_ROOT=<repo>/device_run/root). Python environments: pass PY_ANALYSIS
# and PY_DETECTOR (interpreters with the packages of requirements-analysis.txt / requirements-detector.txt), or a single PY for both.
# Usage: ./run_device.sh [CORE] [CORE2]            env: PY, PY_ANALYSIS, PY_DETECTOR, SKIP_DOWNLOAD=1
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd); cd "$HERE"
PY=${PY:-python3}; PYA=${PY_ANALYSIS:-$PY}; PYD=${PY_DETECTOR:-$PY}
CORE=${1:-$(( $(nproc) > 1 ? 1 : 0 ))}; CORE2=${2:-$(( $(nproc) > 2 ? 2 : CORE ))}
export CUDA_VISIBLE_DEVICES="" SS_ROOT="$HERE/device_run/root"; OUT="$HERE/results/rt_$(hostname)"
mkdir -p "$SS_ROOT/results/rt" "$SS_ROOT/results/motion_scores" "$SS_ROOT/results/det_scores" "$HERE/data/sample-videos" "$HERE/data/models" "$OUT/e1/run1"
ln -sfn ../../exp "$SS_ROOT/exp"; ln -sfn ../../data "$SS_ROOT/data"
# ---- Phase 0.4: data
if [ -z "${SKIP_DOWNLOAD:-}" ]; then
  for f in one-by-one-person-detection.mp4 people-detection.mp4 person-bicycle-car-detection.mp4 face-demographics-walking-and-pause.mp4 worker-zone-detection.mp4 car-detection.mp4 store-aisle-detection.mp4; do
    [ -s "data/sample-videos/$f" ] || curl -sSL -o "data/sample-videos/$f" "https://github.com/intel-iot-devkit/sample-videos/raw/master/$f"
  done
  [ -s data/models/yolo11n.pt ] || curl -sSL -o data/models/yolo11n.pt https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11n.pt
fi
"$PYA" - <<'PYEOF' | tee "$OUT/frame_counts.txt"
import sys, os; sys.path.insert(0, os.environ['SS_ROOT'] + '/exp')
from common import VIDEOS, video_info, frames
exp = {'one-by-one':1394,'people':596,'person-bike-car':647,'walk-and-pause':1091,'worker-zone':910,'car-lot':377,'store-aisle':785}; bad = 0
for v in VIDEOS:
    fps, n = video_info(v); m = sum(1 for _ in frames(v)); ok = m == exp[v] == n; bad += not ok; print(v, 'fps', round(fps, 3), 'frames', m, 'expected', exp[v], 'OK' if ok else 'MISMATCH')
sys.exit(1 if bad else 0)
PYEOF
# ---- Phase 0.5: clean scores (motion: all four kinds, as the script is written; detector: clean)
"$PYA" exp/motion_scores.py 2>&1 | tee "$OUT/motion_scores.log"
"$PYD" exp/rt/run_vm_threads.py exp/det_scores.py yolo11n clean 2>&1 | tee "$OUT/det_scores.log"
# ---- Phase 1: one profiling run (fresh processes, pinned)
{ echo "load=$(cut -d' ' -f1-3 /proc/loadavg)"; taskset -c "$CORE" "$PYA" exp/rt/measure_motion.py 1; } 2>&1 | tee "$OUT/e1/run1/measure_motion.log"
mv "$SS_ROOT/results/rt/lat_motion.npz" "$OUT/e1/run1/lat_motion.npz"
"$PYD" exp/rt/e1_profile.py --out "$OUT/e1/run1" --core "$CORE" --core2 "$CORE2" 2>&1 | tee "$OUT/e1/run1/e1_profile.log"
# ---- stand-alone device benchmark (640 and 320 px, one thread) on the people clip at 12 fps
for S in 640 320; do
  taskset -c "$CORE" "$PYD" exp/rt/run_vm_threads.py exp/rt/bench_device.py --video data/sample-videos/people-detection.mp4 --fps 12 --width 768 --threads 1 --imgsz $S --model data/models/yolo11n.pt --out "$OUT/bench_device_$S.json" 2>&1 | tee "$OUT/bench_device_$S.log"
done
{ echo "host: $(hostname)"; uname -a; lscpu 2>/dev/null | head -20; cat /proc/loadavg; } > "$OUT/platform.txt"
echo "run_device.sh done: results in $OUT"
