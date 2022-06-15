import subprocess
import json
import math

experiments = [(20, 10), (22, 14), (26, 16), (28, 18), (30, 20)]

# Use all 128 cores
ncpus = 128 # min(psutil.cpu_count(logical=True), math.floor(psutil.cpu_count(logical=False) * 1.4)) - 2


# 100 iterations per function version
ITERS = 100


# Each function call is at least 40 microseconds (hopefully not twice that)

def predicted_time_low(log_n, log_w):
    # Assumes 1ms per func iter
    inv_theta = 1/(2.25 * math.sqrt(2**(log_w - log_n)))
    num_iterations = ITERS * (inv_theta * 10 * 2**log_w)
    # Each iterations is 10 microseconds
    time_iter = 40 * 1e-6
    return num_iterations * time_iter / ncpus


def predicted_time_high(log_n, log_w):
    # Assumes 1ms per func iter
    inv_theta = 1/(2.25 * math.sqrt(2**(log_w - log_n)))
    num_iterations = ITERS * (inv_theta * 10 * 2**log_w)
    # Each iterations is 10 microseconds
    time_iter = 80 * 1e-6
    return num_iterations * time_iter / ncpus

# Returns a list of in the order that they appear
def parse_sleeps(output: str):
    res = []
    for l in output.splitlines():
        if 'sleep times' in l:
            l = l.strip()
            cycle_counts = l.split(':')[1].strip().split(' ')
            cycle_counts = [float(s.strip()) for s in cycle_counts]
            res.append(cycle_counts)
    return res
    
def sleep_backups(n, w, sleeps):
    with open('sleep_backup', 'w') as f:
        f.write(json.dumps({'n': n, 'w': w, 'sleeps': sleeps}) + '\n')

total_time = 0
for n, w in experiments:
    if n <= w:
        continue
    pred_low, pred_high = predicted_time_low(n, w), predicted_time_high(n, w)
    print(f'Estimate: [{pred_low}, {pred_high}]s')
    total_time += pred_high

print('Total: ', total_time)

sleep_dictionary = {}
for n, w in experiments:
   index = f'{n}_{w}' 
   cmd_run = subprocess.run(f"python gen.py -min_cpus {ncpus} -max_cpus {ncpus} -min_mem {w} -max_mem {w} -min_nbits {n} -max_nbits {n} -no_hag -iterations {ITERS}".split(' '), capture_output=True, text=True)
   print(cmd_run.stdout)
   sleeps = parse_sleeps(cmd_run.stdout)
   # Make sure not to loose our work
   sleep_backups(n, w, sleeps)
   sleep_dictionary[index] = sleeps
   
   
aggregated_res = {}
with open('gen_full_atk_False_hag_False') as f:
    lines = list(f)
    dicts = [json.loads(l) for l in lines]
    for exp in dicts:
        n, w, _, _ = exp['k']
        index = f'{n}_{w}' 
        sleep_data = sleep_dictionary[index]
        full_record = []
        for run_record in exp['v']['full_data']:
            associated_sleeps = sleep_data[run_record['salt'] - 1]
            exp_total_time = sum(associated_sleeps)

            # We use these to compute the exact t_{c, i}
            # Then retrofit these to the model
            num_steps = run_record['num_steps']
            share_per_core = [s/sum(associated_sleeps) for s in associated_sleeps]
            time_per_point_on_each_core = [associated_sleeps[i] / (share_per_core[i] * num_steps) for i in range(len(share_per_core))]
            r = {
                    'wall_time' : run_record['wall_time'],
                    'total_time': run_record['total_time'],
                    'sleeps': associated_sleeps,
                    'exp_total_time_func_evals': exp_total_time,
                    'ratio_only_func_evals': run_record['total_time'] / exp_total_time,
                    'time_per_point_on_each_core': time_per_point_on_each_core
                    }
            full_record.append(r)

        record = {'n': n, 'w': w, 'full_data': full_record}
        aggregated_res[index] = record

        
with open('aggregated_sleep_function_iterations_readings.json', 'w') as output:
    json.dump(aggregated_res, output)
