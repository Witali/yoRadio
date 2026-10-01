// Pinned esp_audio_codec 2.6.2 experiment. Preserve permission to detect SBR
// after an LC frame with the same ADTS core configuration. No DSP changes.
#include "sdkconfig.h"
#ifdef CONFIG_YORADIO_AAC_SBR_CONTINUITY
#include <stdint.h>

int __real_PVMP4AudioDecodeFrame(uint32_t *external, uint32_t *core);
int __wrap_PVMP4AudioDecodeFrame(uint32_t *external, uint32_t *core) {
    // The native decoder clears both switches after the first LC frame.
    // SBR bitstream storage at core+0x8a60 is retained from AAC-Plus init.
    external[7] = 1;
    ((uint8_t *)core)[8] = 1;
    return __real_PVMP4AudioDecodeFrame(external, core);
}
#endif
