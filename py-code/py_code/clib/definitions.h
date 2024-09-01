#include <assert.h>

// TYPE DEFINITIONS
typedef struct
{
    // 32 bit buffer type
    uint32_t *arr;
    uint32_t size;   // number of 32 bit values in the buffer
    uint32_t idx;    // buffer position
    uint32_t len;    // length of all blocks added to buffer
    uint32_t offset; // buffer position bit offset
} Buffer;

// CHECKS
#define assertmsg(x, msg) assert(((void)msg, x)) // assertion with message