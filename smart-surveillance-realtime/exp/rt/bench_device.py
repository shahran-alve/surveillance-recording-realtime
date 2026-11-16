#!/usr/bin/env python3
"""Stand-alone timing benchmark for a target device (e.g. Raspberry Pi, Jetson, mini PC).

It measures the per-frame service time of the motion triggers and, if Ultralytics is installed, of the detector trigger,
then reports the quantities used in the paper: latency distribution (mean, p50, p95, p99, max), deadline-miss rate at the
camera frame rate, the minimum schedulable detector stride k_min = ceil(C_max * fps), the deadline-aware idle stride
k_idle = floor(pre_roll * fps), the worst-case alert delay (k_idle - 1) / fps + C_max, and the number of cameras one core
can serve under the worst-case (all scenes occupied) load.

Usage:
  python bench_device.py --video clip.mp4 --fps 12 --width 768 --threads 1 --imgsz 640 --model yolo11n.pt
Without --video, 600 synthetic frames with a moving block are used, which is enough for timing but not for accuracy.
Requires: opencv-python (opencv-contrib-python for CNT); optional: ultralytics, torch.
"""
import argparse, json, math, platform, time
import cv2, numpy as np

def get_frames(a):
    if a.video:
        c = cv2.VideoCapture(a.video); F = []
        while len(F) < a.max_frames:
            ok, f = c.read()
            if not ok: break
            h = int(round(f.shape[0] * a.width / f.shape[1])); F.append(cv2.resize(f, (a.width, h), interpolation=cv2.INTER_AREA))
        return F
    rng = np.random.default_rng(0); h = int(a.width * 9 / 16); base = rng.integers(60, 180, (h, a.width, 3), dtype=np.uint8); F = []
    for t in range(min(600, a.max_frames)):
        f = base.copy(); x = (7 * t) % (a.width - 80); f[h // 3:h // 3 + 120, x:x + 80] = 230; F.append(f)
    return F

def fifo_miss(s, T):
    t = 0.0; miss = 0
    for i, c in enumerate(s):
        t = max(t, i * T) + c; miss += (t - i * T) > T
    return 100.0 * miss / len(s)

def stats(s, fps):
    s = np.asarray(s[5:]); T = 1.0 / fps
    return dict(mean_ms=1e3 * s.mean(), p50_ms=1e3 * np.percentile(s, 50), p95_ms=1e3 * np.percentile(s, 95), p99_ms=1e3 * np.percentile(s, 99), max_ms=1e3 * s.max(),
                per_frame_deadline_miss_pct=fifo_miss(s, T), utilisation_per_camera=float(s.mean() * fps))

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--video'); p.add_argument('--fps', type=float, default=12.0); p.add_argument('--width', type=int, default=768)
    p.add_argument('--threads', type=int, default=1); p.add_argument('--imgsz', type=int, default=640); p.add_argument('--model', default='yolo11n.pt')
    p.add_argument('--pre_roll', type=float, default=1.0); p.add_argument('--max_frames', type=int, default=1500); p.add_argument('--out', default='bench_device.json')
    a = p.parse_args(); cv2.setNumThreads(a.threads); F = get_frames(a); out = dict(device=platform.platform(), machine=platform.machine(), frames=len(F), fps=a.fps, threads=a.threads)
    # --- motion triggers
    def fd():
        prev = [None]
        def f(fr):
            g = cv2.GaussianBlur(cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY), (5, 5), 0)
            if prev[0] is not None:
                d = cv2.morphologyEx((cv2.absdiff(g, prev[0]) > 25).astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8)); d.mean()
            prev[0] = g
        return f
    def bgs(m):
        return lambda fr: float((m.apply(fr) == 255).mean())
    M = {'FD': fd(), 'MOG2': bgs(cv2.createBackgroundSubtractorMOG2(detectShadows=True)), 'KNN': bgs(cv2.createBackgroundSubtractorKNN(detectShadows=True))}
    if hasattr(cv2, 'bgsegm'): M['CNT'] = bgs(cv2.bgsegm.createBackgroundSubtractorCNT())
    for name, fn in M.items():
        ts = []
        for fr in F:
            t0 = time.perf_counter(); fn(fr); ts.append(time.perf_counter() - t0)
        out[name] = stats(ts, a.fps); print(name, {k: round(v, 2) for k, v in out[name].items()})
    # --- detector trigger
    try:
        import torch; from ultralytics import YOLO
        torch.set_num_threads(a.threads); m = YOLO(a.model); ts = []
        for fr in F[:5]: m.predict(fr, imgsz=a.imgsz, conf=0.05, classes=[0, 1, 2, 3, 5, 7], verbose=False)
        for fr in F:
            t0 = time.perf_counter(); m.predict(fr, imgsz=a.imgsz, conf=0.05, classes=[0, 1, 2, 3, 5, 7], verbose=False); ts.append(time.perf_counter() - t0)
        d = stats(ts, a.fps); cmax = d['max_ms'] / 1e3; T = 1 / a.fps
        k_idle = max(1, math.floor(a.pre_roll * a.fps + 1e-9)); k_act = min(8, k_idle); k_min = math.ceil(cmax * a.fps)
        d.update(k_min=k_min, k_idle=k_idle, k_act=k_act, feasible=bool(k_min <= k_act),
                 worst_case_alert_delay_s=(k_idle - 1) * T + cmax, ring_buffer_frames=math.ceil((a.pre_roll + cmax) * a.fps),
                 cameras_per_core_worst_case=int(math.floor(k_act * T / cmax)), utilisation_idle=float(np.mean(ts[5:]) * a.fps / k_idle), utilisation_active=float(np.mean(ts[5:]) * a.fps / k_act))
        out[f'detector_{a.imgsz}'] = d; print('detector', {k: (round(v, 3) if isinstance(v, float) else v) for k, v in d.items()})
    except ImportError:
        print('ultralytics/torch not installed: detector not measured')
    json.dump(out, open(a.out, 'w'), indent=1, default=float); print('written', a.out)

if __name__ == '__main__':
    main()
