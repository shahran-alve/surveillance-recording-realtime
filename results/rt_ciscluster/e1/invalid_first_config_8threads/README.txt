Detector profiling runs 1 and 2 produced by the first version of e1_profile.py, which did not neutralise ultralytics' thread reset
(select_device() -> torch.set_num_threads(8) on the first predict). Consequence: the FIRST configuration of the process (clip one-by-one,
640 px, "1 thread") actually ran 8 torch threads pinned to one core (median 85-87 ms instead of ~50 ms, ~15% system time); all later
configurations were correct (set_num_threads(th) is called per configuration). These files are kept for transparency and are NOT used
in any table. run2 is incomplete (process killed during the fix). sysmon_first_minutes.txt: /proc sampling during run2's first minutes.
