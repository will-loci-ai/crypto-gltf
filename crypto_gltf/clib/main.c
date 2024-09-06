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

void get_bits32(uint32_t *arr, uint32_t *buffer_arr, size_t rows, size_t cols, size_t start, size_t stop, uint32_t fill);
void put_bits32(uint32_t *arr, uint32_t *buffer_arr, size_t rows, size_t cols, size_t start, size_t stop);

void get_bits8(uint8_t *arr, uint32_t *buffer_arr, size_t rows, size_t cols, size_t slices, size_t start, size_t stop, uint32_t fill);
void put_bits8(uint8_t *arr, uint32_t *buffer_arr, size_t rows, size_t cols, size_t slices, size_t start, size_t stop);


void get_bits32(uint32_t *arr, uint32_t *buffer_arr, size_t rows, size_t cols, size_t start, size_t stop, uint32_t fill)
{
    // for every element of arr (a matrix), appends bit slice between start and stop to the buffer buffer_arr
    // expects an empty buffer array buffer_arr
    // arr must be of bit length 32

    assertmsg((0 <= start) && (start <= 31), "Error: start must be between 0 and 31.");
    assertmsg((1 <= stop) && (stop <= 32), "Error: stop must be between 1 and 32.");
    assertmsg(start < stop, "Error: mis-ordered start/stop.");

    Buffer buffer;
    uint32_t len = stop - start;
    uint32_t bit_length = rows * cols * len;
    init_buffer(&buffer, buffer_arr, bit_length, len);

    for (int i = 0; i < rows; i++)
    {
        for (int j = 0; j < cols; j++)
        {
            extend(&buffer, slice32(arr[i * cols + j], start, stop));
        }
    }
    fill_buffer(&buffer, fill);
}

void put_bits32(uint32_t *arr, uint32_t *buffer_arr, size_t rows, size_t cols, size_t start, size_t stop)
{
    // inserts one block of buffer_arr into every element of materix arr between bit locations start and stop
    // arr must be of bit length 32

    assertmsg((0 <= start) && (start <= 31), "Error: start must be between 0 and 31.");
    assertmsg((1 <= stop) && (stop <= 32), "Error: stop must be between 1 and 32.");
    assertmsg(start < stop, "Error: mis-ordered start/stop.");

    Buffer buffer;
    uint32_t len = stop - start;
    uint32_t bit_length = rows * cols * len;
    init_buffer(&buffer, buffer_arr, bit_length, len);

    for (int i = 0; i < rows; i++)
    {
        for (int j = 0; j < cols; j++)
        {
            uint32_t block = next_block(&buffer);                                                  // get next block of buffer
            arr[i * cols + j] ^= (slice32(arr[i * cols + j], start, stop) ^ block) << (32 - stop); // insert in matrix element
        }
    }
}

void get_bits8(uint8_t *arr, uint32_t *buffer_arr, size_t rows, size_t cols, size_t slices, size_t start, size_t stop, uint32_t fill)
{
    // for every element of arr (a matrix), appends bit slice between start and stop to the buffer buffer_arr
    // expects an empty buffer array buffer_arr
    // arr must be of bit length 8

    assertmsg((0 <= start) && (start <= 7), "Error: start must be between 0 and 7.");
    assertmsg((1 <= stop) && (stop <= 8), "Error: stop must be between 1 and 8.");
    assertmsg(start < stop, "Error: mis-ordered start/stop.");

    Buffer buffer;
    uint32_t len = stop - start;
    uint32_t bit_length = rows * cols * slices * len;
    init_buffer(&buffer, buffer_arr, bit_length, len);

    for (int i = 0; i < rows; i++)
    {
        for (int j = 0; j < cols; j++)
        {
            for (int k = 0; k < slices; k++)
            {
                extend(&buffer, slice8(arr[i * cols * slices + j * slices + k], start, stop));
            }
        }
    }
    fill_buffer(&buffer, fill);
}

void put_bits8(uint8_t *arr, uint32_t *buffer_arr, size_t rows, size_t cols, size_t slices, size_t start, size_t stop)
{
    // inserts one block of buffer_arr into every element of materix arr between bit locations start and stop
    // arr must be of bit length 32

    assertmsg((0 <= start) && (start <= 7), "Error: start must be between 0 and 7.");
    assertmsg((1 <= stop) && (stop <= 8), "Error: stop must be between 1 and 8.");
    assertmsg(start < stop, "Error: mis-ordered start/stop.");

    Buffer buffer;
    uint32_t len = stop - start;
    uint32_t bit_length = rows * cols * slices * len;
    init_buffer(&buffer, buffer_arr, bit_length, len);

    for (int i = 0; i < rows; i++)
    {
        for (int j = 0; j < cols; j++)
        {
            for (int k = 0; k < slices; k++)
            {
                uint8_t block = next_block(&buffer);                                                                                              // get next block of buffer
                arr[i * cols * slices + j * slices + k] ^= (slice8(arr[i * cols * slices + j * slices + k], start, stop) ^ block) << (8 - stop); // insert in matrix element
            }
        }
    }
}


// BUFFERLIB AND GET_BITS/PUT_BITS TESTING CODE

// int main(int argc, char **argv)
// {

//     // Test code for get_bits32 and put_bits32
//     uint8_t arr8[27] = {137, 169, 24,
//                         250, 93, 122,
//                         57, 163, 124,

//                         18, 223, 79,
//                         45, 157, 3,
//                         139, 129, 182,

//                         201, 242, 163,
//                         2, 148, 54,
//                         233, 250, 247};

//     int rows8 = 3;
//     int cols8 = 9;
//     int slices8 = 1;

//     uint32_t start8, stop8;
//     start8 = 0, stop8 = 8;
//     uint32_t bit_length8 = rows8 * cols8 * slices8 * (stop8 - start8);

//     uint32_t size8 = (bit_length8 - 1) / 32 + 1;
//     uint32_t *buffer_arr8 = calloc(size8, 8);

//     uint32_t fill8 = 4294967295;

//     get_bits8(arr8, buffer_arr8, rows8, cols8, slices8, start8, stop8, fill8);

//     uint8_t putarr8[27] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};

//     put_bits8(putarr8, buffer_arr8, rows8, cols8, slices8, start8, stop8);

//     print_uint8_arr_b(1, 27, putarr8); // should equal arr

//     free(buffer_arr8);

//     // // Test code for get_bits32 and put_bits32
//     // uint32_t arr[9] = {1, 2, 3, 4, 5, 6, 7, 8, 9};

//     // int rows = 3;
//     // int cols = 3;

//     // uint32_t start, stop;
//     // start = 0, stop = 32;
//     // uint32_t bit_length = rows * cols * (stop - start);

//     // uint32_t size = (bit_length - 1) / 32 + 1;
//     // uint32_t *buffer_arr = calloc(size, 4);

//     // uint32_t fill = 3269625783;

//     // get_bits32(arr, buffer_arr, rows, cols, start, stop, fill);

//     // uint32_t putarr[9] = {0, 0, 0, 0, 0, 0, 0, 0, 0};

//     // put_bits32(putarr, buffer_arr, rows, cols, start, stop);

//     // print_uint32_arr_b(3, 3, putarr); // should equal arr

//     // free(buffer_arr);
//     // printf("FINISHED");

//     return 0;
// }
