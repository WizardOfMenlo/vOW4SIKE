import subprocess
import json
import hashlib
import psutil
import math


n_sizes_exp = [30]
w_sizes_exp = [24]

ITERS = 10

ncpus = min(psutil.cpu_count(logical=True), math.floor(psutil.cpu_count(logical=False) * 1.4)) - 1

def range_of_betas(log_w: int) -> list[int]:
    possible_optimal = round(math.log(2**log_w))
    betas = list(set([10] + list(range(possible_optimal - 3, possible_optimal + 3))))
    return [b for b in betas if b > 0]

"""
for n in n_sizes_exp:
    for w in w_sizes_exp:
        # Skip since else we complain
        if n <= w:
            continue
        for beta in range_of_betas(w):
            for i in range(ITERS):
                seed = int.from_bytes(hashlib.shake_128('_'.join(str(x) for x in [n, w, beta, i]).encode()).digest(7), 'big') + 1
                subprocess.run(
                    f"python gen.py -seed {seed} -min_cpus {ncpus} -max_cpus {ncpus} -min_mem {w} -max_mem {w} -min_nbits {n} -max_nbits {n} -min_beta {beta} -max_beta {beta} -no_hag -run_full_atk".split(' '))
"""

# Once we are done parse the resulting
aggregated_res = {}
with open('gen_full_atk_True_hag_False', 'r') as f:
    lines = list(f)
    dicts = [json.loads(l) for l in lines]
    for d in dicts:
        nbits_state, memory_log_size, _, beta = d['k']
        num_steps = d['v']['num_steps']

        key = str(nbits_state)+'_'+str(memory_log_size)
        if key not in aggregated_res:
            aggregated_res[key] = {'n' : nbits_state, 'w': memory_log_size, 'experiments': {} }
        if beta not in aggregated_res[key]['experiments']:
            aggregated_res[key]['experiments'][beta] = {'beta' : beta, 'experiments': [] }
        aggregated_res[key]['experiments'][beta]['experiments'].append(num_steps)

augmented_res = {}

for parameter_set, record in aggregated_res.items():
    for beta in record['experiments'].keys():
        exps = record['experiments'][beta]['experiments']
        avg = sum(exps)/len(exps)
        record['experiments'][beta]['avg_steps'] = avg

    min_exp = min(record['experiments'].values(), key=lambda x: x['avg_steps'])
    min_beta = min_exp['beta']
    min_steps = min_exp['avg_steps']

    new_records = []
    for exp in record['experiments'].values():
        ratio = exp['avg_steps'] / min_steps
        new_record = {'beta': exp['beta'], 'num_steps': exp['avg_steps'], 'ratio': ratio}
        new_records.append(new_record)
    
    augmented_res[parameter_set] = {
        'n': record['n'],
        'w': record['w'],
        'min_beta': min_beta,
        'min_steps': min_steps,
        'experiments': new_records
    }
    
with open('aggregated_beta.json', 'w') as output:
    json.dump(augmented_res, output)
