import json, math
R='/root/results/rt/'; A=json.load(open(R+'analysis.json')); B=json.load(open(R+'analysis2.json')); M=json.load(open('/root/results/det/det_metrics.json')); L=json.load(open(R+'latency_visdrone.json'))
o=[]
def T(cap,lab,spec,head,rows):
    o.append("\\begin{table}[h]\n\\centering\\footnotesize\\setlength{\\tabcolsep}{3.5pt}\n\\begin{tabular}{@{}"+spec+"@{}}\n\\toprule\n"+head+" \\\\\n\\midrule\n"+" \\\\\n".join(rows)+" \\\\\n\\bottomrule\n\\end{tabular}\n\\caption{"+cap+"}\n\\label{"+lab+"}\n\\end{table}\n")
o.append("\\section{Additional real-time results}\\label{sec:s-rt}\n")
o.append("\\begin{figure}[h]\n\\centering\n\\includegraphics[width=\\textwidth]{fig/scenes_supp.pdf}\n\\caption{The seven benchmark scenes (Intel sample videos~\\cite{intelsamples}, CC BY 4.0). \\emph{store-aisle} is a busy control clip in which little storage can be saved.}\n\\label{fig:scenes}\n\\end{figure}\n")
o.append(open('alg_record.tex').read())
# schedulability
rows=[]
for n in ['Detector 640 px','Detector 640 px, 2 threads','Detector 480 px','Detector 320 px']:
    s=A['sched'][n]; rows.append(n.replace('Detector ','').replace(' px','\\,px')+' & '+' & '.join(f"{s[f'kmin{f}']} ({s[f'kmin_p99_{f}']})" for f in (12,15,30))+' & '+' & '.join(f"{100*s[f'util{f}_k{k}']:.1f}" for f in (12,30) for k in (1,8,16)))
T("Schedulability of the detector task. $k_{\\min}=\\lceil C_{\\max}f\\rceil$ from the observed maximum service time, and in parentheses the value obtained from the 99th percentile. $u$: utilisation (\\% of one core, wall-clock share for two threads) per camera at stride $k$.","tab:s-sched","lccccccccc","Configuration & $k_{\\min}$, 12\\,fps & 15\\,fps & 30\\,fps & $u$: 12\\,fps, $k{=}1$ & $k{=}8$ & $k{=}16$ & 30\\,fps, $k{=}1$ & $k{=}8$ & $k{=}16$",rows)
o.append("\\paragraph{Schedulability.} \\Cref{tab:s-sched} shows how strongly the minimum stride depends on whether it is derived from the observed maximum or from the 99th percentile: at 640\\,px on one thread, 5 against 2 frames at 12\\,fps. The difference is a single 359\\,ms invocation among 5,800.\n")
# timing at 1.5 s
rows=[]
for p in ['Every frame','Fixed stride 8','Fixed stride 16','Adaptive 16/8','Adaptive, deadline-aware']:
    r=[]
    for pre in ('1.0','1.5'):
        t=A['timing'][f'{p}|{pre}']; e=A['onset_events'][f'{p}|{pre}']; r+= [f"{t['median']:.2f}/{t['max']:.2f}", f"{t['onset_stored']:.0f}", f"{e['median']:.2f}", f"{e['within_pre']:.0f}", f"{e['start_recorded']:.0f}"]
    rows.append(p+' & '+' & '.join(r))
T("Alert delay with a pre-roll of 1\\,s and 1.5\\,s (trace-driven, including the measured detector response time; one threshold per clip for all policies). Det.: 15 detectable onsets, median/maximum delay (s) and share of onsets stored (\\%). Ann.: 27 annotated event starts, median delay (s), share first detected within the pre-roll (\\%), and share whose frame 1\\,s after the start is stored (\\%). The deadline-aware stride uses $k_{\\mathrm{idle}}=\\lfloor af\\rfloor$, so its idle stride grows with the pre-roll.","tab:s-pre","lcccccccccc"," & \\multicolumn{5}{c}{Pre-roll 1\\,s} & \\multicolumn{5}{c}{Pre-roll 1.5\\,s}\\\\\nPolicy & Det.\\ delay & stored & Ann.\\ delay & in pre-roll & start & Det.\\ delay & stored & Ann.\\ delay & in pre-roll & start",rows)
# phase
rows=[]
for p in ['Fixed stride 8','Fixed stride 16','Adaptive 16/8','Adaptive, deadline-aware']:
    v=A['phase'][p]; f=lambda i,d=1: f"{v['mean'][i]:.{d}f} [{v['min'][i]:.{d}f}--{v['max'][i]:.{d}f}]"
    rows.append(p+' & '+f(0)+' & '+f(1)+' & '+f(2)+' & '+f"{v['mean'][3]:.1f} [{v['min'][3]:.0f}--{v['max'][3]:.0f}]"+' & '+f"{v['mean'][4]:.1f}")
T("Sensitivity to the sampling phase: the first detector sample falls on frame 0 to 7 of each clip (mean and range over the eight phases; clean video; one threshold per clip, selected by leave-one-video-out for the fixed stride of 8 at phase 0).","tab:s-phase","lccccc","Policy & Recall (\\%) & Idle kept (\\%) & Stored (\\%) & Events (of 27) & Det.\\ runs (\\%)",rows)
# hybrids
rows=[]
for g in ['MOG2','CNT','FD']:
    for k,kn in [('clean','clean'),('jitter','jitter'),('illum','illumination')]:
        h=B['hybrid'][f'{g}|{k}']; rows.append(f"{g} gate + detector & {kn} & {h['gate_open']:.1f} & {h['longest_open_run']} & {h['mean_ms']:.1f} & {h['p99_ms']:.1f} & {h['max_ms']:.0f} & {h['miss']:.1f}")
T("Load of motion-gated detectors on one core: share of frames on which the gate is open, longest run of consecutive open frames, service time per frame (gate plus detector when the gate is open) and share of frames that miss the per-frame deadline at the clips' frame rates. Service times of the gate under perturbation are taken from clean video.","tab:s-hybrid","llcccccc","Trigger & Video & Gate open (\\%) & Longest run & Mean (ms) & p99 (ms) & Max (ms) & Misses (\\%)",rows)
# live
rows=[]
for p,n in [('Fixed stride 8','Fixed stride 8'),('Adaptive 16/8','Adaptive 16/8'),('Adaptive, deadline-aware','Deadline-aware')]:
    d=B['live_single'][p]; rows.append(f"1 & {n} & {d['jobs']} & {d['service_mean']:.1f} & {d['resp_p99']:.0f} & {d['resp_max']:.0f} & {d['miss']:.1f} & {d['min_slack_ms']:.0f}")
for N in (4,8,10):
    for p,n in [('Fixed stride 8','Fixed stride 8'),('Adaptive, deadline-aware','Deadline-aware')]:
        d=B['live_multi'][f'{p}|{N}']; rows.append(f"{N} & {n} & {d['jobs']} & {d['service_mean']:.1f} & {d['resp_p99']:.0f} & {d['resp_max']:.0f} & {d['miss']:.1f} & {d['min_slack_ms']:.0f}")
T("Wall-clock validation on one core (640\\,px, one thread). One camera: all seven clips played once at their own frame rate. Several cameras: four clips (people, person-bike-car, car-lot, store-aisle) looped for 120\\,s with staggered start times, one first-come-first-served worker. Response times in ms; slack: smallest margin to a job deadline (negative: deadline missed).","tab:s-live","clcccccc","Cameras & Policy & Jobs & Mean service & p99 response & Max response & Misses (\\%) & Min.\\ slack (ms)",rows)
o.append("\\paragraph{Wall-clock validation.} In the single-camera runs the live decisions were identical to the offline traces for every job. The live service time (about 70\\,ms) is higher than in back-to-back profiling (61.6\\,ms) because each job starts from an idle core. With ten cameras the fixed stride of 8 reaches a utilisation of 0.99 and misses deadlines, while the deadline-aware stride, which samples idle scenes less often, stays at 0.81 (\\cref{tab:s-live}).\n")
# lowres
rows=[]
for det,n in [('yolo11n320','320\\,px'),('yolo11n480','480\\,px')]:
    for suf,pn in [('','Fixed stride 8'),('|da','Deadline-aware')]:
        for k,kn in [('clean','clean'),('jitter','jitter'),('illum','illumination')]:
            x=A['lowres'][det+suf].get(k)
            if x: rows.append(f"{n} & {pn} & {kn} & {x['stored']:.1f} & {x['idle']:.1f} & {x['recall']:.1f} & {x['events']}/27 & {x['calls']:.1f}")
T("Lower-resolution detector as trigger (leave-one-video-out thresholds per configuration, sampling phase 0). Perturbed copies were scored only at 320\\,px.","tab:s-lowres","lllccccc","Input & Policy & Video & Stored & Idle kept & Recall & Events & Det.\\ runs",rows)
cm=A['cameras_motion']
o.append(f"\\paragraph{{Motion triggers on several cameras.}} Replaying the measured per-frame service times of $N$ cameras through one first-come-first-served worker with a per-frame deadline, one core served {cm['FD|15']} cameras with frame differencing, {cm['CNT|15']} with CNT, {cm['MOG2|15']} with MOG2 and {cm['KNN|15']} with KNN at 15\\,fps without a deadline miss, and {cm['FD|30']}, {cm['CNT|30']}, {cm['MOG2|30']} and {cm['KNN|30']} at 30\\,fps.\n")
o.append("\\begin{figure}[h]\n\\centering\n\\includegraphics[width=0.5\\textwidth]{fig/perturb_supp.pdf}\n\\caption{Idle frames stored on clean video and under two perturbations, with thresholds fixed from clean video. Det: detector on every frame ($k{=}1$) or every 8th frame ($k{=}8$).}\n\\label{fig:perturb}\n\\end{figure}\n")
open('supp_rt.tex','w').write('\n'.join(o))
# detector rows
rows=[]
order=[('YOLOX-s','yolox_s_640','640'),('YOLOv8n','yolov8n_640','640'),('YOLO11n','yolo11n_640','640'),('YOLO26n','yolo26n_640','640'),('YOLOv8s','yolov8s_640','640'),('YOLO11s','yolo11s_640','640'),('YOLO26s','yolo26s_640','640'),
 ('YOLO11n','yolo11n_640_tiles','640, tiles'),('YOLO11n','yolo11n_640_tta','640, TTA'),('YOLO11n','yolo11n_960','960'),('YOLO11n','yolo11n_1280','1280'),('YOLO11s','yolo11s_960','960'),('YOLO11s','yolo11s_1280','1280'),
 ('YOLO26n','yolo26n_960','960'),('YOLO26n','yolo26n_1280','1280'),('YOLO26s','yolo26s_960','960'),('YOLO26s','yolo26s_1280','1280')]
print(list(M['yolo11n_640'].keys()), list(M['yolo11n_640']['all'].keys()))
for n,k,inp in order:
    m=M[k]; a=m['all']; per=m.get('person',m.get('pers')); veh=m.get('vehicle',m.get('veh'))
    rows.append(f"{n} & {inp} & {100*a['AP']:.1f} & {100*a['AP50']:.1f} & {100*a['APs']:.1f} & {100*per['AP']:.1f} & {100*veh['AP']:.1f} & {L[k]:.0f} \\\\")
open('det_rows.tex','w').write('\n'.join(rows)); print('\n'.join(rows))
