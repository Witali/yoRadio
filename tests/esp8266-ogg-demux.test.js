const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const {spawnSync} = require("node:child_process");

const root = path.resolve(__dirname, "..");
const component = path.join(root, "esp8266/rtos-sdk-native/components/opus_decoder");

test("bounded Ogg Opus demux handles split input, corruption and chains under sanitizers", t => {
  const windows = process.platform === "win32";
  const compiler = process.env.CC || "cc";
  const run = (program, args, options = {}) => spawnSync(
    windows ? "wsl.exe" : program,
    windows ? ["--exec", program, ...args] : args,
    {encoding: "utf8", timeout: 60000, ...options},
  );
  const probe = run(compiler, ["--version"]);
  if (probe.error?.code === "ENOENT" || probe.status !== 0) {
    t.skip(windows ? "WSL C compiler unavailable" : "Host C compiler unavailable");
    return;
  }
  const hostPath = value => {
    if (!windows) return value;
    const translated = run("wslpath", ["-a", "-u", value]);
    assert.equal(translated.status, 0, translated.stdout + translated.stderr);
    return translated.stdout.trim();
  };
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "yoradio-ogg-demux-"));
  t.after(() => fs.rmSync(dir, {recursive: true, force: true}));
  const executable = hostPath(path.join(dir, "ogg-demux-test"));
  const build = run(compiler, [
    "-std=c11", "-O1", "-g", "-Wall", "-Wextra", "-Werror", "-pedantic",
    "-fsanitize=address,undefined", "-fno-omit-frame-pointer", "-fno-pie", "-no-pie",
    "-I" + hostPath(component),
    hostPath(path.join(component, "ogg_opus_demux.c")),
    hostPath(path.join(__dirname, "native/esp8266_ogg_demux_test.c")),
    "-o", executable,
  ]);
  assert.equal(build.status, 0, build.stdout + "\n" + build.stderr);
  const fixtureDir = path.join(__dirname, "fixtures/opus_native");
  const fixtures = fs.existsSync(fixtureDir) ? fs.readdirSync(fixtureDir)
    .filter(name => name.endsWith(".opus"))
    .map(name => hostPath(path.join(fixtureDir, name))) : [];
  const result = run("env", [
    "ASAN_OPTIONS=detect_leaks=1:halt_on_error=1",
    "UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1",
    executable, ...fixtures,
    ...(process.env.YORADIO_OPUS_LIVE_CAPTURE ?
      ["--live-capture", hostPath(path.resolve(process.env.YORADIO_OPUS_LIVE_CAPTURE))] : []),
  ]);
  assert.equal(result.status, 0, result.stdout + "\n" + result.stderr);
  assert.match(result.stdout, /Ogg Opus demux tests passed/);
  assert.match(result.stdout, /state bytes: 18\d\d/);
  assert.match(result.stdout, /live join opt-in, strict rejection, 1024-byte input and later holes passed/);
  assert.equal((result.stdout.match(/fixture packets identical/g) || []).length,
    fixtures.length);
  t.diagnostic(result.stdout.trim());
});
