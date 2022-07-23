#include <cassert>
#include <omp.h>
#include "vow.hpp"
#include "utils/busy_wait.hpp"
#include "utils/cycles.h"

/**
 * @brief find a number of points and measure how long it takes on the avaliable core
 */
template <class Point, class Memory, class RandomFunction, class PRNG, class Instance>
void vOW<Point, Memory, RandomFunction, PRNG, Instance>::benchmark(uint64_t target_number_of_points, double* eval_calibration, double* mem_calibration)
{
    double total_tp = 0.;
    double *benchmark;
    vOW<Point, Memory, RandomFunction, PRNG, Instance> benchmark_vow(instance);

    #ifdef STORE_IN_DATABASE
    db_settings_t db_settings = load_db_settings();
    #endif

    // init a state from an instance, and set the number of threads to 1
    benchmark_vow.instance->N_OF_CORES = 1;

    // Explicitly disable dynamic teams
    omp_set_dynamic(0);

    // allocate memory for benchmark
    benchmark = (double *)malloc(instance->N_OF_CORES * sizeof(double));
    if (benchmark == NULL)
    {
        fprintf(stderr, "error: could not allocate memory for the benchmarks");
        assert(0);
    }

    // run benchmark on each core
    #pragma omp parallel num_threads(instance->N_OF_CORES)
    {
        int thread_id = omp_get_thread_num();

        private_state_t<Point, PRNG, RandomFunction, Instance> benchmark_ps(
            benchmark_vow.instance
        );
        Trip<Point, Instance> t(benchmark_vow.instance);

        double wall_time = omp_get_wtime();
        for (uint64_t i = 0; i < target_number_of_points; i++)
        {
            benchmark_vow.iteration(benchmark_ps, t, 1.);
        }
        wall_time = omp_get_wtime() - wall_time;

        double tp = 1 / wall_time;
        // save result
        benchmark[thread_id] = tp;
        #pragma omp atomic
        total_tp += tp;
    }

    // printf("benchmark: ");
    // for (int i = 0; i < instance->N_OF_CORES; i++)
    // {
    //     printf("%g ", benchmark[i]);
    // }
    // printf("\n");

    // send benchmark information to database and recover ratios
    #ifdef STORE_IN_DATABASE
    fprintf(stderr, "error: rrprf_from_benchmark not implemented\n");
    #else
    for (uint64_t i = 0; i < instance->N_OF_CORES; i++)
    {
        points_ratio[i] = benchmark[i] / total_tp;
    }
    #endif

    free(benchmark);

    #define WARMUP_ITERS 100000
    #define BENCH_ITERS 10000

    // We run some benchmark for each cores to get the cost of function step
    #pragma omp parallel num_threads(instance->N_OF_CORES)
    { 
        int thread_id = omp_get_thread_num();
        
        private_state_t<Point, PRNG, RandomFunction, Instance> benchmark_ps(
            benchmark_vow.instance
        );

        // Warmup 
        for (int i = 0; i < WARMUP_ITERS; i++) {
            benchmark_vow.step(benchmark_ps);
        }

        int64_t start = cpu_cycles();
        for (int i = 0; i < BENCH_ITERS; i++) {
            benchmark_vow.step(benchmark_ps);
        }
        int64_t end = cpu_cycles();

        eval_calibration[thread_id] = ((double) (end - start))/BENCH_ITERS;
        
        Trip<Point, Instance> t(benchmark_vow.instance);
        Trip<Point, Instance> t_1(benchmark_vow.instance);

        // TODO: Make pseudorandom
        for (int i = 0; i < WARMUP_ITERS; i++) {
            benchmark_vow.memory->send_point(&t, 0, &t_1);
        }

        start = cpu_cycles();
        for (int i = 0; i < BENCH_ITERS; i++) {
            benchmark_vow.memory->send_point(&t, 0, &t_1);
        }
        end = cpu_cycles();

        mem_calibration[thread_id] = ((double) (end - start))/BENCH_ITERS;

    }
}

#include "templating/vow.inc"
