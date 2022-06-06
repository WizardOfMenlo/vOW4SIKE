#include "busy_wait.hpp"


// TODO: Allow for some calibration
void busy_wait(uint64_t iterations) {
    for (uint64_t i = 0; i < iterations; i++) {
        __asm__ volatile("" : "+g" (i) : :);
    }
}
