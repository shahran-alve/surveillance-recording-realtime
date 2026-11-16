# Re-run of the real-time experiments on ciscluster (E1 repeated profiling, E2 live multi-camera, E3 end-to-end recorder)

Generated 2026-11-13 15:48 EST by exp/rt/e_write_summary.py from the raw files listed in section 7. Original results (2-core VM) in results/rt/ were not modified; everything new is under results/rt_ciscluster/.


## Key findings

- E1: the 358.7 ms outlier of the VM is not reproducible here. Over 6 profiling runs and 4 soak tests (about 232,000 inferences) no detector service time exceeded 150 ms; C_max at 640 px / 1 thread is 81.5 ms (frames 11+ of each clip, paper convention) or 113.2 ms including the reproducible first inference on a new clip. k_min = 1 / 3 at 12 / 30 fps in every run (paper: 5 / 11). All quantities that depend only on scores and thresholds (theta = 0.2, 15 onsets, onset stored 100/73/100 %, detector runs 12.6/10.2/11.2 %, single-camera jobs 729/589/644) reproduce exactly; the scores themselves are bit-identical to the original arrays.
- E2 (640 px): largest N with zero misses in both 600-s repeats, live vs simulated: Fixed stride 8 11 vs 12; Adaptive 16/8 14 vs 14; Adaptive, deadline-aware 12 vs 14. Live decisions equal the offline trace on 100 % of jobs in every run. Live misses at or above N* occur in bursts (one to three 60-s windows per run, see section 4), not at process start.
- E2 (320 px): Fixed stride 8 36 vs 37; Adaptive 16/8 44 vs 45; Adaptive, deadline-aware 0 vs 43 (the deadline-aware policy had 4-17 misses out of about 31,000 jobs already at N = 41-42, so no tested N was clean in both repeats).
- E3: in all six recorder passes (3 policies x 1 or 2 cores) the written frame indices equal event_eval.record() applied to the recorder's own decisions (0 differing frames out of 27,246 written), 0 frames were lost from the ring buffer, every measured alert delay is within the bound (k_idle-1)T + R_max (all 15 onsets per pass), the onset frame itself was written for 15/15 (fixed 8, deadline-aware) and 11/15 (adaptive 16/8) onsets as in the paper, no captured frame was later than one frame period, and sharing one core with decode and write raised the detector's mean service time by about 3 ms and its maximum from 72-75 ms to 89-104 ms.


## 1. Platform and idle-machine caveat

From platform.txt (full lscpu there):

```
hostname: ciscluster
uname: Linux ciscluster 4.18.0-553.123.1.el8_10.x86_64 #1 SMP Tue May 5 15:46:59 UTC 2026 x86_64 x86_64 x86_64 GNU/Linux
virt (systemd-detect-virt): none
DMI: Dell Inc. PowerEdge R740xd
OS: PRETTY_NAME="Rocky Linux 8.10 (Green Obsidian)"
CPU(s):              24
Thread(s) per core:  1
Core(s) per socket:  12
Socket(s):           2
NUMA node(s):        2
Model name:          Intel(R) Xeon(R) Gold 6126 CPU @ 2.60GHz
CPU max MHz:         3700.0000
CPU min MHz:         1000.0000
L3 cache:            19712K
NUMA node0 CPU(s):   0,2,4,6,8,10,12,14,16,18,20,22
NUMA node1 CPU(s):   1,3,5,7,9,11,13,15,17,19,21,23
governor:      24 performance
scaling min/max kHz cpu2: 1000000 3700000; driver: intel_cpufreq
turbo: no_turbo=0
Mem:            187           6           5           0         174         179
loadavg at setup: 1.31 0.69 0.44 2/1811 3438489
steal column (/proc/stat cpu, 8th field): 0
slurm: head node of a cluster (squeue/sinfo present); other users may log in
python venvs: python3.11 (Python 3.11.7), see logs/pip_freeze_*.txt
```

- Bare metal (systemd-detect-virt: none), Dell PowerEdge R740xd, 2 x Intel Xeon Gold 6126 (12 cores each, no SMT, 24 CPUs), 187 GB RAM, Rocky Linux 8.10, kernel 4.18.0-553.123.1, governor `performance` (intel_cpufreq passive driver, turbo enabled, 1.0-3.7 GHz), NUMA balancing on, transparent hugepages `always`.
- The machine is the shared Slurm head node of a cluster. Nobody else used CPU during the runs (checked with top before every stage), but other users had idle login sessions. The load average at the Phase 0 check was 0.40 (above the 0.3 criterion of the brief) and 0.13 one minute later; the 1-minute load before every timed run is logged (e1/run*/e1_profile.log BEFORE/AFTER lines, e2_*/e2_run.log, e3/e3_run.log, *_meta.json). During the timed runs the load was 1.0-1.3, i.e. our own pinned process plus the VS Code server of this session (about 1-2 % of one CPU).
- All timed processes were pinned with sched_setaffinity to physical core 2 (NUMA node 0); the 2-thread configuration to cores 2 and 4. /proc/stat steal time was 0 throughout (bare metal). MSR access (turbostat) is not permitted; the sysfs `scaling_cur_freq` readings taken between configurations are unreliable with this passive driver (1.1-3.7 GHz while /proc/cpuinfo showed 3.5-3.7 GHz when sampled during a run), so no frequency claim is made beyond "performance governor, turbo on".
- Python 3.11.7 virtualenvs built from requirements-analysis.txt (opencv-contrib-python-headless 4.10.0.84, numpy 2.x) and requirements-detector.txt (torch 2.14.1+cpu, torchvision 0.29.1+cpu, ultralytics 8.4.190, onnxruntime 1.31.1, opencv-python 5.0.0 as the unpinned latest); CUDA_VISIBLE_DEVICES="" and no GPU present; pip freeze in logs/pip_freeze_*.txt. Frames decoded by the two OpenCV versions are byte-identical (sha256 check, logs/).


## 2. Phase 0 checks

Frame counts (logs/frame_counts.txt):

```
opencv 4.10.0
one-by-one        fps=10.000 video_info_n=1394 decoded=1394 expected=1394 shape=(432, 768, 3) OK
people            fps=12.000 video_info_n=596 decoded=596 expected=596 shape=(432, 768, 3) OK
person-bike-car   fps=12.000 video_info_n=647 decoded=647 expected=647 shape=(432, 768, 3) OK
walk-and-pause    fps=12.000 video_info_n=1091 decoded=1091 expected=1091 shape=(432, 768, 3) OK
worker-zone       fps=11.988 video_info_n=910 decoded=910 expected=910 shape=(432, 768, 3) OK
car-lot           fps=12.500 video_info_n=377 decoded=377 expected=377 shape=(432, 768, 3) OK
store-aisle       fps=11.988 video_info_n=785 decoded=785 expected=785 shape=(431, 768, 3) OK
total 5800 expected 5800
```

Clean 640-px YOLO11n scores regenerated here (det_scores.py, 1 thread) vs. the arrays `score|640|1|<clip>` in results/rt/lat_det.npz:

| clip | n | max abs diff | decisions at 0.2 agree |
|---|---|---|---|
| one-by-one | 1394 | 0.00e+00 | yes |
| people | 596 | 0.00e+00 | yes |
| person-bike-car | 647 | 0.00e+00 | yes |
| walk-and-pause | 1091 | 0.00e+00 | yes |
| worker-zone | 910 | 0.00e+00 | yes |
| car-lot | 377 | 0.00e+00 | yes |
| store-aisle | 785 | 0.00e+00 | yes |

The scores are bit-identical to the original run (max abs difference 0.0 on every clip), so every quantity that depends only on scores and thresholds is expected to reproduce exactly. (Side check in logs/score_check.txt: scores computed with 8 torch threads differ from 1-thread scores by up to 3e-6 and never change a decision.)

Thresholds re-derived by analyze.py (leave-one-video-out, fixed stride 8): theta = 0.2 for every clip, identical to the paper; theta_lowres identical as well (e1/pooled/analysis.json).


## 3. E1: repeated service-time profiling

Runs: run0 = the unmodified measure_det.py (process pinned with `taskset -c 2,4`, i.e. a two-core mask for all configurations; it also produced the 320/480-px score files analyze.py needs). Runs 1-5 = fresh processes of measure_motion.py (unmodified, `taskset -c 2`) and e1_profile.py (the timing loop of measure_det.py copied verbatim, with the affinity switched per configuration: {2} for 1 thread, {2,4} for 2 threads, applied to every thread of the process). Steal time and frequency were recorded before/after every configuration (e1/run*/meta_det.json). Configurations: 640/1, 640/2, 480/1, 320/1 in the original order, 5,800 frames each.

### E1.1 Detector service time per run (ms; frames 11+ of every clip, 5,730 samples per run and configuration)

| run | cfg | mean | p50 | p95 | p99 | p99.9 | max (frames 11+) | max (all frames, clip:frame) | n > 150 ms | n > 120 ms |
|---|---|---|---|---|---|---|---|---|---|---|
| run0 | 640/1 | 50.7 | 48.7 | 57.3 | 59.8 | 67.2 | 74.2 | 106.0 (store-aisle:0) | 0 | 0 |
| run0 | 640/2 | 35.5 | 33.9 | 41.3 | 43.5 | 48.1 | 53.6 | 53.6 (one-by-one:102) | 0 | 0 |
| run0 | 480/1 | 30.1 | 30.0 | 32.4 | 34.4 | 38.6 | 41.1 | 41.1 (one-by-one:850) | 0 | 0 |
| run0 | 320/1 | 17.3 | 17.0 | 19.4 | 20.6 | 24.1 | 26.6 | 26.6 (walk-and-pause:481) | 0 | 0 |
| run1 | 640/1 | 51.2 | 48.2 | 59.5 | 68.3 | 70.1 | 78.2 | 103.9 (store-aisle:0) | 0 | 0 |
| run1 | 640/2 | 34.7 | 33.5 | 40.7 | 41.5 | 44.3 | 61.4 | 61.4 (people:461) | 0 | 0 |
| run1 | 480/1 | 29.9 | 29.5 | 33.3 | 36.3 | 38.6 | 43.6 | 43.6 (store-aisle:617) | 0 | 0 |
| run1 | 320/1 | 17.2 | 17.0 | 18.1 | 21.0 | 24.7 | 27.3 | 27.3 (one-by-one:1152) | 0 | 0 |
| run2 | 640/1 | 52.1 | 48.6 | 60.9 | 62.5 | 70.2 | 77.1 | 101.5 (store-aisle:0) | 0 | 0 |
| run2 | 640/2 | 35.2 | 33.5 | 41.7 | 46.8 | 48.3 | 79.4 | 79.4 (walk-and-pause:562) | 0 | 0 |
| run2 | 480/1 | 30.7 | 29.8 | 34.1 | 36.1 | 40.9 | 45.1 | 45.1 (store-aisle:613) | 0 | 0 |
| run2 | 320/1 | 17.5 | 17.2 | 20.5 | 21.2 | 23.0 | 26.9 | 26.9 (walk-and-pause:741) | 0 | 0 |
| run3 | 640/1 | 51.0 | 48.0 | 58.6 | 61.6 | 69.1 | 72.5 | 103.9 (store-aisle:0) | 0 | 0 |
| run3 | 640/2 | 34.2 | 33.4 | 39.1 | 41.2 | 46.3 | 56.7 | 56.7 (car-lot:235) | 0 | 0 |
| run3 | 480/1 | 30.0 | 29.4 | 35.2 | 35.8 | 37.9 | 42.5 | 42.5 (walk-and-pause:655) | 0 | 0 |
| run3 | 320/1 | 16.9 | 16.8 | 17.6 | 20.0 | 23.7 | 26.0 | 26.0 (store-aisle:349) | 0 | 0 |
| run4 | 640/1 | 51.1 | 48.2 | 58.7 | 64.6 | 68.2 | 80.3 | 105.1 (store-aisle:0) | 0 | 0 |
| run4 | 640/2 | 34.6 | 33.5 | 38.9 | 40.7 | 43.9 | 53.3 | 53.3 (one-by-one:599) | 0 | 0 |
| run4 | 480/1 | 29.9 | 29.3 | 32.7 | 36.2 | 39.9 | 43.9 | 43.9 (person-bike-car:150) | 0 | 0 |
| run4 | 320/1 | 16.9 | 16.8 | 17.4 | 19.4 | 23.8 | 26.2 | 26.2 (car-lot:139) | 0 | 0 |
| run5 | 640/1 | 52.3 | 48.5 | 60.8 | 70.0 | 71.9 | 81.5 | 113.2 (store-aisle:0) | 0 | 0 |
| run5 | 640/2 | 34.5 | 33.5 | 38.6 | 39.7 | 44.2 | 49.0 | 49.0 (one-by-one:942) | 0 | 0 |
| run5 | 480/1 | 30.5 | 30.0 | 32.9 | 34.1 | 39.6 | 44.3 | 44.3 (walk-and-pause:347) | 0 | 0 |
| run5 | 320/1 | 17.0 | 16.8 | 17.7 | 19.8 | 22.5 | 25.5 | 25.5 (walk-and-pause:591) | 0 | 0 |
| pooled 1-5 | 640/1 | 51.5 | 48.4 | 60.1 | 67.1 | 71.2 | 81.5 | 113.2 (store-aisle:0 (run5)) | 0 | 0 |
| pooled 1-5 | 640/2 | 34.7 | 33.5 | 40.2 | 43.2 | 47.1 | 79.4 | 79.4 (walk-and-pause:562 (run2)) | 0 | 0 |
| pooled 1-5 | 480/1 | 30.2 | 29.6 | 33.8 | 35.9 | 39.7 | 45.1 | 45.1 (store-aisle:613 (run2)) | 0 | 0 |
| pooled 1-5 | 320/1 | 17.1 | 16.9 | 18.0 | 21.0 | 23.5 | 27.3 | 27.3 (one-by-one:1152 (run1)) | 0 | 0 |

Service time of frame 0 of each clip at 640/1, runs 1-5 (ms): one-by-one: 58.2, 58.3, 56.8, 53.6, 57.3; people: 61.4, 58.5, 54.2, 58.0, 65.8; person-bike-car: 48.0, 48.0, 47.7, 47.4, 47.6; walk-and-pause: 47.2, 50.4, 47.7, 47.1, 47.1; worker-zone: 52.2, 47.9, 47.4, 48.2, 48.0; car-lot: 73.6, 71.9, 71.1, 73.1, 74.5; store-aisle: 103.9, 101.5, 103.9, 105.1, 113.2. These start-of-clip values are excluded from the distribution columns by the WARM=10 cut of analyze.py (as in the paper) but included in its timing bound (Rmax = lat[idx].max()) and camera simulation.


### E1.2 Five largest service times per run (ms, clip:frame)

| run | cfg | largest five |
|---|---|---|
| run0 | 640/1 | 74.2 (people:10), 73.7 (people:541), 70.0 (worker-zone:564), 69.6 (one-by-one:640), 68.3 (one-by-one:1366) |
| run0 | 640/2 | 53.6 (one-by-one:102), 50.8 (one-by-one:101), 49.4 (one-by-one:114), 49.2 (one-by-one:534), 48.7 (one-by-one:1292) |
| run0 | 480/1 | 41.1 (one-by-one:850), 40.2 (worker-zone:853), 39.4 (one-by-one:849), 39.3 (worker-zone:861), 39.0 (one-by-one:337) |
| run0 | 320/1 | 26.6 (walk-and-pause:481), 26.1 (worker-zone:259), 25.9 (store-aisle:399), 25.7 (store-aisle:401), 25.4 (store-aisle:400) |
| run1 | 640/1 | 78.2 (one-by-one:1260), 70.8 (one-by-one:649), 70.6 (one-by-one:602), 70.2 (one-by-one:591), 70.1 (one-by-one:622) |
| run1 | 640/2 | 61.4 (people:461), 46.0 (people:228), 45.2 (people:198), 44.8 (people:394), 44.7 (people:86) |
| run1 | 480/1 | 43.6 (store-aisle:617), 43.4 (store-aisle:618), 39.7 (one-by-one:899), 39.5 (one-by-one:1076), 39.1 (one-by-one:1075) |
| run1 | 320/1 | 27.3 (one-by-one:1152), 26.9 (one-by-one:1154), 26.7 (one-by-one:1153), 26.5 (one-by-one:1122), 24.9 (one-by-one:1121) |
| run2 | 640/1 | 77.1 (people:192), 74.7 (one-by-one:65), 74.6 (one-by-one:64), 73.1 (people:191), 71.8 (one-by-one:110) |
| run2 | 640/2 | 79.4 (walk-and-pause:562), 50.9 (people:234), 50.2 (people:233), 49.8 (one-by-one:1155), 49.6 (people:429) |
| run2 | 480/1 | 45.1 (store-aisle:613), 44.5 (store-aisle:614), 42.7 (worker-zone:470), 41.6 (worker-zone:549), 41.0 (store-aisle:527) |
| run2 | 320/1 | 26.9 (walk-and-pause:741), 25.4 (walk-and-pause:263), 24.3 (one-by-one:859), 24.0 (one-by-one:94), 23.0 (person-bike-car:259) |
| run3 | 640/1 | 72.5 (one-by-one:24), 72.5 (one-by-one:544), 70.3 (worker-zone:516), 70.0 (one-by-one:1031), 69.4 (people:119) |
| run3 | 640/2 | 56.7 (car-lot:235), 52.6 (car-lot:234), 51.4 (one-by-one:238), 48.5 (one-by-one:113), 47.3 (one-by-one:112) |
| run3 | 480/1 | 42.5 (walk-and-pause:655), 40.5 (walk-and-pause:762), 39.2 (walk-and-pause:656), 39.0 (one-by-one:719), 38.8 (walk-and-pause:564) |
| run3 | 320/1 | 26.0 (store-aisle:349), 25.9 (store-aisle:350), 25.5 (store-aisle:351), 24.7 (store-aisle:352), 24.1 (person-bike-car:377) |
| run4 | 640/1 | 80.3 (people:397), 76.9 (people:234), 75.8 (people:538), 72.2 (people:398), 69.4 (one-by-one:1076) |
| run4 | 640/2 | 53.3 (one-by-one:599), 49.6 (one-by-one:598), 46.5 (one-by-one:399), 45.3 (worker-zone:623), 44.3 (one-by-one:600) |
| run4 | 480/1 | 43.9 (person-bike-car:150), 43.6 (walk-and-pause:111), 43.0 (walk-and-pause:112), 41.3 (person-bike-car:149), 41.2 (person-bike-car:151) |
| run4 | 320/1 | 26.2 (car-lot:139), 25.8 (car-lot:138), 25.4 (people:180), 25.0 (car-lot:140), 24.1 (car-lot:137) |
| run5 | 640/1 | 81.5 (people:559), 80.3 (people:75), 73.7 (people:560), 72.1 (one-by-one:1334), 71.9 (one-by-one:1257) |
| run5 | 640/2 | 49.0 (one-by-one:942), 47.9 (one-by-one:960), 46.6 (walk-and-pause:966), 46.3 (one-by-one:943), 45.1 (worker-zone:156) |
| run5 | 480/1 | 44.3 (walk-and-pause:347), 43.8 (walk-and-pause:348), 43.8 (person-bike-car:431), 42.7 (people:273), 42.7 (person-bike-car:432) |
| run5 | 320/1 | 25.5 (walk-and-pause:591), 23.2 (one-by-one:42), 23.1 (store-aisle:393), 23.1 (one-by-one:727), 22.6 (people:265) |
| pooled 1-5 | 640/1 | 81.5 (people:559, run5), 80.3 (people:75, run5), 80.3 (people:397, run4), 78.2 (one-by-one:1260, run1), 77.1 (people:192, run2) |
| pooled 1-5 | 640/2 | 79.4 (walk-and-pause:562, run2), 61.4 (people:461, run1), 56.7 (car-lot:235, run3), 53.3 (one-by-one:599, run4), 52.6 (car-lot:234, run3) |
| pooled 1-5 | 480/1 | 45.1 (store-aisle:613, run2), 44.5 (store-aisle:614, run2), 44.3 (walk-and-pause:347, run5), 43.9 (person-bike-car:150, run4), 43.8 (walk-and-pause:348, run5) |
| pooled 1-5 | 320/1 | 27.3 (one-by-one:1152, run1), 26.9 (one-by-one:1154, run1), 26.9 (walk-and-pause:741, run2), 26.7 (one-by-one:1153, run1), 26.5 (one-by-one:1122, run1) |

Frames that appear among the five largest in more than one run: 640/1: none; 640/2: none; 480/1: none; 320/1: none.

Spearman rank correlation of per-frame 640/1 service time between runs: min 0.52, max 0.82.


### E1.4 Run conditions (steal jiffies, core-2 frequency readings between configurations, load average)

| run | steal (jiffies, whole run) | freq range (MHz) | load start | load end | wall (s) | affinity sets seen |
|---|---|---|---|---|---|---|
| run1 | 0 | 1141-2075 | 0.49 1.16 1.36 | 1.13 1.13 1.21 | 817 | [[2, 4]]; [[2]] |
| run2 | 0 | 1136-2092 | 1.12 1.13 1.21 | 1.19 1.24 1.22 | 838 | [[2, 4]]; [[2]] |
| run3 | 0 | 1141-1846 | 1.21 1.11 1.14 | 1.23 1.17 1.15 | 816 | [[2, 4]]; [[2]] |
| run4 | 0 | 1123-1848 | 1.06 1.07 1.09 | 1.07 1.12 1.09 | 813 | [[2, 4]]; [[2]] |
| run5 | 0 | 1111-2960 | 1.03 1.05 1.07 | 1.30 1.32 1.22 | 830 | [[2, 4]]; [[2]] |


### E1.3 analyze.py per run and pooled: deadline misses (%), k_min, guaranteed cameras floor(k_act*T/C_max) at 12 fps, simulated cameras per core (640/1)

| run | C_max 640/1 (ms, frames 11+) | miss 12 | miss 15 | miss 30 | k_min 640/1 12/15/30 | k_min 320/1 12/15/30 | guaranteed cams 640/1, 640/2, 480/1, 320/1 | sim cams 640/1 F8 / A16-8 / DA | sim cams 320/1 |
|---|---|---|---|---|---|---|---|---|---|
| run0 | 74.2 | 0.00 | 0.17 | 100.00 | 1/2/3 | 1/1/1 | 8 / 12 / 16 / 25 | 13 / 15 / 15 | 39 / 46 / 44 |
| run1 | 78.2 | 0.00 | 2.51 | 100.00 | 1/2/3 | 1/1/1 | 8 / 10 / 15 / 24 | 13 / 15 / 15 | 39 / 47 / 45 |
| run2 | 77.1 | 0.00 | 0.56 | 100.00 | 1/2/3 | 1/1/1 | 8 / 8 / 14 / 24 | 13 / 15 / 14 | 38 / 46 / 44 |
| run3 | 72.5 | 0.00 | 0.19 | 100.00 | 1/2/3 | 1/1/1 | 9 / 11 / 15 / 25 | 13 / 15 / 15 | 40 / 47 / 45 |
| run4 | 80.3 | 0.00 | 0.45 | 100.00 | 1/2/3 | 1/1/1 | 8 / 12 / 15 / 25 | 13 / 15 / 15 | 40 / 48 / 45 |
| run5 | 81.5 | 0.00 | 4.42 | 100.00 | 1/2/3 | 1/1/1 | 8 / 13 / 15 / 26 | 12 / 15 / 14 | 40 / 48 / 45 |
| pooled (max trace) | 81.5 | 0.00 | 8.25 | 100.00 | 1/2/3 | 1/1/1 | 8 / 8 / 14 / 24 | 12 / 14 / 14 | 37 / 45 / 43 |
| paper (VM) | 358.7 | 3.58 | 46.56 | 100.00 | 5/6/11 | 1/1/2 | 1 / 6 / 9 / 11 | 10 / 12 / 10 | 31 / 38 / 35 |

Pooled over all samples of runs 1-5 (concatenation): max 81.5 ms, per-run maxima 78.2, 77.1, 72.5, 80.3, 81.5 ms, per-run p99 68.3, 62.5, 61.6, 64.6, 70.0 ms; miss rates (mean over runs) 12/15/30 fps: 0.00 / 1.63 / 100.00 %; k_min 12/15/30: 1/2/3.


### E1.5 Motion triggers per run (ms)

| run | trigger | mean | p50 | p99 | max | miss 30 fps (%) |
|---|---|---|---|---|---|---|
| run1 | FD | 0.84 | 0.80 | 1.12 | 6.42 | 0.00 |
| run1 | CNT | 1.54 | 1.50 | 1.96 | 3.31 | 0.00 |
| run1 | MOG2 | 9.08 | 8.79 | 13.96 | 16.55 | 0.00 |
| run1 | KNN | 12.13 | 9.84 | 44.01 | 53.20 | 5.51 |
| run1 | FLOW | 19.62 | 19.41 | 21.12 | 25.01 | 0.00 |
| run1 | GSOC | 35.01 | 32.97 | 42.18 | 93.38 | 48.62 |
| run2 | FD | 0.82 | 0.78 | 1.13 | 6.49 | 0.00 |
| run2 | CNT | 1.55 | 1.52 | 2.01 | 3.84 | 0.00 |
| run2 | MOG2 | 8.97 | 8.73 | 13.91 | 18.62 | 0.00 |
| run2 | KNN | 12.29 | 9.90 | 44.11 | 58.13 | 5.85 |
| run2 | FLOW | 19.61 | 19.39 | 21.71 | 26.42 | 0.00 |
| run2 | GSOC | 36.47 | 35.53 | 43.09 | 108.32 | 89.88 |
| run3 | FD | 0.81 | 0.78 | 1.13 | 6.24 | 0.00 |
| run3 | CNT | 1.59 | 1.53 | 2.36 | 2.48 | 0.00 |
| run3 | MOG2 | 9.04 | 8.88 | 13.90 | 18.92 | 0.00 |
| run3 | KNN | 12.31 | 9.86 | 44.04 | 54.72 | 5.51 |
| run3 | FLOW | 19.58 | 19.38 | 21.36 | 26.43 | 0.00 |
| run3 | GSOC | 34.21 | 33.21 | 41.09 | 82.43 | 53.46 |
| run4 | FD | 0.82 | 0.78 | 1.18 | 6.44 | 0.00 |
| run4 | CNT | 1.57 | 1.53 | 2.31 | 3.78 | 0.00 |
| run4 | MOG2 | 9.11 | 8.77 | 14.27 | 17.56 | 0.00 |
| run4 | KNN | 12.36 | 10.03 | 44.34 | 53.55 | 5.57 |
| run4 | FLOW | 19.46 | 19.39 | 20.61 | 25.62 | 0.00 |
| run4 | GSOC | 33.49 | 32.32 | 41.04 | 82.45 | 32.27 |
| run5 | FD | 0.80 | 0.78 | 1.13 | 6.41 | 0.00 |
| run5 | CNT | 1.55 | 1.54 | 2.29 | 2.42 | 0.00 |
| run5 | MOG2 | 9.08 | 8.78 | 14.38 | 17.91 | 0.00 |
| run5 | KNN | 12.41 | 10.06 | 46.51 | 53.31 | 5.74 |
| run5 | FLOW | 19.48 | 19.36 | 20.86 | 27.34 | 0.00 |
| run5 | GSOC | 33.52 | 32.34 | 41.17 | 77.67 | 30.92 |


### E1.6 Soak tests (640/1 and 320/1, 20 min each, pinned to core 2; ms)

| soak | jobs | mean | p50 | p95 | p99 | p99.9 | max | n > 150 | n > 120 | largest five (clip:frame #job) | steal |
|---|---|---|---|---|---|---|---|---|---|---|---|
| soak_320_b2b | 68051 | 17.6 | 17.3 | 19.6 | 21.8 | 24.5 | 28.0 | 0 | 0 | 28.0 (person-bike-car:30 #36820), 27.9 (one-by-one:1055 #30055), 27.8 (one-by-one:1056 #30056), 27.8 (car-lot:207 #57045), 27.7 (car-lot:231 #16469) | 0 |
| soak_320_paced | 1801 | 18.2 | 17.8 | 21.1 | 22.7 | 24.7 | 26.6 | 0 | 0 | 26.6 (people:87 #1481), 25.6 (one-by-one:1 #1), 24.5 (one-by-one:901 #901), 24.2 (one-by-one:701 #701), 24.1 (one-by-one:902 #902) | 0 |
| soak_640_b2b | 23169 | 51.8 | 51.7 | 56.5 | 62.3 | 67.3 | 78.5 | 0 | 0 | 78.5 (worker-zone:112 #21240), 78.4 (one-by-one:356 #356), 78.3 (store-aisle:90 #16705), 77.8 (people:190 #18984), 76.7 (walk-and-pause:185 #14422) | 0 |
| soak_640_paced | 1801 | 52.3 | 51.3 | 58.3 | 64.0 | 67.9 | 70.4 | 0 | 0 | 70.4 (one-by-one:1165 #1165), 69.4 (people:403 #1797), 67.5 (one-by-one:1039 #1039), 67.2 (people:365 #1759), 67.0 (people:126 #1520) | 0 |

Running maximum as a function of sample count (ms):

| soak | max after n samples | max first half | max second half |
|---|---|---|---|
| soak_320_b2b | 100: 19.9 | 300: 19.9 | 1000: 22.9 | 3000: 27.3 | 10000: 27.3 | 30000: 27.7 | 68051: 28.0 | 27.9 | 28.0 |
| soak_320_paced | 100: 25.6 | 300: 25.6 | 1000: 25.6 | 1801: 26.6 | 25.6 | 26.6 |
| soak_640_b2b | 100: 57.6 | 300: 58.4 | 1000: 78.4 | 3000: 78.4 | 10000: 78.4 | 23169: 78.5 | 78.4 | 78.5 |
| soak_640_paced | 100: 56.1 | 300: 66.6 | 1000: 66.6 | 1801: 70.4 | 66.6 | 70.4 |


**Answers.**

- Is a > 150 ms outlier reproducible? No: in 137,520 profiled inferences (6 runs x 4 configurations) and 94,822 soak inferences there were 0 samples above 150 ms (and 0 above 120 ms in the profiling runs); the per-run maxima at 640/1 (frames 11+) were 78.2, 77.1, 72.5, 80.3, 81.5 ms, their locations differ between runs (no frame is among the five largest in two runs; Spearman rank correlation of per-frame service time between runs 0.5-0.8, so the slow *frames* are only weakly reproducible while the slow *tail* is a property of the run). The one systematic exception is the first inference on a new clip (frame 0 of store-aisle: 104, 102, 104, 105, 113 ms in runs 1-5 and 106 ms in run0; frame 0 of car-lot about 72 ms), which analyze.py excludes from its distribution table (WARM = 10) but includes in its timing bound and camera simulation. The 358.7 ms sample of the VM (one-by-one, frame 60) has no counterpart here: frame 60 of one-by-one took 58.4, 57.2, 60.8, 57.5, 57.1, 58.1 ms in runs 0-5.

- What is C_max on this machine? 640 px / 1 thread: 81.5 ms over frames 11+ of runs 1-5 (the convention of the paper's latency table; 113.2 ms at store-aisle:0 (run5) if the first ten frames of every clip are included); 640/2: 79.4 ms, 480/1: 45.1 ms, 320/1: 27.3 ms. Soak maxima: soak_320_b2b 28.0 ms (68,051 jobs), soak_320_paced 26.6 ms (1,801 jobs), soak_640_b2b 78.5 ms (23,169 jobs), soak_640_paced 70.4 ms (1,801 jobs).

- What are k_min at 12/30 fps? 640/1: 1 / 3 (ceil(C_max f) with C_max = 81.5 ms; 2 / 4 with the all-frames C_max); identical in every single run (paper: 5 / 11). Guaranteed cameras floor(k_act T / C_max) at 12 fps, k_act = 8: 8 at 640/1 (paper: 1).

- Soak: the running maximum settles within the first 1,000-3,000 samples in every soak and the second-half maximum never exceeds the first-half maximum by more than 4 ms (table E1.6); paced operation (one job every 0.667 s from an idle core) gives the same mean as back-to-back inference (52.3 vs 51.8 ms at 640 px).

- Note on the first configuration of each fresh process: in runs 1-5 the first configuration (one-by-one, 640/1) ran with 11-16 % system time (per-core /proc/stat in meta_det.json: 831-1319 jiffies vs. 1-25 for later 1-thread configurations) and a median of about 58 ms instead of 48 ms; a /proc sample taken during one of the discarded runs showed about 35,000 minor page faults per second in that phase (e1/invalid_first_config_8threads/run2/sysmon_first_minutes.txt); the cause was not isolated (transparent hugepages are `always` on this node; allocator re-faulting of the activation buffers is the likely mechanism). It inflates the mean of that one clip-configuration (one-by-one 640/1) but not the maximum, and it is absent from the soak runs, which warm up once and then run for 20 min.


## 4. E2: live multi-camera validation (live2.py)

live2.py keeps live.py unchanged and adds: all seven clips (camera c plays clip c mod 7), the phase stagger and loop restart of jobs_for_camera() in analyze.py, all three policies, per-job score logging, decision agreement with the offline scores, and the thread-reset guard. One FIFO worker, 1 torch thread, process pinned to core 2, frames pre-decoded (decode excluded), 600 s per run, two repeats, fresh process per run. N* = simulated maximum cameras with zero misses from analyze.py on the pooled Phase-1 trace. "sim" columns = the trace-driven prediction for the same N.

### E2.1 Live multi-camera runs, 640 px / 1 thread, 600 s each (ms; "sim" = trace-driven FIFO simulation of analyze.py on the pooled traces for the same N)

| policy | N | rep | jobs | util | miss % (n) | resp p99 | resp max | service mean | service max | sim util | sim miss % | sim p99 | sim max | decision agree % | load end |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Fixed stride 8 | 10 | 1 | 8788 | 0.701 | 0.00 (0) | 169.8 | 273.3 | 47.9 | 72.1 | 0.806 | 0.00 | 219.4 | 302.4 | 100.0 | 0.83 0.71 0.58 |
| Fixed stride 8 | 10 | 2 | 8788 | 0.743 | 0.00 (0) | 187.1 | 285.0 | 50.7 | 73.3 | 0.806 | 0.00 | 219.4 | 302.4 | 100.0 | 0.95 0.92 0.97 |
| Fixed stride 8 | 11 | 1 | 9691 | 0.787 | 0.00 (0) | 175.9 | 258.7 | 48.7 | 70.2 | 0.879 | 0.00 | 213.4 | 308.5 | 100.0 | 0.71 0.79 0.72 |
| Fixed stride 8 | 11 | 2 | 9691 | 0.787 | 0.00 (0) | 174.2 | 231.4 | 48.7 | 69.2 | 0.879 | 0.00 | 213.4 | 308.5 | 100.0 | 0.80 0.89 0.95 |
| Fixed stride 8 | 12 | 1 | 10591 | 0.957 | 4.95 (524) | 1134.6 | 1313.0 | 54.2 | 78.0 | 0.955 | 0.00 | 248.1 | 354.2 | 100.0 | 1.04 1.01 0.90 |
| Fixed stride 8 | 12 | 2 | 10591 | 0.931 | 0.00 (0) | 370.0 | 627.6 | 52.8 | 77.7 | 0.955 | 0.00 | 248.1 | 354.2 | 100.0 | 0.84 0.96 0.99 |
| Fixed stride 8 | 13 | 1 | 11546 | 0.990 | 41.96 (4845) | 2606.1 | 2725.9 | 51.5 | 76.7 | 1.035 | 96.24 | 20868.7 | 21137.9 | 100.0 | 1.01 1.04 1.00 |
| Fixed stride 8 | 13 | 2 | 11546 | 1.000 | 97.16 (11218) | 26323.1 | 26656.8 | 54.3 | 80.1 | 1.035 | 96.24 | 20868.7 | 21137.9 | 100.0 | 1.13 1.06 1.01 |
| Adaptive 16/8 | 12 | 1 | 8193 | 0.749 | 0.00 (0) | 236.8 | 375.1 | 54.9 | 77.3 | 0.740 | 0.00 | 224.9 | 360.5 | 100.0 | 0.61 0.79 0.90 |
| Adaptive 16/8 | 12 | 2 | 8193 | 0.763 | 0.00 (0) | 230.5 | 343.7 | 55.9 | 79.1 | 0.740 | 0.00 | 224.9 | 360.5 | 100.0 | 0.73 0.77 0.84 |
| Adaptive 16/8 | 13 | 1 | 8711 | 0.722 | 0.00 (0) | 232.6 | 345.6 | 49.7 | 75.2 | 0.783 | 0.00 | 274.5 | 430.7 | 100.0 | 0.83 0.78 0.87 |
| Adaptive 16/8 | 13 | 2 | 8711 | 0.711 | 0.00 (0) | 230.5 | 375.6 | 49.0 | 69.5 | 0.783 | 0.00 | 274.5 | 430.7 | 100.0 | 0.58 0.65 0.75 |
| Adaptive 16/8 | 14 | 1 | 9549 | 0.873 | 0.00 (0) | 432.9 | 668.7 | 54.9 | 77.6 | 0.857 | 0.00 | 360.7 | 533.9 | 100.0 | 0.79 0.89 0.91 |
| Adaptive 16/8 | 14 | 2 | 9549 | 0.787 | 0.00 (0) | 336.5 | 648.4 | 49.5 | 70.5 | 0.857 | 0.00 | 360.7 | 533.9 | 100.0 | 1.08 0.93 0.85 |
| Adaptive 16/8 | 15 | 1 | 10207 | 0.845 | 0.00 (0) | 368.0 | 554.8 | 49.7 | 71.9 | 0.925 | 0.65 | 675.3 | 965.8 | 100.0 | 0.60 0.79 0.87 |
| Adaptive 16/8 | 15 | 2 | 10207 | 0.835 | 0.02 (2) | 371.9 | 700.1 | 49.1 | 71.6 | 0.925 | 0.65 | 675.3 | 965.8 | 100.0 | 0.81 0.86 0.87 |
| Adaptive, deadline-aware | 12 | 1 | 9087 | 0.826 | 0.00 (0) | 263.7 | 368.0 | 54.6 | 79.2 | 0.819 | 0.00 | 255.3 | 371.3 | 100.0 | 0.90 0.87 0.90 |
| Adaptive, deadline-aware | 12 | 2 | 9087 | 0.822 | 0.00 (0) | 262.8 | 370.7 | 54.3 | 77.9 | 0.819 | 0.00 | 255.3 | 371.3 | 100.0 | 0.92 0.86 0.91 |
| Adaptive, deadline-aware | 13 | 1 | 9743 | 0.800 | 0.00 (0) | 212.8 | 310.6 | 49.3 | 74.4 | 0.875 | 0.00 | 250.6 | 359.8 | 100.0 | 0.90 0.89 0.91 |
| Adaptive, deadline-aware | 13 | 2 | 9743 | 0.874 | 0.18 (18) | 522.0 | 819.9 | 53.8 | 76.0 | 0.875 | 0.00 | 250.6 | 359.8 | 100.0 | 0.87 0.85 0.90 |
| Adaptive, deadline-aware | 14 | 1 | 10611 | 0.855 | 0.00 (0) | 238.6 | 491.1 | 48.3 | 70.5 | 0.951 | 0.00 | 378.7 | 501.9 | 100.0 | 0.84 0.85 0.90 |
| Adaptive, deadline-aware | 14 | 2 | 10611 | 0.958 | 1.94 (206) | 837.6 | 987.5 | 54.2 | 78.0 | 0.951 | 0.00 | 378.7 | 501.9 | 100.0 | 0.92 0.98 0.97 |
| Adaptive, deadline-aware | 15 | 1 | 11325 | 0.947 | 1.18 (134) | 766.8 | 1035.3 | 50.2 | 71.7 | 1.025 | 94.80 | 15075.4 | 15217.3 | 100.0 | 1.00 0.99 0.96 |
| Adaptive, deadline-aware | 15 | 2 | 11325 | 0.941 | 0.75 (85) | 725.9 | 1082.8 | 49.9 | 76.0 | 1.025 | 94.80 | 15075.4 | 15217.3 | 100.0 | 0.94 1.01 1.00 |

Largest N with zero misses:

| policy | simulated N* | live: largest N with 0 misses in both repeats | N tested live | live N with 0 misses (both repeats) | simulated N with 0 misses (tested range) |
|---|---|---|---|---|---|
| Fixed stride 8 | 12 | 11 | 10, 11, 12, 13 | 10, 11 | 10, 11, 12 |
| Adaptive 16/8 | 14 | 14 | 12, 13, 14, 15 | 12, 13, 14 | 12, 13, 14 |
| Adaptive, deadline-aware | 14 | 12 | 12, 13, 14, 15 | 12 | 12, 13, 14 |

Single camera, all seven clips once:

| policy | jobs | miss % (n) | service mean | service max | resp p99 | resp max | agreement with offline decisions | max |score diff| |
|---|---|---|---|---|---|---|---|---|
| Fixed stride 8 | 729 | 0.00 (0) | 49.3 | 65.6 | 58.5 | 65.7 | 100.00 (0 differ) | 0.00e+00 |
| Adaptive 16/8 | 589 | 0.00 (0) | 50.1 | 67.9 | 62.4 | 68.0 | 100.00 (0 differ) | 0.00e+00 |
| Adaptive, deadline-aware | 644 | 0.00 (0) | 49.3 | 67.8 | 58.3 | 67.9 | 100.00 (0 differ) | 0.00e+00 |


**Largest N with zero misses in every repeat (640 px):** Fixed stride 8: live 11 vs simulated 12 (N tested 10, 11, 12, 13); Adaptive 16/8: live 14 vs simulated 14 (N tested 12, 13, 14, 15); Adaptive, deadline-aware: live 12 vs simulated 14 (N tested 12, 13, 14, 15).

Single-camera pass (all seven clips once, three policies): Fixed stride 8: 729 jobs, 0 misses, service mean/max 49.3/65.6 ms, decisions equal to the offline trace on 100.00 % of jobs (max |score diff| 0.0e+00); Adaptive 16/8: 589 jobs, 0 misses, service mean/max 50.1/67.9 ms, decisions equal to the offline trace on 100.00 % of jobs (max |score diff| 0.0e+00); Adaptive, deadline-aware: 644 jobs, 0 misses, service mean/max 49.3/67.8 ms, decisions equal to the offline trace on 100.00 % of jobs (max |score diff| 0.0e+00).

Runs with misses (640 px): number of missed jobs per 60-s window of the 600-s run, mean service time in the first 120 s vs the rest, worst response time. Misses cluster in a few windows in which the staggered cameras' active phases (k = 8) coincide; they are not a start-up effect. The mean service time differs by up to 3 ms (6 %) between otherwise identical processes, which is the size of the utilisation margin at N*.

| policy | N | rep | missed / jobs | misses per 60-s window | service mean first 120 s / rest (ms) | worst response (s) |
|---|---|---|---|---|---|---|
| Adaptive 16/8 | 15 | 2 | 2 / 10207 | 0 0 0 0 2 0 0 0 0 0 | 49.5 / 49.0 | 0.68 |
| Adaptive, deadline-aware | 13 | 2 | 18 / 9743 | 0 0 0 0 0 0 18 0 0 0 | 53.0 / 54.0 | 0.79 |
| Adaptive, deadline-aware | 14 | 2 | 206 / 10611 | 0 0 0 0 76 0 67 0 63 0 | 54.1 / 54.2 | 0.99 |
| Adaptive, deadline-aware | 15 | 1 | 134 / 11325 | 0 0 0 0 99 0 35 0 0 0 | 50.2 / 50.1 | 1.04 |
| Adaptive, deadline-aware | 15 | 2 | 85 / 11325 | 0 0 0 0 0 0 0 0 85 0 | 49.8 / 49.9 | 1.08 |
| Fixed stride 8 | 12 | 1 | 524 / 10591 | 0 6 0 215 221 0 0 0 52 30 | 54.6 / 54.1 | 1.31 |
| Fixed stride 8 | 13 | 1 | 4845 / 11546 | 0 292 131 1155 1155 1155 702 0 255 0 | 51.4 / 51.5 | 2.73 |
| Fixed stride 8 | 13 | 2 | 11218 / 11546 | 823 1155 1154 1155 1155 1155 1156 1153 1155 1157 | 53.9 / 54.3 | 26.66 |

### E2.2 Live multi-camera runs, 320 px / 1 thread, 600 s each

| policy | N | rep | jobs | util | miss % (n) | resp p99 | resp max | service mean | service max | sim util | sim miss % | sim p99 | sim max | decision agree % | load end |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Fixed stride 8 | 35 | 1 | 31131 | 0.888 | 0.00 (0) | 101.8 | 240.1 | 17.1 | 27.0 | 0.922 | 0.00 | 77.1 | 132.4 | 100.0 | 0.82 0.83 0.63 |
| Fixed stride 8 | 35 | 2 | 31131 | 0.889 | 0.00 (0) | 439.2 | 621.8 | 17.1 | 28.2 | 0.922 | 0.00 | 77.1 | 132.4 | 100.0 | 1.07 1.00 1.00 |
| Fixed stride 8 | 36 | 1 | 31884 | 0.903 | 0.00 (0) | 193.3 | 444.6 | 17.0 | 26.6 | 0.945 | 0.00 | 92.5 | 163.5 | 100.0 | 0.69 0.89 0.79 |
| Fixed stride 8 | 36 | 2 | 31884 | 0.899 | 0.00 (0) | 381.4 | 545.5 | 16.9 | 28.2 | 0.945 | 0.00 | 92.5 | 163.5 | 100.0 | 0.92 1.00 0.99 |
| Fixed stride 8 | 37 | 1 | 32790 | 0.931 | 2.07 (679) | 820.5 | 997.6 | 17.0 | 27.0 | 0.971 | 0.00 | 171.4 | 256.6 | 100.0 | 1.06 1.01 0.92 |
| Fixed stride 8 | 37 | 2 | 32790 | 0.937 | 2.69 (882) | 806.6 | 940.8 | 17.1 | 27.1 | 0.971 | 0.00 | 171.4 | 256.6 | 100.0 | 1.00 1.00 1.00 |
| Fixed stride 8 | 38 | 1 | 33692 | 0.960 | 4.78 (1612) | 1197.2 | 1485.6 | 17.1 | 26.8 | 0.997 | 0.14 | 604.6 | 694.9 | 100.0 | 1.00 1.00 0.99 |
| Fixed stride 8 | 38 | 2 | 33692 | 0.973 | 8.51 (2867) | 1392.3 | 1602.6 | 17.3 | 27.6 | 0.997 | 0.14 | 604.6 | 694.9 | 100.0 | 0.90 0.97 0.99 |
| Adaptive 16/8 | 43 | 1 | 29308 | 0.837 | 0.00 (0) | 534.9 | 663.7 | 17.1 | 27.6 | 0.869 | 0.00 | 140.1 | 268.4 | 100.0 | 0.93 0.88 0.95 |
| Adaptive 16/8 | 43 | 2 | 29308 | 0.838 | 0.00 (0) | 275.4 | 467.3 | 17.2 | 26.5 | 0.869 | 0.00 | 140.1 | 268.4 | 100.0 | 0.79 0.86 0.90 |
| Adaptive 16/8 | 44 | 1 | 29913 | 0.852 | 0.00 (0) | 479.7 | 596.3 | 17.1 | 29.1 | 0.887 | 0.00 | 220.9 | 339.6 | 100.0 | 0.86 0.94 0.97 |
| Adaptive 16/8 | 44 | 2 | 29913 | 0.849 | 0.00 (0) | 372.2 | 591.5 | 17.0 | 26.8 | 0.887 | 0.00 | 220.9 | 339.6 | 100.0 | 0.85 0.86 0.90 |
| Adaptive 16/8 | 45 | 1 | 30527 | 0.878 | 1.26 (384) | 820.4 | 912.7 | 17.3 | 27.7 | 0.905 | 0.00 | 363.0 | 486.7 | 100.0 | 0.87 0.91 0.97 |
| Adaptive 16/8 | 45 | 2 | 30527 | 0.874 | 0.01 (3) | 535.1 | 681.1 | 17.2 | 27.0 | 0.905 | 0.00 | 363.0 | 486.7 | 100.0 | 0.90 0.90 0.91 |
| Adaptive 16/8 | 46 | 1 | 31243 | 0.888 | 1.37 (428) | 862.8 | 1106.0 | 17.1 | 27.3 | 0.927 | 0.31 | 576.1 | 744.3 | 100.0 | 0.98 0.91 0.93 |
| Adaptive 16/8 | 46 | 2 | 31243 | 0.897 | 1.38 (430) | 753.9 | 1018.4 | 17.2 | 27.1 | 0.927 | 0.31 | 576.1 | 744.3 | 100.0 | 0.90 0.94 0.93 |
| Adaptive, deadline-aware | 41 | 1 | 31025 | 0.880 | 0.01 (4) | 434.8 | 689.1 | 17.0 | 34.9 | 0.919 | 0.00 | 142.9 | 192.2 | 100.0 | 0.94 0.95 0.94 |
| Adaptive, deadline-aware | 41 | 2 | 31025 | 0.888 | 0.05 (17) | 488.1 | 717.3 | 17.2 | 26.7 | 0.919 | 0.00 | 142.9 | 192.2 | 100.0 | 0.92 0.93 0.99 |
| Adaptive, deadline-aware | 42 | 1 | 31892 | 0.899 | 0.18 (57) | 593.6 | 732.7 | 16.9 | 27.6 | 0.944 | 0.00 | 292.1 | 398.0 | 100.0 | 0.96 0.92 0.94 |
| Adaptive, deadline-aware | 42 | 2 | 31892 | 0.905 | 0.00 (0) | 388.8 | 505.6 | 17.0 | 27.3 | 0.944 | 0.00 | 292.1 | 398.0 | 100.0 | 1.00 0.99 1.00 |
| Adaptive, deadline-aware | 43 | 1 | 32606 | 0.932 | 2.11 (689) | 982.1 | 1150.8 | 17.1 | 27.0 | 0.966 | 0.00 | 470.7 | 631.7 | 100.0 | 0.90 0.93 0.95 |
| Adaptive, deadline-aware | 43 | 2 | 32606 | 0.935 | 3.12 (1017) | 1391.7 | 1697.9 | 17.2 | 28.4 | 0.966 | 0.00 | 470.7 | 631.7 | 100.0 | 0.99 0.96 0.99 |
| Adaptive, deadline-aware | 44 | 1 | 33307 | 0.949 | 2.95 (983) | 1013.0 | 1181.8 | 17.1 | 26.8 | 0.986 | 2.04 | 878.7 | 1027.9 | 100.0 | 0.99 0.97 0.99 |
| Adaptive, deadline-aware | 44 | 2 | 33307 | 0.946 | 2.22 (741) | 1062.5 | 1314.4 | 17.0 | 27.7 | 0.986 | 2.04 | 878.7 | 1027.9 | 100.0 | 0.95 0.97 1.00 |

Largest N with zero misses:

| policy | simulated N* | live: largest N with 0 misses in both repeats | N tested live | live N with 0 misses (both repeats) | simulated N with 0 misses (tested range) |
|---|---|---|---|---|---|
| Fixed stride 8 | 37 | 36 | 35, 36, 37, 38 | 35, 36 | 35, 36, 37 |
| Adaptive 16/8 | 45 | 44 | 43, 44, 45, 46 | 43, 44 | 43, 44, 45 |
| Adaptive, deadline-aware | 43 | 0 | 41, 42, 43, 44 |  | 41, 42, 43 |

Single camera, all seven clips once:

| policy | jobs | miss % (n) | service mean | service max | resp p99 | resp max | agreement with offline decisions | max |score diff| |
|---|---|---|---|---|---|---|---|---|
| Fixed stride 8 | 729 | 0.00 (0) | 18.0 | 27.6 | 22.5 | 27.7 | 100.00 (0 differ) | 0.00e+00 |
| Adaptive 16/8 | 591 | 0.00 (0) | 17.8 | 24.0 | 22.6 | 24.2 | 100.00 (0 differ) | 0.00e+00 |
| Adaptive, deadline-aware | 646 | 0.00 (0) | 18.0 | 27.0 | 22.7 | 27.1 | 100.00 (0 differ) | 0.00e+00 |


Runs with misses (320 px), same columns:

| policy | N | rep | missed / jobs | misses per 60-s window | service mean first 120 s / rest (ms) | worst response (s) |
|---|---|---|---|---|---|---|
| Adaptive 16/8 | 45 | 1 | 384 / 30527 | 0 384 0 0 0 0 0 0 0 0 | 17.4 / 17.2 | 0.91 |
| Adaptive 16/8 | 45 | 2 | 3 / 30527 | 0 3 0 0 0 0 0 0 0 0 | 17.3 / 17.2 | 0.68 |
| Adaptive 16/8 | 46 | 1 | 428 / 31243 | 0 428 0 0 0 0 0 0 0 0 | 17.1 / 17.0 | 1.11 |
| Adaptive 16/8 | 46 | 2 | 430 / 31243 | 0 0 0 0 0 0 309 0 121 0 | 17.3 / 17.2 | 1.01 |
| Adaptive, deadline-aware | 41 | 1 | 4 / 31025 | 0 0 0 0 4 0 0 0 0 0 | 17.1 / 17.0 | 0.69 |
| Adaptive, deadline-aware | 41 | 2 | 17 / 31025 | 0 0 17 0 0 0 0 0 0 0 | 17.0 / 17.2 | 0.72 |
| Adaptive, deadline-aware | 42 | 1 | 57 / 31892 | 0 0 0 0 0 0 48 0 9 0 | 16.9 / 16.9 | 0.73 |
| Adaptive, deadline-aware | 43 | 1 | 689 / 32606 | 0 0 558 0 0 0 0 0 131 0 | 17.1 / 17.2 | 1.15 |
| Adaptive, deadline-aware | 43 | 2 | 1017 / 32606 | 0 0 70 0 56 0 0 0 891 0 | 17.1 / 17.2 | 1.70 |
| Adaptive, deadline-aware | 44 | 1 | 983 / 33307 | 0 0 490 0 0 0 0 0 493 0 | 17.0 / 17.1 | 1.18 |
| Adaptive, deadline-aware | 44 | 2 | 741 / 33307 | 0 0 62 0 77 0 0 0 602 0 | 16.9 / 17.1 | 1.31 |
| Fixed stride 8 | 37 | 1 | 679 / 32790 | 0 303 0 322 0 0 0 32 22 0 | 17.1 / 17.0 | 1.00 |
| Fixed stride 8 | 37 | 2 | 882 / 32790 | 0 195 0 377 0 310 0 0 0 0 | 17.2 / 17.1 | 0.94 |
| Fixed stride 8 | 38 | 1 | 1612 / 33692 | 0 1109 0 0 0 502 0 0 1 0 | 17.2 / 17.1 | 1.49 |
| Fixed stride 8 | 38 | 2 | 2867 / 33692 | 0 978 0 146 0 199 0 57 1487 0 | 17.4 / 17.3 | 1.60 |

**Largest N with zero misses in every repeat (320 px):** Fixed stride 8: live 36 vs simulated 37 (N tested 35, 36, 37, 38); Adaptive 16/8: live 44 vs simulated 45 (N tested 43, 44, 45, 46); Adaptive, deadline-aware: live 0 vs simulated 43 (N tested 41, 42, 43, 44).


## 5. E3: end-to-end recorder (recorder.py)

recorder.py: capture thread (cv2.VideoCapture, frame step and 768-px resize as common.frames(), frames due at t0 + t/fps, decode+resize timed), ring buffer of p + ceil(R_max fps) frames with p = round(fps) and R_max (s) = 0.11316571850329638 (largest service time over all timed Phase-1 frames of runs 1-5, store-aisle frame 0), detector worker (1 torch thread, theta = 0.2, decision held for k frames, sample plan identical to analyze.py), writer thread (cv2.VideoWriter MJPG, one file per contiguous segment, every written frame index and write time logged). Three policies x seven clips, once with the whole process pinned to core 2 and once to cores 2 and 4. Video segments were written to local disk (session scratchpad, see section 7), not to the NFS home.

### E3 Recorder checks (all seven clips, three policies, one core vs two cores)

| policy | cores | frames written | record() frames | a. differing frames | b. onset frame written | b. delay within bound | b. delay median/max (s) | b. bound min-max (s) | c. frames lost from ring | c. detector frames evicted | d. decode ms mean/p99/max | d. write ms mean/p99/max | d. lateness ms mean/p99/max | d. frames later than T | d. detector service ms mean/p99/max | decision agree % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Adaptive 16/8|cores2-4 | 4477 | 4477 | 0 | 11/15 | 15/15 | 1.049/1.358 | 1.363-1.613 | 0 | 0 | 4.57/29.82/38.35 | 2.60/3.75/8.81 | 4.69/29.94/38.45 | 0/5800 | 52.3/66.4/75.2 | 100.0 |
| Adaptive 16/8|cores2 | 4477 | 4477 | 0 | 11/15 | 15/15 | 1.049/1.362 | 1.363-1.613 | 0 | 0 | 6.40/35.74/70.25 | 2.60/3.77/19.72 | 6.52/35.86/70.33 | 0/5800 | 56.1/73.0/89.3 | 100.0 |
| Adaptive, deadline-aware|cores2-4 | 4496 | 4496 | 0 | 15/15 | 15/15 | 0.718/0.954 | 0.947-1.030 | 0 | 0 | 4.55/29.47/36.94 | 2.62/3.77/7.03 | 4.67/29.59/37.13 | 0/5800 | 51.7/65.0/72.5 | 100.0 |
| Adaptive, deadline-aware|cores2 | 4496 | 4496 | 0 | 15/15 | 15/15 | 0.717/0.954 | 0.947-1.030 | 0 | 0 | 6.54/37.54/64.15 | 2.60/3.71/15.79 | 6.66/37.63/71.61 | 0/5800 | 54.5/98.4/103.9 | 100.0 |
| Fixed stride 8|cores2-4 | 4650 | 4650 | 0 | 15/15 | 15/15 | 0.469/0.764 | 0.696-0.813 | 0 | 0 | 4.52/29.46/34.61 | 2.60/3.78/6.87 | 4.64/29.59/34.73 | 0/5800 | 51.1/62.4/74.8 | 100.0 |
| Fixed stride 8|cores2 | 4650 | 4650 | 0 | 15/15 | 15/15 | 0.476/0.757 | 0.696-0.813 | 0 | 0 | 6.43/36.08/65.14 | 2.58/3.74/15.94 | 6.56/36.19/74.05 | 0/5800 | 54.4/76.3/98.6 | 100.0 |

Phase-1 reference for the detector service time (640/1, pooled runs 1-5): mean 51.5, p99 67.1, max 81.5 ms.

Per-onset detail:

| policy | cores | clip | onset frame | first positive sample | alert delay (s) | bound (s) | within bound | onset frame written |
|---|---|---|---|---|---|---|---|
| Adaptive 16/8|cores2-4 | one-by-one | 745 | 752 | 0.758 | 1.613 | True | True |
| Adaptive 16/8|cores2-4 | one-by-one | 1235 | 1248 | 1.358 | 1.613 | True | False |
| Adaptive 16/8|cores2-4 | people | 179 | 192 | 1.136 | 1.363 | True | False |
| Adaptive 16/8|cores2-4 | people | 340 | 352 | 1.053 | 1.363 | True | True |
| Adaptive 16/8|cores2-4 | people | 523 | 528 | 0.472 | 1.363 | True | True |
| Adaptive 16/8|cores2-4 | person-bike-car | 484 | 496 | 1.053 | 1.363 | True | True |
| Adaptive 16/8|cores2-4 | walk-and-pause | 41 | 48 | 0.632 | 1.363 | True | True |
| Adaptive 16/8|cores2-4 | walk-and-pause | 332 | 344 | 1.054 | 1.363 | True | True |
| Adaptive 16/8|cores2-4 | walk-and-pause | 660 | 672 | 1.049 | 1.363 | True | True |
| Adaptive 16/8|cores2-4 | walk-and-pause | 898 | 904 | 0.549 | 1.363 | True | True |
| Adaptive 16/8|cores2-4 | worker-zone | 35 | 48 | 1.158 | 1.364 | True | False |
| Adaptive 16/8|cores2-4 | worker-zone | 147 | 152 | 0.492 | 1.364 | True | True |
| Adaptive 16/8|cores2-4 | worker-zone | 409 | 424 | 1.331 | 1.364 | True | False |
| Adaptive 16/8|cores2-4 | worker-zone | 573 | 576 | 0.328 | 1.364 | True | True |
| Adaptive 16/8|cores2-4 | worker-zone | 696 | 704 | 0.741 | 1.364 | True | True |
| Adaptive 16/8|cores2 | one-by-one | 745 | 752 | 0.759 | 1.613 | True | True |
| Adaptive 16/8|cores2 | one-by-one | 1235 | 1248 | 1.362 | 1.613 | True | False |
| Adaptive 16/8|cores2 | people | 179 | 192 | 1.132 | 1.363 | True | False |
| Adaptive 16/8|cores2 | people | 340 | 352 | 1.049 | 1.363 | True | True |
| Adaptive 16/8|cores2 | people | 523 | 528 | 0.466 | 1.363 | True | True |
| Adaptive 16/8|cores2 | person-bike-car | 484 | 496 | 1.059 | 1.363 | True | True |
| Adaptive 16/8|cores2 | walk-and-pause | 41 | 48 | 0.635 | 1.363 | True | True |
| Adaptive 16/8|cores2 | walk-and-pause | 332 | 344 | 1.053 | 1.363 | True | True |
| Adaptive 16/8|cores2 | walk-and-pause | 660 | 672 | 1.057 | 1.363 | True | True |
| Adaptive 16/8|cores2 | walk-and-pause | 898 | 904 | 0.558 | 1.363 | True | True |
| Adaptive 16/8|cores2 | worker-zone | 35 | 48 | 1.165 | 1.364 | True | False |
| Adaptive 16/8|cores2 | worker-zone | 147 | 152 | 0.498 | 1.364 | True | True |
| Adaptive 16/8|cores2 | worker-zone | 409 | 424 | 1.331 | 1.364 | True | False |
| Adaptive 16/8|cores2 | worker-zone | 573 | 576 | 0.352 | 1.364 | True | True |
| Adaptive 16/8|cores2 | worker-zone | 696 | 704 | 0.780 | 1.364 | True | True |
| Adaptive, deadline-aware|cores2-4 | one-by-one | 745 | 752 | 0.759 | 1.013 | True | True |
| Adaptive, deadline-aware|cores2-4 | one-by-one | 1235 | 1244 | 0.954 | 1.013 | True | True |
| Adaptive, deadline-aware|cores2-4 | people | 179 | 188 | 0.801 | 1.030 | True | True |
| Adaptive, deadline-aware|cores2-4 | people | 340 | 348 | 0.718 | 1.030 | True | True |
| Adaptive, deadline-aware|cores2-4 | people | 523 | 532 | 0.799 | 1.030 | True | True |
| Adaptive, deadline-aware|cores2-4 | person-bike-car | 484 | 484 | 0.048 | 1.030 | True | True |
| Adaptive, deadline-aware|cores2-4 | walk-and-pause | 41 | 48 | 0.635 | 1.030 | True | True |
| Adaptive, deadline-aware|cores2-4 | walk-and-pause | 332 | 340 | 0.718 | 1.030 | True | True |
| Adaptive, deadline-aware|cores2-4 | walk-and-pause | 660 | 664 | 0.385 | 1.030 | True | True |
| Adaptive, deadline-aware|cores2-4 | walk-and-pause | 898 | 908 | 0.884 | 1.030 | True | True |
| Adaptive, deadline-aware|cores2-4 | worker-zone | 35 | 44 | 0.830 | 0.947 | True | True |
| Adaptive, deadline-aware|cores2-4 | worker-zone | 147 | 149 | 0.235 | 0.947 | True | True |
| Adaptive, deadline-aware|cores2-4 | worker-zone | 409 | 417 | 0.737 | 0.947 | True | True |
| Adaptive, deadline-aware|cores2-4 | worker-zone | 573 | 573 | 0.072 | 0.947 | True | True |
| Adaptive, deadline-aware|cores2-4 | worker-zone | 696 | 699 | 0.322 | 0.947 | True | True |
| Adaptive, deadline-aware|cores2 | one-by-one | 745 | 752 | 0.758 | 1.013 | True | True |
| Adaptive, deadline-aware|cores2 | one-by-one | 1235 | 1244 | 0.954 | 1.013 | True | True |
| Adaptive, deadline-aware|cores2 | people | 179 | 188 | 0.799 | 1.030 | True | True |
| Adaptive, deadline-aware|cores2 | people | 340 | 348 | 0.716 | 1.030 | True | True |
| Adaptive, deadline-aware|cores2 | people | 523 | 532 | 0.799 | 1.030 | True | True |
| Adaptive, deadline-aware|cores2 | person-bike-car | 484 | 484 | 0.049 | 1.030 | True | True |
| Adaptive, deadline-aware|cores2 | walk-and-pause | 41 | 48 | 0.631 | 1.030 | True | True |
| Adaptive, deadline-aware|cores2 | walk-and-pause | 332 | 340 | 0.717 | 1.030 | True | True |
| Adaptive, deadline-aware|cores2 | walk-and-pause | 660 | 664 | 0.382 | 1.030 | True | True |
| Adaptive, deadline-aware|cores2 | walk-and-pause | 898 | 908 | 0.882 | 1.030 | True | True |
| Adaptive, deadline-aware|cores2 | worker-zone | 35 | 44 | 0.833 | 0.947 | True | True |
| Adaptive, deadline-aware|cores2 | worker-zone | 147 | 149 | 0.249 | 0.947 | True | True |
| Adaptive, deadline-aware|cores2 | worker-zone | 409 | 417 | 0.749 | 0.947 | True | True |
| Adaptive, deadline-aware|cores2 | worker-zone | 573 | 573 | 0.104 | 0.947 | True | True |
| Adaptive, deadline-aware|cores2 | worker-zone | 696 | 699 | 0.379 | 0.947 | True | True |
| Fixed stride 8|cores2-4 | one-by-one | 745 | 752 | 0.764 | 0.813 | True | True |
| Fixed stride 8|cores2-4 | one-by-one | 1235 | 1240 | 0.556 | 0.813 | True | True |
| Fixed stride 8|cores2-4 | people | 179 | 184 | 0.469 | 0.696 | True | True |
| Fixed stride 8|cores2-4 | people | 340 | 344 | 0.390 | 0.696 | True | True |
| Fixed stride 8|cores2-4 | people | 523 | 528 | 0.464 | 0.696 | True | True |
| Fixed stride 8|cores2-4 | person-bike-car | 484 | 488 | 0.384 | 0.696 | True | True |
| Fixed stride 8|cores2-4 | walk-and-pause | 41 | 48 | 0.631 | 0.696 | True | True |
| Fixed stride 8|cores2-4 | walk-and-pause | 332 | 336 | 0.391 | 0.696 | True | True |
| Fixed stride 8|cores2-4 | walk-and-pause | 660 | 664 | 0.385 | 0.696 | True | True |
| Fixed stride 8|cores2-4 | walk-and-pause | 898 | 904 | 0.549 | 0.696 | True | True |
| Fixed stride 8|cores2-4 | worker-zone | 35 | 40 | 0.494 | 0.697 | True | True |
| Fixed stride 8|cores2-4 | worker-zone | 147 | 152 | 0.491 | 0.697 | True | True |
| Fixed stride 8|cores2-4 | worker-zone | 409 | 416 | 0.654 | 0.697 | True | True |
| Fixed stride 8|cores2-4 | worker-zone | 573 | 576 | 0.319 | 0.697 | True | True |
| Fixed stride 8|cores2-4 | worker-zone | 696 | 696 | 0.083 | 0.697 | True | True |
| Fixed stride 8|cores2 | one-by-one | 745 | 752 | 0.757 | 0.813 | True | True |
| Fixed stride 8|cores2 | one-by-one | 1235 | 1240 | 0.561 | 0.813 | True | True |
| Fixed stride 8|cores2 | people | 179 | 184 | 0.470 | 0.696 | True | True |
| Fixed stride 8|cores2 | people | 340 | 344 | 0.387 | 0.696 | True | True |
| Fixed stride 8|cores2 | people | 523 | 528 | 0.476 | 0.696 | True | True |
| Fixed stride 8|cores2 | person-bike-car | 484 | 488 | 0.385 | 0.696 | True | True |
| Fixed stride 8|cores2 | walk-and-pause | 41 | 48 | 0.638 | 0.696 | True | True |
| Fixed stride 8|cores2 | walk-and-pause | 332 | 336 | 0.384 | 0.696 | True | True |
| Fixed stride 8|cores2 | walk-and-pause | 660 | 664 | 0.382 | 0.696 | True | True |
| Fixed stride 8|cores2 | walk-and-pause | 898 | 904 | 0.548 | 0.696 | True | True |
| Fixed stride 8|cores2 | worker-zone | 35 | 40 | 0.498 | 0.697 | True | True |
| Fixed stride 8|cores2 | worker-zone | 147 | 152 | 0.497 | 0.697 | True | True |
| Fixed stride 8|cores2 | worker-zone | 409 | 416 | 0.665 | 0.697 | True | True |
| Fixed stride 8|cores2 | worker-zone | 573 | 576 | 0.334 | 0.697 | True | True |
| Fixed stride 8|cores2 | worker-zone | 696 | 696 | 0.097 | 0.697 | True | True |

Per-clip detail:

| policy | cores | clip | written | record() | extra | missing | duplicates | lost from ring | detector evicted | ring capacity | segments | lateness max (ms) | frames later than T |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Adaptive 16/8|cores2-4 | one-by-one | 1220 | 1220 | 0 | 0 | 0 | 0 | 0 | 12 | 6 | 4.59 | 0 |
| Adaptive 16/8|cores2-4 | people | 360 | 360 | 0 | 0 | 0 | 0 | 0 | 14 | 4 | 3.03 | 0 |
| Adaptive 16/8|cores2-4 | person-bike-car | 392 | 392 | 0 | 0 | 0 | 0 | 0 | 14 | 4 | 2.84 | 0 |
| Adaptive 16/8|cores2-4 | walk-and-pause | 800 | 800 | 0 | 0 | 0 | 0 | 0 | 14 | 4 | 2.71 | 0 |
| Adaptive 16/8|cores2-4 | worker-zone | 850 | 850 | 0 | 0 | 0 | 0 | 0 | 14 | 3 | 38.45 | 0 |
| Adaptive 16/8|cores2-4 | car-lot | 170 | 170 | 0 | 0 | 0 | 0 | 0 | 14 | 2 | 3.46 | 0 |
| Adaptive 16/8|cores2-4 | store-aisle | 685 | 685 | 0 | 0 | 0 | 0 | 0 | 14 | 1 | 11.95 | 0 |
| Adaptive 16/8|cores2 | one-by-one | 1220 | 1220 | 0 | 0 | 0 | 0 | 0 | 12 | 6 | 4.39 | 0 |
| Adaptive 16/8|cores2 | people | 360 | 360 | 0 | 0 | 0 | 0 | 0 | 14 | 4 | 2.55 | 0 |
| Adaptive 16/8|cores2 | person-bike-car | 392 | 392 | 0 | 0 | 0 | 0 | 0 | 14 | 4 | 2.51 | 0 |
| Adaptive 16/8|cores2 | walk-and-pause | 800 | 800 | 0 | 0 | 0 | 0 | 0 | 14 | 4 | 3.21 | 0 |
| Adaptive 16/8|cores2 | worker-zone | 850 | 850 | 0 | 0 | 0 | 0 | 0 | 14 | 3 | 70.33 | 0 |
| Adaptive 16/8|cores2 | car-lot | 170 | 170 | 0 | 0 | 0 | 0 | 0 | 14 | 2 | 2.70 | 0 |
| Adaptive 16/8|cores2 | store-aisle | 685 | 685 | 0 | 0 | 0 | 0 | 0 | 14 | 1 | 13.12 | 0 |
| Adaptive, deadline-aware|cores2-4 | one-by-one | 1244 | 1244 | 0 | 0 | 0 | 0 | 0 | 12 | 5 | 4.70 | 0 |
| Adaptive, deadline-aware|cores2-4 | people | 360 | 360 | 0 | 0 | 0 | 0 | 0 | 14 | 4 | 2.49 | 0 |
| Adaptive, deadline-aware|cores2-4 | person-bike-car | 428 | 428 | 0 | 0 | 0 | 0 | 0 | 14 | 4 | 2.97 | 0 |
| Adaptive, deadline-aware|cores2-4 | walk-and-pause | 808 | 808 | 0 | 0 | 0 | 0 | 0 | 14 | 4 | 2.94 | 0 |
| Adaptive, deadline-aware|cores2-4 | worker-zone | 862 | 862 | 0 | 0 | 0 | 0 | 0 | 14 | 3 | 37.13 | 0 |
| Adaptive, deadline-aware|cores2-4 | car-lot | 85 | 85 | 0 | 0 | 0 | 0 | 0 | 14 | 1 | 2.99 | 0 |
| Adaptive, deadline-aware|cores2-4 | store-aisle | 709 | 709 | 0 | 0 | 0 | 0 | 0 | 14 | 1 | 12.27 | 0 |
| Adaptive, deadline-aware|cores2 | one-by-one | 1244 | 1244 | 0 | 0 | 0 | 0 | 0 | 12 | 5 | 4.91 | 0 |
| Adaptive, deadline-aware|cores2 | people | 360 | 360 | 0 | 0 | 0 | 0 | 0 | 14 | 4 | 3.11 | 0 |
| Adaptive, deadline-aware|cores2 | person-bike-car | 428 | 428 | 0 | 0 | 0 | 0 | 0 | 14 | 4 | 2.46 | 0 |
| Adaptive, deadline-aware|cores2 | walk-and-pause | 808 | 808 | 0 | 0 | 0 | 0 | 0 | 14 | 4 | 3.11 | 0 |
| Adaptive, deadline-aware|cores2 | worker-zone | 862 | 862 | 0 | 0 | 0 | 0 | 0 | 14 | 3 | 71.61 | 0 |
| Adaptive, deadline-aware|cores2 | car-lot | 85 | 85 | 0 | 0 | 0 | 0 | 0 | 14 | 1 | 2.51 | 0 |
| Adaptive, deadline-aware|cores2 | store-aisle | 709 | 709 | 0 | 0 | 0 | 0 | 0 | 14 | 1 | 13.44 | 0 |
| Fixed stride 8|cores2-4 | one-by-one | 1244 | 1244 | 0 | 0 | 0 | 0 | 0 | 12 | 6 | 4.02 | 0 |
| Fixed stride 8|cores2-4 | people | 384 | 384 | 0 | 0 | 0 | 0 | 0 | 14 | 4 | 2.52 | 0 |
| Fixed stride 8|cores2-4 | person-bike-car | 408 | 408 | 0 | 0 | 0 | 0 | 0 | 14 | 4 | 2.60 | 0 |
| Fixed stride 8|cores2-4 | walk-and-pause | 816 | 816 | 0 | 0 | 0 | 0 | 0 | 14 | 4 | 2.77 | 0 |
| Fixed stride 8|cores2-4 | worker-zone | 866 | 866 | 0 | 0 | 0 | 0 | 0 | 14 | 3 | 34.73 | 0 |
| Fixed stride 8|cores2-4 | car-lot | 223 | 223 | 0 | 0 | 0 | 0 | 0 | 14 | 3 | 2.92 | 0 |
| Fixed stride 8|cores2-4 | store-aisle | 709 | 709 | 0 | 0 | 0 | 0 | 0 | 14 | 1 | 12.86 | 0 |
| Fixed stride 8|cores2 | one-by-one | 1244 | 1244 | 0 | 0 | 0 | 0 | 0 | 12 | 6 | 4.28 | 0 |
| Fixed stride 8|cores2 | people | 384 | 384 | 0 | 0 | 0 | 0 | 0 | 14 | 4 | 2.70 | 0 |
| Fixed stride 8|cores2 | person-bike-car | 408 | 408 | 0 | 0 | 0 | 0 | 0 | 14 | 4 | 2.41 | 0 |
| Fixed stride 8|cores2 | walk-and-pause | 816 | 816 | 0 | 0 | 0 | 0 | 0 | 14 | 4 | 2.93 | 0 |
| Fixed stride 8|cores2 | worker-zone | 866 | 866 | 0 | 0 | 0 | 0 | 0 | 14 | 3 | 74.05 | 0 |
| Fixed stride 8|cores2 | car-lot | 223 | 223 | 0 | 0 | 0 | 0 | 0 | 14 | 3 | 3.15 | 0 |
| Fixed stride 8|cores2 | store-aisle | 709 | 709 | 0 | 0 | 0 | 0 | 0 | 14 | 1 | 13.39 | 0 |


**Checks.**

- Adaptive 16/8|cores2-4: (a) written frames = record() frames on the recorder's own decisions: 4477 written vs 4477 expected, 0 differing frames; (b) 11 of 15 detectable onset frames written, alert delay median/max 1.049/1.358 s, 15 of 15 within the bound (k_idle-1)T + R_max (1.363-1.613 s); (c) frames needed but evicted from the ring buffer: 0, detector samples whose frame had been evicted: 0 (with a ring sized from the frames-11+ C_max of 81.5 ms instead, 0 pre-roll frames would have been lost); (d) decode+resize mean/p99/max 4.57/29.82/38.35 ms, write 2.60/3.75/8.81 ms, capture lateness 4.69/29.94/38.45 ms (0 of 5800 frames later than one frame period), detector service 52.3/66.4/75.2 ms vs Phase 1 (640/1, pooled) 51.5/67.1/81.5 ms; live decisions equal to the offline trace on 100.0 % of 589 jobs.

- Adaptive 16/8|cores2: (a) written frames = record() frames on the recorder's own decisions: 4477 written vs 4477 expected, 0 differing frames; (b) 11 of 15 detectable onset frames written, alert delay median/max 1.049/1.362 s, 15 of 15 within the bound (k_idle-1)T + R_max (1.363-1.613 s); (c) frames needed but evicted from the ring buffer: 0, detector samples whose frame had been evicted: 0 (with a ring sized from the frames-11+ C_max of 81.5 ms instead, 0 pre-roll frames would have been lost); (d) decode+resize mean/p99/max 6.40/35.74/70.25 ms, write 2.60/3.77/19.72 ms, capture lateness 6.52/35.86/70.33 ms (0 of 5800 frames later than one frame period), detector service 56.1/73.0/89.3 ms vs Phase 1 (640/1, pooled) 51.5/67.1/81.5 ms; live decisions equal to the offline trace on 100.0 % of 589 jobs.

- Adaptive, deadline-aware|cores2-4: (a) written frames = record() frames on the recorder's own decisions: 4496 written vs 4496 expected, 0 differing frames; (b) 15 of 15 detectable onset frames written, alert delay median/max 0.718/0.954 s, 15 of 15 within the bound (k_idle-1)T + R_max (0.947-1.030 s); (c) frames needed but evicted from the ring buffer: 0, detector samples whose frame had been evicted: 0 (with a ring sized from the frames-11+ C_max of 81.5 ms instead, 0 pre-roll frames would have been lost); (d) decode+resize mean/p99/max 4.55/29.47/36.94 ms, write 2.62/3.77/7.03 ms, capture lateness 4.67/29.59/37.13 ms (0 of 5800 frames later than one frame period), detector service 51.7/65.0/72.5 ms vs Phase 1 (640/1, pooled) 51.5/67.1/81.5 ms; live decisions equal to the offline trace on 100.0 % of 644 jobs.

- Adaptive, deadline-aware|cores2: (a) written frames = record() frames on the recorder's own decisions: 4496 written vs 4496 expected, 0 differing frames; (b) 15 of 15 detectable onset frames written, alert delay median/max 0.717/0.954 s, 15 of 15 within the bound (k_idle-1)T + R_max (0.947-1.030 s); (c) frames needed but evicted from the ring buffer: 0, detector samples whose frame had been evicted: 0 (with a ring sized from the frames-11+ C_max of 81.5 ms instead, 0 pre-roll frames would have been lost); (d) decode+resize mean/p99/max 6.54/37.54/64.15 ms, write 2.60/3.71/15.79 ms, capture lateness 6.66/37.63/71.61 ms (0 of 5800 frames later than one frame period), detector service 54.5/98.4/103.9 ms vs Phase 1 (640/1, pooled) 51.5/67.1/81.5 ms; live decisions equal to the offline trace on 100.0 % of 644 jobs.

- Fixed stride 8|cores2-4: (a) written frames = record() frames on the recorder's own decisions: 4650 written vs 4650 expected, 0 differing frames; (b) 15 of 15 detectable onset frames written, alert delay median/max 0.469/0.764 s, 15 of 15 within the bound (k_idle-1)T + R_max (0.696-0.813 s); (c) frames needed but evicted from the ring buffer: 0, detector samples whose frame had been evicted: 0 (with a ring sized from the frames-11+ C_max of 81.5 ms instead, 0 pre-roll frames would have been lost); (d) decode+resize mean/p99/max 4.52/29.46/34.61 ms, write 2.60/3.78/6.87 ms, capture lateness 4.64/29.59/34.73 ms (0 of 5800 frames later than one frame period), detector service 51.1/62.4/74.8 ms vs Phase 1 (640/1, pooled) 51.5/67.1/81.5 ms; live decisions equal to the offline trace on 100.0 % of 729 jobs.

- Fixed stride 8|cores2: (a) written frames = record() frames on the recorder's own decisions: 4650 written vs 4650 expected, 0 differing frames; (b) 15 of 15 detectable onset frames written, alert delay median/max 0.476/0.757 s, 15 of 15 within the bound (k_idle-1)T + R_max (0.696-0.813 s); (c) frames needed but evicted from the ring buffer: 0, detector samples whose frame had been evicted: 0 (with a ring sized from the frames-11+ C_max of 81.5 ms instead, 0 pre-roll frames would have been lost); (d) decode+resize mean/p99/max 6.43/36.08/65.14 ms, write 2.58/3.74/15.94 ms, capture lateness 6.56/36.19/74.05 ms (0 of 5800 frames later than one frame period), detector service 54.4/76.3/98.6 ms vs Phase 1 (640/1, pooled) 51.5/67.1/81.5 ms; live decisions equal to the offline trace on 100.0 % of 729 jobs.


## 6. Paper value (VM) vs this machine

### Paper value (VM) vs this machine

| quantity | paper (VM) | this machine | kind |
|---|---|---|---|
| detector 640/1 mean (ms) | 61.6 | 51.5 (pooled 1-5; per run 50.7, 51.2, 52.1, 51.0, 51.1, 52.3) | timing-dependent |
| detector 640/1 p95 (ms) | 80.1 | 60.1 | timing-dependent |
| detector 640/1 p99 (ms) | 87.2 | 67.1 | timing-dependent |
| detector 640/1 max (ms) | 358.7 | 81.5 (per run 78.2, 77.1, 72.5, 80.3, 81.5) | timing-dependent |
| deadline misses 12/15/30 fps (%) | 3.6 / 46.6 / 100 | 0.00 / 1.63 / 100.00 (mean over runs 1-5) | timing-dependent |
| max 320/1 (ms) | 56.8 | 27.3 (per run 27.3, 26.9, 26.0, 26.2, 25.5) | timing-dependent |
| max 480/1 (ms) | 67.7 | 45.1 (per run 43.6, 45.1, 42.5, 43.9, 44.3) | timing-dependent |
| max 640/2 (ms) | 96.1 | 79.4 (per run 61.4, 79.4, 56.7, 53.3, 49.0) | timing-dependent |
| k_min 640/1 at 12/30 fps | 5 / 11 | 1 / 3 (per run 1/3, 1/3, 1/3, 1/3, 1/3, 1/3) | timing-dependent |
| guaranteed cameras 640/1, 640/2, 480/1, 320/1 (12 fps) | 1 / 6 / 9 / 11 | 8 / 8 / 14 / 24 | timing-dependent |
| simulated cameras 640/1 (F8 / A16-8 / DA) | 10 / 12 / 10 | 12 / 14 / 14 (pooled max trace; per run 13/15/15; 13/15/15; 13/15/14; 13/15/15; 13/15/15; 12/15/14) | timing-dependent |
| simulated cameras 320/1 (F8 / A16-8 / DA) | 31 / 38 / 35 | 37 / 45 / 43 | timing-dependent |
| detectable onsets | 15 | 15 / 15 / 15 | expected-identical (depends only on scores and theta) |
| onset stored (%) F8 / A16-8 / DA | 100 / 73 / 100 | 100 / 73 / 100 | expected-identical (sampling plan depends only on scores) |
| delay median/max (s) F8, A16-8, DA | 0.47/0.76, 1.05/1.36, 0.74/0.95 | 0.47/0.76, 1.05/1.37, 0.72/0.97 | timing-dependent (adds measured service time to a fixed frame offset) |
| detector runs (%) F8 / A16-8 / DA | 12.5 / 10.1 / 11.1 | 12.6 / 10.2 / 11.2 | expected-identical |
| single-camera live jobs F8 / A16-8 / DA | 729 / 589 / 644 | 729 / 589 / 644 | expected-identical |
| hybrid gate misses (%) MOG2 / CNT / FD (clean) | 5.9 / 1.9 / 1.3 | 0.2 / 0.0 / 0.0 | timing-dependent |



"expected-identical" rows depend only on the (bit-identical) scores, thresholds, annotations and policies; "timing-dependent" rows depend on measured service times and therefore on the machine. Note that the paper's k_min of 5 at 12 fps and the single guaranteed camera at 640/1 both derive from the single 358.7 ms sample of the VM; on this machine the equivalent numbers follow from an 81.5 ms maximum.


## 7. Deviations from the brief, failures, wall-clock time, raw files

- SS_ROOT: all RT-pipeline scripts (exp/common.py, event_eval.py, event_analysis.py, motion_scores.py, det_scores.py, exp/rt/*.py) read `SS_ROOT` (default `/root`); diff in logs/ss_root.diff. live.py received only this path edit (no logic change). Scripts outside the RT pipeline (exp/det, exp/trk, exp/sot, exp/quant, other exp/*.py) still hard-code /root. SS_ROOT points to results/rt_ciscluster/root, where `exp` and `data` are symlinks (to the repo exp/ and the gitignored data/) and `results/` holds the new rt/, motion_scores/, det_scores/ and a copy of event_thresholds.json, so that all new outputs live under results/rt_ciscluster/ and results/rt/ stays untouched.
- ultralytics 8.4.190 resets the torch thread count to min(8, cpu-1) = 8 on the first predict (select_device()). On the 2-core VM this was 1, here it silently overrides torch.set_num_threads(1) in det_scores.py, measure_det.py and live.py. The unmodified scripts were therefore run through exp/rt/run_vm_threads.py (sets that constant to 1); all new scripts guard against it. The first version of e1_profile.py lacked the guard: its first configuration ran 8 threads on one core; the two affected runs were discarded (kept in e1/invalid_first_config_8threads/ with a README) and all five runs were redone. The detector scores generated during the first minutes with 8 threads were also discarded and regenerated with 1 thread.
- measure_det.py was not itself run five times: with taskset the 1-thread configurations cannot be pinned to one core while the 2-thread one uses two, so e1_profile.py reproduces its timing loop verbatim with per-configuration affinity (and omits the perturbed 320-px score pass). The unmodified measure_det.py ran once as run0 (two-core mask) and supplied the 320/480-px score files.
- analyze.py per run: run0 has no motion trace of its own (measure_motion.py was run in runs 1-5 only), so run0 was analysed with run1's lat_motion.npz. The "pooled" analyze.py run used element-wise-maximum traces over runs 1-5 (worst case per frame, so C_max is the worst case over runs); distribution statistics and miss rates over the concatenation of runs 1-5 are given alongside.
- C_max convention: the paper's latency table (and k_min) exclude the first 10 frames of every clip (WARM = 10 in analyze.py); the timing bound and camera simulation in analyze.py include them. Both maxima are reported (81.5 ms vs 113.2 ms at 640/1). The recorder ring buffer (E3) was sized with the larger, all-frames value; the consequence of the smaller value is computed from the logs (check c).
- live2.py restarts a looped clip at t0 + L*n*T with frame 0 (as jobs_for_camera() in analyze.py), whereas live.py continued from the last release time; this was done so that live and simulated job sequences coincide.
- E3 video segments were written to the local disk of the node (session scratchpad), not to the NFS home directory; the frame-index and write-time logs are in e3/recorder_*.json.
- The soak at 640 px back-to-back started with a 1-minute load average of 7.8 that was the decaying trace of the seven parallel analyze.py processes which had just finished (no process was running); all other timed stages started at load about 1.0-1.3 (this process plus the VS Code server).
- Phase 0 idle check: load 0.40 at the first check (criterion 0.3), 0.13 a minute later; no foreign CPU activity was seen at any stage start.
- run_device.sh (Phase 4) was written but, as instructed, not run here.
- The interactive assistant session was closed during E2 (the operator logged out); the stages were already chained in detached processes (exp/rt/e_master_chain.sh, e_finalize.sh) and ran to completion unattended. This file was generated by e_write_summary.py when the chain finished and then reviewed.
- E3 video segments (MJPG .avi, 831 MB in total) are on the node's local disk in the session scratchpad (/tmp/claude-8800/.../scratchpad/e3_video/<policy>_cores<c>/) and are not part of the results directory; the written-frame logs in e3/recorder_*.json are the verified artefact.
- In E2 the simulated prediction uses the element-wise-maximum trace of Phase 1 (conservative service times); live utilisation at the same N is therefore 1-10 % lower than simulated, while live misses at N* arise from response-time bursts the deterministic trace does not produce.

Failures / incomplete stages detected automatically (logs containing Traceback, non-zero exit or Killed): none.

Missing outputs: none.

Total wall-clock time from the first setup command (Thu Nov 12 22:11:13 EST 2026) to the end of the pipeline (MASTER CHAIN DONE in logs/master_chain.log): 14.7 h (setup+scores 0.4 h, E1 incl. soak 4.0 h, E2 640 px 4.6 h, E3 0.9 h, E2 320 px 4.8 h).

Raw files (all under results/rt_ciscluster/):

- platform.txt, logs/frame_counts.txt, logs/score_check.{txt,json}, logs/ss_root.diff, logs/pip_freeze_*.txt, logs/download.log, logs/det_scores_*.log, logs/motion_scores.log
- root/results/motion_scores/*.npz, root/results/det_scores/*.npy (regenerated scores), root/results/rt/{lat_det,lat_motion}.npz (= pooled max traces), root/results/rt/analysis.json (pooled), analysis2.json (hybrid gate misses on the pooled traces), analyze2.log
- e1/run0/{lat_det.npz, measure_det.log, analysis.json, analyze.log}; e1/run{1..5}/{lat_det.npz, meta_det.json, e1_profile.log, lat_motion.npz, measure_motion.log, analysis.json, analyze.log}; e1/pooled/{lat_det.npz, lat_motion.npz, analysis.json, analyze.log}; e1/soak/soak_{640,320}_{b2b,paced}.{npz,_meta.json,log}; e1/e1_summary.json; e1/e1_chain.log; e1/invalid_first_config_8threads/
- e2_640/live_<policy>_N<N>_rep<r>.{json,log} (per-job records), e2_640/live_single.{json,log}, e2_640/nstar.txt, e2_640/e2_run.log, e2_640/e2_summary.json; e2_320/ likewise
- e3/recorder_<policy>_cores<c>.{json,log} (capture, detector, written-frame and lost-frame logs), e3/rmax.txt, e3/e3_run.log, e3/e3_verify.{json,log}
- logs/master_chain.log, logs/summary_tables.md (all tables), SUMMARY.md (this file)
- New code: exp/rt/{e1_profile.py, e1_soak.py, e1_run.sh, e1_chain2.sh, e1_analyze.py, live2.py, e2_run.sh, e2_analyze.py, recorder.py, e3_run.sh, e3_verify.py, run_vm_threads.py, e_master_chain.sh, e_summary_tables.py, e_write_summary.py}, run_device.sh (repo root)


All tables are also in logs/summary_tables.md.

## 8. Extensions (added 2026-11-13 17:54 EST; same node, core 2, one torch thread, same guards; no earlier output modified)

### 8A. E2 at 320 px, Adaptive, deadline-aware, N = 38, 39, 40 (new) alongside the earlier 41-44 (600 s, 2 repeats, ms)

| N | rep | run | jobs | util | miss % (n) | resp p99 | resp max | service mean | service max | sim util | sim miss % | sim p99 | sim max | decision agree % | misses per 60-s window | load end |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 38 | 1 | new | 28715 | 0.830 | 0.00 (0) | 86.5 | 143.1 | 17.3 | 27.8 | 0.850 | 0.00 | 83.9 | 125.7 | 100.0 | 0 0 0 0 0 0 0 0 0 0 | 0.72 0.68 0.45 |
| 38 | 2 | new | 28715 | 0.831 | 0.00 (0) | 91.5 | 199.4 | 17.4 | 27.1 | 0.850 | 0.00 | 83.9 | 125.7 | 100.0 | 0 0 0 0 0 0 0 0 0 0 | 0.72 0.86 0.85 |
| 39 | 1 | new | 29499 | 0.848 | 0.00 (0) | 103.6 | 198.7 | 17.2 | 27.5 | 0.874 | 0.00 | 91.7 | 142.1 | 100.0 | 0 0 0 0 0 0 0 0 0 0 | 0.96 0.88 0.68 |
| 39 | 2 | new | 29499 | 0.851 | 0.00 (0) | 90.4 | 157.8 | 17.3 | 26.9 | 0.874 | 0.00 | 91.7 | 142.1 | 100.0 | 0 0 0 0 0 0 0 0 0 0 | 0.75 0.79 0.84 |
| 40 | 1 | new | 30368 | 0.869 | 0.00 (0) | 408.5 | 639.8 | 17.2 | 28.1 | 0.899 | 0.00 | 106.6 | 167.2 | 100.0 | 0 0 0 0 0 0 0 0 0 0 | 0.85 0.90 0.82 |
| 40 | 2 | new | 30368 | 0.867 | 0.00 (0) | 87.8 | 177.3 | 17.1 | 27.2 | 0.899 | 0.00 | 106.6 | 167.2 | 100.0 | 0 0 0 0 0 0 0 0 0 0 | 0.96 0.95 0.92 |
| 41 | 1 | earlier | 31025 | 0.880 | 0.01 (4) | 434.8 | 689.1 | 17.0 | 34.9 | 0.919 | 0.00 | 142.9 | 192.2 | 100.0 | 0 0 0 0 4 0 0 0 0 0 | 0.94 0.95 0.94 |
| 41 | 2 | earlier | 31025 | 0.888 | 0.05 (17) | 488.1 | 717.3 | 17.2 | 26.7 | 0.919 | 0.00 | 142.9 | 192.2 | 100.0 | 0 0 17 0 0 0 0 0 0 0 | 0.92 0.93 0.99 |
| 42 | 1 | earlier | 31892 | 0.899 | 0.18 (57) | 593.6 | 732.7 | 16.9 | 27.6 | 0.944 | 0.00 | 292.1 | 398.0 | 100.0 | 0 0 0 0 0 0 48 0 9 0 | 0.96 0.92 0.94 |
| 42 | 2 | earlier | 31892 | 0.905 | 0.00 (0) | 388.8 | 505.6 | 17.0 | 27.3 | 0.944 | 0.00 | 292.1 | 398.0 | 100.0 | 0 0 0 0 0 0 0 0 0 0 | 1.00 0.99 1.00 |
| 43 | 1 | earlier | 32606 | 0.932 | 2.11 (689) | 982.1 | 1150.8 | 17.1 | 27.0 | 0.966 | 0.00 | 470.7 | 631.7 | 100.0 | 0 0 558 0 0 0 0 0 131 0 | 0.90 0.93 0.95 |
| 43 | 2 | earlier | 32606 | 0.935 | 3.12 (1017) | 1391.7 | 1697.9 | 17.2 | 28.4 | 0.966 | 0.00 | 470.7 | 631.7 | 100.0 | 0 0 70 0 56 0 0 0 891 0 | 0.99 0.96 0.99 |
| 44 | 1 | earlier | 33307 | 0.949 | 2.95 (983) | 1013.0 | 1181.8 | 17.1 | 26.8 | 0.986 | 2.04 | 878.7 | 1027.9 | 100.0 | 0 0 490 0 0 0 0 0 493 0 | 0.99 0.97 0.99 |
| 44 | 2 | earlier | 33307 | 0.946 | 2.22 (741) | 1062.5 | 1314.4 | 17.0 | 27.7 | 0.986 | 2.04 | 878.7 | 1027.9 | 100.0 | 0 0 62 0 77 0 0 0 602 0 | 0.95 0.97 1.00 |

Largest N with zero misses in both repeats (deadline-aware, 320 px, N tested 38, 39, 40, 41, 42, 43, 44): **live 40** (zero-miss N: 38, 39, 40) vs simulated N* = 43 (simulated zero misses at 38, 39, 40, 41, 42, 43 within the tested range).

### 8B. E1 extension: five fresh e1_profile2.py processes, 640 px / 1 thread only, 120-s discarded back-to-back warm-up over all clips, clip order rotated by one position per run (frames 11+ of every clip; ms)

| run | clip order (first 4 chars) | warm-up jobs | warm-up mean | mean | p50 | p95 | p99 | p99.9 | max | max all frames | system-time share % | miss % 12 / 15 / 30 fps | steal | load end |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| run1 | one- > peop > pers > walk > work > car- > stor | 2410 | 49.8 | 49.9 | 48.7 | 54.3 | 59.1 | 63.9 | 73.0 | 73.0 | 2.0 | 0.00 / 0.03 / 100.00 | 0 | 1.00 0.98 0.95 |
| run2 | peop > pers > walk > work > car- > stor > one- | 2418 | 49.6 | 53.5 | 54.0 | 57.3 | 60.6 | 66.9 | 78.8 | 78.8 | 7.9 | 0.00 / 0.21 / 100.00 | 0 | 1.03 1.02 1.00 |
| run3 | pers > walk > work > car- > stor > one- > peop | 2201 | 54.5 | 55.1 | 55.1 | 58.9 | 62.6 | 66.7 | 80.5 | 80.5 | 10.4 | 0.00 / 0.35 / 100.00 | 0 | 1.00 1.00 1.00 |
| run4 | walk > work > car- > stor > one- > peop > pers | 2245 | 53.5 | 52.5 | 52.9 | 57.2 | 61.4 | 67.2 | 78.3 | 78.3 | 6.0 | 0.00 / 0.21 / 100.00 | 0 | 1.02 1.02 1.00 |
| run5 | work > car- > stor > one- > peop > pers > walk | 2428 | 49.4 | 51.1 | 50.8 | 55.5 | 58.7 | 65.4 | 74.5 | 74.5 | 4.7 | 0.00 / 0.14 / 100.00 | 0 | 1.02 1.01 1.00 |
| pooled |  |  |  | 52.4 | 52.8 | 57.0 | 60.8 | 66.7 | 80.5 |  |  | 0.00 / 0.19 / 100.00 |  |  |

Per-clip median service time (system-time share of that clip's configuration in parentheses; * = first clip timed in that process). E1 rows: the original runs 1-5 (no warm-up, fixed order, one-by-one first).

| run | one-by-one | people | person-bike-car | walk-and-pause | worker-zone | car-lot | store-aisle |
|---|---|---|---|---|---|---|---|
| run1 | 48.5 (0.8 %) * | 51.2 (4.6 %) | 48.9 (2.1 %) | 48.3 (1.1 %) | 48.5 (0.7 %) | 48.7 (1.9 %) | 52.4 (4.4 %) |
| run2 | 52.1 (6.5 %) | 52.8 (6.0 %) * | 54.1 (7.7 %) | 54.5 (9.0 %) | 55.0 (9.9 %) | 54.5 (8.7 %) | 54.1 (7.7 %) |
| run3 | 53.9 (9.5 %) | 53.3 (9.5 %) | 55.1 (10.4 %) * | 55.8 (10.8 %) | 55.7 (11.3 %) | 54.7 (10.2 %) | 55.3 (11.0 %) |
| run4 | 50.5 (4.4 %) | 53.5 (8.5 %) | 53.2 (7.5 %) | 49.2 (1.1 %) * | 53.1 (6.6 %) | 53.4 (8.7 %) | 55.5 (10.0 %) |
| run5 | 50.6 (3.5 %) | 48.7 (1.7 %) | 48.4 (2.7 %) | 51.3 (6.5 %) | 50.0 (3.4 %) * | 52.9 (5.8 %) | 54.5 (8.8 %) |
| E1 run1 | 58.3 * | 48.5 | 47.8 | 47.1 | 48.2 | 47.5 | 47.8 |
| E1 run2 | 59.4 * | 57.7 | 47.8 | 47.5 | 48.6 | 48.3 | 48.5 |
| E1 run3 | 58.0 * | 53.8 | 47.3 | 47.5 | 47.0 | 48.4 | 47.9 |
| E1 run4 | 56.0 * | 56.0 | 47.3 | 47.6 | 48.0 | 47.3 | 48.4 |
| E1 run5 | 59.4 * | 58.4 | 47.8 | 47.4 | 48.3 | 47.5 | 48.8 |

Is the slow first configuration gone? The *first-configuration* effect of the original runs (one-by-one first, median about 58 ms with 11-16 % system time, the other clips 47-49 ms) does not recur: the first timed clip of each warmed-up process has a median of 48.5, 52.8, 55.1, 49.2, 50.0 ms with system-time shares of 0.8, 6.0, 10.4, 1.1, 3.4 %, and it is never slower than the other clips of the same process (49.7, 54.1, 54.8, 53.2, 51.1 ms). What the warm-up and rotation reveal instead is a *process-level* state: runs 1 and 5 ran every clip at 48-51 ms with 2-5 % system time, runs 2 and 3 ran every clip at 52-56 ms with 8-10 % system time, and run 4 switched from 49 ms / 1 % on its first clip to 53-56 ms / 6-9 % afterwards (per-clip table). Across the five processes the mean service time follows the system-time share almost linearly (mean = 48.5 + 0.63 x sys-share-%, r = 0.99). In the original E1 runs the same state is visible in the people clip (second configuration, median 54-58 ms in runs 2-5), so the earlier description as a first-configuration warm-up effect was incomplete: processes start in the high-system-time state, most leave it within minutes, some stay in it or re-enter it. The state changes the mean by up to about 5 ms but not the maximum (72.5-81.5 ms in the original runs, 73.0, 78.8, 80.5, 78.3, 74.5 ms here), so C_max, k_min and the deadline-miss rates are unaffected; the miss rate at 15 fps rises with the mean (0.03-0.35 %). The frame-0 transient on store-aisle (101-113 ms in E1) is also gone with warm-up: frame-0 service times store-aisle: 48.9, 57.3, 55.0, 53.3, 51.6; car-lot: 48.1, 54.0, 55.1, 54.1, 58.5 ms, i.e. that transient was tied to the first inference after decoding and allocating a new clip, which the pre-decoded warm-up layout removes.

Pooled over the five warm-up runs (frames 11+): mean 52.4, p50 52.8, p95 57.0, p99 60.8, p99.9 66.7, max 80.5 ms; original E1 runs 1-5 pooled: mean 51.5, p50 48.4, p95 60.1, p99 67.1, p99.9 71.2, max 81.5 ms.

### 8C. Per-process mean detector service time of the E2 640-px runs (ms; one fresh process per run, sorted)

| run | N | jobs | service mean | p50 | p99 | max | mean first 120 s | mean rest | miss % | start |
|---|---|---|---|---|---|---|---|---|---|---|
| Fixedstride8_N10_rep1 | 10 | 8788 | 47.9 | 47.3 | 57.7 | 72.1 | 48.5 | 47.7 | 0.00 | 02:30 |
| Adaptivedeadline-aware_N14_rep1 | 14 | 10611 | 48.3 | 47.5 | 57.6 | 70.5 | 49.4 | 48.1 | 0.00 | 05:45 |
| Fixedstride8_N11_rep2 | 11 | 9691 | 48.7 | 48.1 | 57.7 | 69.2 | 48.6 | 48.8 | 0.00 | 03:24 |
| Fixedstride8_N11_rep1 | 11 | 9691 | 48.7 | 48.0 | 57.9 | 70.2 | 49.2 | 48.6 | 0.00 | 02:41 |
| Adaptive168_N13_rep2 | 13 | 8711 | 49.0 | 48.1 | 60.1 | 69.5 | 48.9 | 49.0 | 0.00 | 04:51 |
| Adaptive168_N15_rep2 | 15 | 10207 | 49.1 | 48.6 | 58.3 | 71.6 | 49.5 | 49.0 | 0.02 | 05:13 |
| single (Adaptive, deadline-aware) | 1 | 644 | 49.3 | 48.3 | 58.2 | 67.8 | - | - | 0.00 | 06:50 |
| Adaptivedeadline-aware_N13_rep1 | 13 | 9743 | 49.3 | 48.7 | 56.3 | 74.4 | 49.3 | 49.3 | 0.00 | 05:34 |
| single (Fixed stride 8) | 1 | 729 | 49.3 | 48.4 | 58.3 | 65.6 | - | - | 0.00 | 06:50 |
| Adaptive168_N14_rep2 | 14 | 9549 | 49.5 | 48.7 | 59.6 | 70.5 | 49.8 | 49.4 | 0.00 | 05:02 |
| Adaptive168_N15_rep1 | 15 | 10207 | 49.7 | 48.9 | 59.5 | 71.9 | 49.1 | 49.8 | 0.00 | 04:29 |
| Adaptive168_N13_rep1 | 13 | 8711 | 49.7 | 48.5 | 61.7 | 75.2 | 52.3 | 49.1 | 0.00 | 04:08 |
| Adaptivedeadline-aware_N15_rep2 | 15 | 11325 | 49.9 | 48.7 | 59.0 | 76.0 | 49.8 | 49.9 | 0.75 | 06:39 |
| single (Adaptive 16/8) | 1 | 589 | 50.1 | 48.8 | 62.3 | 67.9 | - | - | 0.00 | 06:50 |
| Adaptivedeadline-aware_N15_rep1 | 15 | 11325 | 50.2 | 49.7 | 57.5 | 71.7 | 50.2 | 50.1 | 1.18 | 05:56 |
| Fixedstride8_N10_rep2 | 10 | 8788 | 50.7 | 49.5 | 59.7 | 73.3 | 50.4 | 50.8 | 0.00 | 03:13 |
| Fixedstride8_N13_rep1 | 13 | 11546 | 51.5 | 50.3 | 62.9 | 76.7 | 51.4 | 51.5 | 41.96 | 03:03 |
| Fixedstride8_N12_rep2 | 12 | 10591 | 52.8 | 53.1 | 63.2 | 77.7 | 51.8 | 53.0 | 0.00 | 03:35 |
| Adaptivedeadline-aware_N13_rep2 | 13 | 9743 | 53.8 | 53.3 | 62.9 | 76.0 | 53.0 | 54.0 | 0.18 | 06:17 |
| Adaptivedeadline-aware_N14_rep2 | 14 | 10611 | 54.2 | 53.7 | 63.4 | 78.0 | 54.1 | 54.2 | 1.94 | 06:28 |
| Fixedstride8_N12_rep1 | 12 | 10591 | 54.2 | 53.6 | 65.0 | 78.0 | 54.6 | 54.1 | 4.95 | 02:52 |
| Fixedstride8_N13_rep2 | 13 | 11546 | 54.3 | 54.1 | 64.6 | 80.1 | 53.9 | 54.3 | 97.16 | 03:46 |
| Adaptivedeadline-aware_N12_rep2 | 12 | 9087 | 54.3 | 54.0 | 64.1 | 77.9 | 53.0 | 54.6 | 0.00 | 06:06 |
| Adaptivedeadline-aware_N12_rep1 | 12 | 9087 | 54.6 | 54.0 | 63.9 | 79.2 | 54.7 | 54.6 | 0.00 | 05:23 |
| Adaptive168_N12_rep1 | 12 | 8193 | 54.9 | 54.3 | 67.2 | 77.3 | 53.5 | 55.2 | 0.00 | 03:57 |
| Adaptive168_N14_rep1 | 14 | 9549 | 54.9 | 54.9 | 63.6 | 77.6 | 54.5 | 55.0 | 0.00 | 04:19 |
| Adaptive168_N12_rep2 | 12 | 8193 | 55.9 | 55.4 | 66.5 | 79.1 | 55.7 | 55.9 | 0.00 | 04:40 |

Sorted multi-camera means (24 processes): 47.9, 48.3, 48.7, 48.7, 49.0, 49.1, 49.3, 49.5, 49.7, 49.7, 49.9, 50.2, 50.7, 51.5, 52.8, 53.8, 54.2, 54.2, 54.3, 54.3, 54.6, 54.9, 54.9, 55.9. Thirteen processes lie at 47.9-50.7 ms, nine at 53.8-55.9 ms, and two in between (51.5, 52.8 ms); the largest gap between neighbours is 1.3 ms (51.5 to 52.8) against a next-largest gap of 1.1 ms, so the split is suggestive of two groups but not clean by a gap criterion alone. The level is a property of the process rather than of N or policy: each policy has runs on both levels, and for three (policy, N) pairs the two repeats of the same N fall on different levels (adaptive 16/8 N = 14: 49.5 vs 54.9; deadline-aware N = 13: 49.3 vs 53.8 and N = 14: 48.3 vs 54.2 ms); the levels are interleaved over the 4.6 h of runs, so it is not a time-of-day effect. Within a run the level is mostly stable (first-120-s and remaining means within 0.6 ms in 15 of 24 runs), with a largest shift of 3.2 ms (adaptive 16/8, N = 13, repeat 1), consistent with the mid-run state switch seen in 8B run 4. Together with 8B, where the same two levels appear with 2-5 % vs 8-10 % system time, the two groups are best read as processes outside vs inside the high-page-fault state; live2.py did not record per-process system time, so this attribution for E2 is by analogy. Consequence for E2: a process in the high state carries about 5 ms (10 %) more service time per job, which is the utilisation margin at N*, and the runs that missed deadlines at N* are high-level processes (fixed stride 8, N = 12: 54.2 ms with 4.9 % misses vs 52.8 ms with none; deadline-aware N = 14: 54.2 ms with 1.9 % misses vs 48.3 ms with none).

## 9. Allocator / transparent-hugepage test (added 2026-11-13 21:27 EST; e1_profile2.py, 640 px / 1 thread, 120-s warm-up, clip order rotated by run index, core 2, one torch thread; 15 fresh processes interleaved a,b,c,a,b,c,...)

Per run: service time over frames 11+ of every clip (ms), system-time share of the timed part (per-core /proc/stat user+sys), minor page faults per second of the process during the timed part (/proc/self/stat minflt); "high clips" = clips whose median exceeds 52 ms. Verification of the conditions: (b) the environment seen by the process is recorded in meta_det.json (malloc_env); (c) prctl return code 0 and /proc/self/status THP_enabled: 0 are recorded (thp_status).

| condition | run | first clip | mean | p50 | p99 | max | max all frames | sys % | minflt/s | warm-up sys % / minflt/s | high clips | per-clip medians (clip order of E1) | check | steal | load end |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| (a) default | run1 | one-by-one | 50.2 | 50.0 | 59.8 | 72.5 | 72.5 | 5.6 | 31784 | 0.5 / 4268 | 1/7 | 49.2 51.1 50.0 49.4 49.8 52.7 50.9 | THP1 | 0 | 1.04 0.87 0.46 |
| (a) default | run2 | people | 51.3 | 50.0 | 61.6 | 79.2 | 79.2 | 3.2 | 14475 | 6.4 / 24894 | 1/7 | 49.2 49.9 50.4 52.6 51.7 50.1 49.8 | THP1 | 0 | 1.06 1.03 0.96 |
| (a) default | run3 | person-bike-car | 59.8 | 59.3 | 67.3 | 72.8 | 72.8 | 1.6 | 9381 | 0.4 / 2584 | 7/7 | 58.8 58.8 59.4 59.3 59.7 59.3 64.9 | THP1 | 0 | 2.05 2.11 1.92 |
| (a) default | run4 | walk-and-pause | 66.3 | 66.6 | 71.9 | 80.6 | 80.6 | 8.8 | 35524 | 8.8 / 33748 | 7/7 | 66.8 66.8 66.9 66.2 66.1 66.9 67.1 | THP1 | 0 | 2.04 2.05 2.01 |
| (a) default | run5 | worker-zone | 57.0 | 56.6 | 65.2 | 74.1 | 74.1 | 2.4 | 10680 | 8.5 / 29601 | 7/7 | 55.6 55.4 56.3 59.2 59.2 58.2 54.5 | THP1 | 0 | 2.08 2.02 2.01 |
| (b) MALLOC_TRIM_THRESHOLD_=MALLOC_MMAP_THRESHOLD_=4294967296 | run1 | one-by-one | 75.5 | 73.9 | 93.5 | 114.3 | 114.3 | 29.5 | 202631 | 31.8 / 212225 | 7/7 | 80.7 74.8 73.5 70.0 74.3 71.0 70.6 | THP1 malloc env set | 0 | 1.10 1.04 0.77 |
| (b) MALLOC_TRIM_THRESHOLD_=MALLOC_MMAP_THRESHOLD_=4294967296 | run2 | people | 86.4 | 88.6 | 100.4 | 113.7 | 113.7 | 28.4 | 168586 | 29.1 / 170982 | 7/7 | 91.8 73.7 74.7 91.1 87.8 90.3 88.0 | THP1 malloc env set | 0 | 2.01 1.82 1.40 |
| (b) MALLOC_TRIM_THRESHOLD_=MALLOC_MMAP_THRESHOLD_=4294967296 | run3 | person-bike-car | 92.4 | 92.6 | 101.1 | 112.3 | 112.3 | 29.8 | 157442 | 27.5 / 133930 | 7/7 | 89.4 96.3 89.5 90.6 94.2 97.0 94.3 | THP1 malloc env set | 0 | 2.00 2.04 2.00 |
| (b) MALLOC_TRIM_THRESHOLD_=MALLOC_MMAP_THRESHOLD_=4294967296 | run4 | walk-and-pause | 92.9 | 93.2 | 102.9 | 111.0 | 113.5 | 29.7 | 156764 | 28.8 / 148165 | 7/7 | 95.4 90.2 97.8 90.1 92.8 93.5 90.1 | THP1 malloc env set | 0 | 2.00 2.00 2.00 |
| (b) MALLOC_TRIM_THRESHOLD_=MALLOC_MMAP_THRESHOLD_=4294967296 | run5 | worker-zone | 83.1 | 83.4 | 93.8 | 112.7 | 112.7 | 30.7 | 173265 | 28.0 / 149360 | 7/7 | 83.1 84.0 84.9 85.1 82.0 81.8 77.9 | THP1 malloc env set | 0 | 2.03 2.02 2.00 |
| (c) prctl(PR_SET_THP_DISABLE) | run1 | one-by-one | 54.9 | 55.7 | 66.1 | 81.2 | 81.2 | 8.0 | 46161 | 7.0 / 37543 | 7/7 | 54.1 55.8 54.6 56.4 56.1 56.4 55.6 | THP0 | 0 | 1.00 1.00 0.88 |
| (c) prctl(PR_SET_THP_DISABLE) | run2 | people | 66.6 | 68.0 | 73.8 | 80.0 | 80.0 | 7.3 | 37954 | 11.0 / 47263 | 7/7 | 66.2 61.8 62.2 68.7 68.5 68.2 68.2 | THP0 | 0 | 2.06 2.02 1.72 |
| (c) prctl(PR_SET_THP_DISABLE) | run3 | person-bike-car | 63.5 | 64.7 | 69.1 | 77.4 | 77.4 | 6.2 | 34530 | 6.8 / 33142 | 7/7 | 65.5 65.7 64.3 66.4 61.9 64.2 59.2 | THP0 | 0 | 2.01 2.05 2.01 |
| (c) prctl(PR_SET_THP_DISABLE) | run4 | walk-and-pause | 63.6 | 62.1 | 71.8 | 85.8 | 85.8 | 3.4 | 16495 | 0.3 / 1749 | 7/7 | 62.8 61.6 70.6 62.2 61.6 68.3 61.6 | THP0 | 0 | 2.09 2.06 2.01 |
| (c) prctl(PR_SET_THP_DISABLE) | run5 | worker-zone | 56.2 | 54.8 | 67.4 | 80.7 | 80.7 | 3.6 | 17923 | 0.7 / 3887 | 7/7 | 54.0 55.3 61.4 60.6 53.1 56.7 54.4 | THP0 | 0 | 2.04 2.03 2.00 |

Pooled per condition:

| condition | runs | mean | p50 | p99 | max | per-run means | per-run sys % | per-run minflt/s | runs with mean > 52 ms | clips with median > 52 ms |
|---|---|---|---|---|---|---|---|---|---|---|
| (a) default | 5 | 56.9 | 56.6 | 68.6 | 80.6 | 50.2, 51.3, 59.8, 66.3, 57.0 | 5.6, 3.2, 1.6, 8.8, 2.4 | 31784, 14475, 9381, 35524, 10680 | 3 of 5 | 23 of 35 |
| (b) MALLOC_TRIM_THRESHOLD_=MALLOC_MMAP_THRESHOLD_=4294967296 | 5 | 86.1 | 88.1 | 100.2 | 114.3 | 75.5, 86.4, 92.4, 92.9, 83.1 | 29.5, 28.4, 29.8, 29.7, 30.7 | 202631, 168586, 157442, 156764, 173265 | 5 of 5 | 35 of 35 |
| (c) prctl(PR_SET_THP_DISABLE) | 5 | 61.0 | 61.4 | 71.4 | 85.8 | 54.9, 66.6, 63.5, 63.6, 56.2 | 8.0, 7.3, 6.2, 3.4, 3.6 | 46161, 37954, 34530, 16495, 17923 | 5 of 5 | 35 of 35 |

Does either setting remove the ~54 ms / high-system-time state? **No.** (b) the glibc thresholds make every run much worse: means 75.5-92.9 ms, 28-31 % system time, 157,000-203,000 minor faults per second, every clip median above 52 ms. (c) THP disabled is slower than the default run of the same interleaved triple in 3 of 5 triples (54.9 vs 50.2, 66.6 vs 51.3, 63.5 vs 59.8 ms) and faster in two (63.6 vs 66.3, 56.2 vs 57.0 ms, both inside the drift period described below), with 3-10 % system time and 16,000-46,000 faults per second against 2-9 % and 9,000-36,000 for the default; every one of its 35 clip medians is above 52 ms, against 23 of 35 for the default. It therefore does not remove the state, and when the machine was undisturbed (triple 1) it was clearly worse than the default. The default condition itself reproduced the high-system-time state in run 1 and run 4 (5.6 and 8.8 % system time, 32,000-36,000 faults per second).

**Confound in runs 3-5 of every condition, and what it turned out to be.** From about 19:50 the means of all three conditions rose by 15-30 % (default 50.2, 51.3 then 59.8, 66.3, 57.0 ms; THP-off 54.9, 66.6, 63.5, 63.6, 56.2; malloc 75.5, 86.4, 92.4, 92.9, 83.1) *without* a corresponding rise in system time or fault rate (default run 3: 59.8 ms with 1.6 % system time and 9,400 faults per second). This is not the page-fault state. Checks made afterwards (files e9/socket_evidence_2215.txt, e9/hugepage_evidence_2144.txt, sar logs):
- Not CPU competition: sar shows only our core busy (3-4 % of 24 CPUs user time) throughout; the load average of 2.0 from 19:50 onward was our process plus one foreign bash of another user stuck in uninterruptible NFS wait (sar "blocked = 1", %iowait = 1/24), which uses no CPU. Core-throttle counters stayed at 0, package temperatures 42-44 C.
- Not transparent huge pages: the detector processes have only 20-30 MB of their 5.9 GB of anonymous memory on huge pages whether they run fast or slow (per-configuration smaps_rollup in e9/default/run7_*/meta_det.json, and a live reading of run 6), because the frames are 1-MB numpy arrays and the activation buffers are freed and reallocated; the THP hypothesis in the first version of this section is withdrawn.
- Socket / NUMA effect, measured at 22:15: a dependent-integer-chain clock probe (scratchpad/freqprobe.c, value proportional to the core clock) reads 2.25 on socket-0 cores 2 and 4 and 2.42-2.45 on socket-1 cores 3 and 5, i.e. socket 0 runs about 8 % slower than socket 1 at that time (/proc/cpuinfo on core 2 showed 3.42-3.45 GHz at 21:40 against 3.49-3.69 GHz during yesterday's runs). In addition NUMA node 0 had 1.9 GB free against 6.1 GB on node 1, with 86 GB of file cache on node 0, so a 2-GB first-touch allocation from core 2 was placed two thirds on node 1 (remote) and a strided read of it took 183 ms from core 2 against 154 ms from core 3 (+18 %). Both effects act on user time only, which is exactly the signature of the drift.
- Direct test: two default processes run back to back after the scheduled runs, one pinned to core 3 (node 1) and one to core 2 (node 0): 48.7 ms vs 60.1 ms mean (per-clip medians 46.0-50.9 vs 55.3-63.1 ms), same code, same memory layout, same huge-page share.

| run (after the 15 scheduled runs) | mean | p50 | p99 | max | sys % | minflt/s | per-clip medians (clip order of E1) |
|---|---|---|---|---|---|---|---|
| (a) default, core 2, 21:40 | 56.7 | 56.4 | 63.3 | 74.7 | 0.4 | 3738 | 57.1 56.1 56.2 56.5 55.5 56.0 56.9 |
| (c) THP disabled, core 2, 21:48 | 61.2 | 61.1 | 69.1 | 91.8 | 9.8 | 52810 | 61.3 61.5 60.4 60.9 61.5 60.5 61.3 |
| (a) default, core 3 = NUMA node 1, 21:58 | 48.7 | 49.6 | 58.0 | 68.0 | 4.9 | 22949 | 50.2 50.2 48.8 46.2 46.0 46.0 50.9 |
| (a) default, core 2 = NUMA node 0, 22:05 | 60.1 | 60.5 | 68.2 | 78.1 | 6.4 | 30107 | 57.5 59.8 55.3 62.3 63.1 61.8 62.3 |

**Consequences.** (1) The verdict on (b) stands unconditionally ((b) was the slowest process of every interleaved triple by 20-40 ms); the verdict on (c) rests on the two undisturbed triples (1 and 2), on the all-clips-slow pattern in every (c) run, and on the post-hoc pair at 21:40/21:48 (default 56.7 vs THP-off 61.2 ms, 0.4 vs 9.8 % system time), all pointing the same way. (2) The absolute means of section 9 (and of the two post-hoc runs) are not comparable with sections 3 and 8: from about 19:50 on, core 2 was 15-25 % slower than during the earlier experiments for reasons outside the process (socket-0 clock and node-0 memory placement); the earlier results are unaffected because the drift started after they had finished (the 320-px E2 extension ended 17:13, the 8B runs 17:53). (3) The ~54 ms / high-system-time state of sections 3 and 8 is the page-fault state (system time 6-16 %, 30,000-55,000 faults per second); glibc threshold tuning does not remove it (the particular values requested, 4 GB, exceed glibc's 32-MB cap for M_MMAP_THRESHOLD and disable the dynamic threshold, which most plausibly left every activation buffer on mmap/munmap and explains the 5x fault rate; this is an inference from glibc's documented behaviour), and disabling THP does not remove it either. (4) Two recommendations for future timing on this node: record per-run system time, minor faults and a clock probe alongside the service times (the extended e1_profile2.py now records faults and smaps per configuration), and pin to a socket whose node has free local memory, checking /proc/buddyinfo and numastat before the run.

*This conclusions part of section 9 was rewritten by hand after the post-hoc runs; the first, template-generated version (which proposed a huge-page mechanism) was replaced at 22:16 on 2026-11-13. The per-run and pooled tables above are unchanged; the pooled rows refer to the 15 scheduled runs only.*
