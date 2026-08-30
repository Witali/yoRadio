const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const root = path.resolve(__dirname, "..");
const native = path.join(root, "idf", "esp32c3-oled-native");
const read = (...parts) => fs.readFileSync(path.join(native, ...parts), "utf8");

test("ESP32-C3 CPU profiling is opt-in and uses interval runtime statistics", () => {
  const defaults = read("sdkconfig.defaults");
  const profile = read("sdkconfig.cpu-profile.defaults");
  const source = read("main", "cpu_profiler.c");
  const app = read("main", "app_main.c");
  const cmake = read("main", "CMakeLists.txt");

  assert.match(defaults, /CONFIG_FREERTOS_GENERATE_RUN_TIME_STATS=n/);
  assert.match(profile, /CONFIG_FREERTOS_GENERATE_RUN_TIME_STATS=y/);
  assert.match(profile, /CONFIG_FREERTOS_RUN_TIME_STATS_USING_ESP_TIMER=y/);
  assert.match(source, /uxTaskGetSystemState/);
  assert.match(source, /interval_total > idle/);
  assert.match(source, /strncmp\(name, "IDLE", 4\)/);
  assert.match(app, /cpu_profiler_start\(\)/);
  assert.match(cmake, /"cpu_profiler\.c"/);
});
