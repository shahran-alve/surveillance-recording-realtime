"""Run an unmodified script with ultralytics' CPU thread reset pinned to 1 thread.
ultralytics.utils.torch_utils.select_device() calls torch.set_num_threads(NUM_THREADS) with NUM_THREADS = min(8, cpu_count - 1)
on the first predict() call. On the paper's 2-core VM this was 1 (no effect); on a 24-core host it is 8 and would silently
override the torch.set_num_threads(1) in det_scores.py / measure_det.py / live.py. Setting it to 1 reproduces the VM behaviour.
Usage: python run_vm_threads.py SCRIPT [ARGS...]"""
import sys, runpy
import ultralytics.utils.torch_utils as tu
tu.NUM_THREADS = 1
sys.argv = sys.argv[1:]
runpy.run_path(sys.argv[0], run_name='__main__')
