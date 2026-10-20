/* Host fault/recovery contract; neither the source manager nor storage is production. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <setjmp.h>
#include "jpeglib.h"
#include "jerror.h"
#include "probe_memory.h"
#include "probe_faults.h"

typedef struct {
    struct jpeg_source_mgr pub;
    FILE *file;
    JOCTET bytes[1024];
} reuse_source;

typedef struct {
    struct jpeg_error_mgr pub;
    jmp_buf jump;
    int code;
} reuse_error;

typedef struct {
    struct jpeg_decompress_struct codec;
    reuse_error error;
    reuse_source source;
    FILE *input, *output;
    unsigned char row[240 * 4 * 2];
    int created, passed;
    unsigned long rows;
} reuse_session;

typedef struct {
    int passed, error, reused_object;
    unsigned long rows;
    probe_memory_stats memory;
    probe_fault_stats faults;
} reuse_result;

static void fatal(j_common_ptr codec)
{
    /* Retain the real library error code before returning to the owning session. */
    reuse_error *error = (reuse_error *)codec->err;
    error->code = codec->err->msg_code;
    longjmp(error->jump, 1);
}

static void warning(j_common_ptr codec, int level)
{
    /* Truncation or corrupt input must not be accepted through warning recovery. */
    if (level < 0) fatal(codec);
}

static void init_source(j_decompress_ptr codec)
{
    /* The harness opens and rewinds each input before attaching this manager. */
    (void)codec;
}

static boolean fill_source(j_decompress_ptr codec)
{
    /* Exercise a bounded input read, including a real partial read on failure. */
    reuse_source *source = (reuse_source *)codec->src;
    int fail = probe_fault_visit(PROBE_FAULT_INPUT);
    size_t count = fread(source->bytes, 1, sizeof(source->bytes) - (fail ? 1 : 0), source->file);
    if (fail || ferror(source->file)) ERREXIT(codec, JERR_FILE_READ);
    if (!count) ERREXIT(codec, JERR_INPUT_EOF);
    source->pub.next_input_byte = source->bytes;
    source->pub.bytes_in_buffer = count;
    return TRUE;
}

static void skip_source(j_decompress_ptr codec, long count)
{
    /* Skip metadata through the same checked reader; do not bypass injected I/O. */
    if (count <= 0) return;
    while ((size_t)count > codec->src->bytes_in_buffer) {
        count -= (long)codec->src->bytes_in_buffer;
        fill_source(codec);
    }
    codec->src->next_input_byte += count;
    codec->src->bytes_in_buffer -= (size_t)count;
}

static void term_source(j_decompress_ptr codec)
{
    /* File ownership stays with the harness on success, abort and create failure. */
    (void)codec;
}

static reuse_result cycle(reuse_session *s, const char *input, const char *output)
{
    /* REQUESTED_CHANGE: reuse the exact JPEG object after an injected fatal error.
     * Only abort/destroy may follow error_exit.  Failed object creation requires
     * destroy/recreate; successful creation permits jpeg_abort_decompress reuse.
     * Keep mutable cleanup state on the heap so longjmp does not invalidate it. */
    int reused = s->created;
    s->error.code = 0;
    s->passed = 0;
    s->rows = 0;
    if (!setjmp(s->error.jump)) {
        if (!s->created) {
            jpeg_create_decompress(&s->codec);
            s->created = 1;
        }
        s->input = fopen(input, "rb");
        s->output = fopen(output, "wb");
        if (!s->input || !s->output) ERREXIT(&s->codec, JERR_FILE_READ);
        s->source = (reuse_source){0};
        s->source.file = s->input;
        s->source.pub.init_source = init_source;
        s->source.pub.fill_input_buffer = fill_source;
        s->source.pub.skip_input_data = skip_source;
        s->source.pub.resync_to_restart = jpeg_resync_to_restart;
        s->source.pub.term_source = term_source;
        s->codec.src = &s->source.pub;
        jpeg_read_header(&s->codec, TRUE);
        if (!s->codec.image_width || s->codec.image_width > 240 ||
            !s->codec.image_height || s->codec.image_height > 240)
            ERREXIT(&s->codec, JERR_INPUT_EOF);
        s->codec.out_color_space = s->codec.num_components == 4 ? JCS_CMYK :
            s->codec.num_components == 1 ? JCS_GRAYSCALE : JCS_RGB;
        s->codec.quantize_colors = FALSE;
        s->codec.do_block_smoothing = FALSE;
        jpeg_start_decompress(&s->codec);
        size_t row_bytes = (size_t)s->codec.output_width * s->codec.output_components *
            (s->codec.data_precision > 8 ? 2 : 1);
        if (row_bytes > sizeof(s->row)) ERREXIT(&s->codec, JERR_WIDTH_OVERFLOW);
        while (s->codec.output_scanline < s->codec.output_height) {
            JDIMENSION count;
            if (s->codec.data_precision <= 8) {
                JSAMPROW row = s->row;
                count = jpeg_read_scanlines(&s->codec, &row, 1);
            } else if (s->codec.data_precision <= 12) {
                J12SAMPROW row = (J12SAMPROW)s->row;
                count = jpeg12_read_scanlines(&s->codec, &row, 1);
            } else {
                J16SAMPROW row = (J16SAMPROW)s->row;
                count = jpeg16_read_scanlines(&s->codec, &row, 1);
            }
            if (count != 1) ERREXIT(&s->codec, JERR_INPUT_EOF);
            int fail = probe_fault_visit(PROBE_FAULT_OUTPUT);
            size_t written = fwrite(s->row, 1, row_bytes - (fail ? 1 : 0), s->output);
            if (fail || written != row_bytes) ERREXIT(&s->codec, JERR_FILE_WRITE);
            ++s->rows;
        }
        jpeg_finish_decompress(&s->codec);
        s->passed = 1;
    }
    if (s->created) jpeg_abort_decompress(&s->codec);
    else jpeg_destroy_decompress(&s->codec);
    if (s->input) fclose(s->input);
    if (s->output && fclose(s->output)) s->passed = 0;
    s->input = s->output = NULL;
    reuse_result result = {s->passed, s->error.code, reused, s->rows,
                           probe_memory_snapshot(), probe_fault_snapshot()};
    return result;
}

static void print_result(const char *name, const reuse_result *r)
{
    /* Include retained permanent pools; only the final destroy must reach zero. */
    printf("\"%s\":{\"passed\":%s,\"error\":%d,\"reused_object\":%s,\"rows\":%lu,"
           "\"library_pool_current\":%zu,\"library_pool_peak\":%zu,"
           "\"stores_opened\":%u,\"stores_closed\":%u,\"fault_hits\":%lu,\"visits\":{",
           name, r->passed ? "true" : "false", r->error,
           r->reused_object ? "true" : "false", r->rows,
           r->memory.current_bytes, r->memory.peak_bytes, r->memory.stores_opened,
           r->memory.stores_closed, r->faults.hits);
    for (unsigned i = 0; i < PROBE_FAULT_COUNT; ++i)
        printf("%s\"%s\":%lu", i ? "," : "", probe_fault_name((probe_fault_kind)i), r->faults.visits[i]);
    printf("}}");
}

int probe_reuse(int argc, char **argv)
{
    /* Run fault, abort, recovery and final destroy without restarting the process. */
    if (argc != 10 && argc != 11) return 2;
    probe_fault_kind fault = probe_fault_parse(argv[7]);
    if ((int)fault < 0) return 2;
    unsigned long ordinal = strtoul(argv[8], NULL, 10);
    int persistent = atoi(argv[9]);
    if ((fault == PROBE_FAULT_NONE) != (ordinal == 0) ||
        (persistent && fault != PROBE_FAULT_ALLOC)) return 2;
    reuse_session *s = calloc(1, sizeof(*s));
    if (!s) return 2;
    s->codec.err = jpeg_std_error(&s->error.pub);
    s->error.pub.error_exit = fatal;
    s->error.pub.emit_message = warning;
    size_t budget = (size_t)strtoull(argv[5], NULL, 10);
    probe_memory_reset(budget, atoi(argv[6]));
    probe_fault_reset(fault, ordinal, persistent);
    reuse_result first = cycle(s, argv[2], argv[3]);
    probe_fault_reset(PROBE_FAULT_NONE, 0, 0);
    reuse_result recovery = cycle(s, argc == 11 ? argv[10] : argv[2], argv[4]);
    jpeg_destroy_decompress(&s->codec);
    probe_memory_stats final = probe_memory_snapshot();
    printf("{");
    print_result("first", &first);
    printf(",");
    print_result("recovery", &recovery);
    int expected_error = 0;
    switch (fault) {
        case PROBE_FAULT_ALLOC: expected_error = JERR_OUT_OF_MEMORY; break;
        case PROBE_FAULT_OPEN: expected_error = JERR_TFILE_CREATE; break;
        case PROBE_FAULT_READ: expected_error = JERR_TFILE_READ; break;
        case PROBE_FAULT_WRITE: expected_error = JERR_TFILE_WRITE; break;
        case PROBE_FAULT_SEEK: expected_error = JERR_TFILE_SEEK; break;
        case PROBE_FAULT_INPUT: expected_error = JERR_FILE_READ; break;
        case PROBE_FAULT_OUTPUT: expected_error = JERR_FILE_WRITE; break;
        default: break;
    }
    printf(",\"library_pool_final\":%zu,\"stores_opened\":%u,\"stores_closed\":%u,"
           "\"expected_error\":%d,\"session_bytes\":%zu}\n",
           final.current_bytes, final.stores_opened, final.stores_closed,
           expected_error, sizeof(*s));
    free(s);
    return recovery.passed && !final.current_bytes &&
        first.memory.stores_opened == first.memory.stores_closed &&
        final.stores_opened == final.stores_closed &&
        (!budget || final.peak_bytes <= budget) &&
        (fault == PROBE_FAULT_NONE || first.faults.hits) ? 0 : 1;
}
