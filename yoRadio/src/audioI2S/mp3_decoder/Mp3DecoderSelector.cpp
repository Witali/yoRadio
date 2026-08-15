#include "Mp3DecoderSelector.h"

#include <stdlib.h>
#include <string.h>

#define MINIMP3_ONLY_MP3
#define MINIMP3_NO_SIMD
#define MINIMP3_EXTERNAL_SCRATCH
#define MINIMP3_IMPLEMENTATION
#include "../minimp3/minimp3.h"

namespace {

struct ParsedMp3Header {
    int frameBytes;
    int bitrate;
    int sampleRate;
    int channels;
    int version;
};

uint8_t selectedBackend = MP3_DECODER_HELIX;
mp3dec_t miniDecoderStorage = {};
mp3dec_t *miniDecoder = nullptr;
MP3FrameInfo_t miniFrameInfo = {};

bool parseMp3Header(const uint8_t *data, int available, ParsedMp3Header &header) {
    static const uint16_t mpeg1Bitrates[15] = {
        0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320
    };
    static const uint16_t mpeg2Bitrates[15] = {
        0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160
    };
    static const uint16_t sampleRates[3] = {44100, 48000, 32000};

    if(!data || available < 4) return false;
    if(data[0] != 0xFF || (data[1] & 0xE0) != 0xE0) return false;

    const uint8_t versionBits = (data[1] >> 3) & 0x03;
    const uint8_t layerBits = (data[1] >> 1) & 0x03;
    const uint8_t bitrateIndex = data[2] >> 4;
    const uint8_t sampleRateIndex = (data[2] >> 2) & 0x03;
    if(versionBits == 1 || layerBits != 1) return false; // reserved version or not Layer III
    if(bitrateIndex == 0 || bitrateIndex == 15 || sampleRateIndex == 3) return false;

    const bool mpeg1 = versionBits == 3;
    const int bitrateKbps = mpeg1 ? mpeg1Bitrates[bitrateIndex] : mpeg2Bitrates[bitrateIndex];
    int rate = sampleRates[sampleRateIndex];
    if(versionBits == 2) rate /= 2;
    if(versionBits == 0) rate /= 4;

    const int padding = (data[2] >> 1) & 0x01;
    const int frameBytes = ((mpeg1 ? 144000 : 72000) * bitrateKbps) / rate + padding;
    if(frameBytes < 24 || frameBytes > available) return false;

    header.frameBytes = frameBytes;
    header.bitrate = bitrateKbps * 1000;
    header.sampleRate = rate;
    header.channels = ((data[3] >> 6) == 3) ? 1 : 2;
    header.version = mpeg1 ? MPEG1 : (versionBits == 2 ? MPEG2 : MPEG25);
    return true;
}

int findValidatedFrame(unsigned char *buf, int nBytes) {
    if(!buf || nBytes < 4) return -1;
    for(int offset = 0; offset <= nBytes - 4; ++offset) {
        ParsedMp3Header header;
        if(parseMp3Header(buf + offset, nBytes - offset, header)) return offset;
    }
    return -1;
}

void clearMiniFrameInfo() {
    memset(&miniFrameInfo, 0, sizeof(miniFrameInfo));
    miniFrameInfo.bitsPerSample = 16;
    miniFrameInfo.layer = 3;
}

} // namespace

void Mp3DecoderSelect(uint8_t backend) {
    selectedBackend = backend == MP3_DECODER_MINIMP3 ? MP3_DECODER_MINIMP3 : MP3_DECODER_HELIX;
}

uint8_t Mp3DecoderSelected() {
    return selectedBackend;
}

const char* Mp3DecoderName() {
    return selectedBackend == MP3_DECODER_MINIMP3 ? "minimp3" : "Helix legacy";
}

bool Mp3DecoderAllocateBuffers() {
    if(selectedBackend == MP3_DECODER_HELIX) {
        if(MP3Decoder_AllocateBuffers()) return true;

        // Helix uses several sizeable heap allocations.  TLS streams can
        // leave enough total memory but no contiguous blocks large enough
        // for Helix, so retry with the more compact minimp3 backend.
        selectedBackend = MP3_DECODER_MINIMP3;
        log_w("Helix MP3 decoder allocation failed; retrying with minimp3");
    }
    // Allocate the larger scratch block first and keep an existing decoder
    // reservation intact.  This lets HTTPS connections reserve minimp3 before
    // the TLS heap allocations fragment the remaining memory.
    if(!mp3dec_alloc_scratch()) {
        return false;
    }
    // Keep the small decoder state out of the fragmented runtime heap.  The
    // classic ESP32 still has ample static DRAM, while some TLS handshakes
    // leave no contiguous dynamic block large enough even for mp3dec_t.
    miniDecoder = &miniDecoderStorage;
    mp3dec_init(miniDecoder);
    clearMiniFrameInfo();
    return true;
}

bool Mp3DecoderReserveScratch() {
    return mp3dec_alloc_scratch();
}

void Mp3DecoderFreeBuffers() {
    // Selection can change before cleanup (for example HTTPS forces
    // minimp3). Release both backends so the previously active decoder can
    // never survive a codec or station switch.
    MP3Decoder_FreeBuffers();
    miniDecoder = nullptr;
    memset(&miniDecoderStorage, 0, sizeof(miniDecoderStorage));
    mp3dec_free_scratch();
    clearMiniFrameInfo();
}

void Mp3DecoderClearBuffer() {
    if(selectedBackend == MP3_DECODER_HELIX) {
        MP3Decoder_ClearBuffer();
        return;
    }
    if(miniDecoder) mp3dec_init(miniDecoder);
    clearMiniFrameInfo();
}

int Mp3DecoderDecode(unsigned char *inbuf, int *bytesLeft, short *outbuf, int useSize) {
    if(selectedBackend == MP3_DECODER_HELIX) return MP3Decode(inbuf, bytesLeft, outbuf, useSize);
    if(!miniDecoder || !inbuf || !bytesLeft || !outbuf) return ERR_MP3_NULL_POINTER;

    ParsedMp3Header header;
    if(!parseMp3Header(inbuf, *bytesLeft, header)) return ERR_MP3_INDATA_UNDERFLOW;

    mp3dec_frame_info_t info = {};
    const int samplesPerChannel = mp3dec_decode_frame(
        miniDecoder, inbuf, header.frameBytes, outbuf, &info
    );
    if(info.frame_bytes != header.frameBytes) return ERR_MP3_INVALID_FRAMEHEADER;
    if(info.channels < 1 || info.channels > 2 || info.hz != header.sampleRate) {
        return ERR_MP3_INVALID_FRAMEHEADER;
    }

    *bytesLeft -= header.frameBytes;
    miniFrameInfo.bitrate = header.bitrate;
    miniFrameInfo.nChans = header.channels;
    miniFrameInfo.samprate = header.sampleRate;
    miniFrameInfo.bitsPerSample = 16;
    miniFrameInfo.outputSamps = samplesPerChannel * header.channels;
    miniFrameInfo.layer = 3;
    miniFrameInfo.version = header.version;
    return ERR_MP3_NONE;
}

int Mp3DecoderFindSyncWord(unsigned char *buf, int nBytes) {
    return selectedBackend == MP3_DECODER_HELIX ? MP3FindSyncWord(buf, nBytes) : findValidatedFrame(buf, nBytes);
}

int Mp3DecoderGetSampRate() {
    return selectedBackend == MP3_DECODER_HELIX ? MP3GetSampRate() : miniFrameInfo.samprate;
}

int Mp3DecoderGetChannels() {
    return selectedBackend == MP3_DECODER_HELIX ? MP3GetChannels() : miniFrameInfo.nChans;
}

int Mp3DecoderGetBitsPerSample() {
    return selectedBackend == MP3_DECODER_HELIX ? MP3GetBitsPerSample() : miniFrameInfo.bitsPerSample;
}

int Mp3DecoderGetBitrate() {
    return selectedBackend == MP3_DECODER_HELIX ? MP3GetBitrate() : miniFrameInfo.bitrate;
}

int Mp3DecoderGetOutputSamps() {
    return selectedBackend == MP3_DECODER_HELIX ? MP3GetOutputSamps() : miniFrameInfo.outputSamps;
}
