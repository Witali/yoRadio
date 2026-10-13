#include "aac_fill_parser.h"

typedef struct { uint32_t payload_begin, payload_end, payload_bytes; } fill_span_t;

static uint32_t byte_end(const aac_fill_bits_t *bits) {
    // Native ADTS input is at most 8191 bytes. Avoid overflow even for an
    // inconsistent caller; leave room for the controller's following ID read.
    return bits->input_length<=UINT32_MAX/8 ? bits->input_length*8 : UINT32_MAX-7;
}

static bool reject(aac_fill_bits_t *bits) {
    bits->used_bits=byte_end(bits);
    return false;
}

// Width is 4 or 8 and the complete span has already been checked. Read a
// second byte only when needed, including at an exactly allocated input end.
static unsigned take_bits(const uint8_t *data,uint32_t *cursor,unsigned width) {
    unsigned offset=*cursor%8, first_bits=8-offset;
    unsigned value=data[*cursor/8];
    if(width>first_bits) {
        value=(value<<8)|data[*cursor/8+1];
        value >>= 16-offset-width;
    } else value >>= first_bits-width;
    *cursor+=width;
    return value & ((1u<<width)-1);
}

static bool parse_span(aac_fill_bits_t *bits,fill_span_t *span) {
    uint32_t limit=byte_end(bits), cursor=bits->used_bits;
    if(bits->available_bits<limit)limit=bits->available_bits;
    if(!bits->buffer || cursor>limit || limit-cursor<AAC_FIL_COUNT_BITS)
        return reject(bits);
    unsigned count=take_bits(bits->buffer,&cursor,AAC_FIL_COUNT_BITS);
    if(count==AAC_FIL_ESCAPE_COUNT) {
        if(limit-cursor<AAC_FIL_ESCAPE_BITS)return reject(bits);
        count=AAC_FIL_ESCAPE_COUNT-1+take_bits(bits->buffer,&cursor,AAC_FIL_ESCAPE_BITS);
    }
    if(count>(limit-cursor)/8)return reject(bits);
    *span=(fill_span_t){cursor,cursor+count*8,count};
    return true;
}

bool aac_fill_skip(aac_fill_bits_t *bits) {
    fill_span_t span;
    if(!parse_span(bits,&span))return false;
    bits->used_bits=span.payload_end;
    return true;
}

bool aac_fill_sbr(aac_fill_stream_t *stream,aac_fill_bits_t *bits) {
    fill_span_t span;
    if(!parse_span(bits,&span))return false;
    if(!stream || stream->elements<0 || stream->elements>AAC_FIL_SBR_ELEMENTS)
        return reject(bits);
    uint32_t cursor=span.payload_begin;
    if(span.payload_bytes && stream->elements<AAC_FIL_SBR_ELEMENTS) {
        unsigned extension=take_bits(bits->buffer,&cursor,AAC_FIL_EXTENSION_BITS);
        if(extension==AAC_FIL_SBR || extension==AAC_FIL_SBR_CRC) {
            if(span.payload_bytes>sizeof(stream->element[0].payload))return reject(bits);
            aac_fill_element_t *element=&stream->element[stream->elements];
            // The SDK stores the first payload nibble in the low half-byte;
            // extension_type is separate. Keep its exact downstream ABI.
            element->payload[0]=take_bits(bits->buffer,&cursor,AAC_FIL_EXTENSION_BITS);
            for(unsigned i=1;i<span.payload_bytes;++i)
                element->payload[i]=take_bits(bits->buffer,&cursor,8);
            element->extension_type=extension;
            element->payload_bytes=span.payload_bytes;
            ++stream->elements;
        }
    }
    bits->used_bits=span.payload_end;
    return true;
}
