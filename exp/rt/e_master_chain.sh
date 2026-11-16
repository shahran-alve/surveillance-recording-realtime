#!/bin/bash
# Remaining stages after Phase 1, unattended: wait for the running E2 640-px pipeline -> E3 recorder (two pin configs) -> E2 320 px ->
# e2_analyze (640, 320), e3_verify -> summary tables. Everything sequential on the pinned core(s), as in the earlier stages.
set -u
REPO=$(cd "$(dirname "$0")/../.." && pwd); export SS_ROOT=$REPO/results/rt_ciscluster/root CUDA_VISIBLE_DEVICES=""
SP=/tmp/claude-8800/-u-erdos-csga2-mmahmud9-smart-surveillance-realtime/68d9c066-41df-481b-ac8a-d697ba6c7735/scratchpad
PYA=$SP/venv-analysis/bin/python; OUT=$REPO/results/rt_ciscluster; LOG=$OUT/logs/master_chain.log
echo "master chain start $(date)" >> $LOG
while pgrep -f "exp/rt/e2_run.sh 640" > /dev/null; do sleep 30; done; echo "E2 640 finished $(date) load=$(cut -d' ' -f1-3 /proc/loadavg)" >> $LOG
$PYA $REPO/exp/rt/e2_analyze.py $OUT/e2_640 640 > $OUT/e2_640/e2_analyze.log 2>&1; echo "e2_analyze 640 exit=$? $(date)" >> $LOG
sleep 30
$REPO/exp/rt/e3_run.sh >> $LOG 2>&1; echo "E3 finished $(date)" >> $LOG
$PYA $REPO/exp/rt/e3_verify.py $OUT/e3 $OUT/e1/e1_summary.json > $OUT/e3/e3_verify.log 2>&1; echo "e3_verify exit=$? $(date)" >> $LOG
sleep 30
$REPO/exp/rt/e2_run.sh 320 2 >> $LOG 2>&1; echo "E2 320 finished $(date)" >> $LOG
$PYA $REPO/exp/rt/e2_analyze.py $OUT/e2_320 320 > $OUT/e2_320/e2_analyze.log 2>&1; echo "e2_analyze 320 exit=$? $(date)" >> $LOG
$PYA $REPO/exp/rt/e_summary_tables.py $OUT $REPO/results/rt > $OUT/logs/summary_tables.md 2> $OUT/logs/summary_tables.err; echo "tables exit=$? $(date)" >> $LOG
echo "MASTER CHAIN DONE $(date)" >> $LOG
