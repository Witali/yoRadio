const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

test("the radio collector has an isolated setup script", () => {
  const setup = fs.readFileSync(
    path.join(__dirname, "..", "tools", "radio_stream_collector", "setup.ps1"),
    "utf8",
  );
  const firmwareSetup = fs.readFileSync(
    path.join(__dirname, "..", "idf", "esp32-cyd2usb-minimal", "setup.ps1"),
    "utf8",
  );

  assert.match(setup, /requirements-radio-streams\.txt/);
  assert.match(setup, /function Resolve-PythonExecutable/);
  assert.match(setup, /pythoncore-\*/);
  assert.match(setup, /-m venv \$venvRoot/);
  assert.match(setup, /-m pip install --disable-pip-version-check -r \$requirements/);
  assert.match(setup, /\$collector --self-test/);
  assert.doesNotMatch(firmwareSetup, /requirements-radio-streams\.txt/);
});
