const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const root = path.resolve(__dirname, "..");
const read = (...parts) => fs.readFileSync(path.join(root, ...parts), "utf8");
const bridge = read(
  "esp8266", "rtos-sdk-native", "components", "helix_codecs",
  "codec_bridge.cpp",
);
const decoder = read(
  "yoRadio", "src", "audioI2S", "mp3_decoder", "mp3_decoder.cpp",
);
const decoderHeader = read(
  "yoRadio", "src", "audioI2S", "mp3_decoder", "mp3_decoder.h",
);
const audioService = read(
  "esp8266", "rtos-sdk-native", "main", "audio_service.c",
);
const nativeOptions = read(
  "esp8266", "rtos-sdk-native", "main", "Kconfig.projbuild",
);

test("ESP8266 channel choice defaults to mono and retains an explicit stereo profile", () => {
  const defaults = read("esp8266", "rtos-sdk-native", "sdkconfig.defaults");
  const stereo = read("esp8266", "rtos-sdk-native", "sdkconfig.stereo.defaults");
  const cmake = read("esp8266", "rtos-sdk-native", "components", "helix_codecs", "CMakeLists.txt");
  assert.match(nativeOptions, /choice YORADIO_AUDIO_CHANNELS[\s\S]*config YORADIO_AUDIO_MONO[\s\S]*config YORADIO_AUDIO_STEREO[\s\S]*endchoice/);
  assert.match(defaults, /^CONFIG_YORADIO_AUDIO_MONO=y$/m);
  assert.match(stereo, /^CONFIG_YORADIO_AUDIO_STEREO=y$/m);
  assert.match(cmake, /if\(CONFIG_YORADIO_AUDIO_MONO\)[\s\S]*YORADIO_HELIX_MP3_MONO=1/);
  const withoutChannels = value => value.split(/\r?\n/).filter(line => !line.includes("CONFIG_YORADIO_AUDIO_MONO") && !line.includes("CONFIG_YORADIO_AUDIO_STEREO")).join("\n");
  assert.equal(withoutChannels(stereo), withoutChannels(defaults), "stereo profile drifted from board defaults");
  assert.match(decoderHeader, /#ifndef YORADIO_HELIX_MP3_MONO\s+#define YORADIO_HELIX_MP3_MONO 0/);
});

test("ESP8266 Helix MP3 streams 32 frames while libmad retains granule PCM", () => {
  assert.match(bridge, /constexpr size_t kMp3PcmSamples = 576U \* \(CONFIG_YORADIO_AUDIO_MONO \? 1U : 2U\)/);
  assert.match(bridge, /kMp3PcmSamples = MP3_PCM_BLOCK_FRAMES \*/);
  assert.doesNotMatch(bridge, /kMp3PcmSamples = 1152U \* 2U/);
  assert.match(
    bridge,
    /MP3DecodeBlocks\(input, &left, codec->pcm,[\s\S]*emit_mp3_block/,
  );
  assert.match(
    bridge,
    /samples <= 0 \|\|[\s\S]*static_cast<size_t>\(samples\) > kMp3PcmSamples/,
  );
});

test("ESP8266 AAC reserves only its active bounded PCM block", () => {
  assert.match(bridge, /#if YORADIO_ESP8266_AAC_BLOCK_OUTPUT\s+constexpr size_t kAacPcmSamples = YORADIO_ESP8266_AAC_PCM_BLOCK_FRAMES \*\s+\(CONFIG_YORADIO_AUDIO_MONO \? 1U : 2U\)/);
  assert.match(bridge, /AACDecodeBlocks\(input, &left, codec->pcm/);
  assert.match(bridge, /kAacPcmSamples > kMp3PcmSamples \? kAacPcmSamples : kMp3PcmSamples/);
  assert.match(bridge, /pcm_samples_for_kind[\s\S]*HELIX_CODEC_AAC[\s\S]*kAacPcmSamples/);
  assert.match(bridge, /heap_caps_realloc\([\s\S]*sizeof\(int16_t\) \* pcm_samples/);
});

test("ESP8266 enables AAC and refills/yields between compressed frames", () => {
  assert.match(
    nativeOptions,
    /config YORADIO_HELIX_AAC[\s\S]*default y/,
  );
  assert.match(
    audioService,
    /stream_input_refill\([\s\S]*helix_codec_process_one\([\s\S]*if \(decoded == 0\)[\s\S]*vTaskDelay\(pdMS_TO_TICKS\(1\)\)/,
  );
});

test("ESP8266 granule API preserves the conventional full-frame API", () => {
  assert.match(
    decoderHeader,
    /#if defined\(YORADIO_ESP8266_NATIVE\)[\s\S]*MP3DecodeGranules/,
  );
  assert.match(
    decoder,
    /if \(!callback\)[\s\S]*granuleOut \+= gr \* m_MP3DecInfo->nGranSamps/,
  );
  assert.match(
    decoder,
    /Subband\(granuleOut\)[\s\S]*!streamBlocks && !callback\(context, granuleOut,[\s\S]*m_MP3DecInfo->nGranSamps/,
  );
  assert.match(
    decoder,
    /int MP3Decode\([\s\S]*MP3DecodeInternal\(inbuf, bytesLeft, outbuf, useSize/,
  );
});

test("32-frame callbacks publish stream format only on change", () => {
  assert.match(audioService, /context->decoder_bitrate != info->bitrate \|\|[\s\S]*context->decoder_sample_rate != info->sample_rate \|\|[\s\S]*context->decoder_channels != info->channels[\s\S]*native_state_set_stream/);
  assert.match(decoder, /m_OutputBufferSamples = required;[\s\S]*context, true\);[\s\S]*m_OutputBufferSamples = 0/);
});

test("ESP8266 error concealment cannot overrun the granule PCM buffer", () => {
  assert.match(
    decoder,
    /m_OutputBufferSamples > 0 && samples > m_OutputBufferSamples[\s\S]*samples = m_OutputBufferSamples/,
  );
  assert.match(
    decoder,
    /m_OutputBufferSamples = \(YORADIO_HELIX_MP3_MONO \? 1 : m_MAX_NCHAN\) \* m_MAX_NSAMP;[\s\S]*m_OutputBufferSamples = 0;/,
  );
});
