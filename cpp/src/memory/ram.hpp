#pragma once

#include "interface.hpp"
#include "../types/instance.hpp"
#include "../types/triples.hpp"
#include <atomic>

template <class Point, class Instance>
class LocalMemory : public IMemory<Point, Instance>
{
    protected:
        uint64_t max_entries;
        Trip<Point, Instance> **memory;
    public:
        LocalMemory(uint64_t _max_entries, Instance *instance);
        virtual ~LocalMemory();
        bool send_point(Trip<Point, Instance> *t, uint64_t address, Trip<Point, Instance> *read_ptr);
        void reset();
};
