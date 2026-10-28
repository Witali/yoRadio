/* REQUESTED_CHANGE: retain factory byte-clipped TJpgd pixels in the frame cache. */
#include "jpeg_baseline.h"
#include "tjpgd.h"
#include <string.h>

typedef struct {
    const jpeg_decode_request_t *request;
    jpeg_decode_diagnostic_t *diagnostic;
    uint16_t *strip;
    uint32_t position,width,strip_y,next_x,rows;
} baseline_t;

static bool checkpoint(baseline_t *state)
{
    /* Stop both physical input and buffered MCU/row work cooperatively. */
    jpeg_decode_check_t result=state->request->check(state->request->context);
    if(result==JPEG_CHECK_OK)return true;
    state->diagnostic->status=result==JPEG_CHECK_TIME ? JPEG_DECODE_TIME_LIMIT:
        result==JPEG_CHECK_IO_LIMIT ? JPEG_DECODE_IO_LIMIT:JPEG_DECODE_CANCELLED;
    return false;
}

static size_t input(JDEC *decoder,uint8_t *data,size_t bytes)
{
    /* Even TJpgd skip requests stay bounded; all consumed bytes use verified I/O. */
    baseline_t *state=decoder->device;
    if(!checkpoint(state))return 0;
    if(bytes>state->request->length-state->position)bytes=state->request->length-state->position;
    if(!bytes)return 0;
    uint8_t discarded[64];size_t copied=0;
    do {
        size_t count=bytes-copied;
        if(!data && count>sizeof(discarded))count=sizeof(discarded);
        int error=state->request->read(state->request->context,state->position,
                                      data ? data+copied:discarded,count);
        if(error) {
            state->diagnostic->callback_error=error;
            state->diagnostic->status=JPEG_DECODE_INPUT_IO;return 0;
        }
        copied+=count;state->position+=(uint32_t)count;
        if(!checkpoint(state))return 0;
    } while(copied<bytes);
    return bytes;
}

static int output(JDEC *decoder,void *data,JRECT *rect)
{
    /* TJpgd emits MCU rectangles in raster order. Assemble at most16 rows before
     * sending complete ordered rows to the same provisional cache producer API. */
    baseline_t *state=decoder->device;
    if(!checkpoint(state))return 0;
    uint32_t width=(uint32_t)rect->right-rect->left+1;
    uint32_t height=(uint32_t)rect->bottom-rect->top+1;
    if(rect->left!=state->next_x || rect->top!=state->strip_y ||
       !height || height>16 || rect->right>=state->width || rect->bottom>=decoder->height) {
        state->diagnostic->status=JPEG_DECODE_INTERNAL;return 0;
    }
    for(uint32_t y=0;y<height;++y)
        memcpy(state->strip+y*state->width+rect->left,(uint16_t *)data+y*width,width*2u);
    state->next_x=rect->right+1u;
    if(state->next_x==state->width) {
        for(uint32_t y=0;y<height;++y) {
            if(!checkpoint(state))return 0;
            int error=state->request->row(state->request->context,state->strip_y+y,
                                         state->strip+y*state->width,state->width);
            if(error) {
                state->diagnostic->callback_error=error;
                state->diagnostic->status=JPEG_DECODE_OUTPUT_IO;return 0;
            }
            ++state->rows;state->diagnostic->rows=state->rows;
        }
        state->strip_y=rect->bottom+1u;state->next_x=0;
    }
    return 1;
}

jpeg_decode_status_t jpeg_baseline_decode(const jpeg_decode_request_t *request,
    const jpeg_decode_allocator_t *allocator,jpeg_decode_diagnostic_t *diagnostic)
{
    /* Keep factory IDCT/color policy, but validate and populate cache only once.
     * The full privacy gate precedes this function, including exact EOI checks. */
    if(!diagnostic)return JPEG_DECODE_ARGUMENT;
    memset(diagnostic,0,sizeof(*diagnostic));
    if(!request || !request->read || !request->row || !request->check ||
       !allocator || !allocator->allocate || !allocator->release) {
        diagnostic->status=JPEG_DECODE_ARGUMENT;return diagnostic->status;
    }
    baseline_t state={.request=request,.diagnostic=diagnostic};
    void *workspace=allocator->allocate(allocator->context,8192);
    if(!workspace){diagnostic->status=JPEG_DECODE_ALLOCATION;return diagnostic->status;}
    JDEC decoder={0};
    JRESULT result=jd_prepare(&decoder,input,workspace,8192,&state);
    diagnostic->width=decoder.width;diagnostic->height=decoder.height;
    if(result==JDR_OK) {
        if(!decoder.width || decoder.width>240 || !decoder.height || decoder.height>240 ||
           (request->expected_width && decoder.width!=request->expected_width) ||
           (request->expected_height && decoder.height!=request->expected_height)) {
            diagnostic->status=JPEG_DECODE_DIMENSIONS;result=JDR_PAR;
        } else if(decoder.msy>2 || decoder.msx>2 ||
                  (decoder.ncomp==3 && decoder.component_id[0]=='R' &&
                   decoder.component_id[1]=='G' && decoder.component_id[2]=='B')) {
            diagnostic->status=JPEG_DECODE_UNSUPPORTED;result=JDR_FMT3;
        } else {
            state.width=decoder.width;
            size_t strip_bytes=state.width*16u*sizeof(uint16_t);
            state.strip=allocator->allocate(allocator->context,strip_bytes);
            if(!state.strip){diagnostic->status=JPEG_DECODE_ALLOCATION;result=JDR_MEM1;}
            else {
                result=jd_decomp(&decoder,output,0);
                allocator->release(allocator->context,state.strip,strip_bytes);
            }
        }
    }
    allocator->release(allocator->context,workspace,8192);
    diagnostic->input_bytes=state.position;
    if(diagnostic->status==JPEG_DECODE_OK) {
        if(result==JDR_OK && state.rows==decoder.height)diagnostic->status=JPEG_DECODE_OK;
        else if(result==JDR_FMT2 || result==JDR_FMT3)diagnostic->status=JPEG_DECODE_UNSUPPORTED;
        else if(result==JDR_MEM1 || result==JDR_MEM2)diagnostic->status=JPEG_DECODE_UNSUPPORTED;
        else if(result==JDR_INP)diagnostic->status=JPEG_DECODE_TRUNCATED;
        else diagnostic->status=JPEG_DECODE_INVALID;
    }
    return diagnostic->status;
}
