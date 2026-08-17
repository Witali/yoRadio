const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const source = fs.readFileSync(
  path.join(__dirname, "..", "yoRadio", "src", "audioI2S", "Audio.cpp"),
  "utf8",
);

test("audio streams retry when a connected host sends no HTTP header", () => {
  assert.match(
    source,
    /parseHttpResponseHeader[\s\S]*maxHeaderRetries = 2[\s\S]*_client->stop\(\)[\s\S]*httpPrint\(m_lastHost\)/,
  );
  assert.match(
    source,
    /_client->available\(\) == 0[\s\S]*m_headerWaitStartedMs[\s\S]*HEADER_TIMEOUT/,
  );
});

test("header retry state is cleared for a new stream and a valid response", () => {
  assert.match(
    source,
    /setDefaults[\s\S]*m_headerWaitStartedMs = 0[\s\S]*m_headerRetryCount = 0/,
  );
  assert.match(
    source,
    /parseHttpResponseHeader[\s\S]*_client->available\(\) == 0[\s\S]*m_headerWaitStartedMs = 0;[\s\S]*m_headerRetryCount = 0;[\s\S]*char rhl/,
  );
});
