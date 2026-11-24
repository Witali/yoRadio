#pragma once
#include <stdint.h>
typedef uint8_t u8_t;
typedef uint16_t u16_t;
/* Selected IPv4/ethernet profile: transport20 + IP20 + link14. */
typedef enum { PBUF_TRANSPORT=54, PBUF_IP=34, PBUF_LINK=14, PBUF_RAW_TX=0, PBUF_RAW=0 } pbuf_layer;
/* Full public enum values, not the pbuf.type_internal low byte. */
typedef enum { PBUF_RAM=0x280, PBUF_ROM=1, PBUF_REF=0x41, PBUF_POOL=0x182 } pbuf_type;
/* Public fields with natural host pointers/padding; NOT a packed target ABI. */
struct pbuf {
    struct pbuf *next;
    void *payload;
    u16_t tot_len, len;
    u8_t type_internal, flags, ref, if_idx;
};
