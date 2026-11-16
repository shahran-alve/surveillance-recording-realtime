#!/bin/bash
# Section 9 node test: after the post-hoc runs, one default e1_profile2.py process pinned to core 3 (NUMA node 1, free 2-MB blocks available)
# and one pinned to core 2 (node 0, no free 2-MB blocks), both with the new per-configuration smaps (AnonHugePages) record.
REPO=$(cd "$(dirname "$0")/../.." && pwd); export SS_ROOT=$REPO/results/rt_ciscluster/root CUDA_VISIBLE_DEVICES=""
SP=/tmp/claude-8800/-u-erdos-csga2-mmahmud9-smart-surveillance-realtime/68d9c066-41df-481b-ac8a-d697ba6c7735/scratchpad; PYD=$SP/venv-detector/bin/python
E9=$REPO/results/rt_ciscluster/e9; LOG=$E9/e9_run.log
until grep -q "E9 POSTHOC DONE" $LOG; do sleep 20; done; sleep 20
for T in "node1 3" "node0 2"; do set -- $T; D=$E9/default/run7_$1_core$2; mkdir -p $D
  echo "START default $1 core$2 $(date) load=$(cut -d' ' -f1-3 /proc/loadavg)" >> $LOG; cat /proc/buddyinfo > $D/buddyinfo_before.txt
  { $PYD $REPO/exp/rt/e1_profile2.py --out $D --core $2 --warmup 120 --rotate 0; echo "exit=$?"; } > $D/e1_profile2.log 2>&1
  cat /proc/buddyinfo > $D/buddyinfo_after.txt; echo "END default $1 core$2 $(date)" >> $LOG
done
echo "E9 NODE TEST DONE $(date)" >> $LOG
