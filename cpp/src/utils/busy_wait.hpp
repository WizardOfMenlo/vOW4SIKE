#include <stdint.h>

// Should be relatively accurate but hey what do I know
void busy_wait_cycles(uint64_t cycles);

// Around 4 cycles per iteration according to our assembly
void __attribute__ ((noinline)) busy_wait(uint64_t iterations);
