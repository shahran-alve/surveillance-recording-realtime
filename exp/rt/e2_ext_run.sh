#!/bin/bash
# E2 extension (section 8A): live2.py, 320 px, "Adaptive, deadline-aware", N = 38, 39, 40, 600 s, 2 repeats, core 2. New files only.
set -u
REPO=$(cd "$(dirname "$0")/../.." && pwd); export SS_ROOT=$REPO/results/rt_ciscluster/root CUDA_VISIBLE_DEVICES=""
SP=/tmp/claude-8800/-u-erdos-csga2-mmahmud9-smart-surveillance-realtime/68d9c066-41df-481b-ac8a-d697ba6c7735/scratchpad; PYD=$SP/venv-detector/bin/python
E2=$REPO/results/rt_ciscluster/e2_320; P="Adaptive, deadline-aware"; LOG=$E2/e2_ext_run.log
for REP in 1 2; do for N in 38 39 40; do
  TAG="$(echo $P | tr -d ' ,/')_N${N}_rep${REP}"; [ -s $E2/live_$TAG.json ] && { echo "exists $TAG" >> $LOG; continue; }
  echo "START $TAG $(date) load=$(cut -d' ' -f1-3 /proc/loadavg)" >> $LOG
  $PYD $REPO/exp/rt/live2.py --policy "$P" --N $N --horizon 600 --imgsz 320 --threads 1 --core 2 --out $E2/live_$TAG.json --tag $TAG > $E2/live_$TAG.log 2>&1
  echo "END $TAG exit=$? $(date) $(grep '^multi' $E2/live_$TAG.log | cut -c1-200)" >> $LOG
done; done
echo "E2 EXT DONE $(date)" >> $LOG
