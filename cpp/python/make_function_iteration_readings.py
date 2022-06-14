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
    # Assumes 1million cycles per func iter and 4 Ghz
    inv_theta = 1/(2.25 * math.sqrt(2**(log_w - log_n)))
    return ITERS * (inv_theta * 10**6 * 10 * 2**log_w / (4 * 10**9 * ncpus)) / 3600

def predicted_cycles(num_steps, calibrated_cycles):
    return num_steps * calibrated_cycles / ncpus

def parse_cycles(ls: str):
    # You will get a list of cycles, which then you 
    # can average over. Should be good enough for us
    readings = []
    for l in ls.splitlines():
        if l.strip().startswith('Benchmark') and not 'running' in l:
            readings.append(float(l.strip().split(':')[1].replace('cycles', '').strip()))
    return sum(readings) / len(readings)


total_time = 0
for n, w in experiments:
    if n <= w:
        continue
    pred = predicted_time(n, w)
    print('Predict this number of hours ', pred)
    total_time += pred

print('Total: ', total_time)

calibrated_cycles = {}

for n, w in experiments:
   cmd_run = subprocess.run(f"python gen.py -min_cpus {ncpus} -max_cpus {ncpus} -min_mem {w} -max_mem {w} -min_nbits {n} -max_nbits {n} -no_hag -iterations {ITERS}".split(' '), capture_output=True, text=True)
   print(cmd_run.stdout)
   cycles_parsed = parse_cycles(cmd_run.stdout)
   calibrated_cycles[str(n) + '_' + str(w)] = cycles_parsed
   
   
aggregated_res = {}
with open('gen_full_atk_False_hag_False') as f:
    lines = list(f)
    dicts = [json.loads(l) for l in lines]
    for d in dicts:
        nbits_state, memory_log_size, _, _ = d['k']
        num_steps = d['v']['num_steps']
        # Cycles are wall time cycles
        cycles = d['v']['cycles']
        key = str(nbits_state)+'_'+str(memory_log_size)
        exp_cycles = predicted_cycles(num_steps, calibrated_cycles[key])

        aggregated_res[key] = { 'n' : nbits_state, 'w': memory_log_size, 'num_steps': num_steps, 'cycles': cycles, 'exp_cycles': exp_cycles,
                'ratio': cycles/exp_cycles, 'calibration': calibrated_cycles[key] }
        
with open('aggregated_function_iterations_readings.json', 'w') as output:
    json.dump(aggregated_res, output)
