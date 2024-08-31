// MAIN FILE

// LIBRARY INCLUSIONS
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#include "definitions.h"
#include "printlib.h"
#include "utils.h"
#include "bufferlib.h"

void get_bits(uint32_t *arr, uint32_t *buffer_arr, size_t rows, size_t cols, size_t start, size_t stop, uint32_t fill);
void put_bits(uint32_t *arr, uint32_t *buffer_arr, size_t rows, size_t cols, size_t start, size_t stop);

// int main(int argc, char **argv)
// {
//     // Test code for get_bits and put_bits
//     uint32_t arr[9] = {1, 2, 3, 4, 5, 6, 7, 8, 9};

//     int rows = 3;
//     int cols = 3;

//     uint32_t start, stop;
//     start = 0, stop = 32;
//     uint32_t bit_length = rows * cols * (stop - start);

//     uint32_t size = bit_length / 32 + 1;
//     uint32_t *buffer_arr = calloc(size, 4);

//     uint32_t fill = 3269625783;

//     get_bits(arr, buffer_arr, rows, cols, start, stop, fill);

//     uint32_t putarr[9] = {0, 0, 0, 0, 0, 0, 0, 0, 0};

//     put_bits(putarr, buffer_arr, rows, cols, start, stop);

//     print_uint32_arr_b(3, 3, putarr); // should equal arr

//     free(buffer_arr);
//     printf("FINISHED");

//     return 0;
// }

void get_bits(uint32_t *arr, uint32_t *buffer_arr, size_t rows, size_t cols, size_t start, size_t stop, uint32_t fill)
{
    // for every element of arr (a matrix), appends bit slice between start and stop to the buffer buffer_arr
    // expects an empty buffer array buffer_arr
    assertmsg(0 <= start <= 31, "Error: start must be between 0 and 31.");
    assertmsg(1 <= start <= 32, "Error: stop must be between 1 and 32.");
    assertmsg(start < stop, "Error: mis-ordered start/stop.");

    Buffer buffer;
    uint32_t len = stop - start;
    uint32_t bit_length = rows * cols * len;
    init_buffer(&buffer, buffer_arr, bit_length, len);

    for (int i = 0; i < rows; i++)
    {
        for (int j = 0; j < cols; j++)
        {
            extend(&buffer, slice(arr[i * cols + j], start, stop));
        }
    }
    fill_buffer(&buffer, fill);

}

void put_bits(uint32_t *arr, uint32_t *buffer_arr, size_t rows, size_t cols, size_t start, size_t stop)
{
    // inserts one block of buffer_arr into every element of materix arr between bit locations start and stop

    assertmsg(0 <= start <= 31, "Error: start must be between 0 and 31.");
    assertmsg(1 <= start <= 32, "Error: stop must be between 1 and 32.");
    assertmsg(start < stop, "Error: mis-ordered start/stop.");

    Buffer buffer;
    uint32_t len = stop - start;
    uint32_t bit_length = rows * cols * len;
    init_buffer(&buffer, buffer_arr, bit_length, len);

    for (int i = 0; i < rows; i++)
    {
        for (int j = 0; j < cols; j++)
        {
            uint32_t block = next_block(&buffer);                                                // get next block of buffer
            arr[i * cols + j] ^= (slice(arr[i * cols + j], start, stop) ^ block) << (32 - stop); // insert in matrix element
        }
    }
}