#include "small_gzip.h"
#include <string.h>

/* Word-sized ROM tables avoid LX106 byte/halfword XIP load emulation. */
static const uint32_t crc_nibble[16] = {
    0x00000000,0x1db71064,0x3b6e20c8,0x26d930ac,0x76dc4190,0x6b6b51f4,0x4db26158,0x5005713c,
    0xedb88320,0xf00f9344,0xd6d6a3e8,0xcb61b38c,0x9b64c2b0,0x86d3d2d4,0xa00ae278,0xbdbdf21c
};
uint32_t small_gzip_crc32(uint32_t crc, const void *data, size_t size) {
    const unsigned char *p = data;
    while (size--) {
        crc ^= *p++;
        crc = (crc >> 4) ^ crc_nibble[crc & 15U];
        crc = (crc >> 4) ^ crc_nibble[crc & 15U];
    }
    return crc;
}
static void flush(small_gzip_t *s) {
    if (s->used && !s->failed && !s->write(s->context, s->output, s->used)) s->failed = true;
    s->used = 0;
}
static void byte(small_gzip_t *s, unsigned value) {
    if (s->failed) return;
    s->output[s->used++] = (unsigned char)value;
    if (s->used == sizeof(s->output)) flush(s);
}
static void bits(small_gzip_t *s, unsigned value, unsigned count) {
    s->bits |= (uint32_t)value << s->bit_count;
    s->bit_count += count;
    while (s->bit_count >= 8) {
        byte(s, s->bits & 255U);
        s->bits >>= 8;
        s->bit_count -= 8;
    }
}
static unsigned reverse(unsigned code, unsigned count) {
    unsigned result = 0;
    while (count--) { result = (result << 1) | (code & 1U); code >>= 1; }
    return result;
}
static void symbol(small_gzip_t *s, unsigned value) {
    unsigned code, count;
    if (value < 144) { code = 0x30U + value; count = 8; }
    else if (value < 256) { code = 0x190U + value - 144; count = 9; }
    else if (value < 280) { code = value - 256; count = 7; }
    else { code = 0xc0U + value - 280; count = 8; }
    bits(s, reverse(code, count), count);
}
static unsigned hash(const small_gzip_t *s, uint32_t at) {
    return ((unsigned)s->ring[at & 1023U] * 251U ^
            (unsigned)s->ring[(at + 1) & 1023U] * 31U ^
            s->ring[(at + 2) & 1023U]) & 255U;
}
static void token(small_gzip_t *s) {
    static const uint32_t length_base[29] = {3,4,5,6,7,8,9,10,11,13,15,17,19,23,27,31,35,43,51,59,67,83,99,115,131,163,195,227,258};
    static const uint32_t length_bits[29] = {0,0,0,0,0,0,0,0,1,1,1,1,2,2,2,2,3,3,3,3,4,4,4,4,5,5,5,5,0};
    static const uint32_t distance_base[18] = {1,2,3,4,5,7,9,13,17,25,33,49,65,97,129,193,257,385};
    static const uint32_t distance_bits[18] = {0,0,0,0,1,1,2,2,3,3,4,4,5,5,6,6,7,7};
    unsigned available = s->supplied - s->consumed, length = 0, distance = 0;
    if (available > 258) available = 258;
    if (available >= 3) {
        uint32_t previous = s->heads[hash(s, s->consumed)];
        if (previous != UINT32_MAX && previous < s->consumed && s->consumed - previous <= 512) {
            while (length < available && s->ring[(previous + length) & 1023U] ==
                   s->ring[(s->consumed + length) & 1023U]) ++length;
            distance = s->consumed - previous;
        }
    }
    if (length >= 3) {
        unsigned l = 0, d = 0;
        while (l < 28 && length >= length_base[l + 1]) ++l;
        while (d < 17 && distance >= distance_base[d + 1]) ++d;
        symbol(s, 257 + l);
        bits(s, length - length_base[l], length_bits[l]);
        bits(s, reverse(d, 5), 5);
        bits(s, distance - distance_base[d], distance_bits[d]);
    } else {
        length = 1;
        symbol(s, s->ring[s->consumed & 1023U]);
    }
    for (unsigned i = 0; i < length; ++i) {
        if (s->supplied - s->consumed >= 3) s->heads[hash(s, s->consumed)] = s->consumed;
        ++s->consumed;
    }
}
void small_gzip_init(small_gzip_t *s, small_gzip_write_t write, void *context) {
    memset(s, 0, sizeof(*s));
    for (unsigned i = 0; i < 256; ++i) s->heads[i] = UINT32_MAX;
    s->write = write; s->context = context; s->crc = UINT32_MAX;
    s->failed = write == NULL;
    byte(s, 31); byte(s, 139); byte(s, 8); byte(s, 0);
    for (unsigned i = 0; i < 6; ++i) byte(s, i == 5 ? 255 : 0);
    bits(s, 3, 3); /* BFINAL=1, fixed Huffman BTYPE=01. */
}
bool small_gzip_feed(small_gzip_t *s, const void *data, size_t size) {
    if (s->failed || s->finished || (!data && size) || size > UINT32_MAX - s->supplied) return false;
    const unsigned char *p = data;
    s->crc = small_gzip_crc32(s->crc, data, size);
    while (size-- && !s->failed) {
        s->ring[s->supplied++ & 1023U] = *p++;
        if (s->supplied - s->consumed >= 258) token(s);
    }
    return !s->failed;
}
bool small_gzip_finish(small_gzip_t *s) {
    if (s->failed || s->finished) return false;
    while (s->consumed != s->supplied && !s->failed) token(s);
    symbol(s, 256);
    if (s->bit_count) bits(s, 0, 8 - s->bit_count);
    uint32_t crc = s->crc ^ UINT32_MAX;
    for (unsigned i = 0; i < 4; ++i) byte(s, crc >> (8 * i));
    for (unsigned i = 0; i < 4; ++i) byte(s, s->supplied >> (8 * i));
    flush(s); s->finished = true;
    return !s->failed;
}
