const assert = require("node:assert/strict");
const crypto = require("node:crypto");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const root = path.resolve(__dirname, "..");
const documentPath = path.join(root, "docs", "ESP32-C3-0.42-OLED.md");
const schematicPath = path.join(
  root,
  "docs",
  "schematics",
  "ESP32-C3-0.42-OLED-schematic.pdf",
);

test("ESP32-C3 board documentation covers the supported hardware", () => {
  const document = fs.readFileSync(documentPath, "utf8");

  assert.match(document, /OLED SDA \| 5/);
  assert.match(document, /OLED SCL \| 6/);
  assert.match(document, /BOOT \/ radio control \| 9/);
  assert.match(document, /Right PDM audio \| 3/);
  assert.match(document, /Left PDM audio \| 10/);
  assert.match(document, /GPIO10 for the left[\s\S]*GPIO3 for the right/);
  assert.match(document, /R1 1 kOhm[\s\S]*R2 1 kOhm/);
  assert.match(document, /C1 4\.7 nF[\s\S]*C2 4\.7 nF/);
  assert.match(document, /C3 1\.\.4\.7 uF/);
  assert.match(document, /R3 \| 47 to 100 kOhm/);
  assert.match(document, /Never connect a[\s\S]*low-impedance load directly/);
  assert.match(document, /no fitted or\s+usable WS2812 LED/);
  assert.match(document, /github\.com\/01Space\/ESP32-C3-0\.42LCD/);
  assert.match(document, /michiel\.vanderwulp\.be\/domotica\/Modules\/ESP32-C3-SuperMini-OLED/);
  assert.match(document, /WiFi\.softAP/);
  assert.match(document, /schematics\/ESP32-C3-0\.42-OLED-schematic\.pdf/);
});

test("the checked-in ESP32-C3 schematic is a PDF", () => {
  const schematic = fs.readFileSync(schematicPath);

  assert.equal(schematic.subarray(0, 5).toString("ascii"), "%PDF-");
  assert.equal(
    crypto.createHash("sha256").update(schematic).digest("hex"),
    "7be47a67c62b214e4954681fcfc195ad275532ba8e831e67387c4b3c17de1203",
  );
});
