import subprocess
import math
import glob
import sympy
import json
from joblib import Parallel, delayed
from itertools import product

# TODO: Build using the new MEMORY_FILLING_INSTR to enable that instrumentation

def expected_points_to_fill(log_n: int, log_w: int, theta: float) -> float:
      res = 0
      n = 2**log_n
      dist = theta * 2**log_n
      w = 2**log_w
      inv_theta = 1 / theta 

      exp_coeff = n / inv_theta**2

      for k in range(0, w):
          term = math.exp(-k / exp_coeff)*(1 - k/dist)*(1 - k/w)
          res += 1/term
      return res

ITERS = 128
N_JOBS = 16

def run_one_simulation(n: int, w: int):
    theta = 2.25 * math.sqrt(2**(w-n))
    exp = expected_points_to_fill(n, w, theta)
    beta = max(10, round(3 * (exp / 2**w)))
    print(beta)
    subprocess.run(f"python gen.py -min_cpus 16 -max_cpus 16 -min_mem {w} -max_mem {w} -min_nbits {n} -max_nbits {n} -min_beta {beta} -max_beta {beta} -iterations {ITERS} -no_hag".split(' '))

def job(n, w):
    if n > w:
        run_one_simulation(n, w)

num_cpus = 16

n_range = range(20, 32, 2)
w_range = range(8, 26, 2)

#Parallel(n_jobs=N_JOBS)(delayed(job)(n, w) for n,w in product(n_range, w_range))


filenames = glob.glob('memory_consumption_m=*')

results = []

for name in filenames:
    n_split = name.strip().split('_')
    w = int(n_split[2].replace('m=', ''))
    n = int(n_split[3].replace('n=', ''))

    js = {
            'n' : n,
            'w' : w,
            'readings' : [],
            'averages' : {},
            'expected': {}
            }

    with open(name, 'r') as f:
        lines = list(f)
        for line in lines:
            dist_points = int(line.split('with')[1].replace('dist points', '').strip())
            js['readings'].append(dist_points)

    avg_dist = sum(js['readings'])/len(js['readings'])

    theta = 2.25 * math.sqrt(2**(w-n))

    js['averages']['readings'] = len(js['readings'])
    js['averages']['avg_dist'] = avg_dist
    js['expected']['linear'] = 2**w
    js['expected']['coupon_standard'] = 2**w * math.log(2**w) + float(sympy.EulerGamma) * (2**w) + 0.5
    js['expected']['coupon_advanced'] = expected_points_to_fill(n, w, theta)
    js['expected']['linear_ratio'] = avg_dist / js['expected']['linear']
    js['expected']['coupon_standard_ratio'] = avg_dist / js['expected']['coupon_standard']
    js['expected']['coupon_advanced_ratio'] = avg_dist / js['expected']['coupon_advanced']

    results.append(js)

with open('aggregated_mem.json', 'w') as output:
    print(results)
    json.dump(results, output)
