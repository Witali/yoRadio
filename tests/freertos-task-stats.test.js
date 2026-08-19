const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const root = path.resolve(__dirname, "..");
const telnet = fs.readFileSync(
  path.join(root, "yoRadio", "src", "core", "telnet.cpp"),
  "utf8",
);

test("serial and Telnet consoles expose interval FreeRTOS task loads", () => {
  assert.match(telnet, /#include "freertos_stats\.h"/);
  assert.match(telnet, /strcmp\(str, "sys\.tasks"\)/);
  assert.match(telnet, /printRunningTasks\(clients\[clientId\]\)/);
  assert.match(telnet, /printRunningTasks\(Serial\)/);

  const command = telnet.indexOf('strcmp(str, "sys.tasks")');
  const connectedOnly = telnet.indexOf("if(network.status == CONNECTED)");
  assert.ok(command >= 0 && command < connectedOnly,
    "CPU stats must remain available in station, AP, and SD modes");
});
