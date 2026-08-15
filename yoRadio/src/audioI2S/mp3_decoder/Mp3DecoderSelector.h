#pragma once

#include <Arduino.h>
#include "mp3_decoder.h"

enum Mp3DecoderBackend : uint8_t {
    MP3_DECODER_HELIX = 0,
    MP3_DECODER_MINIMP3 = 1
};

void Mp3DecoderSelect(uint8_t backend);
uint8_t Mp3DecoderSelected();
const char* Mp3DecoderName();

bool Mp3DecoderAllocateBuffers();
bool Mp3DecoderReserveScratch();
void Mp3DecoderFreeBuffers();
void Mp3DecoderClearBuffer();
int Mp3DecoderDecode(unsigned char *inbuf, int *bytesLeft, short *outbuf, int useSize);
int Mp3DecoderFindSyncWord(unsigned char *buf, int nBytes);
int Mp3DecoderGetSampRate();
int Mp3DecoderGetChannels();
int Mp3DecoderGetBitsPerSample();
int Mp3DecoderGetBitrate();
int Mp3DecoderGetOutputSamps();
