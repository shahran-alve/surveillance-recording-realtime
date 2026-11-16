#!/bin/bash
# Section 9 post-hoc: one more default and one more THP-disabled process after the foreign load (load average ~2 from 19:40 to 21:27) ended.
REPO=$(cd "$(dirname "$0")/../.." && pwd); export SS_ROOT=$REPO/results/rt_ciscluster/root CUDA_VISIBLE_DEVICES=""
SP=/tmp/claude-8800/-u-erdos-csga2-mmahmud9-smart-surveillance-realtime/68d9c066-41df-481b-ac8a-d697ba6c7735/scratchpad; PYD=$SP/venv-detector/bin/python
E9=$REPO/results/rt_ciscluster/e9; LOG=$E9/e9_run.log
for C in default thp; do
  D=$E9/$C/run6; mkdir -p $D; EXTRA=""; [ $C = thp ] && EXTRA="--thp-disable"
  echo "START $C run6 (post-hoc) $(date) load=$(cut -d' ' -f1-3 /proc/loadavg)" >> $LOG
  { echo "load=$(cut -d' ' -f1-3 /proc/loadavg)"; $PYD $REPO/exp/rt/e1_profile2.py --out $D --core 2 --warmup 120 --rotate 5 $EXTRA; echo "exit=$?"; echo "load=$(cut -d' ' -f1-3 /proc/loadavg)"; } > $D/e1_profile2.log 2>&1
  echo "END $C run6 $(date) load=$(cut -d' ' -f1-3 /proc/loadavg)" >> $LOG
done
echo "E9 POSTHOC DONE $(date)" >> $LOG
