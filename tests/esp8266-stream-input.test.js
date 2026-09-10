const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const {spawnSync} = require("node:child_process");

const root = path.resolve(__dirname, "..");
const main = path.join(root, "esp8266/rtos-sdk-native/main");
const bridge = path.join(root, "esp8266/rtos-sdk-native/components/helix_codecs");
const audio = path.join(root, "yoRadio/src/audioI2S");
const native = path.join(__dirname, "native");

function findVcVars() {
  const base = "C:\\Program Files\\Microsoft Visual Studio";
  if (!fs.existsSync(base)) return null;
  for (const version of fs.readdirSync(base).sort().reverse()) {
    for (const edition of fs.readdirSync(path.join(base, version)).sort().reverse()) {
      const candidate = path.join(base, version, edition, "VC/Auxiliary/Build/vcvars64.bat");
      if (fs.existsSync(candidate)) return candidate;
    }
  }
  return null;
}

function build(t, sources, includes, defines = [], cpp = false) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "yoradio-input-"));
  t.after(() => fs.rmSync(dir, {recursive: true, force: true}));
  const executable = path.join(dir, process.platform === "win32" ? "test.exe" : "test");
  let result;
  if (process.platform === "win32") {
    const vcvars = findVcVars();
    if (!vcvars) { t.skip("Visual C++ build tools unavailable"); return null; }
    const args = ["/nologo", cpp ? "/std:c++17" : "/std:c11", "/O2",
      ...(cpp ? ["/EHsc", "/W3"] : ["/W4", "/WX"]),
      ...includes.map(p => "/I" + p), ...defines.map(d => "/D" + d),
      ...sources, "/Fe:" + executable];
    const batch = path.join(dir, "build.cmd");
    fs.writeFileSync(batch, [
      '@call "' + vcvars + '" >nul',
      "@if errorlevel 1 exit /b %errorlevel%",
      "@cl " + args.map(a => '"' + a + '"').join(" "),
    ].join("\r\n") + "\r\n");
    result = spawnSync("cmd.exe", ["/d", "/c", batch], {cwd: dir, encoding: "utf8", timeout: 60000});
  } else {
    result = spawnSync(cpp ? "c++" : "cc", [cpp ? "-std=c++17" : "-std=c11", "-O2",
      "-Wall", "-Wextra", ...includes.map(p => "-I" + p),
      ...defines.map(d => "-D" + d), ...sources, "-o", executable],
      {cwd: dir, encoding: "utf8", timeout: 60000});
    if (result.error?.code === "ENOENT") { t.skip("Host compiler unavailable"); return null; }
  }
  assert.equal(result.status, 0, result.stdout + "\n" + result.stderr);
  return executable;
}

test("input queue prefills, tops up, cancels and strips arbitrarily split ICY without waits", t => {
  const executable = build(t, [path.join(native, "esp8266_stream_input_test.c")], [main]);
  if (!executable) return;
  const result = spawnSync(executable, [], {encoding: "utf8", timeout: 10000});
  assert.equal(result.status, 0, result.stdout + "\n" + result.stderr);
  assert.match(result.stdout, /Stream input tests passed/);
});

for (const [inputBytes, aacBlocks] of [[1536, 1], [4096, 1], [6144, 1], [4096, 0]]) {
  test("queued MP3/AAC PCM is bit-exact with legacy draining, input=" + inputBytes + ", AAC blocks=" + aacBlocks, t => {
    const executable = build(t, [
      path.join(audio, "mp3_decoder/mp3_decoder.cpp"),
      path.join(audio, "aac_decoder/aac_decoder.cpp"),
      path.join(native, "helix_golden/codec_arena_host.cpp"),
      path.join(bridge, "codec_bridge.cpp"),
      path.join(native, "esp8266_input/bridge_test.cpp"),
    ], [
      path.join(native, "esp8266_input/stubs"), path.join(native, "helix_golden"),
      audio, path.join(audio, "mp3_decoder"), path.join(audio, "aac_decoder"), bridge,
    ], [
      "YORADIO_ESP8266_NATIVE=1", "YORADIO_HELIX_MP3_MONO=1", "YORADIO_HELIX_MP3_SSO=1",
      "YORADIO_ESP8266_AAC_BLOCK_OUTPUT=" + aacBlocks, "YORADIO_ESP8266_AAC_PCM_BLOCK_FRAMES=512",
      "CONFIG_YORADIO_STREAM_INPUT_BYTES=" + inputBytes, "PROGMEM=",
    ], true);
    if (!executable) return;
    const fixtures = [
      "mp3_composite/mix-064.mp3", "mp3_composite/mix-128.mp3", "mp3_composite/mix-320.mp3",
      "aac_composite/mix-048.aac", "aac_composite/mix-096.aac", "helix_golden/stereo-320.aac",
    ].map(p => path.join(__dirname, "fixtures", p));
    const result = spawnSync(executable, fixtures, {encoding: "utf8", timeout: 60000});
    assert.equal(result.status, 0, result.stdout + "\n" + result.stderr);
    assert.equal((result.stdout.match(/PCM identical/g) || []).length, fixtures.length);
    assert.match(result.stdout, /Codec input tests passed/);
  });
}

test("native startup buffers before decoding and does not announce Playing until PCM", () => {
  const source = fs.readFileSync(path.join(main, "audio_service.c"), "utf8");
  const loop = source.slice(source.indexOf('#include "stream_input_refill.inc"'));
  assert.doesNotMatch(loop, /helix_codec_feed\(|helix_codec_commit\(|read_icy_metadata\(/);
  assert.match(loop, /memcpy\(destination, s_work, detect_size\);[\s\S]*stream_icy_audio/);
  assert.match(loop, /stream_input_refill[\s\S]*stream_prefill_ready[\s\S]*helix_codec_process_one/);
  assert.match(loop, /output.decoder_sample_rate[\s\S]*native_state_set_audio\(true, false, NULL\)/);
  assert.match(loop, /else if \(ended\)[\s\S]*feed = end_error/);
});
