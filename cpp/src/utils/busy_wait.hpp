#include <stdint.h>


#define MILLION_CYCLES (1226415)

void __attribute__ ((noinline)) busy_wait(uint64_t iterations);
