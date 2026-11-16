# Smart Surveillance: real-time event-triggered recording

Code, annotations and raw results for the paper
"Smart Surveillance: Deep Learning and Hybrid Approaches for Dynamic Scene Analysis, Object Detection and Motion Tracking"
(S. R. Alve, M. Z. Mahmud, S. Islam, M. S. Reza).

## Contents

| Path | What it is |
|---|---|
| `exp/gt_events.py` | Event annotations (27 events, seven clips, one-second resolution) |
| `exp/common.py`, `exp/perturb.py` | Clip loading (768 px, 10-12.5 fps) and seeded perturbations |
| `exp/motion_scores.py`, `exp/det_scores.py` | Per-frame trigger scores |
| `exp/event_eval.py`, `exp/event_analysis.py` | Recording policy, metrics, leave-one-video-out thresholds |
| `exp/rt/measure_motion.py`, `exp/rt/measure_det.py` | Per-frame service times |
| `exp/rt/analyze.py`, `exp/rt/analyze2.py` | Deadline misses, schedulability, timing guarantee, cameras per core, gated hybrids |
| `exp/rt/live.py` | Wall-clock validation with one or several cameras on one core |
| `exp/rt/bench_device.py` | Stand-alone benchmark for a target device (Raspberry Pi, Jetson, mini PC) |
| `exp/rt/figs_rt.py`, `exp/rt/gen_supp.py` | Figures and supplementary tables |
| `exp/det/`, `exp/trk/`, `exp/quant/`, `exp/sot/` | Detection (VisDrone), tracking (MOT15 TUD), quantization, single-object tracking |
| `results/` | Raw results; `results/rt/` holds service-time traces and the real-time analysis |

## Data (not included)

- Intel sample videos, CC BY 4.0: https://github.com/intel-iot-devkit/sample-videos
- VisDrone2019-DET validation set
- MOT15 sequences TUD-Campus and TUD-Stadtmitte

## Setup

Two environments were used (see `requirements-*.txt`): one with `opencv-contrib-python` 4.10 for the motion triggers and the analysis, and one with PyTorch and Ultralytics for the detector.

The scripts use absolute paths from the original machine (`/root/data`, `/root/results`, `/root/exp`). Change these at the top of `exp/common.py`, `exp/event_eval.py` and the scripts in `exp/rt/` before running.

## Reproducing the real-time study

```
python exp/motion_scores.py && python exp/det_scores.py     # trigger scores
python exp/rt/measure_motion.py                             # service times, motion triggers
python exp/rt/measure_det.py                                # service times, detector (640/480/320 px, 1-2 threads)
python exp/rt/analyze.py                                    # writes results/rt/analysis.json
python exp/rt/live.py 4 8 10                                # wall-clock validation
python exp/rt/analyze2.py                                   # writes results/rt/analysis2.json
python exp/rt/figs_rt.py
```

Run the timing scripts on an otherwise idle machine.

## Benchmarking another device

```
python exp/rt/bench_device.py --video clip.mp4 --fps 12 --width 768 --threads 1 --imgsz 320 --model yolo11n.pt
```

It reports the latency distribution, deadline-miss rate, minimum schedulable stride, worst-case alert delay and guaranteed cameras per core.

## Note on AI assistance

An LLM assistant was used to write and run this code and to produce the event annotations; the authors reviewed both.
