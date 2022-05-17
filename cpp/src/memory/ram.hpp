#pragma once

#include "interface.hpp"
#include "../types/instance.hpp"
#include "../types/triples.hpp"
#include <atomic>

template <class Point, class Instance>
class LocalMemory : public IMemory<Point, Instance>
{
    #ifdef MEMORY_FILLING_INSTR
    private:
        std::atomic_uint64_t current_memory_filling;
        std::atomic_uint64_t distinguished_points;
        std::string filename;
        std::atomic_bool dumped;
    #endif
    protected:
        uint64_t max_entries;
        Trip<Point, Instance> **memory;
    public:
        LocalMemory(uint64_t _max_entries, Instance *instance);
        virtual ~LocalMemory();
        Trip<Point, Instance> *operator[](uint64_t i);
        bool read(Trip<Point, Instance> **t, uint64_t address);
        void write(Trip<Point, Instance> *t, uint64_t address);
        void reset();
};
