#include "sdkconfig.h"
#include "aac_fill_parser.h"

#ifdef CONFIG_YORADIO_QEMU_AAC_LATE_SBR_TEST
void aac_late_sbr_after_fill(void *stream);
#endif

void __wrap_getfill(aac_fill_bits_t *bits) {
    aac_fill_skip(bits);
}

void __wrap_get_sbr_bitstream(aac_fill_stream_t *stream,aac_fill_bits_t *bits) {
    bool valid=aac_fill_sbr(stream,bits);
#ifdef CONFIG_YORADIO_QEMU_AAC_LATE_SBR_TEST
    if(valid)aac_late_sbr_after_fill(stream);
#else
    (void)valid;
#endif
}
