const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const zlib = require("node:zlib");

const root = path.resolve(__dirname, "..");
const read = (...parts) => fs.readFileSync(path.join(root, ...parts), "utf8");

test("firmware warns about significant leading or trailing SSID spaces", () => {
  const header = read("yoRadio", "src", "core", "config.h");
  const config = read("yoRadio", "src", "core", "config.cpp");
  const telnet = read("yoRadio", "src", "core", "telnet.cpp");

  assert.match(header, /static bool ssidHasEdgeSpaces\(const char\* ssid\)/);
  assert.match(config, /ssid\[0\] == ' ' \|\| ssid\[length - 1\] == ' '/);
  assert.match(config, /WARNING: SSID \[%s\] has a leading or trailing space/);
  assert.match(telnet, /##WIFI\.WARNING#/);
  assert.doesNotMatch(telnet, /with PASS:/);
});

test("both Wi-Fi web forms ask before saving edge whitespace", () => {
  const serverHeader = read("yoRadio", "src", "core", "netserver.h");
  const compressedScript = fs.readFileSync(
    path.join(root, "yoRadio", "data", "www", "script.js.gz"),
  );
  const script = zlib.gunzipSync(compressedScript).toString("utf8");

  assert.match(serverHeader, /ssid !== ssid\.trim\(\)/);
  assert.match(serverHeader, /Save exactly as entered\?/);
  assert.match(script, /SSID_WARNING_TEXT/);
  assert.match(script, /inputs\[0\]\.value !== inputs\[0\]\.value\.trim\(\)/);
  assert.match(script, /window\.confirm\(SSID_WARNING_TEXT\)/);
});

test("every firmware target compiles the same Wi-Fi warning sources", () => {
  const c3Build = read("tools", "Build-Esp32C3OledFirmware.ps1");
  const arduinoFlash = read(
    ".agents",
    "skills",
    "flash-reset-esp32",
    "scripts",
    "flash_yoradio.ps1",
  );
  const idfBuild = read(
    "idf",
    "esp32-cyd2usb-minimal",
    "main",
    "CMakeLists.txt",
  );

  assert.match(c3Build, /\$sketch = Join-Path \$repository "yoRadio"/);
  assert.match(arduinoFlash, /\$sketch = Join-Path \$repository "yoRadio"/);
  assert.match(arduinoFlash, /ValidateSet\("DAC", "PDM"\)/);
  for (const source of ["config.cpp", "netserver.cpp", "network.cpp", "telnet.cpp"]) {
    assert.match(idfBuild, new RegExp(`src/core/${source.replace(".", "\\.")}`));
  }
  assert.match(idfBuild, /spiffs_create_partition_image\(spiffs "\$\{YORADIO_ROOT\}\/data"/);
});
