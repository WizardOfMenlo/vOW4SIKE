import subprocess
import json
import os


n_sizes_exp = [10, 14, 18, 20]
w_sizes_exp = [8, 10, 12]

for n in n_sizes_exp:
    for w in w_sizes_exp:
        # Skip since else we complain
        if n < w:
            continue
        subprocess.run(
            f"python gen.py -min_cpus 16 -max_cpus 16 -min_mem {w} -max_mem {w} -min_nbits {n} -max_nbits {n} -min_beta {beta} -max_beta {beta} -no_hag -run_full_atk".split(' '))

aggregated_res = {}

# Once we are done parse the resulting
with open('gen_full_atk_True_hag_False', 'r') as f:
    lines = list(f)
    dicts = [json.loads(l) for l in lines]
    for d in dicts:
        nbits_state, memory_log_size, _, beta = d['k']
        num_steps = d['v']['num_steps']

        key = (nbits_state, memory_log_size)
        if key not in aggregated_res:
            aggregated_res[key] = {'n' : nbits_state, 'w': memory_log_size, 'experiments': [] }
        aggregated_res[key]['experiments'].append({'beta': beta, 'num_steps': num_steps })
        
augmented_res = {}

for parameter_set, record in aggregated_res.items():
    min_exp = min(record['experiments'], key=lambda x: x['num_steps'])
    min_beta = min_exp['beta']
    min_steps = min_exp['num_steps']

    new_records = []
    for exp in record['experiments']:
        ratio = exp['num_steps'] / min_steps
        new_record = {'beta': exp['beta'], 'num_steps': exp['num_steps'], 'ratio': ratio}
        new_records.append(new_record)
    
    augmented_res[parameter_set] = {
        'n': parameter_set[0],
        'w': parameter_set[1],
        'min_beta': min_beta,
        'min_steps': min_steps,
        'experiments': new_records
    }
    
with open('aggregated_beta.json', 'w') as output:
    json.dump(augmented_res, output)