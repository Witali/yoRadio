#pragma once
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* Bounded RFC 1951/1952 encoder, used only to build an optional flash cache.
 * Fixed Huffman codes, one hash candidate, 512-byte backward window. No heap
 * allocation, recursive calls, or input-size-dependent state in this module. */
typedef bool (*small_gzip_write_t)(void *, const unsigned char *, size_t);
typedef struct {
    uint32_t heads[256];
    unsigned char ring[1024], output[512];
    uint32_t consumed, supplied, crc, bits;
    unsigned bit_count, used;
    small_gzip_write_t write;
    void *context;
    bool failed, finished;
} small_gzip_t;

uint32_t small_gzip_crc32(uint32_t crc, const void *data, size_t size);
void small_gzip_init(small_gzip_t *, small_gzip_write_t, void *);
bool small_gzip_feed(small_gzip_t *, const void *, size_t);
bool small_gzip_finish(small_gzip_t *);
