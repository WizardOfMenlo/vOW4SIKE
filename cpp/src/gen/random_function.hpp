#pragma once
#include <cstdint>
#include <time.h>
#include "instance.hpp"
#include "../types/random_function.hpp"
#include "../types/points.hpp"
#include "../prng/interface.hpp"

template <class Point>
class GenRandomFunction : public IRandomFunction<Point>
{
protected:
    void sample_preimages(uint64_t _seed);
public:
    Point *preimages[2];
    uint64_t function_version;
    Point *image;
    struct timespec sleep_elapsed_time;
    struct timespec delay;
    bool should_delay;


    GenRandomFunction(GenInstance *instance);
    virtual ~GenRandomFunction();
    void seed(uint64_t _seed);
    void update();
    void eval(Point &out, Point &in);
    void eval(Point &x);
};
