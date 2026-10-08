/*
 * flac_decoder.cpp
 * Java source code from https://www.nayuki.io/page/simple-flac-implementation
 * adapted to ESP32
 *
 * Created on: Jul 03,2020
 * Updated on: Jul 03,2021
 *
 * Author: Wolle
 *
 *
 */
#include "flac_decoder.h"

namespace {

FLACFrameHeader_t frameHeaderStorage = {};
FLACMetadataBlock_t metadataBlockStorage = {};
#ifdef FLAC_SEGMENTED_WORKSPACE
constexpr size_t kWorkspaceSegmentSamples = 1024;
constexpr size_t kWorkspaceSegmentCount =
    (MAX_BLOCKSIZE + kWorkspaceSegmentSamples - 1) /
    kWorkspaceSegmentSamples;
struct SampleBuffer {
    int32_t* segments[kWorkspaceSegmentCount] = {};
    int32_t& operator[](size_t index) {
        return segments[index / kWorkspaceSegmentSamples]
                       [index % kWorkspaceSegmentSamples];
    }
};
SampleBuffer samplesBuffer[MAX_CHANNELS] = {};
#else
int32_t* samplesStorage = nullptr;
int32_t* samplesBuffer[MAX_CHANNELS] = {};
#endif
constexpr size_t kMaximumLpcOrder = 32;
constexpr uint8_t kMaximumLpcPredictionShift = 15;
int32_t coefs[kMaximumLpcOrder] = {};
uint8_t coefficientCount = 0;
uint16_t allocatedBlockSize = 0;
uint8_t allocatedChannels = 0;
uint16_t outputOffset = 0;

int32_t* allocateSamples(size_t bytes) {
    if(psramFound()) return static_cast<int32_t*>(ps_malloc(bytes));
    return static_cast<int32_t*>(malloc(bytes));
}

} // namespace

FLACFrameHeader_t* FLACFrameHeader = &frameHeaderStorage;
FLACMetadataBlock_t* FLACMetadataBlock = &metadataBlockStorage;

const uint16_t outBuffSize = FLAC_OUTPUT_FRAMES;
uint16_t m_blockSize=0;
uint16_t m_blockSizeLeft = 0;
uint16_t m_validSamples = 0;
uint8_t  m_status = 0;
uint8_t* m_inptr;
int32_t  m_bytesAvail;
int32_t  m_bytesDecoded = 0;
uint32_t m_rIndex=0;
int8_t   m_readError = ERR_FLAC_NONE;
uint64_t m_bitBuffer = 0;
uint8_t  m_bitBufferLen = 0;
bool     m_f_OggS_found = false;

//----------------------------------------------------------------------------------------------------------------------
//          FLAC INI SECTION
//----------------------------------------------------------------------------------------------------------------------
bool FLACDecoder_AllocateBuffers(uint16_t maxBlockSize, uint8_t channels){
    if(maxBlockSize == 0 || maxBlockSize > MAX_BLOCKSIZE ||
       channels == 0 || channels > MAX_CHANNELS) {
        log_e("invalid FLAC buffer geometry: %u samples, %u channels",
              maxBlockSize, channels);
        return false;
    }

    FLACDecoder_FreeBuffers();
#ifdef FLAC_SEGMENTED_WORKSPACE
    const size_t segmentCount =
        (maxBlockSize + kWorkspaceSegmentSamples - 1) /
        kWorkspaceSegmentSamples;
    for(uint8_t channel = 0; channel < channels; ++channel) {
        for(size_t segment = 0; segment < segmentCount; ++segment) {
            const size_t firstSample = segment * kWorkspaceSegmentSamples;
            const size_t sampleCount = std::min(
                kWorkspaceSegmentSamples,
                static_cast<size_t>(maxBlockSize) - firstSample);
            samplesBuffer[channel].segments[segment] =
                allocateSamples(sampleCount * sizeof(int32_t));
            if(!samplesBuffer[channel].segments[segment]) {
                log_e("not enough memory for FLAC workspace segment (%u bytes)",
                      static_cast<unsigned>(sampleCount * sizeof(int32_t)));
                FLACDecoder_FreeBuffers();
                return false;
            }
        }
    }
#else
    const size_t channelBytes = static_cast<size_t>(maxBlockSize) * sizeof(int32_t);
    const size_t workspaceBytes = channelBytes * channels;
    samplesStorage = allocateSamples(workspaceBytes);
    if(!samplesStorage) {
        log_e("not enough memory for FLAC workspace (%u bytes)",
              static_cast<unsigned>(workspaceBytes));
        return false;
    }
    for(uint8_t channel = 0; channel < channels; ++channel) {
        samplesBuffer[channel] = samplesStorage +
                                 static_cast<size_t>(channel) * maxBlockSize;
    }
#endif
    allocatedBlockSize = maxBlockSize;
    allocatedChannels = channels;
    FLACDecoder_ClearBuffer();
    return true;
}
//----------------------------------------------------------------------------------------------------------------------
void FLACDecoder_ClearBuffer(){
    memset(FLACFrameHeader,   0, sizeof(FLACFrameHeader_t));
    memset(FLACMetadataBlock, 0, sizeof(FLACMetadataBlock_t));
    memset(coefs, 0, sizeof(coefs));
    coefficientCount = 0;
    outputOffset = 0;
    m_status = DECODE_FRAME;
    m_readError = ERR_FLAC_NONE;
    return;
}
//----------------------------------------------------------------------------------------------------------------------
void FLACDecoder_FreeBuffers(){
#ifdef FLAC_SEGMENTED_WORKSPACE
    for(uint8_t channel = 0; channel < MAX_CHANNELS; ++channel) {
        for(size_t segment = 0; segment < kWorkspaceSegmentCount; ++segment) {
            free(samplesBuffer[channel].segments[segment]);
            samplesBuffer[channel].segments[segment] = nullptr;
        }
    }
#else
    free(samplesStorage);
    samplesStorage = nullptr;
    for(uint8_t channel = 0; channel < MAX_CHANNELS; ++channel) {
        samplesBuffer[channel] = nullptr;
    }
#endif
    allocatedBlockSize = 0;
    allocatedChannels = 0;
    coefficientCount = 0;
    outputOffset = 0;
    memset(FLACFrameHeader, 0, sizeof(FLACFrameHeader_t));
    memset(FLACMetadataBlock, 0, sizeof(FLACMetadataBlock_t));
}
//----------------------------------------------------------------------------------------------------------------------
size_t FLACDecoder_GetAllocatedBytes(){
    return static_cast<size_t>(allocatedBlockSize) * allocatedChannels * sizeof(int32_t);
}
//----------------------------------------------------------------------------------------------------------------------
//            B I T R E A D E R
//----------------------------------------------------------------------------------------------------------------------
uint32_t readUint(uint8_t nBits){
    if(m_readError) return 0;
    if(nBits > 32) { m_readError = ERR_FLAC_INVALID_DATA; return 0; }
    while (m_bitBufferLen < nBits){
        if(m_bytesAvail <= 0) { m_readError = ERR_FLAC_TRUNCATED_INPUT; return 0; }
        uint8_t temp = *(m_inptr + m_rIndex);
        m_rIndex++;
        m_bytesAvail--;
        m_bitBuffer = (m_bitBuffer << 8) | temp;
        m_bitBufferLen += 8;
    }
    m_bitBufferLen -= nBits;
    uint32_t result = m_bitBuffer >> m_bitBufferLen;
    if (nBits < 32)
        result &= (UINT32_C(1) << nBits) - 1;
    return result;
}

int32_t readSignedInt(int nBits){
    // A residual escape width of zero encodes zero without consuming bits.
    if(nBits == 0) return 0;
    if(nBits < 0 || nBits > 32) { m_readError = ERR_FLAC_INVALID_DATA; return 0; }
    int32_t temp = readUint(nBits) << (32 - nBits);
    temp = temp >> (32 - nBits); // The C++ compiler uses the sign bit to fill vacated bit positions
    return temp;
}

int64_t readRiceSignedInt(uint8_t param){
    if(param > 30) { m_readError = ERR_FLAC_INVALID_DATA; return 0; }
    uint32_t val = 0;
    while (readUint(1) == 0) {
        if(m_readError) return 0;
        if(val == (UINT32_MAX >> param)) { m_readError = ERR_FLAC_INVALID_DATA; return 0; }
        ++val;
    }
    val = (val << param) | readUint(param);
    if(val == UINT32_MAX) { m_readError = ERR_FLAC_INVALID_DATA; return 0; }
    return static_cast<int64_t>(val >> 1) ^ -static_cast<int64_t>(val & 1);
}

void alignToByte() {
    m_bitBufferLen -= m_bitBufferLen % 8;
}
//----------------------------------------------------------------------------------------------------------------------
//              F L A C - D E C O D E R
//----------------------------------------------------------------------------------------------------------------------
void FLACSetRawBlockParams(uint8_t Chans, uint32_t SampRate, uint8_t BPS, uint32_t tsis, uint32_t AuDaLength){
    FLACMetadataBlock->numChannels = Chans;
    FLACMetadataBlock->sampleRate = SampRate;
    FLACMetadataBlock->bitsPerSample = BPS;
    FLACMetadataBlock->totalSamples = tsis;  // total samples in stream
    FLACMetadataBlock->audioDataLength = AuDaLength;
}
//----------------------------------------------------------------------------------------------------------------------
void FLACDecoderReset(){ // set var to default
    m_status = DECODE_FRAME;
    m_bitBuffer = 0;
    m_bitBufferLen = 0;
    outputOffset = 0;
    m_readError = ERR_FLAC_NONE;
    m_f_OggS_found = false;
}
//----------------------------------------------------------------------------------------------------------------------
int FLACFindSyncWord(unsigned char *buf, int nBytes) {
    int i;

    /* find byte-aligned syncword - need 13 matching bits */
    for (i = 0; i < nBytes - 1; i++) {
        if ((buf[i + 0] & 0xFF) == 0xFF  && (buf[i + 1] & 0xF8) == 0xF8) {
            FLACDecoderReset();
            return i;
        }
    }
    return -1;
}
//----------------------------------------------------------------------------------------------------------------------
int FLACFindOggSyncWord(unsigned char *buf, int nBytes){
    int i;

    /* find byte-aligned syncword - need 13 matching bits */
    for (i = 0; i < nBytes - 1; i++) {
        if ((buf[i + 0] & 0xFF) == 0xFF  && (buf[i + 1] & 0xF8) == 0xF8) {
            FLACDecoderReset();
            log_i("FLAC sync found");
            return i;
        }
    }
    /* find byte-aligned OGG Magic - OggS */
    constexpr int kOggCaptureBytes = 4;
    for (i = 0; i <= nBytes - kOggCaptureBytes; i++) {
        if ((buf[i + 0] == 'O') && (buf[i + 1] == 'g') && (buf[i + 2] == 'g') && (buf[i + 3] == 'S')) {
            FLACDecoderReset();
            log_i("OggS found");
            m_f_OggS_found = true;
            return i;
        }
    }
    return -1;
}
//----------------------------------------------------------------------------------------------------------------------
int FLACparseOggHeader(unsigned char *buf, int nBytes){
    // The capture pattern has already been consumed. Only the header length
    // is used by this legacy path; do not read discarded fields or lacing
    // bytes until the entire header is available.
    constexpr int kHeaderAfterCaptureBytes = 23;
    constexpr int kPageSegmentsOffset = kHeaderAfterCaptureBytes - 1;
    if(nBytes < kHeaderAfterCaptureBytes) return ERR_FLAC_TRUNCATED_INPUT;
    const int headerBytes = kHeaderAfterCaptureBytes + buf[kPageSegmentsOffset];
    return nBytes < headerBytes ? ERR_FLAC_TRUNCATED_INPUT : headerBytes;
}
//----------------------------------------------------------------------------------------------------------------------
int8_t FLACDecode(uint8_t *inbuf, int *bytesLeft, short *outbuf){
    flac_profile::Scope scope(flac_profile::frame);
    m_validSamples = 0;
    if(!bytesLeft || !outbuf || !inbuf || *bytesLeft < 0) return ERR_FLAC_INVALID_DATA;
    if(m_readError) return m_readError;

    if(m_f_OggS_found == true){
        m_f_OggS_found = false;
        const int headerBytes = FLACparseOggHeader(inbuf, *bytesLeft);
        if(headerBytes < 0) return static_cast<int8_t>(headerBytes);
        *bytesLeft -= headerBytes;
        return ERR_FLAC_NONE;
    }

    if(m_status != OUT_SAMPLES){
        m_rIndex = 0;
        m_bytesAvail = (*bytesLeft);
        m_inptr = inbuf;
    }

    if(m_status == DECODE_FRAME){  // Read a ton of header fields, and ignore most of them

        if (*bytesLeft >= 4 && (inbuf[0] == 'O') && (inbuf[1] == 'g') && (inbuf[2] == 'g') && (inbuf[3] == 'S')){
            *bytesLeft -= 4;
            m_f_OggS_found = true;
            return ERR_FLAC_NONE;
        }

        uint32_t temp = readUint(8);
        uint16_t sync = temp << 6 |readUint(6);
        if(m_readError) return m_readError;
        if (sync != 0x3FFE){
            log_i("Sync code expected 0x3FFE but received %X", sync);
            return ERR_FLAC_SYNC_CODE_NOT_FOUND;
        }

        readUint(1);
        FLACFrameHeader->blockingStrategy = readUint(1);
        FLACFrameHeader->blockSizeCode = readUint(4);
        FLACFrameHeader->sampleRateCode = readUint(4);
        FLACFrameHeader->chanAsgn = readUint(4);
        FLACFrameHeader->sampleSizeCode = readUint(3);
        if(m_readError) return m_readError;
        if(FLACFrameHeader->chanAsgn > 10) return ERR_FLAC_RESERVED_CHANNEL_ASSIGNMENT;
        const uint8_t frameChannels = FLACFrameHeader->chanAsgn <= 7 ?
                                       FLACFrameHeader->chanAsgn + 1 : 2;
        if(frameChannels > allocatedChannels ||
           (FLACMetadataBlock->numChannels && frameChannels != FLACMetadataBlock->numChannels))
            return ERR_FLAC_UNKNOWN_CHANNEL_ASSIGNMENT;

        if(!FLACMetadataBlock->numChannels){
            if(FLACFrameHeader->chanAsgn == 0) FLACMetadataBlock->numChannels = 1;
            if(FLACFrameHeader->chanAsgn == 1) FLACMetadataBlock->numChannels = 2;
            if(FLACFrameHeader->chanAsgn > 7)  FLACMetadataBlock->numChannels = 2;
        }
        if(FLACMetadataBlock->numChannels < 1) return ERR_FLAC_UNKNOWN_CHANNEL_ASSIGNMENT;

        // RFC 9639 section 9.1.4: zero inherits STREAMINFO; three is reserved.
        static const uint8_t frameDepths[] = {0, 8, 12, 0, 16, 20, 24, 32};
        const uint8_t frameDepth = frameDepths[FLACFrameHeader->sampleSizeCode];
        if(FLACFrameHeader->sampleSizeCode == 3) return ERR_FLAC_INVALID_DATA;
        if(frameDepth) FLACMetadataBlock->bitsPerSample = frameDepth;
        if(FLACMetadataBlock->bitsPerSample > FLAC_MAX_BITS_PER_SAMPLE)
            return ERR_FLAC_BITS_PER_SAMPLE_TOO_BIG;
        if(FLACMetadataBlock->bitsPerSample < FLAC_MIN_BITS_PER_SAMPLE)
            return ERR_FLAG_BITS_PER_SAMPLE_UNKNOWN;

        if(!FLACMetadataBlock->sampleRate){
            if(FLACFrameHeader->sampleRateCode == 1)  FLACMetadataBlock->sampleRate =  88200;
            if(FLACFrameHeader->sampleRateCode == 2)  FLACMetadataBlock->sampleRate = 176400;
            if(FLACFrameHeader->sampleRateCode == 3)  FLACMetadataBlock->sampleRate = 192000;
            if(FLACFrameHeader->sampleRateCode == 4)  FLACMetadataBlock->sampleRate =   8000;
            if(FLACFrameHeader->sampleRateCode == 5)  FLACMetadataBlock->sampleRate =  16000;
            if(FLACFrameHeader->sampleRateCode == 6)  FLACMetadataBlock->sampleRate =  22050;
            if(FLACFrameHeader->sampleRateCode == 7)  FLACMetadataBlock->sampleRate =  24000;
            if(FLACFrameHeader->sampleRateCode == 8)  FLACMetadataBlock->sampleRate =  32000;
            if(FLACFrameHeader->sampleRateCode == 9)  FLACMetadataBlock->sampleRate =  44100;
            if(FLACFrameHeader->sampleRateCode == 10) FLACMetadataBlock->sampleRate =  48000;
            if(FLACFrameHeader->sampleRateCode == 11) FLACMetadataBlock->sampleRate =  96000;
        }

        readUint(1);
        temp = (readUint(8) << 24);
        temp = ~temp;

        uint32_t shift = 0x80000000; // Number of leading zeros
        int8_t count = 0;
        for(int i=0; i<32; i++){
            if((temp & shift) == 0) {count++; shift >>= 1;}
            else break;
        }
        count--;
        for (int i = 0; i < count; i++) readUint(8);
        m_blockSize = 0;

        if (FLACFrameHeader->blockSizeCode == 1)
            m_blockSize = 192;
        else if (2 <= FLACFrameHeader->blockSizeCode && FLACFrameHeader->blockSizeCode <= 5)
            m_blockSize = 576 << (FLACFrameHeader->blockSizeCode - 2);
        else if (FLACFrameHeader->blockSizeCode == 6)
            m_blockSize = readUint(8) + 1;
        else if (FLACFrameHeader->blockSizeCode == 7)
            m_blockSize = readUint(16) + 1;
        else if (8 <= FLACFrameHeader->blockSizeCode && FLACFrameHeader->blockSizeCode <= 15)
            m_blockSize = 256 << (FLACFrameHeader->blockSizeCode - 8);
        else{
            return ERR_FLAC_RESERVED_BLOCKSIZE_UNSUPPORTED;
        }
        if(m_readError) return m_readError;
        if(!m_blockSize) return ERR_FLAC_INVALID_DATA;

        if(m_blockSize > MAX_BLOCKSIZE){
            log_e("Error: blockSize too big");
            return ERR_FLAC_BLOCKSIZE_TOO_BIG;
        }
        if(m_blockSize > allocatedBlockSize ||
           FLACMetadataBlock->numChannels > allocatedChannels) {
            log_e("FLAC frame exceeds decoder buffer: %u/%u samples, %u/%u channels",
                  m_blockSize, allocatedBlockSize,
                  FLACMetadataBlock->numChannels, allocatedChannels);
            return ERR_FLAC_BLOCKSIZE_TOO_BIG;
        }

        if(FLACFrameHeader->sampleRateCode == 12)
            readUint(8);
        else if (FLACFrameHeader->sampleRateCode == 13 || FLACFrameHeader->sampleRateCode == 14){
            readUint(16);
        }
        readUint(8);
        if(m_readError) return m_readError;
        m_status = DECODE_SUBFRAMES;
        *bytesLeft = m_bytesAvail;
        m_blockSizeLeft = m_blockSize;

        return ERR_FLAC_NONE;
    }

    if(m_status == DECODE_SUBFRAMES){

        // Decode each channel's subframe, then skip footer
        int ret = decodeSubframes();
        if(ret != 0) return ret;
        if(m_readError) return m_readError;
        // Invalid decorrelated channels must not wrap during s16 conversion.
        const int32_t sourceLimit = INT32_C(1) << (FLACMetadataBlock->bitsPerSample - 1);
        for(uint8_t ch = 0; ch < FLACMetadataBlock->numChannels; ++ch)
            for(uint16_t i = 0; i < m_blockSize; ++i)
                if(samplesBuffer[ch][i] < -sourceLimit || samplesBuffer[ch][i] >= sourceLimit)
                    return ERR_FLAC_INVALID_DATA;
        // Do not expose PCM from a frame whose two-byte footer is missing.
        constexpr int kFrameFooterBytes = 2;
        if(m_bytesAvail + m_bitBufferLen / 8 < kFrameFooterBytes)
            return ERR_FLAC_TRUNCATED_INPUT;
        m_status = OUT_SAMPLES;
    }

    if(m_status == OUT_SAMPLES){  // Write the decoded samples
        // blocksize can be much greater than outbuff, so we can't stuff all in once
        // therefore we need often more than one loop (split outputblock into pieces)
        uint16_t blockSize;
        if(m_blockSize < outBuffSize + outputOffset) blockSize = m_blockSize - outputOffset;
        else blockSize = outBuffSize;


        for (int i = 0; i < blockSize; i++) {
            for (int j = 0; j < FLACMetadataBlock->numChannels; j++) {
                int32_t val = samplesBuffer[j][i + outputOffset];
                const int sourceBits = FLACMetadataBlock->bitsPerSample;
                // Align full-scale signed PCM to the 16-bit output. Arithmetic
                // right shift matches FFmpeg's s16 conversion without dither;
                // multiplication avoids undefined left shift of negative PCM.
                if(sourceBits > FLAC_PCM_BITS_PER_SAMPLE)
                    val >>= sourceBits - FLAC_PCM_BITS_PER_SAMPLE;
                else
                    val *= INT32_C(1) << (FLAC_PCM_BITS_PER_SAMPLE - sourceBits);
                outbuf[2*i+j] = static_cast<int16_t>(val);
            }
        }

        m_validSamples = blockSize * FLACMetadataBlock->numChannels;
        outputOffset += blockSize;

        if(outputOffset != m_blockSize) return GIVE_NEXT_LOOP;
        outputOffset = 0;
    }

    alignToByte();
    readUint(16);
    if(m_readError) { m_validSamples = 0; return m_readError; }
    m_bytesDecoded = *bytesLeft - m_bytesAvail;
//    log_i("m_bytesDecoded %i", m_bytesDecoded);
//    m_compressionRatio = (float)m_bytesDecoded / (float)m_blockSize * FLACMetadataBlock->numChannels * (16/8);
//    log_i("m_compressionRatio % f", m_compressionRatio);
    *bytesLeft = m_bytesAvail;
    m_status = DECODE_FRAME;
    return ERR_FLAC_NONE;
}
//----------------------------------------------------------------------------------------------------------------------
uint16_t FLACGetOutputSamps(){
    int vs = m_validSamples;
    m_validSamples=0;
    return vs;
}
//----------------------------------------------------------------------------------------------------------------------
uint64_t FLACGetTotoalSamplesInStream(){
    return FLACMetadataBlock->totalSamples;
}
//----------------------------------------------------------------------------------------------------------------------
uint8_t FLACGetBitsPerSample(){
    return FLACMetadataBlock->bitsPerSample;
}
uint8_t FLACGetOutputBitsPerSample(){
    return FLAC_PCM_BITS_PER_SAMPLE;
}
//----------------------------------------------------------------------------------------------------------------------
uint8_t FLACGetChannels(){
    return FLACMetadataBlock->numChannels;
}
//----------------------------------------------------------------------------------------------------------------------
uint32_t FLACGetSampRate(){
    return FLACMetadataBlock->sampleRate;
}
//----------------------------------------------------------------------------------------------------------------------
uint32_t FLACGetBitRate(){
    if(FLACMetadataBlock->totalSamples){
        const uint64_t encodedBits =
            static_cast<uint64_t>(FLACMetadataBlock->audioDataLength) * 8U;
        return static_cast<uint32_t>(
            encodedBits * FLACMetadataBlock->sampleRate /
            FLACMetadataBlock->totalSamples);
    }
    return 0;
}
//----------------------------------------------------------------------------------------------------------------------
uint32_t FLACGetAudioFileDuration() {
    if(FLACGetSampRate()){
        uint32_t afd = FLACGetTotoalSamplesInStream()/ FLACGetSampRate(); // AudioFileDuration
        return afd;
    }
    return 0;
}
//----------------------------------------------------------------------------------------------------------------------
int8_t decodeSubframes(){
    flac_profile::Scope scope(flac_profile::stereo);
    if(FLACFrameHeader->chanAsgn <= 7) {
        for (int ch = 0; ch < FLACMetadataBlock->numChannels; ch++) {
            const int8_t result = decodeSubframe(FLACMetadataBlock->bitsPerSample, ch);
            if(result != ERR_FLAC_NONE) return result;
        }
    }
    else if (8 <= FLACFrameHeader->chanAsgn && FLACFrameHeader->chanAsgn <= 10) {
        int8_t result = decodeSubframe(
            FLACMetadataBlock->bitsPerSample + (FLACFrameHeader->chanAsgn == 9 ? 1 : 0), 0);
        if(result != ERR_FLAC_NONE) return result;
        result = decodeSubframe(
            FLACMetadataBlock->bitsPerSample + (FLACFrameHeader->chanAsgn == 9 ? 0 : 1), 1);
        if(result != ERR_FLAC_NONE) return result;
        if(FLACFrameHeader->chanAsgn == 8) {
            for (int i = 0; i < m_blockSize; i++)
                samplesBuffer[1][i] = samplesBuffer[0][i] - samplesBuffer[1][i];
        }
        else if (FLACFrameHeader->chanAsgn == 9) {
            for (int i = 0; i < m_blockSize; i++)
                samplesBuffer[0][i] += samplesBuffer[1][i];
        }
        else if (FLACFrameHeader->chanAsgn == 10) {
            for (int i = 0; i < m_blockSize; i++) {
                int32_t side = samplesBuffer[1][i];
                int32_t right = samplesBuffer[0][i] - (side >> 1);
                samplesBuffer[1][i] = right;
                samplesBuffer[0][i] = right + side;
            }
        }
        else {
            log_e("unknown channel assignment");
            return ERR_FLAC_UNKNOWN_CHANNEL_ASSIGNMENT;
        }
    }
    else{
        log_e("Reserved channel assignment");
        return ERR_FLAC_RESERVED_CHANNEL_ASSIGNMENT;
    }
    return ERR_FLAC_NONE;
}
//----------------------------------------------------------------------------------------------------------------------
int8_t decodeSubframe(uint8_t sampleDepth, uint8_t ch) {
    flac_profile::Scope scope(flac_profile::subframe);
    if(sampleDepth < 1 || sampleDepth > FLAC_MAX_BITS_PER_SAMPLE + 1)
        return ERR_FLAC_INVALID_DATA;
    int8_t ret = 0;
    readUint(1);
    uint8_t type = readUint(6);
    int shift = readUint(1);
    if (shift == 1) {
        while (readUint(1) == 0) {
            if(m_readError) return m_readError;
            if(++shift >= sampleDepth) return ERR_FLAC_INVALID_DATA;
        }
    }
    if(m_readError) return m_readError;
    if(shift >= sampleDepth) return ERR_FLAC_INVALID_DATA;
    sampleDepth -= shift;

    if(type == 0){  // Constant coding
        int32_t s= readSignedInt(sampleDepth);
        for(int i=0; i < m_blockSize; i++){
            samplesBuffer[ch][i] = s;
        }
    }
    else if (type == 1) {  // Verbatim coding
        for (int i = 0; i < m_blockSize; i++)
            samplesBuffer[ch][i] = readSignedInt(sampleDepth);
    }
    else if (8 <= type && type <= 12){
        ret = decodeFixedPredictionSubframe(type - 8, sampleDepth, ch);
        if(ret) return ret;
    }
    else if (32 <= type && type <= 63){
        ret = decodeLinearPredictiveCodingSubframe(type - 31, sampleDepth, ch);
        if(ret) return ret;
    }
    else{
        return ERR_FLAC_RESERVED_SUB_TYPE;
    }
    if(m_readError) return m_readError;
    // Check the reduced-depth samples before restoring wasted bits. A valid
    // 24-bit stereo side sample can require 25 bits.
    const int32_t sampleLimit = INT32_C(1) << (sampleDepth - 1);
    for (int i = 0; i < m_blockSize; i++){
        const int32_t value = samplesBuffer[ch][i];
        if(value < -sampleLimit || value >= sampleLimit) return ERR_FLAC_INVALID_DATA;
        samplesBuffer[ch][i] = static_cast<int32_t>(static_cast<uint32_t>(value) << shift);
    }
    return ERR_FLAC_NONE;
}
//----------------------------------------------------------------------------------------------------------------------
int8_t decodeFixedPredictionSubframe(uint8_t predOrder, uint8_t sampleDepth, uint8_t ch) {
    if(predOrder > 4 || predOrder >= m_blockSize) return ERR_FLAC_PREORDER_TOO_BIG;
    uint8_t ret = 0;
    for(uint8_t i = 0; i < predOrder; i++)
        samplesBuffer[ch][i] = readSignedInt(sampleDepth);
    ret = decodeResiduals(predOrder, ch);
    if(ret) return ret;
    coefficientCount = predOrder;
    if(predOrder == 1) { coefs[0] = 1; }
    if(predOrder == 2) { coefs[0] = 2; coefs[1] = -1; }
    if(predOrder == 3) { coefs[0] = 3; coefs[1] = -3; coefs[2] = 1; }
    if(predOrder == 4) { coefs[0] = 4; coefs[1] = -6; coefs[2] = 4; coefs[3] = -1; }
    if(predOrder > 4) return ERR_FLAC_PREORDER_TOO_BIG; // Error: preorder > 4"
    restoreLinearPrediction(ch, 0);
    return ERR_FLAC_NONE;
}
//----------------------------------------------------------------------------------------------------------------------
int8_t decodeLinearPredictiveCodingSubframe(int lpcOrder, int sampleDepth, uint8_t ch){
    int8_t ret = 0;
    if(lpcOrder < 1 || lpcOrder > static_cast<int>(sizeof(coefs) / sizeof(coefs[0])) ||
       lpcOrder >= m_blockSize) return ERR_FLAC_PREORDER_TOO_BIG;
    for (int i = 0; i < lpcOrder; i++)
        samplesBuffer[ch][i] = readSignedInt(sampleDepth);
    int precision = readUint(4) + 1;
    int shift = readSignedInt(5);
    if(m_readError) return m_readError;
    if(precision == 16 || shift < 0) return ERR_FLAC_INVALID_DATA;
    coefficientCount = static_cast<uint8_t>(lpcOrder);
    for (uint8_t i = 0; i < coefficientCount; i++)
        coefs[i] = readSignedInt(precision);
    ret = decodeResiduals(lpcOrder, ch);
    if(ret) return ret;
    restoreLinearPrediction(ch, shift);
    return ERR_FLAC_NONE;
}
//----------------------------------------------------------------------------------------------------------------------
int8_t decodeResiduals(uint8_t warmup, uint8_t ch) {
    flac_profile::Scope scope(flac_profile::residual);

    int method = readUint(2);
    if (method >= 2)
        return ERR_FLAC_RESERVED_RESIDUAL_CODING; // Reserved residual coding method
    uint8_t paramBits = method == 0 ? 4 : 5;
    int escapeParam = (method == 0 ? 0xF : 0x1F);
    int partitionOrder = readUint(4);

    int numPartitions = 1 << partitionOrder;
    if (m_blockSize % numPartitions != 0)
        return ERR_FLAC_WRONG_RICE_PARTITION_NR; //Error: Block size not divisible by number of Rice partitions
    int partitionSize = m_blockSize/ numPartitions;
    if(partitionSize <= warmup) return ERR_FLAC_WRONG_RICE_PARTITION_NR;

    for (int i = 0; i < numPartitions; i++) {
        int start = i * partitionSize + (i == 0 ? warmup : 0);
        int end = (i + 1) * partitionSize;

        int param = readUint(paramBits);
        if (param < escapeParam) {
            for (int j = start; j < end; j++){
                samplesBuffer[ch][j] = readRiceSignedInt(param);
                if(m_readError) return m_readError;
            }
        } else {
            int numBits = readUint(5);
            for (int j = start; j < end; j++){
                samplesBuffer[ch][j] = readSignedInt(numBits);
                if(m_readError) return m_readError;
            }
        }
    }
    return ERR_FLAC_NONE;
}
//----------------------------------------------------------------------------------------------------------------------
namespace {

// A repeated/alternating coefficient run has only a few nonzero differences.
// Updating the unshifted prediction then costs fewer products than a new dot
// product. Keep a small fixed stack limit and fall back for arbitrary LPC.
constexpr size_t kMaximumSparseLpcDeltas = 4;
constexpr size_t kMinimumRollingLpcOrder = 8;

// Keep this optional recurrence out of the ordinary dot-product loop: inlining
// it increases that loop's stack frame and instruction-cache footprint on RV32.
__attribute__((noinline))
bool restoreSparseDeltaPrediction(uint8_t ch, uint8_t shift, size_t order) {
    if(order < kMinimumRollingLpcOrder) return false;
    constexpr size_t kEndpointProducts = 2;
    constexpr size_t kMinimumProductReduction = 2;
    const size_t allowedDeltas = std::min(kMaximumSparseLpcDeltas,
        order / kMinimumProductReduction - kEndpointProducts);
    size_t positiveDeltas = 0, negativeDeltas = 0;
    for(size_t j = 1; j < order; ++j) {
        positiveDeltas += coefs[j] != coefs[j - 1];
        negativeDeltas += coefs[j] != -coefs[j - 1];
        // Counts only increase. Once both signs exceed the budget, the rest
        // of the coefficients cannot make this recurrence worthwhile.
        if(positiveDeltas > allowedDeltas && negativeDeltas > allowedDeltas)
            return false;
    }
    const bool alternating = negativeDeltas < positiveDeltas;
    const size_t deltaCount = std::min(positiveDeltas, negativeDeltas);
    // The two endpoint products count too. Demand at least a halving of
    // multiply count to pay for the sparse indices and mode checks.
    if(coefficientCount >= m_blockSize) return true;

    int32_t deltaCoefficients[kMaximumSparseLpcDeltas];
    uint8_t deltaOffsets[kMaximumSparseLpcDeltas];
    size_t nextDelta = 0;
    for(size_t j = 1; j < order; ++j) {
        const int32_t delta = alternating ? coefs[j] + coefs[j - 1]
                                          : coefs[j] - coefs[j - 1];
        if(delta) {
            deltaCoefficients[nextDelta] = delta;
            deltaOffsets[nextDelta++] = static_cast<uint8_t>(j);
        }
    }
    const int32_t firstCoefficient = coefs[0];
    const int32_t outgoingCoefficient = alternating ? -coefs[order - 1] : coefs[order - 1];
    const bool subtractEndpoints = outgoingCoefficient == firstCoefficient;
    const bool addEndpoints = outgoingCoefficient == -firstCoefficient;
    int64_t prediction = 0;
    for(size_t j = 0; j < order; ++j)
        prediction += static_cast<int64_t>(samplesBuffer[ch][coefficientCount - 1 - j]) * coefs[j];

    for(size_t i = coefficientCount; i < m_blockSize; ++i) {
        const int64_t value = samplesBuffer[ch][i] + (prediction >> shift);
        if(value < INT32_MIN || value > INT32_MAX) {
            m_readError = ERR_FLAC_INVALID_DATA;
            return true;
        }
        samplesBuffer[ch][i] = static_cast<int32_t>(value);
        if(i + 1 == m_blockSize) break;
        const int32_t outgoing = samplesBuffer[ch][i - order];
        // P(next) = s*P + c0*x(new) + sum((cj-s*c(j-1))*x(i-j))
        //           - s*c(last)*x(outgoing), with s = +1 or -1.
        // Shift only when reconstructing PCM; never round the carried sum.
        if(alternating) prediction = -prediction;
        if(subtractEndpoints)
            prediction += (value - outgoing) * firstCoefficient;
        else if(addEndpoints)
            prediction += (value + outgoing) * firstCoefficient;
        else
            prediction += value * firstCoefficient - static_cast<int64_t>(outgoing) * outgoingCoefficient;
        for(size_t j = 0; j < deltaCount; ++j)
            prediction += static_cast<int64_t>(samplesBuffer[ch][i - deltaOffsets[j]]) * deltaCoefficients[j];
    }
    return true;
}

} // namespace

void restoreLinearPrediction(uint8_t ch, uint8_t shift) {
    flac_profile::Scope scope(flac_profile::prediction);
    if(shift > kMaximumLpcPredictionShift) {
        m_readError = ERR_FLAC_INVALID_DATA;
        return;
    }
    // Keep the encoded order for warm-up/residual positions. Trailing zero
    // coefficients do not contribute, even when the encoded order is 32.
    size_t activeCoefficients = coefficientCount;
    while(activeCoefficients && coefs[activeCoefficients - 1] == 0)
        --activeCoefficients;
    if(!activeCoefficients) return;
    if(restoreSparseDeltaPrediction(ch, shift, activeCoefficients)) return;
    const auto restoreSample = [shift](int32_t* sample, int64_t sum) {
        const int64_t value = *sample + (sum >> shift);
        if(value < INT32_MIN || value > INT32_MAX) {
            m_readError = ERR_FLAC_INVALID_DATA;
            return false;
        }
        *sample = static_cast<int32_t>(value);
        return true;
    };
    size_t sampleIndex = coefficientCount;
    while(sampleIndex < m_blockSize) {
        int32_t* output = &samplesBuffer[ch][sampleIndex];
        size_t spanEnd = m_blockSize;
#ifdef FLAC_SEGMENTED_WORKSPACE
        const size_t segmentOffset = sampleIndex % kWorkspaceSegmentSamples;
        spanEnd = std::min(spanEnd,
            sampleIndex + kWorkspaceSegmentSamples - segmentOffset);
        // Only the prefix of an allocation can read history from its
        // neighbour. Never walk a pointer across separate allocations.
        if(segmentOffset < activeCoefficients) {
            const size_t prefixEnd = std::min(spanEnd,
                sampleIndex + activeCoefficients - segmentOffset);
            for(; sampleIndex < prefixEnd; ++sampleIndex, ++output) {
                int64_t sum = 0;
                for(size_t j = 0; j < activeCoefficients; ++j)
                    sum += static_cast<int64_t>(samplesBuffer[ch][sampleIndex - 1 - j]) * coefs[j];
                if(!restoreSample(output, sum)) return;
            }
        }
#endif
        // Resolve segment geometry and the output pointer once per span,
        // rather than repeating divisions/lookups for every output sample.
        int32_t* const end = output + (spanEnd - sampleIndex);
        for(; output != end; ++output) {
            int64_t sum = 0;
            const int32_t* history = output - 1;
            // Four taps share one loop branch and pointer update on RV32.
            // Keep every product and addition wide; high-depth FLAC can
            // overflow a 32-bit accumulator even when the final PCM fits.
            constexpr size_t kTapsPerGroup = 4;
            size_t j = 0;
            for(; j + kTapsPerGroup <= activeCoefficients; j += kTapsPerGroup) {
                sum += static_cast<int64_t>(history[-static_cast<int>(j)]) * coefs[j];
                sum += static_cast<int64_t>(history[-static_cast<int>(j + 1)]) * coefs[j + 1];
                sum += static_cast<int64_t>(history[-static_cast<int>(j + 2)]) * coefs[j + 2];
                sum += static_cast<int64_t>(history[-static_cast<int>(j + 3)]) * coefs[j + 3];
            }
            for(; j < activeCoefficients; ++j)
                sum += static_cast<int64_t>(history[-static_cast<int>(j)]) * coefs[j];
            if(!restoreSample(output, sum)) return;
        }
        sampleIndex = spanEnd;
    }
}
//----------------------------------------------------------------------------------------------------------------------

