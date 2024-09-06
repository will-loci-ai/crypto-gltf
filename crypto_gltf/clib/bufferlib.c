#include <stdint.h>
#include <assert.h>
#include <stdlib.h>

#include "definitions.h"
#include "utils.h"
#include "printlib.h"

void init_buffer(Buffer *buffer, uint32_t *arr, uint32_t bit_length, uint32_t len)
{
    // initialise memory buffer
    buffer->arr = arr; // buffer memory, already initialised in python
    buffer->size = (bit_length - 1) / 32 + 1;
    buffer->idx = 0;
    buffer->offset = 0;
    buffer->len = len;
}

void free_buffer(Buffer *buffer)
{
    // free memory at buffer and set fields to 0
    free(buffer->arr);
    buffer->arr = NULL;
    buffer->len = buffer->size = buffer->idx = buffer->offset = 0;
}

void extend(Buffer *buffer, uint32_t block)
{
    // append block to a buffer

    if (buffer->len + buffer->offset > 32)
    {
        // block straddles current idx and the next
        // fill in rest of this idx and add remaining block to next idx
        assertmsg(buffer->idx < buffer->size, 
            "Error: end of buffer reached.");
        buffer->arr[buffer->idx] |= block >> 
            (buffer->offset + buffer->len - 32);
        buffer->idx++;

        assertmsg(buffer->arr[buffer->idx] == 0, 
            "Error: non-zero buffer provided.");
        buffer->arr[buffer->idx] |= block << 
            (32 - buffer->offset - buffer->len);
        buffer->offset = buffer->offset + buffer->len - 32;
    }
    else
    {
        // fill all block into idx
        buffer->arr[buffer->idx] |= block <<   
            (32 - buffer->offset - buffer->len);
        buffer->offset += buffer->len;
        if (buffer->offset == 32)
        {
            buffer->offset = 0;
            buffer->idx++;
            if (buffer->idx != buffer->size) 
            // i.e. end of buffer not yet reached
            {
                assertmsg(buffer->arr[buffer->idx] == 0, 
                    "Error: non-zero buffer provided.");
            }
        }
    }
}

void fill_buffer(Buffer *buffer, uint32_t fill)
{
    // fill remaining bits of buffer with fill value
    // important for encryption padding 
    // so padded values are random bits
    if (buffer->idx == buffer->size)
    {
        // final buffer element already filled, 
        // buffer->len is divisible by 32
        assertmsg(buffer->offset == 0, "Error: buffer overflow");
    }
    else
    {
        assertmsg((buffer->idx + 1 == buffer->size), 
            "Error: end of buffer not reached during fill_buffer().");
        buffer->arr[buffer->idx] |= fill >> buffer->offset; 
        // here len is 32
    }
}

uint32_t next_block(Buffer *buffer)
{
    // get next block of buffer bits
    uint32_t block;
    if (buffer->len + buffer->offset > 32)
    {
        // block bits straddle idx and idx+1
        assertmsg(buffer->idx < buffer->size, 
            "Error: end of buffer reached.");

        uint32_t remainder = buffer->len + buffer->offset - 32;
        block = slice32(buffer->arr[buffer->idx], 
            buffer->offset, 32) << remainder;
        block += slice32(buffer->arr[buffer->idx + 1], 
            0, remainder);
        buffer->offset = remainder;
        buffer->idx++;
    }
    else
    {
        // all block bits lie in idx
        block = slice32(buffer->arr[buffer->idx], buffer->offset, 
            buffer->offset + buffer->len);
        buffer->offset += buffer->len;
        if (buffer->offset == 32)
        {
            buffer->offset = 0;
            buffer->idx++;
        }
    }
    return block;
}
