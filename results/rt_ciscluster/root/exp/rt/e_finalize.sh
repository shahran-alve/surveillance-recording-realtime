#!/bin/bash
# Waits for the master chain, then writes SUMMARY.md automatically (so the deliverable exists even if the interactive session is gone).
REPO=$(cd "$(dirname "$0")/../.." && pwd); export SS_ROOT=$REPO/results/rt_ciscluster/root CUDA_VISIBLE_DEVICES=""
SP=/tmp/claude-8800/-u-erdos-csga2-mmahmud9-smart-surveillance-realtime/68d9c066-41df-481b-ac8a-d697ba6c7735/scratchpad; OUT=$REPO/results/rt_ciscluster
until grep -q "MASTER CHAIN DONE" $OUT/logs/master_chain.log 2>/dev/null; do sleep 60; done
$SP/venv-analysis/bin/python $REPO/exp/rt/e_write_summary.py $OUT $REPO/results/rt > $OUT/logs/write_summary.log 2>&1; echo "SUMMARY written exit=$? $(date)" >> $OUT/logs/master_chain.log
