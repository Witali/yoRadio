#include <stdint.h>
#include "coder.h"
#define R8(n) (((n) + 7) & ~7)
#ifdef AAC_ENABLE_SBR
#error This probe must measure ESP8266 AAC-LC without SBR
#endif
char size_aac_info[sizeof(AACDecInfo)];
char size_aac_base[sizeof(PSInfoBase)];
char size_aac_total[1600 + 4096 + R8(sizeof(AACDecInfo)) + R8(sizeof(PSInfoBase))];
