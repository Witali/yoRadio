'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {spawnSync} = require('node:child_process');
const root = path.resolve(__dirname, '..');
const main = path.join(root, 'esp8266/rtos-sdk-native/main');
const fixture = path.join(__dirname, 'native/sdk_rx_diag');
const overlay = require('../tools/esp8266_audio_profile/build_sdk_rx_diag.cjs');
const sdk = process.env.YORADIO_TEST_SDK_PATH || path.join(root,
  '.worktree/esp8266-native-port/.build/esp8266-rtos-sdk');
const haveSdk = overlay.specs.every(spec => fs.existsSync(path.join(sdk, spec.source)));
const slash = value => value.replaceAll('\\', '/');
function temporary(t) {
  fs.mkdirSync(path.join(root, '.build'), {recursive: true});
  const dir = fs.mkdtempSync(path.join(root, '.build/sdk-rx-diag-test-'));
  t.after(() => fs.rmSync(dir, {recursive: true, force: true}));
  return dir;
}
function copySdk(destination, newline = '\n') {
  for (const spec of overlay.specs) {
    const filename = path.join(destination, spec.source);
    fs.mkdirSync(path.dirname(filename), {recursive: true});
    fs.writeFileSync(filename, overlay.normalize(fs.readFileSync(path.join(sdk, spec.source)))
      .replaceAll('\n', newline));
  }
}
function sdkTest(name, fn) {
  test(name, {skip: !haveSdk && 'Install the pinned ESP8266 SDK or set YORADIO_TEST_SDK_PATH'}, fn);
}

sdkTest('SDK overlay is pinned, deterministic, LF/CRLF tolerant and does not modify SDK sources', t => {
  const dir = temporary(t), copied = path.join(dir, 'sdk'), out = path.join(dir, 'overlay');
  copySdk(copied);
  const originalHashes = overlay.specs.map(spec => overlay.sha256(fs.readFileSync(path.join(sdk, spec.source))));
  const manifest = overlay.generate(copied, out);
  const manifestText = fs.readFileSync(path.join(out, 'manifest.json'), 'utf8');
  assert.equal(manifest.counterBytes, 32);
  assert.equal(manifest.files.length, 3);
  assert.deepEqual(fs.readdirSync(out).sort(), ['manifest.json', ...overlay.specs.map(s => s.output)].sort());
  overlay.generate(copied, out);
  assert.equal(fs.readFileSync(path.join(out, 'manifest.json'), 'utf8'), manifestText);
  for (const [i, spec] of overlay.specs.entries()) {
    const original = fs.readFileSync(path.join(copied, spec.source), 'utf8');
    const patched = fs.readFileSync(path.join(out, spec.output), 'utf8');
    assert.equal(patched.split('\n').filter(line => !line.endsWith(' /* sdk-rx-diag */')).join('\n'), original);
    assert.equal(overlay.sha256(patched), manifest.files[i].outputSha256);
    assert.equal(overlay.sha256(fs.readFileSync(path.join(sdk, spec.source))), originalHashes[i]);
  }
  copySdk(copied, '\r\n');
  const crlf = overlay.generate(copied, path.join(dir, 'crlf'));
  assert.deepEqual(crlf.files.map(f => f.outputSha256), manifest.files.map(f => f.outputSha256));
  assert.deepEqual(crlf.files.map(f => f.normalizedSha256), manifest.files.map(f => f.normalizedSha256));
});

sdkTest('hash changes and missing/duplicate anchors fail closed before producing output', t => {
  const dir = temporary(t), copied = path.join(dir, 'sdk'), out = path.join(dir, 'overlay');
  copySdk(copied);
  for (const spec of overlay.specs) {
    const original = overlay.normalize(fs.readFileSync(path.join(copied, spec.source)));
    for (const patch of spec.patches) {
      assert.throws(() => overlay.patchSource(original.replace(patch.anchor, ''), spec), /exactly one overlay anchor/);
      assert.throws(() => overlay.patchSource(original + patch.anchor, spec), /exactly one overlay anchor/);
    }
  }
  overlay.generate(copied, out);
  const before = fs.readdirSync(out).map(name => [name, overlay.sha256(fs.readFileSync(path.join(out, name)))]);
  // Corrupt the LAST source so a streaming/partial implementation would leak two outputs.
  fs.appendFileSync(path.join(copied, overlay.specs[2].source), '\n/* different SDK */\n');
  assert.throws(() => overlay.generate(copied, path.join(dir, 'new-output')), /SHA-256 mismatch/);
  assert.equal(fs.existsSync(path.join(dir, 'new-output')), false);
  assert.throws(() => overlay.generate(copied, out), /SHA-256 mismatch/);
  assert.deepEqual(fs.readdirSync(out).map(name => [name, overlay.sha256(fs.readFileSync(path.join(out, name)))]), before);
  assert.throws(() => overlay.generate(copied, path.join(copied, 'forbidden')), /outside the installed SDK/);
  assert.equal(fs.existsSync(path.join(copied, 'forbidden')), false);
});

test('CLI rejects unknown or incomplete arguments without a hash-bypass switch', () => {
  const cli = path.join(root, 'tools/esp8266_audio_profile/build_sdk_rx_diag.cjs');
  for (const args of [[], ['--sdk', sdk], ['--sdk', sdk, '--out', '.build/unused', '--skip-hash']]) {
    const result = spawnSync(process.execPath, [cli, ...args], {encoding: 'utf8'});
    assert.notEqual(result.status, 0);
    assert.match(result.stderr, /Usage:/);
  }
});

function extract(source, signature) {
  const first = source.indexOf(signature);
  assert.ok(first >= 0, signature);
  const last = source.indexOf('\n}\n', first);
  assert.ok(last > first, signature);
  return source.slice(first, last + 3);
}
const unix = name => process.platform === 'win32' ? slash(name).replace(/^([a-z]):/i,
  (_, drive) => '/mnt/' + drive.toLowerCase()) : name;
function unixRun(command, args, options = {}) {
  return spawnSync(process.platform === 'win32' ? 'wsl.exe' : command,
    process.platform === 'win32' ? ['--exec', command, ...args] : args,
    {encoding: 'utf8', timeout: 60000, ...options});
}
function success(result) { assert.equal(result.status, 0, result.stdout + '\n' + result.stderr); }

test('real counter module and generated SDK flow: ASan/UBSan, concurrent snapshots, ownership and 32-byte state', t => {
  const dir = temporary(t), inc = path.join(dir, 'sdk_fragments.inc');
  if (haveSdk) {
    const out = path.join(dir, 'overlay');
    overlay.generate(sdk, out);
    const adapter = fs.readFileSync(path.join(out, 'tcpip_adapter_lwip.c'), 'utf8');
    const tcpip = fs.readFileSync(path.join(out, 'tcpip.c'), 'utf8');
    const wlan = fs.readFileSync(path.join(out, 'wlanif.c'), 'utf8');
    const first = adapter.indexOf('struct tcpip_adapter_pbuf {');
    const last = adapter.indexOf('\n};', first);
    assert.ok(first >= 0 && last > first);
    fs.writeFileSync(inc, adapter.slice(first, last + 3) + '\n' +
      extract(adapter, 'static void tcpip_adapter_free_pbuf(') + '\n' +
      extract(adapter, 'static int tcpip_adapter_recv_cb(') + '\n' +
      extract(tcpip, 'err_t\ntcpip_inpkt(') + '\n' +
      extract(wlan, 'static inline struct pbuf* ethernetif_transform_pbuf(') + '\n' +
      extract(wlan, 'static int8_t low_level_output('));
  }
  const common = ['-std=c11', '-Wall', '-Wextra', '-Werror', '-Wno-pointer-to-int-cast', '-O1',
    '-fno-omit-frame-pointer', '-fsanitize=address,undefined', '-pthread',
    '-DYORADIO_ESP8266_SDK_RX_DIAG=1', `-DSDK_RX_DIAG_FUNCTIONS=${haveSdk ? 1 : 0}`,
    '-I' + unix(main), '-I' + unix(fixture), '-I' + unix(dir)];
  const object = path.join(dir, 'diag.o'), executable = path.join(dir, 'diag-test');
  success(unixRun('gcc', [...common, '-c', unix(path.join(main, 'sdk_rx_diag.c')), '-o', unix(object)]));
  success(unixRun('gcc', [...common, unix(path.join(fixture, 'test.c')), unix(object), '-o', unix(executable)]));
  const run = unixRun(unix(executable), []);
  success(run);
  assert.match(run.stdout, /balanced lifetime, concurrent snapshots passed/);
  if (haveSdk) assert.match(run.stdout, /injected control-flow tests passed/);
  const plain = path.join(dir, 'plain.o');
  success(unixRun('gcc', ['-O2', '-DYORADIO_ESP8266_SDK_RX_DIAG=1', '-I' + unix(main),
    '-I' + unix(fixture), '-c', unix(path.join(main, 'sdk_rx_diag.c')), '-o', unix(plain)]));
  const symbols = unixRun('nm', ['-S', unix(plain)]);
  success(symbols);
  assert.match(symbols.stdout, /0000000000000020 b s_sdk_rx_diag/);
  const allocated = symbols.stdout.split('\n').filter(line => / [bBdD] /.test(line));
  assert.equal(allocated.length, 1, symbols.stdout);
  assert.doesNotMatch(symbols.stdout, / U (malloc|calloc|free|printf|xTaskCreate|sys_arch_protect)/);
  const off = path.join(dir, 'off.o');
  success(unixRun('gcc', ['-O2', '-c', unix(path.join(main, 'sdk_rx_diag.c')), '-o', unix(off)]));
  const offSymbols = unixRun('nm', ['-S', unix(off)]);
  success(offSymbols);
  assert.equal(offSymbols.stdout.trim(), '');
});

function vcvars() {
  const base = 'C:/Program Files/Microsoft Visual Studio';
  if (fs.existsSync(base)) for (const version of fs.readdirSync(base)) {
    for (const edition of fs.readdirSync(path.join(base, version))) {
      const file = path.join(base, version, edition, 'VC/Auxiliary/Build/vcvars64.bat');
      if (fs.existsSync(file)) return file;
    }
  }
  throw new Error('Visual C++ tools required for the tiny CMake target-membership test');
}
function configure(source, build, sdkCopy, definitions) {
  const bundled = path.join(root, '.build/esp8266-tools/tools/cmake/3.13.4/bin/cmake.exe');
  const cmake = fs.existsSync(bundled) ? bundled : 'cmake';
  const args = ['-S', source, '-B', build, ...definitions];
  const env = {...process.env, IDF_PATH: slash(sdkCopy)};
  if (process.platform !== 'win32') return spawnSync(cmake, args, {encoding: 'utf8', env, timeout: 60000});
  args.push('-G', 'NMake Makefiles');
  const batch = path.join(source, 'configure.cmd');
  fs.writeFileSync(batch, `@call "${vcvars()}" >nul\r\n@if errorlevel 1 exit /b %errorlevel%\r\n` +
    `@"${cmake}" ${args.map(arg => '"' + arg + '"').join(' ')}\r\n`);
  return spawnSync('cmd.exe', ['/d', '/c', batch], {encoding: 'utf8', env, timeout: 60000});
}

sdkTest('actual CMake targets: exact replacement, OFF restoration and fail-closed diagnostics/membership', t => {
  const dir = temporary(t), copied = path.join(dir, 'sdk'), source = path.join(dir, 'project');
  const build = path.join(dir, 'build');
  copySdk(copied);
  fs.mkdirSync(source);
  fs.writeFileSync(path.join(source, 'other.c'), 'int unrelated_sdk_source;\n');
  const helper = slash(path.join(root, 'esp8266/rtos-sdk-native/cmake/sdk_rx_diag.cmake'));
  const cm = name => '$' + '{' + name + '}';
  fs.writeFileSync(path.join(source, 'CMakeLists.txt'), `cmake_minimum_required(VERSION 3.5)
project(sdk_rx_diag_membership C)
add_library(lwip STATIC "$ENV{IDF_PATH}/${overlay.specs[1].source}" "$ENV{IDF_PATH}/${overlay.specs[2].source}" other.c)
add_library(tcpip_adapter STATIC "$ENV{IDF_PATH}/${overlay.specs[0].source}")
target_compile_definitions(lwip PRIVATE PRESERVED_SDK_DEFINITION=1)
target_compile_options(lwip PRIVATE -preserved-sdk-option)
if(BAD_MEMBERSHIP STREQUAL "missing")
  set_property(TARGET tcpip_adapter PROPERTY SOURCES other.c)
elseif(BAD_MEMBERSHIP STREQUAL "duplicate")
  set_property(TARGET tcpip_adapter APPEND PROPERTY SOURCES "$ENV{IDF_PATH}/${overlay.specs[0].source}")
endif()
function(idf_component_get_property output component property)
  set(${cm('output')} ${cm('component')} PARENT_SCOPE)
endfunction()
include("${helper}")
get_target_property(lwip_sources lwip SOURCES)
get_target_property(adapter_sources tcpip_adapter SOURCES)
get_target_property(lwip_definitions lwip COMPILE_DEFINITIONS)
get_target_property(lwip_options lwip COMPILE_OPTIONS)
file(WRITE "${cm('CMAKE_BINARY_DIR')}/targets.txt" "${cm('lwip_sources')}\n${cm('adapter_sources')}\n${cm('lwip_definitions')}\n${cm('lwip_options')}\n")
`);
  const on = ['-DYORADIO_ESP8266_SDK_RX_DIAG=ON', '-DYORADIO_ESP8266_DIAGNOSTIC=ON',
    '-DYORADIO_RX_DIAG_NODE=' + process.execPath, '-DBAD_MEMBERSHIP='];
  success(configure(source, build, copied, on));
  const targets = fs.readFileSync(path.join(build, 'targets.txt'), 'utf8');
  for (const spec of overlay.specs) {
    assert.ok(targets.includes(slash(path.join(build, 'sdk-rxdiag', spec.output))), targets);
    assert.ok(!targets.includes(slash(path.join(copied, spec.source))), targets);
  }
  assert.match(targets, /other\.c/);
  assert.match(targets, /PRESERVED_SDK_DEFINITION=1/);
  assert.match(targets, /YORADIO_ESP8266_SDK_RX_DIAG=1/);
  assert.match(targets, /-preserved-sdk-option/);
  success(configure(source, build, copied, ['-DYORADIO_ESP8266_SDK_RX_DIAG=OFF',
    '-DYORADIO_ESP8266_DIAGNOSTIC=OFF', '-DYORADIO_RX_DIAG_NODE=/must-not-run-node']));
  const off = fs.readFileSync(path.join(build, 'targets.txt'), 'utf8');
  assert.doesNotMatch(off, /sdk-rxdiag|YORADIO_ESP8266_SDK_RX_DIAG/);
  for (const spec of overlay.specs) assert.ok(off.includes(slash(path.join(copied, spec.source))));
  for (const extra of ['-DYORADIO_ESP8266_DIAGNOSTIC=OFF', '-DBAD_MEMBERSHIP=missing', '-DBAD_MEMBERSHIP=duplicate']) {
    const result = configure(source, build, copied, [...on, extra]);
    assert.notEqual(result.status, 0, result.stdout + result.stderr);
    assert.match(result.stdout + result.stderr, /require YORADIO_ESP8266_DIAGNOSTIC|expected exactly one/);
  }
  fs.appendFileSync(path.join(copied, overlay.specs[1].source), '/* pin mismatch */');
  const mismatch = configure(source, build, copied, on);
  assert.notEqual(mismatch.status, 0);
  assert.match(mismatch.stdout + mismatch.stderr, /SHA-256 mismatch/);
});

test('production defaults omit diagnostic source and module has no allocation, logging or task creation', () => {
  const cmake = fs.readFileSync(path.join(root, 'esp8266/rtos-sdk-native/CMakeLists.txt'), 'utf8');
  const mainCmake = fs.readFileSync(path.join(main, 'CMakeLists.txt'), 'utf8');
  const module = fs.readFileSync(path.join(main, 'sdk_rx_diag.c'), 'utf8');
  assert.match(cmake, /option\(YORADIO_ESP8266_SDK_RX_DIAG\s+"[^"]+" OFF\)/);
  assert.match(mainCmake, /if\(YORADIO_ESP8266_SDK_RX_DIAG\)[\s\S]+?list\(APPEND YORADIO_SOURCES "sdk_rx_diag\.c"\)/);
  assert.doesNotMatch(module, /\b(malloc|calloc|free|printf|xTaskCreate|sys_arch_protect|SYS_ARCH_PROTECT)\s*\(/);
  assert.equal((module.match(/taskENTER_CRITICAL\(\)/g) || []).length, 4);
  assert.equal((module.match(/taskEXIT_CRITICAL\(\)/g) || []).length, 4);
});
