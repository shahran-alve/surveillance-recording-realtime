#!/bin/bash
# Section 8 chain: wait for the E2 extension -> e1b_run.sh (five warm-up/rotated profiling runs) -> e8_analyze.py
REPO=$(cd "$(dirname "$0")/../.." && pwd); export SS_ROOT=$REPO/results/rt_ciscluster/root CUDA_VISIBLE_DEVICES=""
SP=/tmp/claude-8800/-u-erdos-csga2-mmahmud9-smart-surveillance-realtime/68d9c066-41df-481b-ac8a-d697ba6c7735/scratchpad; OUT=$REPO/results/rt_ciscluster; LOG=$OUT/logs/e8_chain.log
echo "e8 chain start $(date)" >> $LOG
until grep -q "E2 EXT DONE" $OUT/e2_320/e2_ext_run.log 2>/dev/null; do sleep 30; done; echo "E2 ext finished $(date)" >> $LOG; sleep 30
$REPO/exp/rt/e1b_run.sh; echo "e1b finished $(date)" >> $LOG
$SP/venv-analysis/bin/python $REPO/exp/rt/e8_analyze.py $OUT > $OUT/logs/e8_analyze.log 2>&1; echo "e8_analyze exit=$? $(date)" >> $LOG
echo "E8 CHAIN DONE $(date)" >> $LOG
