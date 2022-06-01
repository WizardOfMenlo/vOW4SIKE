import subprocess
import json
import hashlib
import psutil
import math


experiments = [
            
            # Should take ~ 3m * 50 = 2.5h x 7 ~ 18 h * 7 ~ 5 days
            (24, 12, 50), (24, 13, 50), (24, 14, 50), (24, 16, 50), (24, 17, 50), (24, 19, 50), (24, 20, 50),

            # Should take ~ 2m * 50 ~ 1.6 h x 3 ~ 5h * 7 ~ 1.5 days
            (32, 22, 50), (32, 23, 50), (32, 26, 50),
            
            # vow original (should we include this?)
            #(32, 10, 50),
            ]

ncpus = min(psutil.cpu_count(logical=True), math.floor(psutil.cpu_count(logical=False) * 1.4)) - 1

print(""" __    __  __                            __  __  __                 
        /  |  /  |/  |                          /  |/  |/  |                
        $$ | /$$/ $$ |  ______   _______    ____$$ |$$/ $$ |   __   ______  
        $$ |/$$/  $$ | /      \ /       \  /    $$ |/  |$$ |  /  | /      \ 
        $$  $$<   $$ |/$$$$$$  |$$$$$$$  |/$$$$$$$ |$$ |$$ |_/$$/ /$$$$$$  |
        $$$$$  \  $$ |$$ |  $$ |$$ |  $$ |$$ |  $$ |$$ |$$   $$<  $$    $$ |
        $$ |$$  \ $$ |$$ \__$$ |$$ |  $$ |$$ \__$$ |$$ |$$$$$$  \ $$$$$$$$/ 
        $$ | $$  |$$ |$$    $$/ $$ |  $$ |$$    $$ |$$ |$$ | $$  |$$       |
        $$/   $$/ $$/  $$$$$$/  $$/   $$/  $$$$$$$/ $$/ $$/   $$/  $$$$$$$/ 
                                                                            
                                                                                                                                                
                                                                                                                                                                                                                    """)
print('Welcome! Will be running the following experiments: ')
print(experiments)
print(f'We will be using {ncpus}')
print('Sit back and enjoy the ride!')

def range_of_betas(log_w: int) -> list[int]:
    possible_optimal = round(math.log(2**log_w))
    betas = list(set([10] + list(range(possible_optimal - 3, possible_optimal + 3))))
    return [b for b in betas if b > 0]

for n, w, ITERS in experiments:
        # Skip since else we complain
        if n <= w:
            continue
        for beta in range_of_betas(w):
            for i in range(ITERS):
                seed = int.from_bytes(hashlib.shake_128('_'.join(str(x) for x in [n, w, beta, i]).encode()).digest(7), 'big') + 1
                subprocess.run(
                    f"python3 gen.py -seed {seed} -min_cpus {ncpus} -max_cpus {ncpus} -min_mem {w} -max_mem {w} -min_nbits {n} -max_nbits {n} -min_beta {beta} -max_beta {beta} -no_hag -run_full_atk".split(' '))

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
