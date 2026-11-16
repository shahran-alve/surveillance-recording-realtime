#!/bin/bash
# Phase 1 pipeline: wait for score generation -> e1_run.sh (run0 + runs 1-5) -> analyze.py per run and pooled (parallel, separate
# staging roots) -> pooled traces + analysis.json installed in SS_ROOT/results/rt -> analyze2.py (hybrid part) -> soak tests.
set -u
REPO=$(cd "$(dirname "$0")/../.." && pwd); export SS_ROOT=$REPO/results/rt_ciscluster/root CUDA_VISIBLE_DEVICES=""
SP=/tmp/claude-8800/-u-erdos-csga2-mmahmud9-smart-surveillance-realtime/68d9c066-41df-481b-ac8a-d697ba6c7735/scratchpad
PYA=$SP/venv-analysis/bin/python; PYD=$SP/venv-detector/bin/python; E1=$REPO/results/rt_ciscluster/e1; mkdir -p $E1 $E1/soak $E1/pooled
LOG=$E1/e1_chain.log; echo "chain start $(date)" >> $LOG
while pgrep -f "exp/motion_scores.py" > /dev/null; do sleep 20; done
sleep 60; echo "scores done, load=$(cut -d' ' -f1-3 /proc/loadavg) $(date)" >> $LOG
# ---- profiling
$REPO/exp/rt/e1_run.sh >> $LOG 2>&1
# ---- pooled traces (element-wise max over runs 1-5)
$PYA - <<PYEOF >> $LOG 2>&1
import numpy as np, glob, os
E1 = '$E1'; runs = [f'{E1}/run{k}' for k in range(1, 6)]
for fn in ['lat_det.npz', 'lat_motion.npz']:
    Z = [np.load(f'{r}/{fn}') for r in runs]; out = {}
    for key in Z[0].files:
        if key.startswith('score'): out[key] = Z[0][key]; continue
        out[key] = np.max(np.stack([z[key] for z in Z]), axis=0)
    np.savez(f'{E1}/pooled/{fn}', **out); print('pooled', fn, len(out))
PYEOF
# ---- analyze.py per run and pooled, in parallel with separate staging roots
for k in run0 run1 run2 run3 run4 run5 pooled; do
  RT=$SP/aroot_$k; rm -rf $RT; mkdir -p $RT/results/rt; ln -sfn $REPO/exp $RT/exp; ln -sfn $REPO/data $RT/data
  ln -sfn $SS_ROOT/results/motion_scores $RT/results/motion_scores; ln -sfn $SS_ROOT/results/det_scores $RT/results/det_scores; cp $SS_ROOT/results/event_thresholds.json $RT/results/
  cp $E1/$k/lat_det.npz $RT/results/rt/; if [ -s $E1/$k/lat_motion.npz ]; then cp $E1/$k/lat_motion.npz $RT/results/rt/; else cp $E1/run1/lat_motion.npz $RT/results/rt/; echo "$k: lat_motion.npz taken from run1" >> $LOG; fi
  ( SS_ROOT=$RT $PYA $REPO/exp/rt/analyze.py > $E1/$k/analyze.log 2>&1; cp $RT/results/rt/analysis.json $E1/$k/analysis.json; echo "analyze $k exit=$? $(date)" >> $LOG ) &
done
wait
# ---- install pooled traces + analysis as the machine's results/rt (used by live2.py, recorder.py, analyze2.py)
cp $E1/pooled/lat_det.npz $E1/pooled/lat_motion.npz $E1/pooled/analysis.json $SS_ROOT/results/rt/
$PYA $REPO/exp/rt/analyze2.py > $SS_ROOT/results/rt/analyze2.log 2>&1; echo "analyze2 exit=$? $(date)" >> $LOG
# ---- soak tests, pinned to core 2
for S in 640 320; do for M in b2b paced; do
  echo "soak $S $M start $(date) load=$(cut -d' ' -f1-3 /proc/loadavg)" >> $LOG
  $PYD $REPO/exp/rt/e1_soak.py --mode $M --imgsz $S --minutes 20 --core 2 --out $E1/soak/soak_${S}_${M}.npz > $E1/soak/soak_${S}_${M}.log 2>&1; echo "soak $S $M exit=$? $(date)" >> $LOG
done; done
$PYA $REPO/exp/rt/e1_analyze.py $E1 >> $LOG 2>&1
echo "PHASE 1 CHAIN DONE $(date)" >> $LOG
