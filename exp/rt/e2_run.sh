#!/bin/bash
# E2 orchestration. N* per policy = simulated max cameras (analysis.json 'cameras', pooled Phase-1 traces, this machine).
# Runs live2.py at N*-2, N*-1, N*, N*+1 for 600 s, 2 repeats, fresh process per run, pinned to one core; then the single-camera pass.
# Usage: e2_run.sh IMGSZ [CORE]     (IMGSZ 640 or 320)
set -u
REPO=$(cd "$(dirname "$0")/../.." && pwd); export SS_ROOT=$REPO/results/rt_ciscluster/root CUDA_VISIBLE_DEVICES=""
SP=/tmp/claude-8800/-u-erdos-csga2-mmahmud9-smart-surveillance-realtime/68d9c066-41df-481b-ac8a-d697ba6c7735/scratchpad; PYD=$SP/venv-detector/bin/python
IMGSZ=${1:-640}; CORE=${2:-2}; E2=$REPO/results/rt_ciscluster/e2_$IMGSZ; mkdir -p $E2
LNAME="$IMGSZ px, 1 thread"
for P in "Fixed stride 8" "Adaptive 16/8" "Adaptive, deadline-aware"; do
  NSTAR=$($PYD -c "import json,sys; A=json.load(open('$SS_ROOT/results/rt/analysis.json')); print(A['cameras']['$P|$LNAME']['nmax'])")
  echo "policy=$P N*=$NSTAR" | tee -a $E2/nstar.txt
  for REP in 1 2; do for N in $((NSTAR-2)) $((NSTAR-1)) $NSTAR $((NSTAR+1)); do
    [ $N -lt 1 ] && continue
    TAG="$(echo $P | tr -d ' ,/')_N${N}_rep${REP}"; [ -s $E2/live_$TAG.json ] && continue
    echo "START $TAG $(date) load=$(cut -d' ' -f1-3 /proc/loadavg)" >> $E2/e2_run.log
    $PYD $REPO/exp/rt/live2.py --policy "$P" --N $N --horizon 600 --imgsz $IMGSZ --threads 1 --core $CORE --out $E2/live_$TAG.json --tag $TAG > $E2/live_$TAG.log 2>&1
    echo "END $TAG exit=$? $(date) $(grep '^multi' $E2/live_$TAG.log | cut -c1-200)" >> $E2/e2_run.log
  done; done
done
# single-camera pass, every clip once, three policies
if [ ! -s $E2/live_single.json ]; then
  echo "START single $(date) load=$(cut -d' ' -f1-3 /proc/loadavg)" >> $E2/e2_run.log
  $PYD $REPO/exp/rt/live2.py --single --imgsz $IMGSZ --threads 1 --core $CORE --out $E2/live_single.json --tag single > $E2/live_single.log 2>&1
  echo "END single exit=$? $(date)" >> $E2/e2_run.log
fi
echo "E2 $IMGSZ DONE $(date)" >> $E2/e2_run.log
