/* Host capability/resource probe; not an ESP32 backend or a conformance verdict. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <setjmp.h>
#include "jpeglib.h"
#include "probe_memory.h"
#include "table_dump.h"
#include "probe_faults.h"

typedef struct { struct jpeg_error_mgr pub; jmp_buf jump; } probe_error;
typedef struct {
    struct jpeg_decompress_struct codec;
    probe_error error;
    FILE *input, *output, *extra;
    unsigned char *row;
} decode_session;
typedef struct {
    struct jpeg_compress_struct codec;
    probe_error error;
    FILE *output;
    unsigned char *row;
} encode_session;

static void fail(j_common_ptr codec)
{
    /* Return errors to the harness instead of allowing libjpeg to exit the process. */
    probe_error *error = (probe_error *)codec->err;
    char message[JMSG_LENGTH_MAX];
    (*codec->err->format_message)(codec, message);
    fprintf(stderr, "%s\n", message);
    longjmp(error->jump, 1);
}
static void warn(j_common_ptr codec, int level)
{
    /* A damaged input must not be silently repaired and reported as successful. */
    if (level < 0) fail(codec);
}
static unsigned sample(unsigned x, unsigned y, unsigned channel, unsigned precision, int patterned)
{
    /* Known exact source samples make lossless tests independent of the decoder. */
    unsigned maximum = (1u << precision) - 1u;
    return patterned ? (x * 17u + y * 31u + channel * 47u) & maximum : 1u << (precision - 1u);
}
static int generate(const char *path, const char *mode, unsigned precision,
                    unsigned width, unsigned height, int predictor, int transform,
                    unsigned restart)
{
    /* Create real JPEG fixtures, with independently predictable lossless samples. */
    if (precision < 2 || precision > 16 || width == 0 || width > 240 ||
        height == 0 || height > 240 || predictor < 1 || predictor > 7 ||
        transform < 0 || (unsigned)transform >= precision) return 2;
    encode_session *s = calloc(1, sizeof(*s));
    if (!s) return 2;
    struct jpeg_compress_struct *codec = &s->codec;
    codec->err = jpeg_std_error(&s->error.pub); s->error.pub.error_exit = fail;
    probe_memory_reset(0, 0);
    if (setjmp(s->error.jump)) {
        jpeg_destroy_compress(codec);
        if (s->output) fclose(s->output);
        free(s->row); free(s);
        return 1;
    }
    s->output = fopen(path, "wb");
    if (!s->output) { free(s); return 2; }
    jpeg_create_compress(codec);
    jpeg_stdio_dest(codec, s->output);
    int gray = strstr(mode, "gray") != NULL;
    int cmyk = strstr(mode, "cmyk") != NULL || strstr(mode, "ycck") != NULL;
    int lossless = strstr(mode, "lossless") != NULL;
    codec->image_width = width; codec->image_height = height;
    codec->input_components = gray ? 1 : cmyk ? 4 : 3;
    codec->in_color_space = gray ? JCS_GRAYSCALE : cmyk ? JCS_CMYK : JCS_RGB;
    jpeg_set_defaults(codec);
    codec->data_precision = (int)precision;
    jpeg_set_quality(codec, strstr(mode, "q83") ? 83 : 100, FALSE);
    codec->optimize_coding = TRUE;
    if (strstr(mode, "ycck")) jpeg_set_colorspace(codec, JCS_YCCK);
    if (strstr(mode, "444"))
        for (int i = 0; i < codec->num_components; ++i)
            codec->comp_info[i].h_samp_factor = codec->comp_info[i].v_samp_factor = 1;
    if (strstr(mode, "422")) {
        codec->comp_info[0].h_samp_factor = 2; codec->comp_info[0].v_samp_factor = 1;
        for (int i = 1; i < codec->num_components; ++i)
            codec->comp_info[i].h_samp_factor = codec->comp_info[i].v_samp_factor = 1;
    }
    if (strstr(mode, "arith")) codec->arith_code = TRUE;
    if (strstr(mode, "progressive")) jpeg_simple_progression(codec);
    if (lossless) {
        jpeg_set_colorspace(codec, codec->in_color_space);
        jpeg_enable_lossless(codec, predictor, transform);
    }
    codec->restart_interval = restart;
    jpeg_start_compress(codec, TRUE);
    size_t samples = (size_t)width * codec->input_components;
    s->row = malloc(samples * (precision > 8 ? 2 : 1));
    if (!s->row) longjmp(s->error.jump, 1);
    while (codec->next_scanline < codec->image_height) {
        for (unsigned x = 0; x < width; ++x)
            for (unsigned c = 0; c < (unsigned)codec->input_components; ++c) {
                unsigned value = sample(x, codec->next_scanline, c, precision,
                                        lossless || strstr(mode, "rich") != NULL);
                if (precision > 8) ((unsigned short *)s->row)[x * codec->input_components + c] = (unsigned short)value;
                else s->row[x * codec->input_components + c] = (unsigned char)value;
            }
        if (precision <= 8) { JSAMPROW p = s->row; jpeg_write_scanlines(codec, &p, 1); }
        else if (precision <= 12) { J12SAMPROW p = (J12SAMPROW)s->row; jpeg12_write_scanlines(codec, &p, 1); }
        else { J16SAMPROW p = (J16SAMPROW)s->row; jpeg16_write_scanlines(codec, &p, 1); }
    }
    jpeg_finish_compress(codec); jpeg_destroy_compress(codec);
    free(s->row); fclose(s->output); free(s);
    return 0;
}

static int decode(const char *input, const char *output, size_t budget, int backing,
                  int smoothing, int quantize, const char *color_dump)
{
    /* Measure only library pools, with separate row size and complete error unwind. */
    decode_session *s = calloc(1, sizeof(*s));
    if (!s) return 2;
    probe_memory_reset(budget, backing);
    s->codec.err = jpeg_std_error(&s->error.pub);
    s->error.pub.error_exit = fail; s->error.pub.emit_message = warn;
    volatile int passed = 0;
    volatile size_t row_bytes = 0;
    volatile unsigned width = 0, height = 0, precision = 0, channels = 0;
    if (!setjmp(s->error.jump)) {
        s->input = fopen(input, "rb"); s->output = fopen(output, "wb");
        if (!s->input || !s->output) goto done;
        jpeg_create_decompress(&s->codec);
        jpeg_stdio_src(&s->codec, s->input);
        jpeg_read_header(&s->codec, TRUE);
        width = s->codec.image_width; height = s->codec.image_height; precision = s->codec.data_precision;
        if (!width || !height || width > 240 || height > 240) goto done;
        s->codec.out_color_space = s->codec.num_components == 4 ? JCS_CMYK :
            s->codec.num_components == 1 ? JCS_GRAYSCALE : JCS_RGB;
        s->codec.do_block_smoothing = smoothing ? TRUE : FALSE;
        s->codec.quantize_colors = quantize ? TRUE : FALSE;
        jpeg_start_decompress(&s->codec);
        channels = s->codec.output_components;
        if (color_dump) {
            /* Table inspection intentionally stops before entropy/output; destroy
             * releases the session normally after all actual values are copied. */
            s->extra = fopen(color_dump, "wb");
            if (s->extra && jpeg_probe_dump_tables12(&s->codec, s->output, s->extra)) passed = 1;
            goto done;
        }
        row_bytes = (size_t)width * channels * (precision > 8 ? 2 : 1);
        s->row = malloc(row_bytes);
        if (!s->row) goto done;
        while (s->codec.output_scanline < s->codec.output_height) {
            JDIMENSION count;
            if (precision <= 8) { JSAMPROW p = s->row; count = jpeg_read_scanlines(&s->codec, &p, 1); }
            else if (precision <= 12) { J12SAMPROW p = (J12SAMPROW)s->row; count = jpeg12_read_scanlines(&s->codec, &p, 1); }
            else { J16SAMPROW p = (J16SAMPROW)s->row; count = jpeg16_read_scanlines(&s->codec, &p, 1); }
            if (count != 1 || fwrite(s->row, 1, row_bytes, s->output) != row_bytes) goto done;
        }
        jpeg_finish_decompress(&s->codec);
        passed = 1;
    }
done:
    jpeg_destroy_decompress(&s->codec);
    if (s->input) fclose(s->input);
    if (s->output) fclose(s->output);
    if (s->extra) fclose(s->extra);
    free(s->row);
    probe_memory_stats m = probe_memory_snapshot();
    printf("{\"passed\":%s,\"width\":%u,\"height\":%u,\"precision\":%u,\"channels\":%u,"
           "\"library_pool_peak\":%zu,\"library_pool_final\":%zu,\"row_bytes\":%zu,"
           "\"stores_opened\":%u,\"stores_closed\":%u,\"backing_capacity\":%llu,\"backing_read_bytes\":%llu,"
           "\"backing_write_bytes\":%llu,\"nor_calls\":%llu,\"nor_read_bytes\":%llu,\"nor_program_bytes\":%llu,"
           "\"nor_erases\":%llu,\"nor_fault_hits\":%llu,\"scratch_peak_bytes\":%zu,\"scratch_peak_files\":%u,\"scratch_error\":%u}\n",
           passed ? "true" : "false", width, height, precision, channels,
           m.peak_bytes, m.current_bytes, row_bytes, m.stores_opened, m.stores_closed,
           m.backing_capacity, m.bytes_read, m.bytes_written,m.nor_calls,m.nor_read_bytes,m.nor_program_bytes,
           m.nor_erases,m.nor_fault_hits,m.scratch_peak_bytes,m.scratch_peak_files,m.scratch_error);
    free(s);
    return passed && m.current_bytes == 0 && m.stores_opened == m.stores_closed ? 0 : 1;
}

int main(int argc, char **argv)
{
    /* Keep fixture generation and measured decode in separate process invocations. */
    if (argc > 1 && !strcmp(argv[1], "reuse")) return probe_reuse(argc, argv);
    if ((argc == 5 || argc == 10) && !strcmp(argv[1], "generate"))
        return generate(argv[2], argv[3], (unsigned)strtoul(argv[4], NULL, 10),
                        argc == 10 ? (unsigned)atoi(argv[5]) : 240,
                        argc == 10 ? (unsigned)atoi(argv[6]) : 240,
                        argc == 10 ? atoi(argv[7]) : 1,
                        argc == 10 ? atoi(argv[8]) : 0,
                        argc == 10 ? (unsigned)atoi(argv[9]) : 0);
    if ((argc == 6 || argc == 8) && !strcmp(argv[1], "decode"))
        return decode(argv[2], argv[3], (size_t)strtoull(argv[4], NULL, 10), atoi(argv[5]),
                      argc == 8 ? atoi(argv[6]) : 0, argc == 8 ? atoi(argv[7]) : 0, NULL);
    if (argc == 5 && !strcmp(argv[1], "dump-tables"))
        return decode(argv[2], argv[3], 0, 0, 0, 0, argv[4]);
    fprintf(stderr, "generate path mode precision [width height predictor transform restart] | "
                    "decode input output budget backing [smoothing quantize] | "
                    "dump-tables input range-output color-output\n");
    return 2;
}
