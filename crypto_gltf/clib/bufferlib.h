void print_buffer(Buffer *buffer);
void init_buffer(Buffer *buffer, uint32_t *arr, uint32_t bit_length, uint32_t len);
void free_buffer(Buffer *buffer);
void extend(Buffer *buffer, uint32_t block);
uint32_t next_block(Buffer *buffer);
void fill_buffer(Buffer *buffer, uint32_t fill);