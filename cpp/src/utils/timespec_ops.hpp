#pragma once

#include <time.h>

struct timespec diff_timespec(const struct timespec *time1, const struct timespec *time0);
struct timespec add_timespec(const struct timespec *time1, const struct timespec *time0);
