import subprocess
import json
import psutil
import math

# Each iterations needs to compute 10 w distinguished! points
# So that is 10^7 * theta * w cycles / (4 * 10^9 * L) = theta * w / 400 * L seconds
# Suppose we run on Daisen and take 80 cores. We can run in 5-6h all iterations for w = 2^17

experiments = [ (24, 17), (24, 16) ]

ncpus = 16 # min(psutil.cpu_count(logical=True), math.floor(psutil.cpu_count(logical=False) * 1.4)) - 1

ITERS = 5

# We have set the cycles for function iterations to be ~ 1 million cycles. 
# We want to verify that a function iterations that computes that many points incurs in the appropriate slowdown

def predicted_time(log_n, log_w):
    # Assumes 1ms per func iter
    inv_theta = 1/(2.25 * math.sqrt(2**(log_w - log_n)))
    num_iterations = ITERS * (inv_theta * 10 * 2**log_w)
    # Each iterations is 10 microseconds
    time_iter = 10 * 1e-6
    return num_iterations * time_iter / ncpus

total_time = 0
for n, w in experiments:
    if n <= w:
        continue
    pred = predicted_time(n, w)
    print('Predict this number of hours ', pred / 3600)
    total_time += pred / 3600

print('Total: ', total_time)

for n, w in experiments:
   cmd_run = subprocess.run(f"python gen.py -min_cpus {ncpus} -max_cpus {ncpus} -min_mem {w} -max_mem {w} -min_nbits {n} -max_nbits {n} -no_hag -iterations {ITERS}".split(' '))
   
   
aggregated_res = {}
with open('gen_full_atk_False_hag_False') as f:
    lines = list(f)
    dicts = [json.loads(l) for l in lines]
    for d in dicts:
        nbits_state, memory_log_size, _, _ = d['k']
        num_steps = d['v']['num_steps']
        # Cycles are wall time cycles
        wall_time = d['v']['wall_time']
        key = str(nbits_state)+'_'+str(memory_log_size)
        predicted_wall_time = predicted_time(nbits_state, memory_log_size)

        aggregated_res[key] = { 'n' : nbits_state, 'w': memory_log_size, 'num_steps': num_steps, 'wall_time': wall_time, 'exp_wall_time': predicted_wall_time,
                'ratio': wall_time/predicted_wall_time }
        
with open('aggregated_sleep_function_iterations_readings.json', 'w') as output:
    json.dump(aggregated_res, output)
