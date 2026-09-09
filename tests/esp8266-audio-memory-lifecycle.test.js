const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const root = path.resolve(__dirname, "..");
const read = (...parts) => fs.readFileSync(path.join(root, ...parts), "utf8");
const arena = read(
  "esp8266", "rtos-sdk-native", "components", "helix_codecs",
  "CodecMemoryArena.cpp",
);
const bridge = read(
  "esp8266", "rtos-sdk-native", "components", "helix_codecs",
  "codec_bridge.cpp",
);
const audio = read(
  "esp8266", "rtos-sdk-native", "main", "audio_service.c",
);
const mp3Only = read(
  "esp8266", "rtos-sdk-native",
  "sdkconfig.libmad-mp3-only-qio80.defaults",
);
const libmadFrame = read(
  "esp8266", "rtos-sdk-native", "components", "libmad8266", "upstream",
  "libmad", "frame.h",
);
const codecCmake = read(
  "esp8266", "rtos-sdk-native", "components", "helix_codecs",
  "CMakeLists.txt",
);
const mp3Header = read(
  "yoRadio", "src", "audioI2S", "mp3_decoder", "mp3_decoder.h",
);
const mp3Decoder = read(
  "yoRadio", "src", "audioI2S", "mp3_decoder", "mp3_decoder.cpp",
);

test("libmad follows the same symmetric CodecArena ownership as Helix", () => {
  const free = bridge.match(/void libmad_free\(\) \{[\s\S]*?\n\}/);
  assert.ok(free);
  assert.match(free[0], /mad_stream_finish/);
  assert.match(free[0], /mad_frame_finish/);
  assert.match(free[0], /CodecArenaFree\(s_libmad\.frame->tmp\)/);
  assert.match(free[0], /CodecArenaFree\(s_libmad\.frame->xr_raw\)/);
  assert.match(free[0], /CodecArenaFree\(s_libmad\.synth\)/);
  assert.match(free[0], /CodecArenaFree\(s_libmad\.stream\)/);
  assert.match(free[0], /CodecArenaFree\(s_libmad\.frame\)/);
  assert.match(free[0], /CodecArenaRelease\(CODEC_ARENA_MP3\)/);
  assert.match(bridge, /if \(!s_libmad\.stream[\s\S]*libmad_free\(\)/);
});

test("ESP8266 reports DRAM and IRAM separately and enforces reserve after allocation", () => {
  assert.match(arena, /CodecArenaHeapUsed\(\)/);
  assert.match(arena, /CodecArenaWordUsed\(\)/);
  assert.match(arena, /Owner released with %u DRAM bytes live/);
  assert.match(bridge, /codec->dram_used = [\s\S]*CodecArenaHeapUsed\(\)/);
  assert.match(bridge, /CodecArenaPreallocatedInIram\(\)/);
  assert.match(bridge, /word_in_iram \? 0U : word_capacity/);
  assert.match(bridge, /codec->iram_used = word_in_iram \? word_capacity : 0U/);
  assert.match(
    bridge,
    /size_t free_heap = esp_get_free_heap_size\(\);[\s\S]*size_t reserve = codec->reserve_heap_bytes;[\s\S]*free_heap >= reserve/,
  );
  assert.match(bridge, /#if CONFIG_YORADIO_OGG_OPUS\s+if \(codec->kind == HELIX_CODEC_OPUS\) reserve = std::max\(reserve, size_t\(4096\)\);\s+#endif/);
  assert.match(bridge, /helix_codec_switch[\s\S]*update_codec_memory\(codec\)/);
});

test("audio workspace is lazy, reusable for station changes, and released on stop", () => {
  const init = audio.match(/esp_err_t audio_service_init\(void\) \{[\s\S]*?\n\}/);
  assert.ok(init);
  assert.match(init[0], /helix_codec_prepare/);
  assert.doesNotMatch(init[0], /helix_codec_create/);
  assert.match(audio, /helix_codec_t \*codec = NULL/);
  assert.match(
    audio,
    /codec\s*\? helix_codec_switch\(codec, codec_kind\)[\s\S]*helix_codec_create\(codec_kind/,
  );
  assert.match(audio, /if \(!command\.play\)[\s\S]*release_codec\(&codec, &codec_kind, "stop"\)/);
  assert.match(audio, /uxTaskGetStackHighWaterMark\(NULL\)/);
});

test("full codec profile reserves IRAM for AAC and MP3 while libmad-only stays smaller", () => {
  assert.match(mp3Only, /CONFIG_YORADIO_MP3_DECODER_LIBMAD=y/);
  assert.match(mp3Only, /# CONFIG_YORADIO_HELIX_AAC is not set/);
  assert.match(arena, /!CONFIG_YORADIO_HELIX_AAC && CONFIG_YORADIO_MP3_DECODER_LIBMAD[\s\S]*12U \* 1024U/);
  assert.match(arena, /#else[\s\S]*16U \* 1024U[\s\S]*kWordSpillBytes = 0U/);
  assert.match(bridge, /kAacPcmSamples = 1024U \* 2U/);
  assert.match(bridge, /kMp3PcmSamples = 576U \* \(CONFIG_YORADIO_AUDIO_MONO \? 1U : 2U\)/);
  assert.match(bridge, /codec->pcm_samples = pcm_samples_for_kind\(kind\)/);
  assert.match(bridge, /sizeof\(int16_t\) \* codec->pcm_samples/);
});

test("ESP8266 splits the word-only IMDCT output into the IRAM arena", () => {
  assert.match(mp3Header, /YORADIO_ESP8266_NATIVE[\s\S]*int \(\*outBuf\[m_MAX_NCHAN\]\)\[m_NBANDS\]/);
  assert.match(mp3Header, /int \*overBuf\[m_MAX_NCHAN\]/);
  assert.match(mp3Decoder, /m_SubbandInfo[\s\S]*CodecArenaCalloc32/);
  assert.match(mp3Decoder, /m_IMDCTInfo->outBuf\[0\][\s\S]*CodecArenaCalloc32/);
  assert.match(mp3Decoder, /m_IMDCTInfo->outBuf\[1\][\s\S]*CodecArenaCalloc\(/);
  assert.match(mp3Decoder, /m_IMDCTInfo->overBuf\[0\][\s\S]*CodecArenaCalloc\(/);
  assert.match(mp3Decoder, /m_IMDCTInfo->overBuf\[1\][\s\S]*CodecArenaCalloc\(/);
  assert.match(mp3Decoder, /CodecArenaFree\(m_IMDCTInfo->outBuf\[0\]\)[\s\S]*CodecArenaFree\(m_IMDCTInfo->outBuf\[1\]\)/);
  assert.match(mp3Decoder, /CodecArenaFree\(m_IMDCTInfo->overBuf\[0\]\)[\s\S]*CodecArenaFree\(m_IMDCTInfo->overBuf\[1\]\)/);
});

test("ESP8266 preserves heap for lwIP after starting the MP3 decoder", () => {
  assert.match(audio, /#if CONFIG_YORADIO_OGG_OPUS[\s\S]*#define AUDIO_STACK_BYTES 5120U[\s\S]*#else\s*#define AUDIO_STACK_BYTES 4096U/);
  assert.match(audio, /#define AUDIO_STACK_BYTES 4096U/);
  assert.match(audio, /#define CODEC_HEAP_RESERVE_BYTES 1152U/);
  assert.match(bridge, /heap_caps_realloc\([\s\S]*MALLOC_CAP_8BIT/);
});

test("libmad places only aligned Layer III word workspaces in ESP8266 IRAM", () => {
  assert.match(
    codecCmake,
    /CONFIG_YORADIO_MP3_DECODER_LIBMAD[\s\S]*YORADIO_LIBMAD_EXTERNAL_FRAME_WORKSPACE=1/,
  );
  assert.match(
    libmadFrame,
    /YORADIO_LIBMAD_EXTERNAL_FRAME_WORKSPACE[\s\S]*mad_fixed_t \*xr_raw;[\s\S]*mad_fixed_t \*tmp;/,
  );
  assert.match(
    bridge,
    /frame->xr_raw = static_cast<mad_fixed_t \*>\([\s\S]*CodecArenaCalloc32/,
  );
  assert.match(
    bridge,
    /frame->tmp = static_cast<mad_fixed_t \*>\([\s\S]*CodecArenaCalloc32/,
  );
  assert.match(bridge, /kLibmadXrSamples = 576U \* 2U/);
  assert.match(bridge, /kLibmadReorderSamples = 576U/);
});
