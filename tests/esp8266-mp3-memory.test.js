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

test("ESP8266 MP3 streams one granule through a half-size PCM buffer", () => {
  assert.match(bridge, /constexpr size_t kPcmSamples = 576U \* 2U/);
  assert.doesNotMatch(bridge, /kPcmSamples = 1152U \* 2U/);
  assert.match(
    bridge,
    /MP3DecodeGranules\(input, &left, codec->pcm, 0,[\s\S]*emit_mp3_granule/,
  );
  assert.match(
    bridge,
    /samples <= 0 \|\| static_cast<size_t>\(samples\) > kPcmSamples/,
  );
});

test("ESP8266 AAC reserves a complete stereo PCM frame before decoding", () => {
  assert.match(
    bridge,
    /#if CONFIG_YORADIO_HELIX_AAC[\s\S]*kPcmSamples = 1024U \* 2U;[\s\S]*#else[\s\S]*kPcmSamples = 576U \* 2U;/,
  );
});

test("ESP8266 enables AAC and yields between compressed input chunks", () => {
  assert.match(
    nativeOptions,
    /config YORADIO_HELIX_AAC[\s\S]*default y/,
  );
  assert.match(
    audioService,
    /helix_codec_commit\([\s\S]*if \(feed == 0\) vTaskDelay\(pdMS_TO_TICKS\(1\)\)/,
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
    /Subband\(granuleOut\)[\s\S]*callback\(context, granuleOut,[\s\S]*m_MP3DecInfo->nGranSamps/,
  );
  assert.match(
    decoder,
    /int MP3Decode\([\s\S]*MP3DecodeInternal\(inbuf, bytesLeft, outbuf, useSize/,
  );
});

test("ESP8266 error concealment cannot overrun the granule PCM buffer", () => {
  assert.match(
    decoder,
    /m_OutputBufferSamples > 0 && samples > m_OutputBufferSamples[\s\S]*samples = m_OutputBufferSamples/,
  );
  assert.match(
    decoder,
    /m_OutputBufferSamples = m_MAX_NCHAN \* m_MAX_NSAMP;[\s\S]*m_OutputBufferSamples = 0;/,
  );
});
