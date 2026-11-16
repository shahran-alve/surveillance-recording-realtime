#!/bin/bash
# E3 orchestration: recorder.py for the three policies on all seven clips, once pinned to one core and once to two cores.
# R_max = pooled C_max (640 px, 1 thread) of Phase 1 = largest service time over ALL timed frames of runs 1-5 (incl. the first 10 frames of
# each clip, which analyze.py's latency table excludes), read from e1/e1_summary.json ('max_all_frames'). Video segments go to local disk (VIDDIR).
set -u
REPO=$(cd "$(dirname "$0")/../.." && pwd); export SS_ROOT=$REPO/results/rt_ciscluster/root CUDA_VISIBLE_DEVICES=""
SP=/tmp/claude-8800/-u-erdos-csga2-mmahmud9-smart-surveillance-realtime/68d9c066-41df-481b-ac8a-d697ba6c7735/scratchpad; PYD=$SP/venv-detector/bin/python
E3=$REPO/results/rt_ciscluster/e3; mkdir -p $E3; VIDDIR=${VIDDIR:-$SP/e3_video}
RMAX=$($PYD -c "import json; print(json.load(open('$REPO/results/rt_ciscluster/e1/e1_summary.json'))['pooled']['all']['Detector 640 px']['max_all_frames']/1e3)")
echo "R_max (s) = $RMAX" | tee $E3/rmax.txt
for CORES in 2 2,4; do for P in "Fixed stride 8" "Adaptive 16/8" "Adaptive, deadline-aware"; do
  TAG="$(echo $P | tr -d ' ,/')_cores$(echo $CORES | tr ',' '-')"
  echo "START $TAG $(date) load=$(cut -d' ' -f1-3 /proc/loadavg)" >> $E3/e3_run.log
  $PYD $REPO/exp/rt/recorder.py --policy "$P" --rmax $RMAX --cores $CORES --outdir $E3 --viddir $VIDDIR/$TAG > $E3/recorder_$TAG.log 2>&1
  echo "END $TAG exit=$? $(date)" >> $E3/e3_run.log
done; done
echo "E3 DONE $(date)" >> $E3/e3_run.log
