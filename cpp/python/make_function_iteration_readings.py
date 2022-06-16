import subprocess
import json
import math

# Each iterations needs to compute 10 w distinguished! points
# So that is 10^7 * theta * w cycles / (4 * 10^9 * L) = theta * w / 400 * L seconds
# Suppose we run on Daisen and take 80 cores. We can run in 5-6h all iterations for w = 2^17

experiments = [ (24, 17) ] # (24, 16) ]

ncpus = 16 # min(psutil.cpu_count(logical=True), math.floor(psutil.cpu_count(logical=False) * 1.4)) - 1

ITERS = 1

# We have set the cycles for function iterations to be ~ 1 million cycles. 
# We want to verify that a function iterations that computes that many points incurs in the appropriate slowdown

def predicted_time(log_n, log_w):
    # Assumes 1million cycles per func iter and 4 Ghz
    inv_theta = 1/(2.25 * math.sqrt(2**(log_w - log_n)))
    return ITERS * (inv_theta * 10**6 * 10 * 2**log_w / (4 * 10**9 * ncpus)) / 3600

def predicted_cycles(num_steps, calibrated_cycles):
    return num_steps * calibrated_cycles / ncpus

def parse_cycles(ls: str):
    readings = []
    for l in ls.splitlines():
        if 'core benchmark' in l:
            l = l.strip()
            cycle_counts = l.split(':')[1].strip().split(' ')
            cycle_counts = [float(s.strip()) for s in cycle_counts]
            readings.append(cycle_counts)
    return readings

def cycles_backup(n, w, cycles):
    with open('cycles_backup', 'w') as f:
        f.write(json.dumps({ 'n': n, 'w': w, 'cycles': cycles}))

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
   index = f'{n}_{w}'
   cmd_run = subprocess.run(f"python gen.py -min_cpus {ncpus} -max_cpus {ncpus} -min_mem {w} -max_mem {w} -min_nbits {n} -max_nbits {n} -no_hag -iterations {ITERS}".split(' '), capture_output=True, text=True)
   print(cmd_run.stdout)
   cycles_parsed = parse_cycles(cmd_run.stdout)
   cycles_backup(n, w, cycles_parsed)
   calibrated_cycles[index] = cycles_parsed
   
   
aggregated_res = {}
with open('gen_full_atk_False_hag_False') as f:
    lines = list(f)
    dicts = [json.loads(l) for l in lines]
    for exp in dicts:
        n, w, _, _ = exp['k']
        index = index = f'{n}_{w}'
        cycle_data = calibrated_cycles[index]
        full_record = []
        for run_record in exp['v']['full_data']:
            associated_cycles = cycle_data[run_record['salt'] - 1]
            num_steps = run_record['num_steps']
            avg_cycle_per_step = sum(associated_cycles)/len(associated_cycles)
            exp_cycles = avg_cycle_per_step * num_steps / ncpus
            actual_cycles = run_record['cycles']
            r = {
                    'num_steps': num_steps,
                    'benchmarked_cycles': calibrated_cycles,
                    'expected_cycles' : exp_cycles,
                    'actual_cycles' : actual_cycles,
                    'ratio': actual_cycles / exp_cycles
                }
            full_record.append(r)
        record = {'n': n, 'w': w, 'full_data' : full_record }
        aggregated_res[index] = record
        
with open('aggregated_function_iterations_readings.json', 'w') as output:
    json.dump(aggregated_res, output)
