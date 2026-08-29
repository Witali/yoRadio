const assert = require("node:assert/strict");
const crypto = require("node:crypto");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const root = path.resolve(__dirname, "..");
const firmwareDirectory = path.join(
  root,
  "firmware",
  "development",
  "esp32c3-oled-native-production",
);
const binaryPath = path.join(firmwareDirectory, "app.bin");
const manifestPath = path.join(firmwareDirectory, "manifest.md");
const changelogPath = path.join(root, "firmware", "CHANGELOG.md");
const readmePath = path.join(root, "firmware", "README.md");

test("the ESP32-C3 development image is identified by its manifest", () => {
  const binary = fs.readFileSync(binaryPath);
  const manifest = fs.readFileSync(manifestPath, "utf8");
  const hash = crypto.createHash("sha256").update(binary).digest("hex");
  const formattedSize = binary.length.toLocaleString("en-US");

  assert.ok(manifest.includes(`| \`app.bin\` | ${formattedSize} |`));
  assert.match(manifest.toLowerCase(), new RegExp(hash));
  assert.match(manifest, /Flash offset[\s\S]*`0x10000`/);
  assert.match(manifest, /Embedded source revision: `d595dac`/);
});

test("the ESP32-C3 development image is described in the changelog", () => {
  const changelog = fs.readFileSync(changelogPath, "utf8");

  assert.match(changelog, /## Development — 2026-08-29/);
  assert.match(
    changelog,
    /development\/esp32c3-oled-native-production\/app\.bin/,
  );
  assert.match(
    changelog,
    /development\/esp32c3-oled-native-production\/manifest\.md/,
  );
  assert.match(changelog, /SNTP server-name lifetime/);
  assert.match(changelog, /MP3, AAC and Ogg streams near 320 kbit\/s/);
});

test("firmware archive policy requires manifest and changelog updates", () => {
  const readme = fs.readFileSync(readmePath, "utf8");

  assert.match(
    readme,
    /Whenever a development `app\.bin` is replaced,[\s\S]*update its `manifest\.md`[\s\S]*`CHANGELOG\.md` in the same commit/,
  );
});
