#!/bin/bash
# E1 extension (section 8B): five fresh e1_profile2.py processes, 640/1 only, 120-s discarded warm-up, clip order rotated by run index.
set -u
REPO=$(cd "$(dirname "$0")/../.." && pwd); export SS_ROOT=$REPO/results/rt_ciscluster/root CUDA_VISIBLE_DEVICES=""
SP=/tmp/claude-8800/-u-erdos-csga2-mmahmud9-smart-surveillance-realtime/68d9c066-41df-481b-ac8a-d697ba6c7735/scratchpad; PYD=$SP/venv-detector/bin/python
E1B=$REPO/results/rt_ciscluster/e1b; mkdir -p $E1B; LOG=$E1B/e1b_run.log; CORE=2
stamp() { echo "$1 t=$(date +%s) load=$(cut -d' ' -f1-3 /proc/loadavg) steal=$(awk '/^cpu /{print $9}' /proc/stat)"; }
for k in 1 2 3 4 5; do
  D=$E1B/run$k; mkdir -p $D; [ -s $D/meta_det.json ] && continue
  { stamp BEFORE; $PYD $REPO/exp/rt/e1_profile2.py --out $D --core $CORE --warmup 120 --rotate $((k-1)); echo "exit=$?"; stamp AFTER; } > $D/e1_profile2.log 2>&1
  echo "run$k done $(date)" >> $LOG
done
echo "E1B DONE $(date)" >> $LOG
