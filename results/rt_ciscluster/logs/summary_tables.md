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

### E1.4 Run conditions (steal jiffies, core-2 frequency readings between configurations, load average)

| run | steal (jiffies, whole run) | freq range (MHz) | load start | load end | wall (s) | affinity sets seen |
|---|---|---|---|---|---|---|
| run1 | 0 | 1141-2075 | 0.49 1.16 1.36 | 1.13 1.13 1.21 | 817 | [[2, 4]]; [[2]] |
| run2 | 0 | 1136-2092 | 1.12 1.13 1.21 | 1.19 1.24 1.22 | 838 | [[2, 4]]; [[2]] |
| run3 | 0 | 1141-1846 | 1.21 1.11 1.14 | 1.23 1.17 1.15 | 816 | [[2, 4]]; [[2]] |
| run4 | 0 | 1123-1848 | 1.06 1.07 1.09 | 1.07 1.12 1.09 | 813 | [[2, 4]]; [[2]] |
| run5 | 0 | 1111-2960 | 1.03 1.05 1.07 | 1.30 1.32 1.22 | 830 | [[2, 4]]; [[2]] |

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

