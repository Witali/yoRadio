/* REQUESTED_CHANGE: bounded, reusable native decoder independent of network/LCD. */
#include "jpeg_decoder_internal.h"

void jpeg_decoder_fail(jpeg_decoder_t *s,jpeg_decode_status_t status,uint64_t required,uint64_t available)
{
    /* Custom resource/I/O errors do not masquerade as damaged JPEG errors. */
    s->diagnostic.status=status;s->diagnostic.required=required;s->diagnostic.available=available;
    s->diagnostic.available_known=status==JPEG_DECODE_POOL_LIMIT || status==JPEG_DECODE_BACKING_LIMIT ||
        status==JPEG_DECODE_BACKING_FILES || status==JPEG_DECODE_DIMENSIONS;
    longjmp(s->jump,1);
}

void jpeg_decoder_checkpoint(jpeg_decoder_t *s)
{
    /* Check around synchronous callbacks and RAM-only rows; ongoing I/O cannot
     * be interrupted, but a result after its deadline cannot be successful. */
    jpeg_decode_check_t check=s->request.check(s->request.context);
    if(check==JPEG_CHECK_OK)return;
    jpeg_decode_status_t status=check==JPEG_CHECK_CANCELLED ? JPEG_DECODE_CANCELLED :
        check==JPEG_CHECK_TIME ? JPEG_DECODE_TIME_LIMIT :
        check==JPEG_CHECK_IO_LIMIT ? JPEG_DECODE_IO_LIMIT : JPEG_DECODE_INTERNAL;
    jpeg_decoder_fail(s,status,0,0);
}

void jpeg_decoder_callback_error(jpeg_decoder_t *s,jpeg_decode_status_t status,int error)
{
    /* A flash callback may fail specifically because its shared deadline/quota
     * expired. Retain its concrete code, then ask the owner before degrading the
     * cause to generic I/O. Cleanup still runs without a live operation budget. */
    s->diagnostic.callback_error=error;jpeg_decoder_checkpoint(s);
    jpeg_decoder_fail(s,status,0,0);
}

static void fatal(j_common_ptr codec)
{
    /* Retain stable category, library cause and relevant numeric parameter.
     * Allocation failures can be retries, so only classify the final fatal. */
    jpeg_decoder_t *s=codec->client_data;int code=codec->err->msg_code;
    s->diagnostic.library_error=code;s->diagnostic.library_parameter=0;
    if(s->diagnostic.status==JPEG_DECODE_OK) {
        jpeg_decode_status_t status=JPEG_DECODE_INVALID;jpeg_decode_detail_t detail=JPEG_DETAIL_NONE;
        switch(code) {
            case JERR_OUT_OF_MEMORY:
                status=s->allocation_status ? s->allocation_status : JPEG_DECODE_ALLOCATION;
                s->diagnostic.required=s->allocation_required;
                if(status==JPEG_DECODE_POOL_LIMIT){s->diagnostic.available=s->config.pool_limit;s->diagnostic.available_known=true;}
                break;
            case JERR_INPUT_EOF: case JERR_INPUT_EMPTY: case JWRN_JPEG_EOF: status=JPEG_DECODE_TRUNCATED;break;
            case JERR_SOF_UNSUPPORTED:
                status=JPEG_DECODE_UNSUPPORTED;detail=JPEG_DETAIL_PROCESS;
                s->diagnostic.library_parameter=codec->err->msg_parm.i[0];break;
            case JERR_BAD_PRECISION:
                status=JPEG_DECODE_UNSUPPORTED;detail=JPEG_DETAIL_PRECISION;
                s->diagnostic.library_parameter=codec->err->msg_parm.i[0];break;
            case JERR_COMPONENT_COUNT:
                status=JPEG_DECODE_UNSUPPORTED;detail=JPEG_DETAIL_COLORSPACE;
                s->diagnostic.library_parameter=codec->err->msg_parm.i[0];break;
            case JERR_IMAGE_TOO_BIG:
                status=JPEG_DECODE_DIMENSIONS;s->diagnostic.width=s->codec.image_width;s->diagnostic.height=s->codec.image_height;
                detail=s->codec.image_width>s->config.max_width ? JPEG_DETAIL_WIDTH : JPEG_DETAIL_HEIGHT;
                s->diagnostic.required=detail==JPEG_DETAIL_WIDTH ? s->codec.image_width : s->codec.image_height;
                s->diagnostic.available=detail==JPEG_DETAIL_WIDTH ? s->config.max_width : s->config.max_height;
                s->diagnostic.available_known=true;break;
            case JERR_FRACT_SAMPLE_NOTIMPL: case JERR_CCIR601_NOTIMPL:
                status=JPEG_DECODE_UNSUPPORTED;detail=JPEG_DETAIL_SAMPLING;break;
            case JERR_ARITH_NOTIMPL: status=JPEG_DECODE_UNSUPPORTED;detail=JPEG_DETAIL_ARITHMETIC;break;
            case JERR_CONVERSION_NOTIMPL: status=JPEG_DECODE_UNSUPPORTED;detail=JPEG_DETAIL_COLORSPACE;break;
            case JERR_EMPTY_IMAGE:
                if(s->codec.image_width && !s->codec.image_height && s->codec.num_components>0){status=JPEG_DECODE_UNSUPPORTED;detail=JPEG_DETAIL_DNL;}
                break;
            case JERR_NOT_COMPILED: case JERR_NOTIMPL: status=JPEG_DECODE_UNSUPPORTED;detail=JPEG_DETAIL_FEATURE;break;
            case JERR_BAD_LIB_VERSION: case JERR_BAD_STRUCT_SIZE: case JERR_BAD_STATE:
            case JERR_BAD_VIRTUAL_ACCESS: case JERR_VIRTUAL_BUG: case JERR_BAD_POOL_ID:
                status=JPEG_DECODE_INTERNAL;break;
            default: break;
        }
        s->diagnostic.status=status;s->diagnostic.detail=detail;
    }
    longjmp(s->jump,1);
}

static void warning(j_common_ptr codec,int level)
{
    /* Truncated/corrupt inputs must not succeed via libjpeg's silent recovery. */
    if(level<0)fatal(codec);
}

static void init_source(j_decompress_ptr codec)
{ /* Position/buffer ownership is reset by decode before attaching a new source. */ (void)codec; }

static boolean fill_source(j_decompress_ptr codec)
{
    /* Exact bounded reads; EOF is never replaced with a synthetic EOI marker. */
    jpeg_decoder_t *s=codec->client_data;jpeg_decoder_checkpoint(s);
    size_t count=s->request.length-s->position;if(count>sizeof(s->input))count=sizeof(s->input);
    if(!count)jpeg_decoder_fail(s,JPEG_DECODE_TRUNCATED,(uint64_t)s->position+1u,s->request.length);
    int result=s->request.read(s->request.context,s->position,s->input,count);
    if(result)jpeg_decoder_callback_error(s,JPEG_DECODE_INPUT_IO,result);
    s->position+=(uint32_t)count;s->diagnostic.input_bytes+=count;jpeg_decoder_checkpoint(s);
    s->source.next_input_byte=s->input;s->source.bytes_in_buffer=count;return TRUE;
}

static void skip_source(j_decompress_ptr codec,long bytes)
{
    /* Metadata skips use the same reader/deadline/bounds, not an unchecked seek. */
    if(bytes<=0)return;
    while((size_t)bytes>codec->src->bytes_in_buffer){bytes-=(long)codec->src->bytes_in_buffer;fill_source(codec);}
    codec->src->next_input_byte+=bytes;codec->src->bytes_in_buffer-=(size_t)bytes;
}

static void term_source(j_decompress_ptr codec)
{ /* Source callbacks remain borrowed by the caller; there is no file to close. */ (void)codec; }

jpeg_decoder_t *jpeg_decoder_create(const jpeg_decoder_config_t *config,jpeg_decode_diagnostic_t *diagnostic)
{
    /* Context/row buffers are separate from the explicitly named library pool cap. */
    jpeg_decode_diagnostic_t result={0};result.status=JPEG_DECODE_ARGUMENT;result.context_bytes=sizeof(jpeg_decoder_t);
    if(!config || !config->allocator.allocate || !config->allocator.release || !config->pool_limit ||
       !config->max_width || config->max_width>240 || !config->max_height || config->max_height>240 ||
       (config->backing.capacity && (!config->backing.open || !config->backing.read ||
                                    !config->backing.write || !config->backing.close))) {
        if(diagnostic)*diagnostic=result;
        return NULL;
    }
    jpeg_decoder_t *s=config->allocator.allocate(config->allocator.context,sizeof(*s));
    if(!s){result.status=JPEG_DECODE_ALLOCATION;result.required=sizeof(*s);if(diagnostic)*diagnostic=result;return NULL;}
    memset(s,0,sizeof(*s));s->config=*config;result.status=JPEG_DECODE_OK;
    if(diagnostic)*diagnostic=result;
    return s;
}

static void dimensions(jpeg_decoder_t *s)
{
    /* Device/output limits are resource policy, not a corrupt-JPEG diagnosis. */
    uint32_t width=s->codec.image_width,height=s->codec.image_height;
    s->diagnostic.width=width;s->diagnostic.height=height;
    uint32_t expected=s->request.expected_width;
    if(width>s->config.max_width || (expected && width!=expected)) {
        s->diagnostic.detail=JPEG_DETAIL_WIDTH;
        jpeg_decoder_fail(s,JPEG_DECODE_DIMENSIONS,width,expected ? expected : s->config.max_width);
    }
    expected=s->request.expected_height;
    if(height>s->config.max_height || (expected && height!=expected)) {
        s->diagnostic.detail=JPEG_DETAIL_HEIGHT;
        jpeg_decoder_fail(s,JPEG_DECODE_DIMENSIONS,height,expected ? expected : s->config.max_height);
    }
}

static void decode_rows(jpeg_decoder_t *s)
{
    /* Convert one bounded row, preserving full precision until RGB565 output. */
    unsigned channels=(unsigned)s->codec.output_components,precision=(unsigned)s->codec.data_precision;
    size_t bytes=(size_t)s->codec.output_width*channels*(precision>8 ? 2u : 1u);
    if(bytes>sizeof(s->samples))jpeg_decoder_fail(s,JPEG_DECODE_INTERNAL,bytes,sizeof(s->samples));
    color_sample_format_t format=channels==1 ? COLOR_SAMPLES_GRAY : channels==3 ? COLOR_SAMPLES_RGB :
        s->codec.saw_Adobe_marker ? COLOR_SAMPLES_CMYK_ADOBE : COLOR_SAMPLES_CMYK;
    while(s->codec.output_scanline<s->codec.output_height) {
        jpeg_decoder_checkpoint(s);JDIMENSION count;
        if(precision<=8){JSAMPROW row=(JSAMPROW)s->samples;count=jpeg_read_scanlines(&s->codec,&row,1);}
        else if(precision<=12){J12SAMPROW row=(J12SAMPROW)s->samples;count=jpeg12_read_scanlines(&s->codec,&row,1);}
        else {J16SAMPROW row=(J16SAMPROW)s->samples;count=jpeg16_read_scanlines(&s->codec,&row,1);}
        if(count!=1)jpeg_decoder_fail(s,JPEG_DECODE_INTERNAL,0,0);
        if(!color_convert_row_rgb565(s->samples,bytes,s->codec.output_width,precision,format,s->rgb565,240)) {
            s->diagnostic.detail=JPEG_DETAIL_SAMPLE_RANGE;jpeg_decoder_fail(s,JPEG_DECODE_INVALID,0,0);
        }
        if(s->request.row) {
            int result=s->request.row(s->request.context,s->diagnostic.rows,s->rgb565,s->codec.output_width);
            if(result)jpeg_decoder_callback_error(s,JPEG_DECODE_OUTPUT_IO,result);
        }
        jpeg_decoder_checkpoint(s);++s->diagnostic.rows;
    }
}

jpeg_decode_status_t jpeg_decoder_decode(jpeg_decoder_t *s,const jpeg_decode_request_t *request,jpeg_decode_diagnostic_t *diagnostic)
{
    /* REQUESTED_CHANGE: one reusable JPEG object, real allocation cap and exact
     * backing preflight. Mutable longjmp/cleanup state is in the owning context. */
    if(!s || !request || !request->read || !request->check || s->active ||
       request->expected_width>s->config.max_width || request->expected_height>s->config.max_height) {
        if(diagnostic){memset(diagnostic,0,sizeof(*diagnostic));diagnostic->status=JPEG_DECODE_ARGUMENT;}return JPEG_DECODE_ARGUMENT;
    }
    s->request=*request;s->diagnostic=(jpeg_decode_diagnostic_t){0};s->diagnostic.context_bytes=sizeof(*s);
    s->diagnostic.reused_object=s->created;s->diagnostic.pool_peak=s->pool_current;
    s->position=0;s->sample_arrays=0;s->backing_files=0;s->allocation_status=JPEG_DECODE_OK;s->active=true;
    if(!setjmp(s->jump)) {
        jpeg_decoder_checkpoint(s);
        if(!s->created) {
            s->codec.err=jpeg_std_error(&s->error);s->error.error_exit=fatal;s->error.emit_message=warning;
            s->codec.client_data=s;jpeg_create_decompress(&s->codec);s->created=true;jpeg_decoder_install_memory(s);
        }
        s->source=(struct jpeg_source_mgr){0};s->source.init_source=init_source;s->source.fill_input_buffer=fill_source;
        s->source.skip_input_data=skip_source;s->source.resync_to_restart=jpeg_resync_to_restart;s->source.term_source=term_source;
        s->codec.src=&s->source;
        if(jpeg_read_header(&s->codec,TRUE)!=JPEG_HEADER_OK)jpeg_decoder_fail(s,JPEG_DECODE_INVALID,0,0);
        dimensions(s);
        if(s->codec.num_components!=1 && s->codec.num_components!=3 && s->codec.num_components!=4) {
            s->diagnostic.detail=JPEG_DETAIL_COLORSPACE;jpeg_decoder_fail(s,JPEG_DECODE_UNSUPPORTED,0,0);
        }
        if(s->codec.arith_code && (s->codec.master->lossless || s->codec.data_precision!=8)) {
            s->diagnostic.detail=JPEG_DETAIL_ARITHMETIC;jpeg_decoder_fail(s,JPEG_DECODE_UNSUPPORTED,0,0);
        }
        s->codec.out_color_space=s->codec.num_components==4 ? JCS_CMYK : s->codec.num_components==1 ? JCS_GRAYSCALE : JCS_RGB;
        s->codec.quantize_colors=FALSE;s->codec.buffered_image=FALSE;s->codec.raw_data_out=FALSE;s->codec.do_block_smoothing=FALSE;
        jpeg_start_decompress(&s->codec);decode_rows(s);jpeg_finish_decompress(&s->codec);jpeg_decoder_checkpoint(s);
    }
    if(s->created)jpeg_abort_decompress(&s->codec);else jpeg_destroy_decompress(&s->codec);
    jpeg_decoder_release_backing(s);
    s->active=false;s->diagnostic.pool_retained=s->pool_current;
    if(diagnostic)*diagnostic=s->diagnostic;
    return s->diagnostic.status;
}

void jpeg_decoder_destroy(jpeg_decoder_t *s)
{
    /* Owner invokes only outside callbacks/decode; destroy releases permanent pools too. */
    if(!s || s->active)return;
    if(s->created)jpeg_destroy_decompress(&s->codec);
    jpeg_decode_allocator_t allocator=s->config.allocator;allocator.release(allocator.context,s,sizeof(*s));
}

const char *jpeg_decoder_status_name(jpeg_decode_status_t status)
{
    /* Stable external categories; library-specific numeric causes stay diagnostic. */
    static const char *const names[]={"ok","argument","invalid-jpeg","truncated-jpeg","unsupported-jpeg",
        "image-dimensions","library-pool-limit","allocation-failed","backing-capacity","backing-files",
        "input-io","output-io","backing-io","cancelled","time-limit","io-budget","internal"};
    return (unsigned)status<sizeof(names)/sizeof(names[0]) ? names[status] : "internal";
}
