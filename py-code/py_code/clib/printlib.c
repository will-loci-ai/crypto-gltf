// LIBRARY OF PRINTING FUNCTIONS

// LIB INCLUSIONS
#include <stdio.h>
#include <math.h>
#include <stdint.h>
#include "definitions.h"

void print_s(const char *input)
{
    // prints a string
    printf("%s\n", input);
}

void print_i(int input)
{
    // prints an integer
    printf("%d\n", input);
}

void print_f(float input)
{
    // prints an float
    printf("%f\n", input);
}

void print_b(size_t const size, void const *const ptr)
{
    // print binary of data at ptr
    unsigned char *b = (unsigned char *)ptr;
    unsigned char byte;
    int i, j;

    for (i = size - 1; i >= 0; i--)
    {
        for (j = 7; j >= 0; j--)
        {
            byte = (b[i] >> j) & 1;
            printf("%u", byte);
        }
        printf(" ");
    }
}

void print_float_arr(int rows, int cols, float arr[rows][cols])
{
    // print an array of floats
    for (int i = 0; i < rows; i++)
    {
        for (int j = 0; j < cols; j++)
        {
            printf("%f ", arr[i][j]);
        }
        printf("\n");
    }
    printf("\n");
}

void print_uint32_arr_b(size_t const rows, size_t const cols, uint32_t const *arr)
{
    // print uint32_t array in binary form

    for (int i = 0; i < rows; i++)
    {
        for (int j = 0; j < cols; j++)
        {
            print_b(4, &arr[i * cols + j]);
            printf("    ");
        }
        printf("\n");
    }
    printf("\n");
}

void print_uint8_arr_b(size_t const rows, size_t const cols, uint8_t const *arr)
{
    // print uint8_t array in binary form

    for (int i = 0; i < rows; i++)
    {
        for (int j = 0; j < cols; j++)
        {
            print_b(1, &arr[i * cols + j]);
            printf("    ");
        }
        printf("\n");
    }
    printf("\n");
}

void print_buffer(Buffer *buffer)
{
    // print buffer
    for (int i = 0; i <= buffer->idx; i++)
    {
        print_b(4, &buffer->arr[i]);
        printf("\n");
    }
    printf("\n");
}