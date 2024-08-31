#include <stdio.h>
#include <stdint.h>

uint32_t slice(uint32_t num, size_t start, size_t stop)
{
    // returns bit slice between start and stop at num
    if (start == 0 && stop == 32)
    {
        return num;
    }
    uint64_t mask = (1 << (stop - start)) - 1;
    return (num >> 32 - stop) & mask;
}
