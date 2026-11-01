#include "opus_family1_playback.h"
#include <stdio.h>
int main(void) {
    printf("{\"adapter_bytes\":%zu,\"raw_owner_bytes\":%zu,\"packet_owner_bytes\":%zu,\"static_zero_bytes\":%zu}\n",
        sizeof(opus_family1_playback),sizeof(opus_family1_decoder),sizeof(ogg_opus_audio_packets),
#ifdef YORADIO_OPUS_TAGS_STREAM_H
        sizeof(ofp_zero_chunk)
#else
        (size_t)0
#endif
    );return 0;
}
