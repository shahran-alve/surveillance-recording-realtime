#!/bin/bash
REPO=$(cd "$(dirname "$0")/../.." && pwd); export SS_ROOT=$REPO/results/rt_ciscluster/root CUDA_VISIBLE_DEVICES=""
SP=/tmp/claude-8800/-u-erdos-csga2-mmahmud9-smart-surveillance-realtime/68d9c066-41df-481b-ac8a-d697ba6c7735/scratchpad; OUT=$REPO/results/rt_ciscluster
until grep -q "E9 DONE" $OUT/e9/e9_run.log 2>/dev/null; do sleep 60; done
$SP/venv-analysis/bin/python $REPO/exp/rt/e9_analyze.py $OUT > $OUT/logs/e9_analyze.log 2>&1 && $SP/venv-analysis/bin/python $REPO/exp/rt/e9_write.py $OUT >> $OUT/logs/e9_analyze.log 2>&1; echo "E9 SUMMARY exit=$? $(date)" >> $OUT/e9/e9_run.log
