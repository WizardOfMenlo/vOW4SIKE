#include <cstdlib>
#include <cstdint>
#include <iostream>
#include <fstream>
#include "../utils/memavail.h"
#include "ram.hpp"

template <class Point, class Instance>
LocalMemory<Point, Instance>::LocalMemory(uint64_t _max_entries, Instance *instance)
{
    #ifdef MEMORY_FILLING_INSTR
    current_memory_filling = 0;
    distinguished_points = 0;
    dumped = false;
    filename = std::string("memory_consumption_m=") + std::to_string(instance->MEMORY_LOG_SIZE) + "_n=" + std::to_string(instance->NBITS_STATE);
    #endif
    
    max_entries = _max_entries;
    uint64_t total_cost = max_entries * (
        sizeof(Trip<Point, Instance> *)
        + sizeof(Trip<Point, Instance>)
        + 2 * (
            sizeof(Point)
            + sizeof(digit_t) * instance->NWORDS_STATE
        )
    );
    unsigned long long max_mem_avail = memavail();

    if (total_cost > max_mem_avail)
    {
        std::cout << "Maximum available memory is " << max_mem_avail << " bytes." << std::endl << std::endl;

        std::cout << "Trying to alloc " << max_entries * sizeof(Trip<Point, Instance> *) << " bytes for pointers." << std::endl << std::endl;
        std::cout   << "Sizes are" << std::endl
                    << "Trip<Point, Instance> * " << sizeof(Trip<Point, Instance> *) << "bytes," << std::endl
                    << "Trip<Point, Instance>   " << sizeof(Trip<Point, Instance>) << "bytes," << std::endl
                    << "IPoint        " << sizeof(IPoint) << "bytes," << std::endl
                    << "Point         " << sizeof(Point) << "bytes," << std::endl
                    << "state         " << sizeof(digit_t) * instance->NWORDS_STATE << "bytes." << std::endl << std::endl;


        uint64_t total_reduced_cost = max_entries * (
            sizeof(Trip<Point, Instance> *)        // 8 bytes
            + sizeof(Trip<Point, Instance>)        // 24 bytes
            + 2 * (
                sizeof(Point)
                + instance->NBYTES_STATE
            )
        );

        uint64_t total_min_cost = max_entries * (
            sizeof(Trip<Point, Instance> *)        // 8 bytes
            + sizeof(Trip<Point, Instance>)        // 24 bytes
            + 2 * (
                8 + instance->NBYTES_STATE 
            )
        );

        std::cout << "Total memory usage would be " << total_cost << " bytes, or " 
                  << total_cost/1073741824. << " gigabytes." << std::endl << std::endl;

        std::cout << "Could allocates bytes rather than digit_t in the Point implementation" 
                  << " and reduce to " << total_reduced_cost/1073741824. << " gigabytes." << std::endl << std::endl;

        std::cout << "Could probably reduce more by removing pointer to word in IPoint union,"
                  << " and pointers to instance in Point, to get to "<< total_min_cost/1073741824. << " gigabytes." << std::endl << std::endl;

        memory_exception mem_ex;
        throw mem_ex;
    }
    
    if ((memory = (Trip<Point, Instance> **)calloc(max_entries, sizeof(Trip<Point, Instance> *))) == NULL)
    {
        memory_exception mem_ex;
        throw mem_ex;
    }
    for (uint64_t i = 0; i < max_entries; i++)
    {
        memory[i] = new Trip<Point, Instance>(instance);
    }
}


template <class Point, class Instance>
LocalMemory<Point, Instance>::~LocalMemory()
{
    for (uint64_t i = 0; i < max_entries; i++)
    {
        delete memory[i];
    }
    free(memory);
}

template <class Point, class Instance>
bool LocalMemory<Point, Instance>::send_point(Trip<Point, Instance> *t, uint64_t address, Trip<Point, Instance>* read_ptr)
{
    // Read into the ptr that we have been given
    read_ptr->from_trip(memory[address]);

    // Write the final point
    memory[address]->from_trip(t);

    return true;
}

template <class Point, class Instance>
void LocalMemory<Point, Instance>::reset()
{
    for (uint64_t i = 0; i < max_entries; i++)
    {
        memory[i]->reset();
    }
}

// template
#include "../templating/memory.inc"
