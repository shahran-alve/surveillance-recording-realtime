#!/bin/bash
# Section 9: e1_profile2.py (640/1, 120-s warm-up, clip order rotated by run index) under three conditions, five fresh processes each,
# interleaved a,b,c,a,b,c,...:  a = default; b = MALLOC_TRIM_THRESHOLD_=4294967296 MALLOC_MMAP_THRESHOLD_=4294967296; c = prctl(PR_SET_THP_DISABLE).
set -u
REPO=$(cd "$(dirname "$0")/../.." && pwd); export SS_ROOT=$REPO/results/rt_ciscluster/root CUDA_VISIBLE_DEVICES=""
SP=/tmp/claude-8800/-u-erdos-csga2-mmahmud9-smart-surveillance-realtime/68d9c066-41df-481b-ac8a-d697ba6c7735/scratchpad; PYD=$SP/venv-detector/bin/python
E9=$REPO/results/rt_ciscluster/e9; mkdir -p $E9; LOG=$E9/e9_run.log; CORE=2
stamp() { echo "$1 t=$(date +%s) load=$(cut -d' ' -f1-3 /proc/loadavg) steal=$(awk '/^cpu /{print $9}' /proc/stat)"; }
for k in 1 2 3 4 5; do for C in default malloc thp; do
  D=$E9/$C/run$k; mkdir -p $D; [ -s $D/meta_det.json ] && continue
  case $C in
    default) ENV=""; EXTRA="";;
    malloc)  ENV="MALLOC_TRIM_THRESHOLD_=4294967296 MALLOC_MMAP_THRESHOLD_=4294967296"; EXTRA="";;
    thp)     ENV=""; EXTRA="--thp-disable";;
  esac
  echo "START $C run$k $(date) load=$(cut -d' ' -f1-3 /proc/loadavg)" >> $LOG
  { stamp BEFORE; env $ENV $PYD $REPO/exp/rt/e1_profile2.py --out $D --core $CORE --warmup 120 --rotate $((k-1)) $EXTRA; echo "exit=$?"; stamp AFTER; } > $D/e1_profile2.log 2>&1
  echo "END $C run$k exit=$(grep -c '^DONE' $D/e1_profile2.log) $(date)" >> $LOG
done; done
echo "E9 DONE $(date)" >> $LOG
