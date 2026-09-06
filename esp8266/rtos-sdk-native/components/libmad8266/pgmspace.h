#pragma once

/* ESP8266 RTOS SDK maps const data through the flash cache by default.  This
 * compatibility surface keeps the ESP8266Audio libmad port independent from
 * Arduino while preserving its PROGMEM source annotations. */
#include <stdint.h>
#include <string.h>

#ifndef PROGMEM
#define PROGMEM
#endif
#ifndef PSTR
#define PSTR(value) (value)
#endif
#ifndef memcpy_P
#define memcpy_P(destination, source, size) \
    memcpy((destination), (source), (size))
#endif
#ifndef pgm_read_byte
#define pgm_read_byte(address) (*(const uint8_t *)(address))
#endif
#ifndef pgm_read_word
#define pgm_read_word(address) (*(const uint16_t *)(address))
#endif
#ifndef pgm_read_dword
#define pgm_read_dword(address) (*(const uint32_t *)(address))
#endif
