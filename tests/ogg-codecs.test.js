const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const root = path.join(__dirname, "..");

function read(...parts) {
  return fs.readFileSync(path.join(root, ...parts), "utf8");
}

test("minimal IDF build pins the official OGG Vorbis and Opus component", () => {
  const setup = read("idf", "esp32-cyd2usb-minimal", "setup.ps1");
  const project = read("idf", "esp32-cyd2usb-minimal", "CMakeLists.txt");
  const main = read("idf", "esp32-cyd2usb-minimal", "main", "CMakeLists.txt");
  const config = read("idf", "esp32-cyd2usb-minimal", "sdkconfig.defaults");

  assert.match(setup, /esp-adf-libs\.git/);
  assert.match(setup, /67b8d0e98f58c774b8652480893037273190e8dc/);
  assert.match(setup, /SparsePath "esp_audio_codec"/);
  assert.match(project, /YORADIO_AUDIO_CODEC_COMPONENT/);
  assert.match(main, /OggDecoder\.cpp/);
  assert.match(main, /esp_audio_codec/);
  assert.match(config, /CONFIG_AUDIO_DECODER_OPUS_SUPPORT=y/);
  assert.match(config, /CONFIG_AUDIO_DECODER_VORBIS_SUPPORT=y/);
  assert.match(config, /CONFIG_AUDIO_SIMPLE_DEC_OGG_SUPPORT=y/);
  assert.match(config, /CONFIG_AUDIO_DECODER_MP3_SUPPORT=n/);
  assert.match(config, /CONFIG_AUDIO_ENCODER_OPUS_SUPPORT=n/);
});

test("audio source recognizes common OGG extensions and MIME types", () => {
  const source = read("yoRadio", "src", "audioI2S", "Audio.cpp");

  for (const extension of [".ogg", ".oga", ".opus"]) {
    assert.match(source, new RegExp(`endsWith\\([^\\n]+\\"\\${extension}\\"\\)`));
  }
  for (const contentType of [
    "application/ogg",
    "application/x-ogg",
    "audio/ogg",
    "audio/opus",
    "audio/vorbis",
    "audio/x-vorbis+ogg",
  ]) {
    assert.ok(source.includes(`"${contentType}"`), `${contentType} is missing`);
  }
});

test("OGG owns decoder memory exclusively and grows only its PCM frame buffer", () => {
  const source = read("yoRadio", "src", "audioI2S", "Audio.cpp");
  const arena = read("yoRadio", "src", "audioI2S", "CodecMemoryArena.cpp");

  assert.match(source, /case CODEC_OGG:[\s\S]*CodecArenaDiscard\(\)[\s\S]*OggDecoderOpen\(\)/);
  assert.match(source, /OggDecoderClose\(\)[\s\S]*free\(m_oggOutBuff\)[\s\S]*CodecArenaReserve\(\)/);
  assert.match(source, /OGG_DECODE_OUTPUT_TOO_SMALL[\s\S]*realloc\(m_oggOutBuff, requiredOutputSize\)/);
  assert.match(source, /maxOggPcmFrame = 64U \* 1024U/);
  assert.match(arena, /Cannot discard codec arena owned by decoder/);
});
