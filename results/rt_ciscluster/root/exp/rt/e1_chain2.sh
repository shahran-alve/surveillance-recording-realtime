#!/bin/bash
# Phase 1 pipeline, restarted after the e1_profile.py thread fix. Keeps run0 and the existing lat_motion.npz of runs 1-2 (separate,
# unaffected processes); runs the remaining measure_motion.py and all five e1_profile.py runs, then pooled traces, analyze.py per run
# and pooled (parallel), analyze2.py, soak tests, e1_analyze.py.
set -u
REPO=$(cd "$(dirname "$0")/../.." && pwd); export SS_ROOT=$REPO/results/rt_ciscluster/root CUDA_VISIBLE_DEVICES=""
SP=/tmp/claude-8800/-u-erdos-csga2-mmahmud9-smart-surveillance-realtime/68d9c066-41df-481b-ac8a-d697ba6c7735/scratchpad
PYA=$SP/venv-analysis/bin/python; PYD=$SP/venv-detector/bin/python; E1=$REPO/results/rt_ciscluster/e1; mkdir -p $E1/soak $E1/pooled
LOG=$E1/e1_chain.log; echo "chain2 start $(date) load=$(cut -d' ' -f1-3 /proc/loadavg)" >> $LOG; CORE=2; CORE2=4
stamp() { echo "$1 t=$(date +%s) load=$(cut -d' ' -f1-3 /proc/loadavg) steal=$(awk '/^cpu /{print $9}' /proc/stat) MHz=$(($(cat /sys/devices/system/cpu/cpu$CORE/cpufreq/scaling_cur_freq)/1000))"; }
for k in 1 2 3 4 5; do
  D=$E1/run$k; mkdir -p $D
  if [ ! -s $D/lat_motion.npz ]; then
    { stamp BEFORE; taskset -c $CORE $PYA $REPO/exp/rt/measure_motion.py 1; echo "exit=$?"; stamp AFTER; } > $D/measure_motion.log 2>&1
    mv $SS_ROOT/results/rt/lat_motion.npz $D/lat_motion.npz
  fi
  { stamp BEFORE; $PYD $REPO/exp/rt/e1_profile.py --out $D --core $CORE --core2 $CORE2; echo "exit=$?"; stamp AFTER; } > $D/e1_profile.log 2>&1
  echo "run$k done $(date)" >> $LOG
done
$PYA - <<PYEOF >> $LOG 2>&1
import numpy as np
E1 = '$E1'; runs = [f'{E1}/run{k}' for k in range(1, 6)]
for fn in ['lat_det.npz', 'lat_motion.npz']:
    Z = [np.load(f'{r}/{fn}') for r in runs]; out = {}
    for key in Z[0].files:
        if key.startswith('score'): out[key] = Z[0][key]; continue
        out[key] = np.max(np.stack([z[key] for z in Z]), axis=0)
    np.savez(f'{E1}/pooled/{fn}', **out); print('pooled', fn, len(out))
PYEOF
for k in run0 run1 run2 run3 run4 run5 pooled; do
  RT=$SP/aroot_$k; rm -rf $RT; mkdir -p $RT/results/rt; ln -sfn $REPO/exp $RT/exp; ln -sfn $REPO/data $RT/data
  ln -sfn $SS_ROOT/results/motion_scores $RT/results/motion_scores; ln -sfn $SS_ROOT/results/det_scores $RT/results/det_scores; cp $SS_ROOT/results/event_thresholds.json $RT/results/
  cp $E1/$k/lat_det.npz $RT/results/rt/; if [ -s $E1/$k/lat_motion.npz ]; then cp $E1/$k/lat_motion.npz $RT/results/rt/; else cp $E1/run1/lat_motion.npz $RT/results/rt/; echo "$k: lat_motion.npz taken from run1" >> $LOG; fi
  ( SS_ROOT=$RT $PYA $REPO/exp/rt/analyze.py > $E1/$k/analyze.log 2>&1; echo "analyze $k exit=$? $(date)" >> $LOG; cp $RT/results/rt/analysis.json $E1/$k/analysis.json ) &
done
wait
cp $E1/pooled/lat_det.npz $E1/pooled/lat_motion.npz $E1/pooled/analysis.json $SS_ROOT/results/rt/
$PYA $REPO/exp/rt/analyze2.py > $SS_ROOT/results/rt/analyze2.log 2>&1; echo "analyze2 exit=$? $(date)" >> $LOG
for S in 640 320; do for M in b2b paced; do
  echo "soak $S $M start $(date) load=$(cut -d' ' -f1-3 /proc/loadavg)" >> $LOG
  $PYD $REPO/exp/rt/e1_soak.py --mode $M --imgsz $S --minutes 20 --core 2 --out $E1/soak/soak_${S}_${M}.npz > $E1/soak/soak_${S}_${M}.log 2>&1; echo "soak $S $M exit=$? $(date)" >> $LOG
done; done
$PYA $REPO/exp/rt/e1_analyze.py $E1 >> $LOG 2>&1
echo "PHASE 1 CHAIN DONE $(date)" >> $LOG
