#include <stdio.h>
#include <stdint.h>

uint32_t slice32(uint32_t num, size_t start, size_t stop)
{
    // returns bit slice between start and stop for 32 bit num
    if (start == 0 && stop == 32)
    {
        return num;
    }
    uint64_t mask = (1 << (stop - start)) - 1;
    return (num >> 32 - stop) & mask;
}

uint8_t slice8(uint8_t num, size_t start, size_t stop)
{
    // returns bit slice between start and stop for 8 bit num
    if (start == 0 && stop == 8)
    {
        return num;
    }
    uint64_t mask = (1 << (stop - start)) - 1;
    return (num >> 8 - stop) & mask;
}
