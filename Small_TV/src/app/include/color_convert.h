#pragma once
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

typedef enum
{
    COLOR_SAMPLES_GRAY,
    COLOR_SAMPLES_RGB,
    COLOR_SAMPLES_CMYK,       /* Conventional ink coverage: zero means no ink. */
    COLOR_SAMPLES_CMYK_ADOBE  /* Inverted stored samples: maximum means no ink. */
} color_sample_format_t;

uint16_t rgb565_from_rgb888(uint32_t rgb);
uint32_t rgb888_from_rgb565(uint16_t rgb);

/* Convert packed native-endian samples, with no allocation or LCD/codec I/O.
 * Precision 2..8 uses uint8_t samples; 9..16 uses native-endian uint16_t values.
 * YCCK must first be decoded to CMYK by the codec.  Polarity is explicit.
 * The source and destination must not overlap.  Invalid sizes, formats, samples
 * or precision return false before writing any output.  Output words are native
 * RGB565; the display driver owns SPI byte order.  CMYK is a generic display
 * fallback, not an ICC color-management transform. */
bool color_convert_row_rgb565(const void *source, size_t source_bytes, size_t pixels,
                              unsigned precision, color_sample_format_t format,
                              uint16_t *destination, size_t destination_pixels);
