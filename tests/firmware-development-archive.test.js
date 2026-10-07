const assert = require("node:assert/strict");
const crypto = require("node:crypto");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const root = path.resolve(__dirname, "..");
const developmentRoot = path.join(root, "firmware", "development");
const changelogPath = path.join(root, "firmware", "CHANGELOG.md");
const readmePath = path.join(root, "firmware", "README.md");
const artifacts = [
  ["app.bin", "0x10000"],
  ["full.bin", "0x0"],
  ["bootloader.bin", "0x0"],
  ["partitions.bin", "0x8000"],
  ["boot_app0.bin", "0xe000"],
];
const variants = [
  "esp32c3-oled-native-production",
  "esp32c3-oled-native-development",
];

for (const variant of variants) {
  test(`${variant} artifacts match their manifest`, () => {
    const firmwareDirectory = path.join(developmentRoot, variant);
    const manifest = fs.readFileSync(
      path.join(firmwareDirectory, "manifest.md"),
      "utf8",
    );

    const app = fs.readFileSync(path.join(firmwareDirectory, "app.bin"));
    const version = app.subarray(48, 80).toString("utf8").split("\0")[0];
    const embeddedVersion = manifest.match(/Embedded version: `([^`]+)`/);
    const embeddedRevision = manifest.match(/Embedded source revision: `([0-9a-f]+)`/i);
    assert.ok(embeddedVersion || embeddedRevision, "manifest must identify its source");
    if (embeddedVersion) assert.equal(embeddedVersion[1], version);
    if (embeddedRevision) assert.ok(version.includes(`-g${embeddedRevision[1]}`));

    for (const [name, offset] of artifacts) {
      const binary = fs.readFileSync(path.join(firmwareDirectory, name));
      const hash = crypto.createHash("sha256").update(binary).digest("hex");
      const row = manifest.split(/\r?\n/).find(line => line.startsWith(`| \`${name}\` |`));
      assert.ok(row, `missing manifest row for ${name}`);
      const cells = row.split("|").map(cell => cell.trim());
      assert.equal(Number(cells[2].replaceAll(",", "")), binary.length);
      assert.equal(cells[3], `\`${offset}\``);
      assert.equal(cells[4].toLowerCase(), `\`${hash}\``);
    }

    assert.equal(
      fs.statSync(path.join(firmwareDirectory, "full.bin")).size,
      4 * 1024 * 1024,
    );
  });
}

test("both ESP32-C3 artifact sets are described in the changelog", () => {
  const changelog = fs.readFileSync(changelogPath, "utf8");

  assert.match(changelog, /## Development — 2026-08-29/);
  for (const variant of variants) {
    assert.ok(changelog.includes(`development/${variant}/`));
  }
  assert.match(changelog, /SNTP server-name lifetime/);
  assert.match(changelog, /MP3, AAC and Ogg streams near 320 kbit\/s/);
});

test("firmware archive policy requires manifest and changelog updates", () => {
  const readme = fs.readFileSync(readmePath, "utf8");

  assert.match(
    readme,
    /Whenever a development `app\.bin` is replaced,[\s\S]*update its `manifest\.md`[\s\S]*`CHANGELOG\.md` in the same commit/,
  );
  assert.match(readme, /`full\.bin` — merged 4 MiB image/);
  assert.match(readme, /combined image deliberately does not contain user SPIFFS data/);
});
