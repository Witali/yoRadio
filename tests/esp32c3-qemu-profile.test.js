const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const root = path.resolve(__dirname, "..");
const nativeRoot = path.join(root, "idf", "esp32c3-oled-native");
const read = (...parts) =>
  fs.readFileSync(path.join(nativeRoot, ...parts), "utf8");

test("QEMU profile is isolated from hardware builds", () => {
  const build = read("build-qemu.ps1");
  const qemuDefaults = read("sdkconfig.qemu.defaults");
  const defaults = read("sdkconfig.defaults");
  const production = read("build-production.ps1");

  assert.match(build, /sdkconfig\.qemu\.defaults/);
  assert.match(qemuDefaults, /CONFIG_YORADIO_QEMU=y/);
  assert.match(qemuDefaults, /CONFIG_ESP_CONSOLE_UART_DEFAULT=y/);
  assert.doesNotMatch(defaults, /CONFIG_YORADIO_QEMU=y/);
  assert.doesNotMatch(production, /qemu/i);
});

test("QEMU smoke validates persistent storage and the scheduler", () => {
  const app = read("main", "app_main.c");
  const kconfig = read("main", "Kconfig.projbuild");

  assert.match(kconfig, /config YORADIO_QEMU/);
  assert.match(app, /#ifdef CONFIG_YORADIO_QEMU/);
  assert.match(app, /fopen\("\/spiffs\/data\/playlist\.csv", "rb"\)/);
  assert.match(app, /xTaskCreate\(qemu_smoke_task/);
  assert.match(app, /QEMU_SMOKE_PASS NVS, SPIFFS and FreeRTOS/);
  assert.match(app, /esp_restart\(\)/);
});

test("QEMU runner merges flash and requires the firmware pass marker", () => {
  const runner = read("run-qemu.ps1");
  const documentation = read("QEMU.md");

  assert.match(runner, /qemu-system-riscv32\.exe/);
  assert.match(runner, /--chip esp32c3 merge-bin/);
  assert.match(runner, /"-M", "esp32c3"/);
  assert.match(runner, /QEMU_SMOKE_PASS/);
  assert.match(documentation, /does not emulate the board's SSD1306/);
  assert.match(documentation, /physical board/);
});
