#include "flac_decoder.cpp"
#include <cassert>
#include <cstdio>

static void input(uint8_t *data, unsigned bytes) {
    FLACDecoderReset(); m_inptr=data; m_bytesAvail=bytes; m_rIndex=0;
}

int main() {
    uint8_t ones[] = {255,255,255,255};
    input(ones,4); assert(readUint(31)==0x7fffffffU && !m_readError);
    input(ones,4); assert(readUint(32)==0xffffffffU && !m_readError);
    input(nullptr,0); assert(readSignedInt(0)==0 && !m_readError);
    input(nullptr,0); assert(readSignedInt(33)==0 && m_readError==ERR_FLAC_INVALID_DATA);
    input(nullptr,0); assert(readSignedInt(-1)==0 && m_readError==ERR_FLAC_INVALID_DATA);
    uint8_t zeros[] = {0};
    input(zeros,1); assert(readRiceSignedInt(0)==0 && m_readError==ERR_FLAC_TRUNCATED_INPUT);
    uint8_t rice[] = {0x1f,0xff,0xff,0xff,0x80};
    input(rice,5); assert(readRiceSignedInt(30)==2147483647 && !m_readError);
    rice[4]=0x40;
    input(rice,5); assert(readRiceSignedInt(30)==-2147483647 && !m_readError);
    rice[4]=0xc0;
    input(rice,5); assert(readRiceSignedInt(30)==0 && m_readError==ERR_FLAC_INVALID_DATA);
    assert(FLACDecoder_AllocateBuffers(16,2));
    m_blockSize=16;
    // Constant side channels use 17 bits even in a 16-bit stereo stream.
    uint8_t side[] = {0,0x7f,0xff,0x80};
    input(side,sizeof(side)); assert(decodeSubframe(17,1)==0);
    for(unsigned i=0;i<16;++i) assert(samplesBuffer[1][i]==65535);
    uint8_t wide_side[] = {0,0x7f,0xff,0xff,0x80};
    input(wide_side,sizeof(wide_side)); assert(decodeSubframe(25,1)==0);
    for(unsigned i=0;i<16;++i) assert(samplesBuffer[1][i]==16777215);
    input(nullptr,0); assert(decodeSubframe(0,0)==ERR_FLAC_INVALID_DATA);
    input(nullptr,0); assert(decodeSubframe(33,0)==ERR_FLAC_INVALID_DATA);
    // Corrupt residual/predictor combinations must not overflow signed32.
    input(nullptr,0);m_blockSize=2;coefficientCount=1;coefs[0]=16383;
    samplesBuffer[0][0]=16777215;samplesBuffer[0][1]=INT32_MAX;
    restoreLinearPrediction(0,0);assert(m_readError==ERR_FLAC_INVALID_DATA);
    m_blockSize=16;
    // Fixed order zero, Rice escape width zero: sixteen zero residuals.
    uint8_t escaped[] = {0x10,0x03,0xc0};
    input(escaped,sizeof(escaped)); assert(decodeSubframe(16,0)==0);
    for(unsigned i=0;i<16;++i) assert(samplesBuffer[0][i]==0);
    // Invalid wasted-bit run, predictor order and residual partition size.
    uint8_t wasted[] = {1,0,0};
    input(wasted,sizeof(wasted)); assert(decodeSubframe(16,0)<0);
    input(nullptr,0); m_blockSize=1;
    assert(decodeFixedPredictionSubframe(4,16,0)<0);
    assert(decodeLinearPredictiveCodingSubframe(32,16,0)<0);
    m_blockSize=16; uint8_t partition[] = {0x10};
    input(partition,1); assert(decodeResiduals(1,0)==ERR_FLAC_WRONG_RICE_PARTITION_NR);
    // Ogg header skipping must inspect neither the fixed header nor lacing
    // table until its declared bytes are present.
    uint8_t ogg[25]={0}; ogg[22]=2;
    assert(FLACparseOggHeader(ogg,22)==ERR_FLAC_TRUNCATED_INPUT);
    assert(FLACparseOggHeader(ogg,24)==ERR_FLAC_TRUNCATED_INPUT);
    assert(FLACparseOggHeader(ogg,25)==25);
    uint8_t capture[] = {'O','g','g'};
    assert(FLACFindOggSyncWord(capture,3)==-1);
    // Error state clears for a fresh stream using the standard reset path.
    input(nullptr,0); readUint(8); assert(m_readError);
    FLACDecoder_ClearBuffer(); assert(!m_readError);
    FLACDecoder_FreeBuffers();
    puts("PASS widths/zero-residual/17-and-25-bit-side/predictor-overflow/truncated-unary/wasted-bits/predictor/partition/Ogg/reset");
}
