#include <assert.h>

// TYPE DEFINITIONS
typedef struct
{
    // array type
    uint32_t *arr;
    uint32_t size;
    uint32_t idx;
    uint32_t len;
    uint32_t offset;
} Buffer;

// CHECKS
#define assertmsg(x, msg) assert(((void)msg, x)) // assertion with message