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

function compile(outputDir, name, reference) {
  const executable = path.join(
    outputDir, process.platform === "win32" ? `${name}.exe` : name,
  );
  const sources = [
    path.join(audio, "mp3_decoder", "mp3_decoder.cpp"),
    path.join(audio, "aac_decoder", "aac_decoder.cpp"),
    path.join(native, "codec_arena_host.cpp"),
    path.join(native, "decode_fixture.cpp"),
  ];
  const defines = ["YORADIO_ESP8266_NATIVE=1"];
  if(reference) defines.push("YORADIO_HELIX_REFERENCE_FIXED_POINT=1");

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
    sha256: crypto.createHash("sha256").update(pcm).digest("hex"),
  };
}

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
