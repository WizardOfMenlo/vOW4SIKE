from math import sqrt, log2

cpus = 128
time_per_func_iter_low = 40
time_per_func_iter_high = 2 * time_per_func_iter_low
hours = 8
exp_iters = 100

total_func_iters = 128 * 8 * 3600 * 1e6 / time_per_func_iter_high
func_iters_per_single_exp = total_func_iters / 100

budget = func_iters_per_single_exp / (1.2 * 4.4)

print(log2(budget))

def calculate(ls):
    s = 0
    for n,w in ls:
        s += sqrt(2**(n+w))
    return log2(s)
