#include <stdint.h>


#define BILLION_CYCLES (1300000000)

void __attribute__ ((noinline)) busy_wait(uint64_t iterations);
