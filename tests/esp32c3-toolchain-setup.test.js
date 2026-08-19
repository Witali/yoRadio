const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const root = path.resolve(__dirname, "..");
const read = (...parts) => fs.readFileSync(path.join(root, ...parts), "utf8");

test("setup reuses Arduino CLI from PATH before downloading a local copy", () => {
  const setup = read("tools", "Setup-Esp32C3OledArduino.ps1");
  const pathLookup = setup.indexOf("Get-Command arduino-cli");
  const localLookup = setup.indexOf("Test-Path -LiteralPath $LocalPath");
  const download = setup.indexOf("Invoke-WebRequest");

  assert.ok(pathLookup >= 0);
  assert.ok(localLookup > pathLookup);
  assert.ok(download > localLookup);
  assert.match(setup, /arduinoCliVersion = "1\.5\.1"/);
  assert.match(setup, /arduinoCliArchiveSha256 = "FABE42E0/);
});

test("setup pins the repository-local ESP32 core and Arduino libraries", () => {
  const setup = read("tools", "Setup-Esp32C3OledArduino.ps1");

  assert.match(setup, /esp32CoreVersion = "3\.3\.8"/);
  assert.match(setup, /\.build\\arduino/);
  assert.match(setup, /Adafruit BusIO@1\.17\.4/);
  assert.match(setup, /Adafruit GFX Library@1\.12\.6/);
  assert.match(setup, /Adafruit ST7735 and ST7789 Library@1\.11\.0/);
  assert.match(setup, /RTClib@2\.1\.4/);
  assert.match(setup, /XPT2046_Touchscreen@1\.4\.0/);
  assert.match(setup, /lib install --no-deps \$library/);
});

test("ESP32-C3 build bootstraps its local toolchain without another repository", () => {
  const build = read("tools", "Build-Esp32C3OledFirmware.ps1");

  assert.match(build, /Join-Path \$repository "tools\\Setup-Esp32C3OledArduino\.ps1"/);
  assert.match(build, /\.build\\arduino-cli\.yaml/);
  assert.match(build, /--config-file \$configPath/);
  assert.match(build, /compiler\.optimization_flags=-O3/);
  assert.doesNotMatch(build, /HLV-codec/);
});
