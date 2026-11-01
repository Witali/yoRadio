#ifndef YORADIO_OPUS_TAGS_STREAM_H
#define YORADIO_OPUS_TAGS_STREAM_H

/* RFC 7845 section5.2 + RFC 3629 section4, constant-memory validation only.
 * Declared vendor/comment vectors are UTF-8, not NUL-terminated strings. No
 * text or whole packet allocation, metadata display, tag-name/R128 processing
 * or gain application occurs. All declared vectors are validated, including
 * comments beyond61440B; the permission to ignore those comments is not used.
 * Arbitrary bytes AFTER the completed comment list are a legal binary tail.
 * The only size policy is the expressly permitted >120MiB total header limit.
 *
 * The byte parser is independent of container ownership. The verified-page
 * wrapper starts from the caller's real held HEAD event and then validates
 * the real held comment pages. It NEVER ACKs/resets a page. Page-state commit
 * is transactional; on any error the original stream state and page remain
 * unchanged. A successfully committed page token cannot be fed twice.
 */
#include "ogg_page_input.h"
enum { OPUS_TAGS_MAX_BYTES=125829120 };
typedef enum { OTS_MORE=0,OTS_COMPLETE=1,OTS_INVALID=-1,OTS_UTF8=-2,OTS_LIMIT=-3,OTS_ARGUMENT=-4 } opus_tags_status;
typedef enum { OTP_MAGIC=0,OTP_VENDOR_LENGTH,OTP_VENDOR,OTP_COUNT,OTP_COMMENT_LENGTH,OTP_COMMENT,OTP_TAIL } opus_tags_phase;
typedef struct {
    uint64_t bytes;
    uint32_t word,remaining,comments;
    uint8_t phase,field_bytes,magic_bytes,utf8_remaining,utf8_low,utf8_high;
    bool complete;
    opus_tags_status fault;
} opus_tags_parser;
typedef struct {
    opus_tags_parser parser;
    uint32_t generation,serial;
    uint64_t last_token;
    bool active,partial,complete;
} opus_tags_stream;

static inline void otp_reset(opus_tags_parser *s) {memset(s,0,sizeof(*s));}
static inline bool otp_utf8_byte(opus_tags_parser *s,uint8_t byte) {
    if(s->utf8_remaining) {
        if(byte<s->utf8_low || byte>s->utf8_high)return false;
        --s->utf8_remaining;s->utf8_low=0x80;s->utf8_high=0xbf;return true;
    }
    if(byte<0x80)return true;
    s->utf8_low=0x80;s->utf8_high=0xbf;
    if(byte>=0xc2 && byte<=0xdf){s->utf8_remaining=1;return true;}
    if(byte>=0xe0 && byte<=0xef) {
        s->utf8_remaining=2;if(byte==0xe0)s->utf8_low=0xa0;if(byte==0xed)s->utf8_high=0x9f;return true;
    }
    if(byte>=0xf0 && byte<=0xf4) {
        s->utf8_remaining=3;if(byte==0xf0)s->utf8_low=0x90;if(byte==0xf4)s->utf8_high=0x8f;return true;
    }
    return false;
}
static inline opus_tags_status otp_fault(opus_tags_parser *s,opus_tags_status code) {s->fault=code;return code;}
static inline void otp_comment_done(opus_tags_parser *s) {
    --s->comments;s->phase=s->comments?OTP_COMMENT_LENGTH:OTP_TAIL;
}
/* used includes the first invalid text/magic octet. For the size policy it
 * includes only bytes within the permitted limit; no next byte is consumed.
 * A failure is sticky until reset, so a partial parser cannot be replayed.
 */
static inline opus_tags_status otp_feed(opus_tags_parser *s,const uint8_t *data,size_t bytes,size_t *used) {
    if(!s || !used || (bytes && !data))return OTS_ARGUMENT;
    *used=0;if(s->fault)return s->fault;if(s->complete)return OTS_ARGUMENT;
    while(*used<bytes) {
        if(s->bytes>=OPUS_TAGS_MAX_BYTES)return otp_fault(s,OTS_LIMIT);
        if(s->phase==OTP_TAIL) {
            size_t take=bytes-*used;uint64_t room=OPUS_TAGS_MAX_BYTES-s->bytes;if(take>room)take=(size_t)room;
            s->bytes+=take;*used+=take;if(*used<bytes)return otp_fault(s,OTS_LIMIT);break;
        }
        uint8_t byte=data[(*used)++];++s->bytes;
        switch((opus_tags_phase)s->phase) {
        case OTP_MAGIC:
            if(byte!=(uint8_t)"OpusTags"[s->magic_bytes])return otp_fault(s,OTS_INVALID);
            if(++s->magic_bytes==8)s->phase=OTP_VENDOR_LENGTH;
            break;
        case OTP_VENDOR_LENGTH:case OTP_COUNT:case OTP_COMMENT_LENGTH:
            s->word|=(uint32_t)byte<<(8u*s->field_bytes);
            if(++s->field_bytes==4) {
                uint32_t value=s->word;s->word=0;s->field_bytes=0;
                if(s->phase==OTP_COUNT){s->comments=value;s->phase=value?OTP_COMMENT_LENGTH:OTP_TAIL;}
                else {
                    bool vendor=s->phase==OTP_VENDOR_LENGTH;s->remaining=value;s->utf8_remaining=0;s->utf8_low=s->utf8_high=0;
                    if(value)s->phase=vendor?OTP_VENDOR:OTP_COMMENT;
                    else if(vendor)s->phase=OTP_COUNT;
                    else otp_comment_done(s);
                }
            }
            break;
        case OTP_VENDOR:case OTP_COMMENT:
            if(!otp_utf8_byte(s,byte))return otp_fault(s,OTS_UTF8);
            if(!--s->remaining) {
                if(s->utf8_remaining)return otp_fault(s,OTS_UTF8);
                if(s->phase==OTP_VENDOR)s->phase=OTP_COUNT;else otp_comment_done(s);
            }
            break;
        case OTP_TAIL:default:return otp_fault(s,OTS_INVALID);
        }
    }
    return OTS_MORE;
}
static inline opus_tags_status otp_finish(opus_tags_parser *s) {
    if(!s)return OTS_ARGUMENT;
    if(s->fault)return s->fault;
    if(s->complete)return OTS_COMPLETE;
    if(s->phase!=OTP_TAIL || s->field_bytes || s->remaining || s->utf8_remaining)return otp_fault(s,OTS_INVALID);
    s->complete=true;return OTS_COMPLETE;
}
static inline void ots_reset(opus_tags_stream *s) {memset(s,0,sizeof(*s));}
static inline bool ots_begin(opus_tags_stream *s,const ogg_page_input *head) {
    if(!s || !head || s->active || !head->ready || !head->event.crc_verified || !head->event.opus ||
        !(head->event.flags&OOPT_HEAD) || !(head->event.flags&OOPT_PAGE))return false;
    opus_tags_stream next={.generation=head->event.generation,.serial=head->event.serial,.last_token=head->event.token,.active=true};*s=next;return true;
}
static inline opus_tags_status ots_page(opus_tags_stream *s,const ogg_page_input *input) {
    if(!s || !input || !s->active || s->complete || !input->ready || !input->event.crc_verified || !input->event.opus ||
        !(input->event.flags&OOPT_PAGE) || (input->event.flags&OOPT_HEAD) || input->event.generation!=s->generation || input->event.serial!=s->serial ||
        input->event.token<=s->last_token || !input->page || input->size<27 || memcmp(input->page,"OggS\0",5))return OTS_ARGUMENT;
    const uint8_t *page=input->page;unsigned count=page[26];size_t payload=27u+count,total=payload;
    if(payload>input->size || oopt_le32(page+14)!=s->serial || oopt_le32(page+18)!=input->event.sequence)return OTS_ARGUMENT;
    for(unsigned i=0;i<count;++i)total+=page[27+i];
    if(total!=input->size || (count && ((page[5]&1u)!=0)!=s->partial))return OTS_INVALID;
    opus_tags_stream next=*s;bool completed=false;
    for(unsigned segment=0;segment<count;++segment) {
        unsigned lace=page[27+segment];size_t used=0;opus_tags_status status=otp_feed(&next.parser,page+payload,lace,&used);
        if(status<0)return status;
        if(used!=lace)return OTS_INVALID;
        payload+=lace;next.partial=lace==255;
        if(lace<255) {
            if(segment+1u!=count)return OTS_INVALID;
            status=otp_finish(&next.parser);if(status!=OTS_COMPLETE)return status;
            completed=true;
        }
    }
    if(completed!=((input->event.flags&OOPT_TAGS)!=0) || (!completed && (input->event.flags&OOPT_LINK_END)))return OTS_INVALID;
    next.complete=completed;next.last_token=input->event.token;*s=next;return completed?OTS_COMPLETE:OTS_MORE;
}
#endif
