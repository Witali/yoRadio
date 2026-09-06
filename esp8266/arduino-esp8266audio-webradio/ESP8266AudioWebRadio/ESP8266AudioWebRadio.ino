/*
  WebRadio firmware for ESP8266.

  The streaming lifecycle and fixed preallocation model are derived from the
  ESP8266Audio WebRadio and StreamMP3FromHTTP examples by Earle F. Philhower,
  III. ESP8266Audio is licensed under GPL-3.0-or-later. This project is also
  distributed under GPL-3.0-or-later; see the repository LICENSE file.
*/

#include <Arduino.h>
#include <EEPROM.h>
#include <ESP8266WebServer.h>
#include <ESP8266WiFi.h>

#include "AudioFileSourceBuffer.h"
#include "AudioFileSourceICYStream.h"
#include "AudioGeneratorAAC.h"
#include "AudioGeneratorMP3.h"
#include "AudioOutputI2SNoDAC.h"

namespace {

constexpr uint32_t kSettingsMagic = 0x59415245UL;  // "YARE"
constexpr uint16_t kSettingsVersion = 1;
constexpr uint32_t kWifiConnectTimeoutMs = 15000;
constexpr uint32_t kRetryDelayMs = 2500;
constexpr uint32_t kButtonDebounceMs = 35;
constexpr size_t kStreamBufferBytes = 5 * 1024;
constexpr size_t kCodecWorkspaceBytes = 29192;
constexpr uint8_t kBootButtonPin = 0;
constexpr char kAccessPointName[] = "WebRadio";

enum class Codec : uint8_t { Mp3 = 0, Aac = 1 };

struct Settings {
  uint32_t magic;
  uint16_t version;
  uint8_t codec;
  uint8_t volume;
  char ssid[33];
  char password[65];
  char url[192];
  uint32_t checksum;
};

ESP8266WebServer server(80);
Settings settings{};
AudioFileSourceICYStream *source = nullptr;
AudioFileSourceBuffer *streamBuffer = nullptr;
AudioGenerator *decoder = nullptr;
AudioOutputI2SNoDAC *audioOutput = nullptr;
void *streamStorage = nullptr;
void *codecStorage = nullptr;

char title[128] = "Stopped";
char playerStatus[96] = "Stopped";
bool accessPointMode = false;
bool startRequested = false;
bool stopRequested = false;
bool userStopped = true;
uint32_t retryAt = 0;
uint32_t restartAt = 0;

const char kPlayerPage[] PROGMEM = R"HTML(<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>WebRadio</title><style>
body{font:16px system-ui;background:#111;color:#f0c83c;max-width:720px;margin:auto;padding:24px}input,select,button{font:inherit;padding:10px;margin:5px 0;background:#242424;color:#f0c83c;border:1px solid #f0c83c;border-radius:6px}input[type=url]{box-sizing:border-box;width:100%}button:disabled{opacity:.45}small{color:#bbb}#title{overflow:hidden;white-space:nowrap;text-overflow:ellipsis}
</style></head><body><h1>WebRadio</h1><h2 id="title">Stopped</h2><p id="state">Loading...</p>
<form id="play"><label>HTTP stream URL</label><input id="url" name="url" type="url" maxlength="191" required>
<select id="codec" name="codec"><option value="mp3">MP3</option><option value="aac">AAC</option></select>
<button id="playButton">Play</button> <button id="stopButton" type="button">Stop</button></form>
<label>Volume <span id="volumeText"></span></label><input id="volume" type="range" min="0" max="150">
<p><small>Reference firmware using ESP8266Audio ICY stream, fixed buffer and NoDAC I2S-PDM on GPIO3.</small></p>
<script>
const q=s=>document.querySelector(s);let first=true;
async function call(path,params={}){let u=new URL(path,location.href);Object.entries(params).forEach(x=>u.searchParams.set(...x));let r=await fetch(u,{cache:'no-store'});if(!r.ok)throw Error(await r.text());return r.json()}
async function refresh(){try{let s=await call('/api/status');q('#title').textContent=s.title;q('#state').textContent=`${s.status} | ${s.codec.toUpperCase()} | heap ${s.free_heap} | RSSI ${s.rssi}`;if(first){q('#url').value=s.url;q('#codec').value=s.codec;q('#volume').value=s.volume;first=false}q('#volumeText').textContent=s.volume;q('#playButton').disabled=s.pending;q('#stopButton').disabled=s.pending}catch(e){q('#state').textContent=e.message}setTimeout(refresh,2000)}
q('#play').onsubmit=async e=>{e.preventDefault();q('#playButton').disabled=true;await call('/api/play',{url:q('#url').value,codec:q('#codec').value});first=true};
q('#stopButton').onclick=async()=>{q('#stopButton').disabled=true;await call('/api/stop')};
q('#volume').onchange=async e=>{await call('/api/volume',{value:e.target.value});first=true};refresh();
</script></body></html>)HTML";

const char kWifiPage[] PROGMEM = R"HTML(<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>WebRadio</title><style>body{font:16px system-ui;background:#111;color:#f0c83c;max-width:560px;margin:auto;padding:24px}input,button{box-sizing:border-box;width:100%;font:inherit;padding:12px;margin:6px 0;background:#242424;color:#f0c83c;border:1px solid #f0c83c;border-radius:6px}</style></head>
<body><h1>WebRadio</h1><p>Connect this board to a 2.4 GHz access point.</p><form action="/api/wifi" method="get">
<label>SSID</label><input name="ssid" maxlength="32" required><label>Password</label><input name="password" type="password" maxlength="64"><button>Save and restart</button></form></body></html>)HTML";

uint32_t checksum(const Settings &value) {
  const uint8_t *bytes = reinterpret_cast<const uint8_t *>(&value);
  uint32_t hash = 2166136261UL;
  for (size_t i = 0; i < offsetof(Settings, checksum); ++i) {
    hash ^= bytes[i];
    hash *= 16777619UL;
  }
  return hash;
}

void defaults() {
  memset(&settings, 0, sizeof(settings));
  settings.magic = kSettingsMagic;
  settings.version = kSettingsVersion;
  settings.codec = static_cast<uint8_t>(Codec::Mp3);
  settings.volume = 100;
  settings.checksum = checksum(settings);
}

void loadSettings() {
  EEPROM.begin(sizeof(Settings));
  EEPROM.get(0, settings);
  EEPROM.end();
  if (settings.magic != kSettingsMagic ||
      settings.version != kSettingsVersion ||
      settings.checksum != checksum(settings) || settings.volume > 150 ||
      settings.codec > static_cast<uint8_t>(Codec::Aac)) {
    defaults();
  }
  settings.ssid[sizeof(settings.ssid) - 1] = 0;
  settings.password[sizeof(settings.password) - 1] = 0;
  settings.url[sizeof(settings.url) - 1] = 0;
}

void saveSettings() {
  settings.checksum = checksum(settings);
  EEPROM.begin(sizeof(Settings));
  EEPROM.put(0, settings);
  EEPROM.commit();
  EEPROM.end();
}

const char *codecName() {
  return settings.codec == static_cast<uint8_t>(Codec::Aac) ? "aac" : "mp3";
}

void copyFlashString(char *destination, size_t capacity, const char *source) {
  strncpy_P(destination, source, capacity - 1);
  destination[capacity - 1] = 0;
}

void metadataCallback(void *, const char *type, bool, const char *value) {
  if (strstr_P(type, PSTR("Title"))) copyFlashString(title, sizeof(title), value);
}

void statusCallback(void *, int code, const char *message) {
  copyFlashString(playerStatus, sizeof(playerStatus), message);
  Serial.printf_P(PSTR("audio status %d: %s\n"), code, playerStatus);
}

void stopPlaying(bool userRequest) {
  if (decoder) {
    decoder->stop();
    delete decoder;
    decoder = nullptr;
  }
  if (streamBuffer) {
    streamBuffer->close();
    delete streamBuffer;
    streamBuffer = nullptr;
  }
  if (source) {
    source->close();
    delete source;
    source = nullptr;
  }
  userStopped = userRequest;
  retryAt = 0;
  strlcpy(playerStatus, "Stopped", sizeof(playerStatus));
  strlcpy(title, "Stopped", sizeof(title));
}

void startPlaying() {
  startRequested = false;
  stopPlaying(false);
  if (accessPointMode || !settings.url[0]) {
    strlcpy(playerStatus, "No stream URL", sizeof(playerStatus));
    userStopped = true;
    return;
  }

  Serial.printf_P(PSTR("Starting %s stream: %s; heap=%u\n"), codecName(),
                  settings.url, ESP.getFreeHeap());
  source = new AudioFileSourceICYStream(settings.url);
  if (source) source->RegisterMetadataCB(metadataCallback, nullptr);
  if (source)
    streamBuffer = new AudioFileSourceBuffer(source, streamStorage,
                                             kStreamBufferBytes);
  if (streamBuffer) streamBuffer->RegisterStatusCB(statusCallback, nullptr);

  if (settings.codec == static_cast<uint8_t>(Codec::Aac)) {
    decoder = new AudioGeneratorAAC(codecStorage, kCodecWorkspaceBytes);
  } else {
    decoder = new AudioGeneratorMP3(codecStorage, kCodecWorkspaceBytes);
  }
  if (decoder) decoder->RegisterStatusCB(statusCallback, nullptr);

  if (!source || !streamBuffer || !decoder ||
      !decoder->begin(streamBuffer, audioOutput)) {
    stopPlaying(false);
    strlcpy(playerStatus, "Unable to start stream", sizeof(playerStatus));
    retryAt = millis() + kRetryDelayMs;
    return;
  }
  audioOutput->SetGain(static_cast<float>(settings.volume) / 100.0f);
  strlcpy(playerStatus, "Playing", sizeof(playerStatus));
  userStopped = false;
}

size_t appendJsonString(char *output, size_t capacity, size_t offset,
                        const char *input) {
  if (offset < capacity) output[offset++] = '"';
  while (*input && offset + 2 < capacity) {
    const uint8_t ch = static_cast<uint8_t>(*input++);
    if (ch == '"' || ch == '\\') {
      output[offset++] = '\\';
      output[offset++] = static_cast<char>(ch);
    } else if (ch >= 0x20) {
      output[offset++] = static_cast<char>(ch);
    }
  }
  if (offset < capacity) output[offset++] = '"';
  if (offset < capacity) output[offset] = 0;
  return offset;
}

void sendStatus() {
  char payload[768];
  size_t used = strlcpy(payload, "{\"playing\":", sizeof(payload));
  used += strlcpy(payload + used,
                  decoder && decoder->isRunning() ? "true,\"pending\":"
                                                  : "false,\"pending\":",
                  sizeof(payload) - used);
  used += strlcpy(payload + used,
                  startRequested || stopRequested ? "true,\"title\":"
                                                  : "false,\"title\":",
                  sizeof(payload) - used);
  used = appendJsonString(payload, sizeof(payload), used, title);
  used += strlcpy(payload + used, ",\"status\":", sizeof(payload) - used);
  used = appendJsonString(payload, sizeof(payload), used, playerStatus);
  used += strlcpy(payload + used, ",\"url\":", sizeof(payload) - used);
  used = appendJsonString(payload, sizeof(payload), used, settings.url);
  snprintf(payload + used, sizeof(payload) - used,
           ",\"codec\":\"%s\",\"volume\":%u,\"free_heap\":%u,"
           "\"rssi\":%d}",
           codecName(), settings.volume, ESP.getFreeHeap(), WiFi.RSSI());
  server.sendHeader(F("Cache-Control"), F("no-store"));
  server.send(200, F("application/json; charset=utf-8"), payload);
}

void sendAccepted() {
  server.sendHeader(F("Cache-Control"), F("no-store"));
  server.send(202, F("application/json"), F("{\"accepted\":true}"));
}

void setupWebServer() {
  server.on("/", HTTP_GET, []() {
    server.sendHeader(F("Cache-Control"), F("no-store"));
    server.send_P(200, PSTR("text/html; charset=utf-8"),
                  accessPointMode ? kWifiPage : kPlayerPage);
  });
  server.on("/api/status", HTTP_GET, sendStatus);
  server.on("/api/play", HTTP_GET, []() {
    if (accessPointMode) {
      server.send(409, F("text/plain"), F("Wi-Fi setup mode"));
      return;
    }
    if (server.hasArg("url")) {
      server.arg("url").toCharArray(settings.url, sizeof(settings.url));
    }
    if (!settings.url[0]) {
      server.send(400, F("text/plain"), F("Missing stream URL"));
      return;
    }
    if (server.arg("codec") == "aac")
      settings.codec = static_cast<uint8_t>(Codec::Aac);
    else if (server.hasArg("codec"))
      settings.codec = static_cast<uint8_t>(Codec::Mp3);
    saveSettings();
    startRequested = true;
    stopRequested = false;
    sendAccepted();
  });
  server.on("/api/stop", HTTP_GET, []() {
    stopRequested = true;
    startRequested = false;
    sendAccepted();
  });
  server.on("/api/volume", HTTP_GET, []() {
    if (!server.hasArg("value")) {
      server.send(400, F("text/plain"), F("Missing volume"));
      return;
    }
    settings.volume = constrain(server.arg("value").toInt(), 0, 150);
    if (audioOutput)
      audioOutput->SetGain(static_cast<float>(settings.volume) / 100.0f);
    saveSettings();
    sendStatus();
  });
  server.on("/api/wifi", HTTP_GET, []() {
    if (!server.hasArg("ssid")) {
      server.send(400, F("text/plain"), F("Missing SSID"));
      return;
    }
    server.arg("ssid").toCharArray(settings.ssid, sizeof(settings.ssid));
    server.arg("password").toCharArray(settings.password,
                                        sizeof(settings.password));
    saveSettings();
    server.send(200, F("text/plain"), F("Saved. Restarting..."));
    restartAt = millis() + 750;
  });
  server.onNotFound([]() { server.send(404, F("text/plain"), F("Not found")); });
  server.begin();
}

void connectWifi() {
  WiFi.persistent(false);
  WiFi.mode(WIFI_STA);
  WiFi.setAutoReconnect(true);
  WiFi.hostname("webradio");
  if (settings.ssid[0])
    WiFi.begin(settings.ssid, settings.password);
  else
    WiFi.begin();

  const uint32_t started = millis();
  while (WiFi.status() != WL_CONNECTED &&
         millis() - started < kWifiConnectTimeoutMs) {
    delay(100);
  }
  if (WiFi.status() == WL_CONNECTED) {
    WiFi.setSleepMode(WIFI_NONE_SLEEP);
    Serial.printf_P(PSTR("Wi-Fi connected: %s, http://%s/\n"),
                    WiFi.SSID().c_str(), WiFi.localIP().toString().c_str());
    return;
  }

  WiFi.disconnect();
  WiFi.mode(WIFI_AP);
  accessPointMode = WiFi.softAP(kAccessPointName);
  Serial.printf_P(PSTR("Setup AP: %s, http://%s/\n"), kAccessPointName,
                  WiFi.softAPIP().toString().c_str());
}

void pollButton() {
  static bool rawPressed = false;
  static bool stablePressed = false;
  static uint32_t changedAt = 0;
  const bool pressed = digitalRead(kBootButtonPin) == LOW;
  if (pressed != rawPressed) {
    rawPressed = pressed;
    changedAt = millis();
  }
  if (pressed == stablePressed || millis() - changedAt < kButtonDebounceMs)
    return;
  stablePressed = pressed;
  if (stablePressed || accessPointMode) return;

  if (decoder && decoder->isRunning()) {
    stopRequested = true;
    startRequested = false;
  } else if (settings.url[0]) {
    startRequested = true;
    stopRequested = false;
  }
}

}  // namespace

void setup() {
  pinMode(kBootButtonPin, INPUT_PULLUP);
  Serial.begin(115200);
  delay(200);
  Serial.println(F("\nWebRadio"));

  streamStorage = malloc(kStreamBufferBytes);
  codecStorage = malloc(kCodecWorkspaceBytes);
  if (!streamStorage || !codecStorage) {
    Serial.printf_P(PSTR("FATAL: cannot reserve %u audio bytes; heap=%u\n"),
                    kStreamBufferBytes + kCodecWorkspaceBytes,
                    ESP.getFreeHeap());
    while (true) delay(1000);
  }

  loadSettings();
  audioOutput = new AudioOutputI2SNoDAC();
  if (!audioOutput) {
    Serial.println(F("FATAL: cannot allocate NoDAC output"));
    while (true) delay(1000);
  }
  audioOutput->SetGain(static_cast<float>(settings.volume) / 100.0f);
  audioLogger = &Serial;

  connectWifi();
  setupWebServer();
  if (!accessPointMode && settings.url[0]) startRequested = true;
}

void loop() {
  server.handleClient();
  pollButton();

  if (restartAt && static_cast<int32_t>(millis() - restartAt) >= 0) {
    ESP.restart();
  }
  if (stopRequested) {
    stopRequested = false;
    stopPlaying(true);
  }
  if (startRequested) startPlaying();

  if (decoder && decoder->isRunning()) {
    strlcpy(playerStatus, "Playing", sizeof(playerStatus));
    if (!decoder->loop()) {
      stopPlaying(false);
      strlcpy(playerStatus, "Stream ended; retrying", sizeof(playerStatus));
      retryAt = millis() + kRetryDelayMs;
    }
  } else if (!userStopped && retryAt &&
             static_cast<int32_t>(millis() - retryAt) >= 0) {
    retryAt = 0;
    startRequested = true;
  }
  delay(0);
}
