#include "dns_packet.h"
#include <stdbool.h>
#include <string.h>

/* Only one uncompressed IN question. Packet length is checked before each read. */
size_t captive_dns_reply(uint8_t *packet,size_t length,size_t capacity)
{
    if (length>capacity || length<12 || packet[2]&0xf8 || packet[4]!=0 || packet[5]!=1) return 0;
    size_t pos=12,name_bytes=0;
    for (;;) {
        if (pos>=length) return 0;
        unsigned label=packet[pos++];
        if (!label) break;
        if (label>63 || label>length-pos || (name_bytes+=label+1)>254) return 0;
        pos+=label;
    }
    if (length-pos<4) return 0;
    bool ipv4=packet[pos]==0 && packet[pos+1]==1 && packet[pos+2]==0 && packet[pos+3]==1;
    pos+=4;
    if (ipv4 && capacity-pos<16) return 0;
    packet[2]=0x80|(packet[2]&1); packet[3]=0x80;
    memset(packet+6,0,6); packet[7]=ipv4?1:0;
    if (ipv4) {
        const uint8_t answer[]={0xc0,0x0c,0,1,0,1,0,0,0,60,0,4,192,168,43,1};
        memcpy(packet+pos,answer,sizeof(answer)); pos+=sizeof(answer);
    }
    return pos;
}
