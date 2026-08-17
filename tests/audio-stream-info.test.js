const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

function read(...parts) {
  return fs.readFileSync(path.join(__dirname, "..", ...parts), "utf8");
}

test("CYD player enables decoded stream information", () => {
  const options = read("yoRadio", "myoptions.h");
  assert.match(options, /#define SHOW_STREAM_INFO\s+true/);
});

test("audio callbacks retain decoder sample rate and channel count", () => {
  const config = read("yoRadio", "src", "core", "config.h");
  const handlers = read("yoRadio", "src", "core", "audiohandlers.h");

  assert.match(config, /uint32_t sampleRate/);
  assert.match(config, /uint8_t channels/);
  assert.match(handlers, /strstr\(info, "SampleRate: "\)/);
  assert.match(handlers, /strstr\(info, "Channels: "\)/);
  assert.match(handlers, /config\.station\.sampleRate = value/);
  assert.match(handlers, /config\.station\.channels = value/);
});

test("player shows compact mono, stereo, or multichannel stream layout without codec", () => {
  const display = read("yoRadio", "src", "core", "display.cpp");

  assert.match(display, /"%s kHz mono"/);
  assert.match(display, /"%s kHz stereo"/);
  assert.match(display, /"%s kHz %u channels"/);
  assert.match(display, /config\.station\.channels == 1U/);
  assert.match(display, /config\.station\.channels == 2U/);
  assert.doesNotMatch(display, /\(%u ch\)/);
});

test("stream information is cleared between stations", () => {
  const config = read("yoRadio", "src", "core", "config.cpp");
  const player = read("yoRadio", "src", "core", "player.cpp");

  for (const source of [config, player]) {
    assert.match(source, /station\.sampleRate\s*=\s*0/);
    assert.match(source, /station\.channels\s*=\s*0/);
  }
});

test("decoded stream parameters are checked after every audio frame", () => {
  const source = read("yoRadio", "src", "audioI2S", "Audio.cpp");

  assert.doesNotMatch(source, /f_setDecodeParamsOnce/);
  assert.match(source, /updateDecoderParameters\(pcmAvailable\)/);
  assert.match(source, /updateDecoderParameters\(pcmAvailable\)[\s\S]*m_validSamples = Mp3DecoderGetOutputSamps/);
  assert.match(source, /Mp3DecoderGetSampRate\(\)/);
  assert.match(source, /AACGetSampRate\(\)/);
  assert.match(source, /FLACGetSampRate\(\)/);
  assert.match(source, /OggDecoderGetInfo\(/);
});

test("audio output is reconfigured only when decoded layout changes", () => {
  const source = read("yoRadio", "src", "audioI2S", "Audio.cpp");

  assert.match(source, /firstParameters \|\| sampleRate != getSampleRate\(\)[\s\S]*setSampleRate\(sampleRate\)/);
  assert.match(source, /firstParameters \|\| channels != getChannels\(\)[\s\S]*setChannels\(channels\)/);
  assert.match(source, /firstParameters \|\| bitsPerSample != getBitsPerSample\(\)[\s\S]*setBitsPerSample\(bitsPerSample\)/);
  assert.match(source, /Stream parameters changed:[\s\S]*showCodecParams\(\)/);
});

test("HE-AAC reports the nominal stream rate without changing the decoded PCM rate", () => {
  const audio = read("yoRadio", "src", "audioI2S", "Audio.cpp");
  const decoder = read("yoRadio", "src", "audioI2S", "aac_decoder", "aac_decoder.cpp");

  assert.match(audio, /streamSampleRate = AACGetStreamSampRate\(\)/);
  assert.match(audio, /SampleRate: %lu", streamSampleRate/);
  assert.match(decoder, /AACGetSampRate\(\).*sbrEnabled/);
  assert.match(decoder, /AACGetStreamSampRate\(\).*sbrPresent/);
  assert.match(decoder, /sbrPresent = 1;[\s\S]*#ifdef AAC_ENABLE_SBR[\s\S]*sbrEnabled = 1/);
});
