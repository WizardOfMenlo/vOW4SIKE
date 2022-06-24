#pragma once
#include <cstdint>
#include <exception>
#include <time.h>
#include "../config.h"
#include "../types/triples.hpp"
#include "../types/state.hpp"

template <class Point, class Instance>
class IMemory
{
    public:
        virtual bool send_point(Trip<Point, Instance> *t, uint64_t address, Trip<Point, Instance> *read_ptr, struct timespec* elapsed);
        virtual void reset() = 0;
};

class memory_exception : public std::exception
{
  virtual const char* what() const throw()
  {
    return "Could not initialise memory";
  }
};
