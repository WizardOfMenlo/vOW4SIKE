#include "timespec_ops.hpp"

struct timespec diff_timespec(const struct timespec *time1,
    const struct timespec *time0) {
  struct timespec diff = {.tv_sec = time1->tv_sec - time0->tv_sec, .tv_nsec =
      time1->tv_nsec - time0->tv_nsec};
  if (diff.tv_nsec < 0) {
    diff.tv_nsec += 1000000000;
    diff.tv_sec--;
  }
  return diff;
}


struct timespec add_timespec(const struct timespec *time1,
    const struct timespec *time0) {
  struct timespec sum = {.tv_sec = time1->tv_sec + time0->tv_sec, .tv_nsec =
      time1->tv_nsec + time0->tv_nsec};
  if (sum.tv_nsec >= 1000000000) {
    sum.tv_nsec -= 1000000000;
    sum.tv_sec++;
  }
  return sum;
}
