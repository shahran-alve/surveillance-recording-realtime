#!/bin/bash
# E1 orchestration: run 0 = the unmodified measure_det.py (pinned to cores 2,4 with taskset; it also writes the 320/480-px
# score files that analyze.py needs); runs 1-5 = measure_motion.py (unmodified, taskset -c 2) + e1_profile.py (detector timing loop
# of measure_det.py with per-configuration affinity). Each script invocation is a fresh process. Steal time / frequency / load are
# logged before and after every invocation.
set -u
REPO=$(cd "$(dirname "$0")/../.." && pwd); export SS_ROOT=$REPO/results/rt_ciscluster/root CUDA_VISIBLE_DEVICES=""
SP=/tmp/claude-8800/-u-erdos-csga2-mmahmud9-smart-surveillance-realtime/68d9c066-41df-481b-ac8a-d697ba6c7735/scratchpad
PYA=$SP/venv-analysis/bin/python; PYD=$SP/venv-detector/bin/python
E1=$REPO/results/rt_ciscluster/e1; mkdir -p $E1; CORE=2; CORE2=4
stamp() { echo "$1 t=$(date +%s) load=$(cut -d' ' -f1-3 /proc/loadavg) steal=$(awk '/^cpu /{print $9}' /proc/stat) MHz=$(($(cat /sys/devices/system/cpu/cpu$CORE/cpufreq/scaling_cur_freq)/1000))"; }
# ---- run 0: original measure_det.py
mkdir -p $E1/run0; { stamp BEFORE; taskset -c $CORE,$CORE2 $PYD $REPO/exp/rt/measure_det.py; echo "exit=$?"; stamp AFTER; } > $E1/run0/measure_det.log 2>&1
mv $SS_ROOT/results/rt/lat_det.npz $E1/run0/lat_det.npz
# ---- runs 1-5
for k in 1 2 3 4 5; do
  D=$E1/run$k; mkdir -p $D
  { stamp BEFORE; taskset -c $CORE $PYA $REPO/exp/rt/measure_motion.py 1; echo "exit=$?"; stamp AFTER; } > $D/measure_motion.log 2>&1
  mv $SS_ROOT/results/rt/lat_motion.npz $D/lat_motion.npz
  { stamp BEFORE; $PYD $REPO/exp/rt/e1_profile.py --out $D --core $CORE --core2 $CORE2; echo "exit=$?"; stamp AFTER; } > $D/e1_profile.log 2>&1
done
echo E1 PROFILING DONE $(date)
