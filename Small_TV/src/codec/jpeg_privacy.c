/* REQUESTED_CHANGE: bounded metadata validation for ordinary multi-scan JPEG. */
#include "jpeg_privacy.h"
#include <stdbool.h>
#include <string.h>

typedef struct {
    const jpeg_privacy_source_t *source;
    jpeg_privacy_diagnostic_t *diagnostic;
    uint32_t position,base;
    size_t buffered;
    uint8_t bytes[256];
} privacy_reader_t;

static bool fail(privacy_reader_t *reader,jpeg_privacy_result_t result)
{
    /* Keep the first concrete parser/callback failure for the HTTP owner. */
    if(reader->diagnostic->status==JPEG_PRIVACY_OK)
        reader->diagnostic->status=result;
    return false;
}

static bool checkpoint(privacy_reader_t *reader)
{
    /* Check deadlines/cancellation even while processing cached entropy bytes. */
    int error=reader->source->check(reader->source->context);
    if(!error)return true;
    reader->diagnostic->callback_error=error;
    return fail(reader,JPEG_PRIVACY_STOP);
}

static bool byte(privacy_reader_t *reader,uint8_t *value)
{
    /* Fetch one bounded byte through a small caller-independent read buffer. */
    if(!checkpoint(reader))return false;
    if(reader->position>=reader->source->length)return fail(reader,JPEG_PRIVACY_TRUNCATED);
    if(reader->position<reader->base || reader->position-reader->base>=reader->buffered) {
        reader->base=reader->position;
        reader->buffered=reader->source->length-reader->position;
        if(reader->buffered>sizeof(reader->bytes))reader->buffered=sizeof(reader->bytes);
        int error=reader->source->read(reader->source->context,reader->position,
                                       reader->bytes,reader->buffered);
        if(error) {
            reader->diagnostic->callback_error=error;
            return fail(reader,JPEG_PRIVACY_IO);
        }
        if(!checkpoint(reader))return false;
    }
    *value=reader->bytes[reader->position++-reader->base];return true;
}

static bool payload(privacy_reader_t *reader,uint8_t *data,size_t count)
{
    /* Read only short structural headers, never a variable-size metadata blob. */
    for(size_t i=0;i<count;++i)if(!byte(reader,&data[i]))return false;
    return true;
}

static bool frame_marker(unsigned marker)
{
    /* Preserve process/precision for later codec dispatch, without rejecting
     * lossless/arithmetic/hierarchical processes as if they were private data. */
    return marker>=0xc0 && marker<=0xcf && marker!=0xc4 && marker!=0xc8 && marker!=0xcc;
}

static bool segment(privacy_reader_t *reader,unsigned marker,uint32_t end,uint16_t size)
{
    /* Only fixed-size JFIF/Adobe headers survive the metadata policy. Codec
     * validation owns table consistency, colorspace, sampling and capabilities. */
    uint8_t header[14];
    if(marker==0xfe || (marker>=0xe0 && marker<=0xef && marker!=0xe0 && marker!=0xee))
        return fail(reader,JPEG_PRIVACY_METADATA);
    if(marker==0xe0) {
        if(size<7)return fail(reader,JPEG_PRIVACY_METADATA);
        if(!payload(reader,header,5))return false;
        if(memcmp(header,"JFIF\0",5))return fail(reader,JPEG_PRIVACY_METADATA);
        if(size<16)return fail(reader,JPEG_PRIVACY_INVALID);
        if(!payload(reader,header+5,9))return false;
        if(header[5]!=1 || header[6]>2 || header[7]>2)
            return fail(reader,JPEG_PRIVACY_METADATA);
        if(header[12] || header[13])return fail(reader,JPEG_PRIVACY_THUMBNAIL);
        if(size!=16)return fail(reader,JPEG_PRIVACY_METADATA);
    } else if(marker==0xee) {
        if(size!=14)return fail(reader,JPEG_PRIVACY_METADATA);
        if(!payload(reader,header,12))return false;
        if(memcmp(header,"Adobe",5) || header[5] || header[6]!=100 ||
           header[7] || header[8] || header[9] || header[10] || header[11]>2)
            return fail(reader,JPEG_PRIVACY_METADATA);
    } else if(frame_marker(marker)) {
        if(size<8)return fail(reader,JPEG_PRIVACY_INVALID);
        if(!payload(reader,header,6))return false;
        if(!reader->diagnostic->process) {
            reader->diagnostic->process=(uint8_t)marker;
            reader->diagnostic->precision=header[0];
            reader->diagnostic->height=((uint32_t)header[1]<<8)|header[2];
            reader->diagnostic->width=((uint32_t)header[3]<<8)|header[4];
            reader->diagnostic->components=header[5];
        }
    } else if(marker!=0xc4 && marker!=0xcc && marker!=0xda &&
              (marker<0xdb || marker>0xdf)) {
        return fail(reader,JPEG_PRIVACY_INVALID);
    }
    reader->position=end;return checkpoint(reader);
}

jpeg_privacy_result_t jpeg_privacy_check(const jpeg_privacy_source_t *source,
                                       jpeg_privacy_diagnostic_t *diagnostic)
{
    /* Walk marker segments and every entropy scan to EOI exactly at EOF.
     * FF00 is stuffed entropy, restart/TEM markers have no segment length;
     * fill bytes are permitted before markers. DNL resumes its current scan. */
    jpeg_privacy_diagnostic_t local={0};
    if(!diagnostic)diagnostic=&local;
    memset(diagnostic,0,sizeof(*diagnostic));
    if(!source || !source->read || !source->check) {
        diagnostic->status=JPEG_PRIVACY_ARGUMENT;return diagnostic->status;
    }
    privacy_reader_t reader={.source=source,.diagnostic=diagnostic};
    uint8_t value,marker=0;
    if(!byte(&reader,&value) || value!=0xff || !byte(&reader,&marker) || marker!=0xd8) {
        if(diagnostic->status==JPEG_PRIVACY_OK)diagnostic->status=JPEG_PRIVACY_INVALID;
        return diagnostic->status;
    }
    bool entropy=false;
    for(;;) {
        bool in_scan=entropy;
        if(!byte(&reader,&value))break;
        if(entropy && value!=0xff)continue;
        diagnostic->offset=reader.position-1;
        if(value!=0xff){fail(&reader,JPEG_PRIVACY_INVALID);break;}
        do {if(!byte(&reader,&marker))goto done;} while(marker==0xff);
        diagnostic->marker=marker;
        if(entropy && (marker==0 || marker==0x01 || (marker>=0xd0 && marker<=0xd7)))continue;
        if(marker==0xd9) {
            if(!diagnostic->process || !diagnostic->scans)fail(&reader,JPEG_PRIVACY_INVALID);
            else if(reader.position!=source->length)fail(&reader,JPEG_PRIVACY_TRAILING);
            goto done;
        }
        if(marker==0x01)continue;
        if(marker==0 || marker==0xd8 || (marker>=0xd0 && marker<=0xd7)) {
            fail(&reader,JPEG_PRIVACY_INVALID);break;
        }
        uint8_t high,low;
        if(!byte(&reader,&high) || !byte(&reader,&low))break;
        uint16_t size=(uint16_t)(((unsigned)high<<8)|low);
        if(size<2){fail(&reader,JPEG_PRIVACY_INVALID);break;}
        if((uint32_t)(size-2)>source->length-reader.position) {
            fail(&reader,JPEG_PRIVACY_TRUNCATED);break;
        }
        uint32_t end=reader.position+size-2;
        if(!segment(&reader,marker,end,size))break;
        entropy=marker==0xda || (in_scan && marker==0xdc);
        if(marker==0xda) {
            if(!diagnostic->process){fail(&reader,JPEG_PRIVACY_INVALID);break;}
            ++diagnostic->scans;
        }
    }
done:
    return diagnostic->status;
}

const char *jpeg_privacy_status_name(jpeg_privacy_result_t status)
{
    /* Stable domain errors; no private strings from the input are ever echoed. */
    static const char *const names[]={"ok","argument","invalid-jpeg","truncated-jpeg",
        "private-metadata","embedded-thumbnail","trailing-data","input-io","stopped"};
    return (unsigned)status<sizeof(names)/sizeof(names[0]) ? names[status] : "unknown";
}
