const test = require("node:test");
const assert = require("node:assert/strict");
const crypto = require("node:crypto");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const {spawnSync} = require("node:child_process");

const root = path.resolve(__dirname, "..");
const audio = path.join(root, "yoRadio", "src", "audioI2S");
const native = path.join(__dirname, "native", "helix_golden");
const fixtures = path.join(__dirname, "fixtures", "helix_golden");
const expected = JSON.parse(
  fs.readFileSync(path.join(fixtures, "expected.json"), "utf8"),
);

function findVcVars() {
  const base = "C:\\Program Files\\Microsoft Visual Studio";
  if(!fs.existsSync(base)) return null;
  for(const version of fs.readdirSync(base).sort().reverse()) {
    const versionDir = path.join(base, version);
    for(const edition of fs.readdirSync(versionDir).sort().reverse()) {
      const candidate = path.join(
        versionDir, edition, "VC", "Auxiliary", "Build", "vcvars64.bat",
      );
      if(fs.existsSync(candidate)) return candidate;
    }
  }
  return null;
}

function compile(outputDir, name, reference, mp3Sso = false, aacSso = false, options = {}) {
  const executable = path.join(
    outputDir, process.platform === "win32" ? `${name}.exe` : name,
  );
  const sources = [
    path.join(audio, "mp3_decoder", "mp3_decoder.cpp"),
    path.join(audio, "aac_decoder", "aac_decoder.cpp"),
    path.join(native, "codec_arena_host.cpp"),
    path.join(native, "decode_fixture.cpp"),
  ];
  if(options.unit) {
    sources[0] = path.join(native, "mp3_mono_state_test.cpp");
    sources.pop();
  }
  if(options.reorderUnit) {
    sources[0] = path.join(native, "mp3_reorder_state_test.cpp");
    sources.splice(2, 2); // this harness supplies its own checked allocator
  }
  if(options.blockUnit) {
    sources[0] = path.join(native, "mp3_block_state_test.cpp");
    sources.pop();
  }
  if(options.aacBlockUnit) {
    sources.splice(0, 2, path.join(native, "aac_block_state_test.cpp"));
    sources.pop();
  }
  const defines = ["YORADIO_ESP8266_NATIVE=1"];
  if(options.aacHuffmanUnit) {
    sources.splice(0, 2, path.join(native, "aac_huffman_state_test.cpp"));
    sources.pop();
  }
  if(reference) defines.push("YORADIO_HELIX_REFERENCE_FIXED_POINT=1");
  if(reference) defines.push("YORADIO_HELIX_AAC_REFERENCE_HUFFMAN=1");
  if(mp3Sso) defines.push("YORADIO_HELIX_MP3_SSO=1");
  if(aacSso) defines.push("YORADIO_HELIX_AAC_SSO=1");
  if(options.mono) defines.push("YORADIO_HELIX_MP3_MONO=1");
  if(options.profile) defines.push("YORADIO_ESP8266_HELIX_STAGE_PROFILE=1");
  if(options.sharedReorder !== undefined)
    defines.push(`YORADIO_HELIX_MP3_SHARED_REORDER=${options.sharedReorder ? 1 : 0}`);

  let build;
  if(process.platform === "win32") {
    const vcvars = findVcVars();
    if(!vcvars) return {skip: "Visual C++ build tools are not installed"};
    const args = [
      "/nologo", "/std:c++17", "/O2", "/EHsc", "/W3",
      ...defines.map(value => `/D${value}`),
      `/I${native}`, `/I${audio}`,
      `/I${path.join(audio, "mp3_decoder")}`,
      `/I${path.join(audio, "aac_decoder")}`,
      ...sources,
      `/Fe:${executable}`,
    ];
    const quote = value => `"${value.replaceAll('"', '""')}"`;
    const command = [
      `@call "${vcvars}" >nul`,
      "@if errorlevel 1 exit /b %errorlevel%",
      `@cl ${args.map(quote).join(" ")}`,
    ].join("\r\n") + "\r\n";
    const batch = path.join(outputDir, `build-${name}.cmd`);
    fs.writeFileSync(batch, command);
    build = spawnSync("cmd.exe", ["/d", "/c", batch], {
      cwd: outputDir,
      encoding: "utf8",
    });
  } else {
    const args = [
      "-std=c++17", "-O2", "-Wall", "-Wextra",
      ...defines.map(value => `-D${value}`),
      `-I${native}`, `-I${audio}`,
      `-I${path.join(audio, "mp3_decoder")}`,
      `-I${path.join(audio, "aac_decoder")}`,
      ...sources, "-o", executable,
    ];
    build = spawnSync("c++", args, {cwd: outputDir, encoding: "utf8"});
    if(build.error?.code === "ENOENT") {
      return {skip: "A host C++ compiler is not installed"};
    }
  }
  assert.equal(build.status, 0, `${build.stdout}\n${build.stderr}`);
  return {executable};
}

function comparePcm(reference, candidate) {
  assert.equal(candidate.length, reference.length, "PCM length differs");
  let signal = 0;
  let noise = 0;
  let maximumError = 0;
  for(let offset = 0; offset < reference.length; offset += 2) {
    const expected = reference.readInt16LE(offset);
    const actual = candidate.readInt16LE(offset);
    const error = actual - expected;
    signal += expected * expected;
    noise += error * error;
    maximumError = Math.max(maximumError, Math.abs(error));
  }
  return {
    snrDb: noise === 0 ? Infinity : 10 * Math.log10(signal / noise),
    maximumError,
  };
}

function decode(executable, codec, fixture, output) {
  const result = spawnSync(executable, [codec, fixture, output], {
    encoding: "utf8",
  });
  assert.equal(result.status, 0, `${result.stdout}\n${result.stderr}`);
  const pcm = fs.readFileSync(output);
  assert.ok(pcm.length > 0, `${codec} decoder produced no PCM`);
  return {
    pcm,
    summary: result.stdout.trim(),
    profile: result.stderr.trim(),
    sha256: crypto.createHash("sha256").update(pcm).digest("hex"),
  };
}

function mp3Modes(source, selectMode) {
  const data = Buffer.from(source);
  const rates = [0,32,40,48,56,64,80,96,112,128,160,192,224,256,320];
  const samples = [44100,48000,32000];
  let frames = 0;
  let start = 0;
  if(data.subarray(0,3).toString() === "ID3") {
    start = 10;
    start += (data[6] << 21) | (data[7] << 14) | (data[8] << 7) | data[9];
  }
  for(let offset = start; offset + 4 <= data.length;) {
    assert.equal(data[offset], 0xff);
    assert.equal(data[offset + 1] & 0xfe, 0xfa, "fixture must be MPEG1 Layer III");
    const size = Math.floor(144000 * rates[data[offset + 2] >> 4] /
      samples[(data[offset + 2] >> 2) & 3]) + ((data[offset + 2] >> 1) & 1);
    if(offset + size > data.length) break;
    data[offset + 3] = (data[offset + 3] & 15) | selectMode(frames++);
    offset += size;
  }
  assert.ok(frames > 4);
  return data;
}

function downmix(stereo) {
  const mono = Buffer.alloc(stereo.length / 2);
  for(let offset = 0; offset < stereo.length; offset += 4)
    mono.writeInt16LE((stereo.readInt16LE(offset) + stereo.readInt16LE(offset + 2)) >> 1, offset / 2);
  return mono;
}

test("AAC flash Huffman lookup matches every canonical code and suffix", t => {
  const generated = spawnSync(process.execPath, [path.join(root, 'tools/esp8266_audio_profile/generate_aac_prefix.js'), '--check'], {encoding:'utf8'});
  assert.equal(generated.status, 0, generated.stdout + generated.stderr);
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'aac-huffman-'));
  t.after(() => fs.rmSync(dir, {recursive:true, force:true}));
  const binary = compile(dir, 'aac-huffman', false, false, false, {aacHuffmanUnit:true});
  if(binary.skip) return t.skip(binary.skip);
  const run = spawnSync(binary.executable, [], {encoding:'utf8'});
  assert.equal(run.status, 0, run.stdout + run.stderr);
  t.diagnostic(run.stdout.trim());
});

test("AAC exact optimizations preserve PCM on all retained rates and channels", t => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'aac-exact-speed-'));
  t.after(() => fs.rmSync(dir, {recursive:true, force:true}));
  const ref = compile(dir, 'aac-reference', true);
  const fast = compile(dir, 'aac-fast', false);
  if(ref.skip || fast.skip) return t.skip(ref.skip || fast.skip);
  for(const fixture of [path.join(fixtures, 'stereo-320.aac'),
    path.join(__dirname, 'fixtures/helix_aac_blocks/mono-22050.aac'),
    path.join(__dirname, 'fixtures/helix_aac_blocks/stereo-44100.aac')]) {
    const a = decode(ref.executable, 'aac', fixture, path.join(dir, 'a.pcm'));
    const b = decode(fast.executable, 'aac-blocks-512', fixture, path.join(dir, 'b.pcm'));
    const quality = comparePcm(a.pcm, b.pcm);
    assert.deepEqual(a.pcm, b.pcm);
    assert.equal(quality.maximumError, 0);
    t.diagnostic(`${path.basename(fixture)}: samples=${a.pcm.length / 2}, maxError=${quality.maximumError}, SNR=${quality.snrDb} dB`);
  }
});

test("AAC sequential block windows preserve exact PCM and overlap state", t => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "aac-window-blocks-"));
  t.after(() => fs.rmSync(dir, {recursive:true, force:true}));
  for(const sso of [false, true]) {
    const binary = compile(dir, `aac-state-${sso}`, false, false, sso, {aacBlockUnit:true});
    if(binary.skip) return t.skip(binary.skip);
    const run = spawnSync(binary.executable, [], {encoding:"utf8"});
    assert.equal(run.status, 0, run.stdout + run.stderr);
    t.diagnostic(run.stdout.trim());
  }
});

test("AAC 32/64/128/256/512-frame callbacks match full-frame decode and mono downmix", t => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "aac-pcm-blocks-"));
  t.after(() => fs.rmSync(dir, {recursive:true, force:true}));
  const inputs = [
    [path.join(fixtures, "stereo-320.aac"), 2],
    [path.join(__dirname, "fixtures", "helix_aac_blocks", "mono-22050.aac"), 1],
    [path.join(__dirname, "fixtures", "helix_aac_blocks", "stereo-44100.aac"), 2],
  ];
  for(const sso of [false, true]) {
    const binary = compile(dir, `aac-blocks-${sso}`, false, false, sso);
    if(binary.skip) return t.skip(binary.skip);
    for(const [fixture, channels] of inputs) {
      const reference = decode(binary.executable, "aac", fixture, path.join(dir, "reference.pcm"));
      for(const frames of [32, 64, 128, 256, 512]) for(const mono of [false, true]) {
        const actual = decode(binary.executable, `aac-blocks-${frames}${mono ? "-mono" : ""}`, fixture, path.join(dir, "blocks.pcm"));
        const expectedPcm = mono && channels === 2 ? downmix(reference.pcm) : reference.pcm;
        const quality = comparePcm(expectedPcm, actual.pcm);
        assert.equal(quality.maximumError, 0);
        assert.equal(quality.snrDb, Infinity);
        assert.deepEqual(actual.pcm, expectedPcm,
          `AAC ${frames} frames, mono=${mono}, SSO=${sso}, ${fixture}`);
      }
    }
  }
  t.diagnostic('AAC block matrix: all PCM samples bit-identical; maximum error=0, SNR=Infinity dB versus exact matching full-frame arithmetic');
});

test("32-frame MP3 output matches granules and full frames byte for byte", t => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "helix-blocks-"));
  t.after(() => fs.rmSync(dir, {recursive:true, force:true}));
  const original = fs.readFileSync(path.join(fixtures, "stereo-320.mp3"));
  const inputs = [
    ["noise-320", original],
    ["modes", mp3Modes(original, i => [0x60,0x00,0x50,0x70,0x80][i % 5])],
    ...["mpeg1", "mpeg2", "mpeg25", "mono"].map(name => [name,
      fs.readFileSync(path.join(__dirname, "fixtures", "helix_mono", `${name}.mp3`))]),
  ];
  for(const mono of [false, true]) for(const sso of [false, true]) {
    const binary = compile(dir, `blocks-${mono}-${sso}`, false, sso, false, {mono});
    if(binary.skip) return t.skip(binary.skip);
    for(const [name, data] of inputs) {
      const input = path.join(dir, `${name}.mp3`);
      fs.writeFileSync(input, data);
      const reference = decode(binary.executable, "mp3", input, path.join(dir, "frame.pcm"));
      for(const api of ["mp3-granules", "mp3-blocks"]) {
        const actual = decode(binary.executable, api, input, path.join(dir, "out.pcm"));
        assert.equal(actual.summary, reference.summary);
        assert.deepEqual(actual.pcm, reference.pcm, `${name}, mono=${mono}, SSO=${sso}, ${api}`);
      }
    }
  }
  t.diagnostic("6 vectors x mono/stereo x exact/SSO: frame, granule and 32-frame PCM identical; canaries intact");
});

test("32-frame MP3 output handles cancellation, reset and bounded error concealment", t => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "helix-block-state-"));
  t.after(() => fs.rmSync(dir, {recursive:true, force:true}));
  for(const mono of [false, true]) {
    const binary = compile(dir, `state-${mono}`, false, true, false, {mono, blockUnit:true});
    if(binary.skip) return t.skip(binary.skip);
    const run = spawnSync(binary.executable, [], {encoding:"utf8"});
    assert.equal(run.status, 0, run.stdout + run.stderr);
    t.diagnostic(run.stdout.trim());
  }
});

test("shared MP3 reorder scratch is bit-exact against the separate allocation", t => {
  const outputDir = fs.mkdtempSync(path.join(os.tmpdir(), "helix-reorder-pcm-"));
  t.after(() => fs.rmSync(outputDir, {recursive:true, force:true}));
  const original = fs.readFileSync(path.join(fixtures, "stereo-320.mp3"));
  const inputs = [
    ["noise-320", original],
    ["mode-switches", mp3Modes(original, i => [0x60,0x00,0x50,0x70,0x80][i % 5])],
    ...["mpeg1", "mpeg2", "mpeg25", "mono"].map(name => [name,
      fs.readFileSync(path.join(__dirname, "fixtures", "helix_mono", `${name}.mp3`))]),
  ];
  for(const mono of [false, true]) {
    const before = compile(outputDir, `before-${mono}`, false, true, false, {mono, sharedReorder:false});
    if(before.skip) return t.skip(before.skip);
    const after = compile(outputDir, `after-${mono}`, false, true, false, {mono, sharedReorder:true});
    for(const [name, data] of inputs) {
      const fixture = path.join(outputDir, `${name}.mp3`);
      fs.writeFileSync(fixture, data);
      for(const api of ["mp3", "mp3-granules"]) {
        const oldPcm = decode(before.executable, api, fixture, path.join(outputDir, "before.pcm"));
        const newPcm = decode(after.executable, api, fixture, path.join(outputDir, "after.pcm"));
        assert.equal(newPcm.summary, oldPcm.summary);
        assert.deepEqual(newPcm.pcm, oldPcm.pcm, `${name} mono=${mono} ${api}: shared scratch changed PCM`);
      }
    }
  }
  t.diagnostic("6 MP3 vectors x mono/stereo x frame/granule API: identical PCM bytes");
});

test("shared MP3 reorder has one owner, saves 792 heap bytes and survives allocation failures", t => {
  const outputDir = fs.mkdtempSync(path.join(os.tmpdir(), "helix-reorder-state-"));
  t.after(() => fs.rmSync(outputDir, {recursive:true, force:true}));
  const reports = [];
  for(const sharedReorder of [false, true]) {
    const binary = compile(outputDir, `state-${sharedReorder}`, false, true, false,
      {mono:true, sharedReorder, reorderUnit:true});
    if(binary.skip) return t.skip(binary.skip);
    const result = spawnSync(binary.executable, [], {encoding:"utf8"});
    assert.equal(result.status, 0, result.stdout + result.stderr);
    const values = /heap=(\d+) word=(\d+) allocations=(\d+)/.exec(result.stdout);
    assert.ok(values, result.stdout);
    reports.push(values.slice(1).map(Number));
    t.diagnostic(`${sharedReorder ? "shared" : "separate"}: ${result.stdout.trim()}`);
  }
  assert.equal(reports[0][0] - reports[1][0], 792);
  assert.equal(reports[0][1], reports[1][1], "word arena grew");
  assert.equal(reports[0][2] - reports[1][2], 1);
});

test("MP3 build-time mono skips M/S side and preserves fallback/mode transitions", t => {
  const outputDir = fs.mkdtempSync(path.join(os.tmpdir(), "helix-mono-"));
  t.after(() => fs.rmSync(outputDir, {recursive: true, force: true}));
  const stereo = compile(outputDir, "stereo", false, true, false, {profile:true});
  if(stereo.skip) return t.skip(stereo.skip);
  const mono = compile(outputDir, "mono", false, true, false, {mono:true, profile:true});
  const original = fs.readFileSync(path.join(fixtures, "stereo-320.mp3"));
  for(const [name, data] of [
    ["original", original],
    ["mid-side", mp3Modes(original, () => 0x60)],
    ["left-right", mp3Modes(original, () => 0x00)],
    ["dual-channel", mp3Modes(original, () => 0x80)],
    ["intensity", mp3Modes(original, () => 0x50)],
    ["mid-side-intensity", mp3Modes(original, () => 0x70)],
    ["transitions", mp3Modes(original, i => [0x60,0x00,0x50,0x70,0x60][i % 5])],
    ...["mpeg1", "mpeg2", "mpeg25", "mono"].map(name => [name,
      fs.readFileSync(path.join(__dirname, "fixtures", "helix_mono", `${name}.mp3`))]),
  ]) {
    const fixture = path.join(outputDir, `${name}.mp3`);
    fs.writeFileSync(fixture, data);
    const ref = decode(stereo.executable, "mp3", fixture, path.join(outputDir, `${name}-stereo.pcm`));
    const actual = decode(mono.executable, "mp3", fixture, path.join(outputDir, `${name}-mono.pcm`));
    const granules = decode(mono.executable, "mp3-granules", fixture, path.join(outputDir, `${name}-granules.pcm`));
    assert.deepEqual(actual.pcm, granules.pcm, `${name}: frame/granule API differs`);
    const quality = comparePcm(name === "mono" ? ref.pcm : downmix(ref.pcm), actual.pcm);
    assert.ok(quality.snrDb >= 48, `${name}: SNR=${quality.snrDb}`);
    assert.ok(quality.maximumError <= 64, `${name}: error=${quality.maximumError}`);
    const calls = value => Number(/huffman=(\d+)/.exec(value.profile)[1]);
    if(["mid-side", "mpeg1", "mpeg2", "mpeg25"].includes(name))
      assert.ok(calls(actual) < calls(ref), `${name}: side Huffman was not skipped`);
    if(name === "mono") assert.deepEqual(actual.pcm, ref.pcm, "native mono must remain bit-exact");
    if(["left-right", "dual-channel", "intensity", "mid-side-intensity"].includes(name))
      assert.equal(calls(actual), calls(ref), `${name}: unsafe side skip`);
    t.diagnostic(`${name}: SNR=${quality.snrDb.toFixed(2)} dB maxError=${quality.maximumError}, Huffman ${calls(ref)} -> ${calls(actual)}`);
  }
});

test("MP3 mono overlap state is safe across windows, channel modes and reset", t => {
  const outputDir = fs.mkdtempSync(path.join(os.tmpdir(), "helix-mono-state-"));
  t.after(() => fs.rmSync(outputDir, {recursive:true, force:true}));
  const binary = compile(outputDir, "mono-state", false, false, false, {mono:true, unit:true});
  if(binary.skip) return t.skip(binary.skip);
  const result = spawnSync(binary.executable, [], {encoding:"utf8"});
  assert.equal(result.status, 0, result.stdout + result.stderr);
  t.diagnostic(result.stdout.trim());
});

test("ESP8266 optimized Helix MP3/AAC PCM matches the 64-bit reference", t => {
  const outputDir = fs.mkdtempSync(path.join(os.tmpdir(), "helix-golden-"));
  t.after(() => fs.rmSync(outputDir, {recursive: true, force: true}));
  const reference = compile(outputDir, "helix-reference", true);
  if(reference.skip) return t.skip(reference.skip);
  const optimized = compile(outputDir, "helix-lx106", false);

  for(const [codec, filename] of [
    ["mp3", "stereo-320.mp3"],
    ["aac", "stereo-320.aac"],
  ]) {
    const fixture = path.join(fixtures, filename);
    assert.ok(fs.statSync(fixture).size > 1000, `${filename} fixture is missing`);
    const oldPcm = decode(
      reference.executable, codec, fixture,
      path.join(outputDir, `${codec}-reference.pcm`),
    );
    const newPcm = decode(
      optimized.executable, codec, fixture,
      path.join(outputDir, `${codec}-optimized.pcm`),
    );
    assert.equal(oldPcm.pcm.length, expected[codec].bytes, `${codec} golden PCM length changed`);
    assert.equal(oldPcm.sha256, expected[codec].sha256, `${codec} golden PCM hash changed`);
    assert.equal(newPcm.summary, oldPcm.summary, `${codec} sample count changed`);
    assert.equal(newPcm.pcm.length, oldPcm.pcm.length, `${codec} PCM length changed`);
    assert.equal(newPcm.sha256, oldPcm.sha256, `${codec} PCM hash changed`);
    assert.deepEqual(newPcm.pcm, oldPcm.pcm, `${codec} PCM bytes changed`);
    t.diagnostic(`${codec}: ${newPcm.summary}, sha256=${newPcm.sha256}`);
  }
});

test("ESP8266 Helix SSO preserves MP3 frame layout and useful PCM quality", t => {
  const kconfig = fs.readFileSync(path.join(
    root, "esp8266", "rtos-sdk-native", "main", "Kconfig.projbuild",
  ), "utf8");
  const cmake = fs.readFileSync(path.join(
    root, "esp8266", "rtos-sdk-native", "components", "helix_codecs",
    "CMakeLists.txt",
  ), "utf8");
  const profile = fs.readFileSync(path.join(
    root, "esp8266", "rtos-sdk-native",
    "sdkconfig.helix-sso-qio80.defaults",
  ), "utf8");
  assert.match(kconfig, /config YORADIO_HELIX_MP3_SSO/);
  assert.match(cmake, /CONFIG_YORADIO_HELIX_MP3_SSO/);
  assert.match(profile, /CONFIG_YORADIO_HELIX_MP3_SSO=y/);

  const outputDir = fs.mkdtempSync(path.join(os.tmpdir(), "helix-sso-"));
  t.after(() => fs.rmSync(outputDir, {recursive: true, force: true}));
  const reference = compile(outputDir, "helix-reference", true);
  if(reference.skip) return t.skip(reference.skip);
  const sso = compile(outputDir, "helix-sso", false, true);
  const fixture = path.join(fixtures, "stereo-320.mp3");
  const oldPcm = decode(
    reference.executable, "mp3", fixture,
    path.join(outputDir, "mp3-reference.pcm"),
  );
  const newPcm = decode(
    sso.executable, "mp3", fixture,
    path.join(outputDir, "mp3-sso.pcm"),
  );
  assert.equal(newPcm.summary, oldPcm.summary, "MP3 sample count changed");
  const quality = comparePcm(oldPcm.pcm, newPcm.pcm);
  assert.ok(Number.isFinite(quality.snrDb) && quality.snrDb >= 48,
    `unexpected SSO SNR ${quality.snrDb}`);
  assert.ok(quality.maximumError <= 34,
    `unexpected SSO maximum error ${quality.maximumError}`);
  t.diagnostic(`SSO SNR=${quality.snrDb.toFixed(2)} dB, ` +
    `maxError=${quality.maximumError} PCM levels`);
});

test("ESP8266 Helix AAC SSO preserves frame layout and useful PCM quality", t => {
  const kconfig = fs.readFileSync(path.join(
    root, "esp8266", "rtos-sdk-native", "main", "Kconfig.projbuild",
  ), "utf8");
  const cmake = fs.readFileSync(path.join(
    root, "esp8266", "rtos-sdk-native", "components", "helix_codecs",
    "CMakeLists.txt",
  ), "utf8");
  const profile = fs.readFileSync(path.join(
    root, "esp8266", "rtos-sdk-native", "sdkconfig.aac-sso-qio80.defaults",
  ), "utf8");
  assert.match(kconfig, /config YORADIO_HELIX_AAC_SSO/);
  assert.match(cmake, /CONFIG_YORADIO_HELIX_AAC_SSO/);
  assert.match(profile, /CONFIG_YORADIO_HELIX_AAC_SSO=y/);

  const outputDir = fs.mkdtempSync(path.join(os.tmpdir(), "helix-aac-sso-"));
  t.after(() => fs.rmSync(outputDir, {recursive: true, force: true}));
  const reference = compile(outputDir, "helix-reference", true);
  if(reference.skip) return t.skip(reference.skip);
  const sso = compile(outputDir, "helix-aac-sso", false, false, true);
  const fixture = path.join(fixtures, "stereo-320.aac");
  const oldPcm = decode(
    reference.executable, "aac", fixture,
    path.join(outputDir, "aac-reference.pcm"),
  );
  const newPcm = decode(
    sso.executable, "aac", fixture,
    path.join(outputDir, "aac-sso.pcm"),
  );
  assert.equal(newPcm.summary, oldPcm.summary, "AAC sample count changed");
  const quality = comparePcm(oldPcm.pcm, newPcm.pcm);
  assert.ok(Number.isFinite(quality.snrDb) && quality.snrDb >= 80,
    `unexpected AAC SSO SNR ${quality.snrDb}`);
  assert.ok(quality.maximumError <= 1,
    `unexpected AAC SSO maximum error ${quality.maximumError}`);
  t.diagnostic(`AAC SSO SNR=${quality.snrDb.toFixed(2)} dB, ` +
    `maxError=${quality.maximumError} PCM levels`);
});
