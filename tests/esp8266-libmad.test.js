const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const {spawnSync} = require("node:child_process");

const root = path.resolve(__dirname, "..");
const component = path.join(
  root, "esp8266", "rtos-sdk-native", "components", "libmad8266",
);
const libmad = path.join(component, "upstream", "libmad");
const fixture = path.join(
  root, "tests", "fixtures", "helix_golden", "stereo-320.mp3",
);

function wslPath(file) {
  const result = spawnSync("wsl.exe", ["-e", "wslpath", "-a", file], {
    encoding: "utf8",
  });
  if(result.status !== 0) return null;
  return result.stdout.trim();
}

function compile(outputDir, externalWorkspace = false) {
  if(process.platform !== "win32") {
    return {skip: "This ESP8266 libmad host test currently uses WSL GCC"};
  }
  const linuxOutput = wslPath(outputDir);
  if(!linuxOutput) return {skip: "WSL GCC is not available"};
  const suffix = externalWorkspace ? "-external-workspace" : "";
  const executable = `${linuxOutput}/libmad-golden${suffix}`;
  const definitions = externalWorkspace
    ? ["-DYORADIO_LIBMAD_EXTERNAL_FRAME_WORKSPACE=1"] : [];
  const sourceNames = [
    "bit.c", "fixed.c", "frame.c", "huffman.c", "layer3.c", "stream.c",
    "synth.c", "timer.c", "version.c",
  ];
  const includeArgs = ["-I", wslPath(component), "-I", wslPath(libmad)];
  const objects = [];
  for(const name of sourceNames) {
    const object = `${linuxOutput}/${name}.o`;
    const build = spawnSync("wsl.exe", ["-e", "gcc", "-O2", ...definitions,
      ...includeArgs,
      "-c", wslPath(path.join(libmad, name)), "-o", object], {encoding: "utf8"});
    assert.equal(build.status, 0, `${build.stdout}\n${build.stderr}`);
    objects.push(object);
  }
  const mainObject = `${linuxOutput}/decode_fixture.o`;
  const mainBuild = spawnSync("wsl.exe", ["-e", "g++", "-std=c++17", "-O2",
    ...definitions, ...includeArgs, "-c", wslPath(path.join(
      root, "tests", "native", "libmad_golden", "decode_fixture.cpp",
    )), "-o", mainObject], {encoding: "utf8"});
  assert.equal(mainBuild.status, 0, `${mainBuild.stdout}\n${mainBuild.stderr}`);
  const link = spawnSync("wsl.exe", ["-e", "g++", ...objects, mainObject,
    "-o", executable], {encoding: "utf8"});
  assert.equal(link.status, 0, `${link.stdout}\n${link.stderr}`);
  return {executable, viaWsl: true};
}

function compileHelix(outputDir) {
  const linuxOutput = wslPath(outputDir);
  const audio = path.join(root, "yoRadio", "src", "audioI2S");
  const native = path.join(root, "tests", "native", "helix_golden");
  const executable = `${linuxOutput}/helix-golden`;
  const sources = [
    path.join(audio, "mp3_decoder", "mp3_decoder.cpp"),
    path.join(audio, "aac_decoder", "aac_decoder.cpp"),
    path.join(native, "codec_arena_host.cpp"),
    path.join(native, "decode_fixture.cpp"),
  ].map(wslPath);
  const build = spawnSync("wsl.exe", ["-e", "g++", "-std=c++17", "-O2",
    "-DYORADIO_ESP8266_NATIVE=1", "-I", wslPath(native),
    "-I", wslPath(audio), "-I", wslPath(path.join(audio, "mp3_decoder")),
    "-I", wslPath(path.join(audio, "aac_decoder")), ...sources,
    "-o", executable], {encoding: "utf8"});
  assert.equal(build.status, 0, `${build.stdout}\n${build.stderr}`);
  return executable;
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

test("ESP8266 libmad backend is pinned, selectable, and decodes golden MP3", t => {
  const kconfig = fs.readFileSync(path.join(
    root, "esp8266", "rtos-sdk-native", "main", "Kconfig.projbuild",
  ), "utf8");
  const cmake = fs.readFileSync(path.join(
    root, "esp8266", "rtos-sdk-native", "components", "helix_codecs",
    "CMakeLists.txt",
  ), "utf8");
  const readme = fs.readFileSync(path.join(component, "README.md"), "utf8");
  const defaultConfig = fs.readFileSync(path.join(
    root, "esp8266", "rtos-sdk-native", "sdkconfig.defaults",
  ), "utf8");
  const libmadConfig = fs.readFileSync(path.join(
    root, "esp8266", "rtos-sdk-native", "sdkconfig.libmad.defaults",
  ), "utf8");
  const libmadQio80Config = fs.readFileSync(path.join(
    root, "esp8266", "rtos-sdk-native", "sdkconfig.libmad-qio80.defaults",
  ), "utf8");
  assert.match(kconfig, /config YORADIO_MP3_DECODER_LIBMAD/);
  assert.match(kconfig, /default YORADIO_MP3_DECODER_HELIX/);
  assert.match(cmake, /CONFIG_YORADIO_MP3_DECODER_LIBMAD/);
  assert.match(cmake, /libmad8266\/upstream\/libmad/);
  assert.match(readme, /10d929ac01436dfe8856e0a06fd9ec35a848c6e2/);
  assert.match(defaultConfig, /CONFIG_YORADIO_MP3_DECODER_HELIX=y/);
  assert.match(libmadConfig, /CONFIG_IDF_TARGET="esp8266"/);
  assert.match(libmadConfig, /CONFIG_YORADIO_MP3_DECODER_LIBMAD=y/);
  assert.match(libmadQio80Config, /CONFIG_ESPTOOLPY_FLASHFREQ_80M=y/);
  assert.match(libmadQio80Config, /CONFIG_YORADIO_MP3_DECODER_LIBMAD=y/);
  assert.ok(fs.existsSync(path.join(libmad, "COPYING")));
  assert.ok(fs.existsSync(path.join(component, "ESP8266Audio-LICENSE.txt")));

  const outputDir = fs.mkdtempSync(path.join(os.tmpdir(), "libmad-golden-"));
  t.after(() => fs.rmSync(outputDir, {recursive: true, force: true}));
  const build = compile(outputDir);
  if(build.skip) return t.skip(build.skip);
  const pcmPath = path.join(outputDir, "libmad.pcm");
  const decoded = spawnSync("wsl.exe", ["-e", build.executable,
    wslPath(fixture), wslPath(pcmPath)], {
    encoding: "utf8",
  });
  assert.equal(decoded.status, 0, `${decoded.stdout}\n${decoded.stderr}`);
  const pcm = fs.readFileSync(pcmPath);
  assert.ok(pcm.length >= 80000, "libmad produced too little PCM");
  assert.match(decoded.stdout, /rate=48000 channels=2/);
  const externalBuild = compile(outputDir, true);
  const externalPcmPath = path.join(outputDir, "libmad-external.pcm");
  const externalDecoded = spawnSync("wsl.exe", ["-e", externalBuild.executable,
    wslPath(fixture), wslPath(externalPcmPath)], {encoding: "utf8"});
  assert.equal(externalDecoded.status, 0,
    `${externalDecoded.stdout}\n${externalDecoded.stderr}`);
  assert.deepEqual(fs.readFileSync(externalPcmPath), pcm,
    "external libmad frame workspace changed PCM output");
  const helixExecutable = compileHelix(outputDir);
  const helixPcmPath = path.join(outputDir, "helix.pcm");
  const helixDecoded = spawnSync("wsl.exe", ["-e", helixExecutable, "mp3",
    wslPath(fixture), wslPath(helixPcmPath)], {encoding: "utf8"});
  assert.equal(helixDecoded.status, 0,
    `${helixDecoded.stdout}\n${helixDecoded.stderr}`);
  const quality = comparePcm(fs.readFileSync(helixPcmPath), pcm);
  assert.ok(Number.isFinite(quality.snrDb) && quality.snrDb > 0,
    `unexpected libmad SNR ${quality.snrDb}`);
  t.diagnostic(`${decoded.stdout.trim()}, SNR=${quality.snrDb.toFixed(2)} dB, ` +
    `maxError=${quality.maximumError} PCM levels`);
});
