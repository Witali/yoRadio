/* TJpgDec R0.03 configuration for the ESP32-C2 software decoder.
 * Adapted from Espressif's sdkconfig-based configuration; decoder unchanged.
 * FIXED_RECONSTRUCTION: factory 0x42011624..0x420116c6 clips each IDCT
 * component to a byte before YCbCr conversion. The fast path retains signed
 * overshoot and changes RGB565 colors near black in the status JPEGs. */
#pragma once
#define JD_SZBUF 512
#define JD_FORMAT 1
#define JD_USE_SCALE 0
#define JD_TBLCLIP 1
#define JD_FASTDECODE 0
#define JD_DEFAULT_HUFFMAN 0
