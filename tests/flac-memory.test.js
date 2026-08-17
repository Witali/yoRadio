const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const root = path.resolve(__dirname, '..');
const decoderHeader = fs.readFileSync(path.join(
  root, 'yoRadio/src/audioI2S/flac_decoder/flac_decoder.h'), 'utf8');
const decoderSource = fs.readFileSync(path.join(
  root, 'yoRadio/src/audioI2S/flac_decoder/flac_decoder.cpp'), 'utf8');
const audioSource = fs.readFileSync(path.join(
  root, 'yoRadio/src/audioI2S/Audio.cpp'), 'utf8');

test('FLAC sample storage follows the stream block size', () => {
  assert.doesNotMatch(
    decoderHeader,
    /int32_t\s+samplesBuffer\s*\[\s*MAX_CHANNELS\s*\]\s*\[\s*MAX_BLOCKSIZE\s*\]/,
  );
  assert.match(
    decoderSource,
    /channelBytes\s*=\s*static_cast<size_t>\(maxBlockSize\)\s*\*\s*sizeof\(int32_t\)/,
  );
  assert.match(
    decoderSource,
    /for\s*\(uint8_t channel = 0; channel < channels; \+\+channel\)/,
  );
  assert.match(
    audioSource,
    /FLACDecoder_AllocateBuffers\(m_flacMaxBlockSize, m_flacNumChannels\)/,
  );
});

test('FLAC on RAM-only boards is not rejected before allocation', () => {
  const flacCase = audioSource.match(
    /case CODEC_FLAC:[\s\S]*?break;\s*case CODEC_WAV:/,
  );
  assert.ok(flacCase);
  assert.doesNotMatch(flacCase[0], /FLAC works only with PSRAM/);
  assert.match(flacCase[0], /CodecArenaDiscard\(\)/);
});

test('large wrapped audio frames are linearized without another buffer', () => {
  const changeBlock = audioSource.match(
    /void AudioBuffer::changeMaxBlockSize[\s\S]*?uint16_t AudioBuffer::getMaxBlockSize/,
  );
  const getReadPointer = audioSource.match(
    /uint8_t\* AudioBuffer::getReadPtr[\s\S]*?void AudioBuffer::resetBuffer/,
  );
  assert.ok(changeBlock);
  assert.ok(getReadPointer);
  assert.doesNotMatch(changeBlock[0], /wrap reserve; clamping/);
  assert.match(getReadPointer[0], /reverseRange\(m_buffer, m_readPtr\)/);
  assert.match(getReadPointer[0], /m_writePtr = m_buffer \+ filled/);
});

test('FLAC prediction avoids heap churn and 32-bit accumulation overflow', () => {
  assert.match(decoderSource, /int32_t coefs\[32\]/);
  assert.doesNotMatch(decoderSource, /vector<int32_t>\s*coefs/);
  assert.match(decoderSource, /int64_t sum = 0/);
});
