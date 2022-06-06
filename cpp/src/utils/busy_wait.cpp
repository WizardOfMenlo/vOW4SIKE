#include "busy_wait.hpp"

void busy_wait_cycles(uint64_t cycles) {
    busy_wait(cycles >> 2);
}

void busy_wait(uint64_t iterations) {
    for (uint64_t i = 0; i < iterations; i++) {
        __asm__ volatile("" : "+g" (i) : :);
    }
}
