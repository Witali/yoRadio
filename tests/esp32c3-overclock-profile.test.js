const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const root = path.resolve(__dirname, "..");
const read = (...parts) => fs.readFileSync(path.join(root, ...parts), "utf8");

test("overclock experiment is isolated from the production profile", () => {
  const experiment = read(
    "idf", "esp32c3-oled-native", "build-overclock.ps1");
  const production = read(
    "idf", "esp32c3-oled-native", "build-production.ps1");
  const defaults = read(
    "idf", "esp32c3-oled-native", "sdkconfig.defaults");

  assert.match(experiment, /build-overclock/);
  assert.match(experiment, /sdkconfig\.overclock\.defaults/);
  assert.match(experiment, /YORADIO_OVERCLOCK_EXPERIMENT=ON/);
  assert.doesNotMatch(production, /OVERCLOCK/);
  assert.match(defaults, /CONFIG_ESP_DEFAULT_CPU_FREQ_MHZ_160=y/);
});

test("experiment has an IRAM clock window and independent recovery", () => {
  const source = read(
    "idf", "esp32c3-oled-native", "main", "overclock_experiment.c");

  assert.match(source, /IRAM_ATTR __attribute__\(\(noinline\)\) experiment_sample_t run_200mhz_window/);
  assert.match(source, /RTC_NOINIT_ATTR/);
  assert.match(source, /WDT_STAGE_ACTION_RESET_RTC/);
  assert.match(source, /wait_for_boot_press\(\);[\s\S]*Starting 100 ms/);
  assert.match(source, /bbpll_program_official_480mhz/);
  assert.match(source, /SYSTEM_CPUPERIOD_SEL, 1/);
  assert.match(source, /EXPERIMENT_WINDOW_TICKS 1600000U/);
});

test("experiment documentation explicitly rejects production use", () => {
  const documentation = read("docs", "ESP32C3_OVERCLOCK_EXPERIMENT.md");

  assert.match(documentation, /maximum CPU frequency of 160 MHz/);
  assert.match(documentation, /app-flash/);
  assert.match(documentation, /RTC watchdog/);
  assert.match(documentation, /Never use this profile as the production/);
});
