const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

test("project setup installs the radio collector Python requirements", () => {
  const setup = fs.readFileSync(
    path.join(__dirname, "..", "idf", "esp32-cyd2usb-minimal", "setup.ps1"),
    "utf8",
  );

  assert.match(setup, /requirements-radio-streams\.txt/);
  assert.match(setup, /-m pip install --disable-pip-version-check -r \$radioCollectorRequirements/);
  assert.match(setup, /Get-FileHash[^\n]*\$radioCollectorRequirements[^\n]*SHA256/);
  assert.match(setup, /radio-streams-requirements\.sha256/);
});
