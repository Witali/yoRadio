const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const root = path.join(__dirname, "..");

function read(...parts) {
  return fs.readFileSync(path.join(root, ...parts), "utf8");
}

test("audio processing runs in a dedicated task on core 1", () => {
  const player = read("yoRadio", "src", "core", "player.cpp");

  assert.match(player, /#define PLAYER_TASK_CORE_ID 1/);
  assert.match(player, /#define PLAYER_TASK_PRIORITY 2/);
  assert.match(player, /#define PLAYER_TASK_STACK_SIZE 1024 \* 8/);
  assert.match(player, /static StaticTask_t playerTaskControlBlock/);
  assert.match(player, /static StackType_t playerTaskStack\[PLAYER_TASK_STACK_SIZE\]/);
  assert.match(player, /xTaskCreateStaticPinnedToCore\([\s\S]*loopPlayerTask[\s\S]*"AudioTask"/);
  assert.match(player, /setConnectionTaskEnabled\(false\)/);
  assert.match(player, /player\.loop\(\);[\s\S]*vTaskDelay\(PLAYER_TASK_DELAY\)/);
  assert.match(player, /##AUDIO\.TASK#: core=%d priority=%u loops=%lu max_loop_us=%lu stack_free=%u/);
});

test("dedicated audio task performs bounded connections without a helper task", () => {
  const audioHeader = read("yoRadio", "src", "audioI2S", "AudioEx.h");
  const audioSource = read("yoRadio", "src", "audioI2S", "Audio.cpp");

  assert.match(audioHeader, /void setConnectionTaskEnabled\(bool enabled\)/);
  assert.match(audioSource, /!config\.store\.watchdog \|\| !_connectionTaskEnabled/);
  assert.match(audioSource, /connect\(h_host, port, m_f_ssl \? m_timeout_ms_ssl : m_timeout_ms\)/);
});

test("Arduino loop uses player only as a task-creation fallback", () => {
  const main = read("yoRadio", "src", "main.cpp");
  const loopBody = main.match(/void loop\(\) \{([\s\S]*?)\n\}/)?.[1];

  assert.ok(loopBody, "Arduino loop body is missing");
  assert.match(main, /player\.startTask\(\)/);
  assert.match(loopBody, /if\(!player\.taskRunning\(\)\) player\.loop\(\)/);
  assert.doesNotMatch(loopBody, /\n\s*player\.loop\(\);/);
});

test("network and display tasks remain isolated on core 0", () => {
  const asyncHeader = read("yoRadio", "src", "AsyncWebServer", "AsyncTCP.h");
  const asyncSource = read("yoRadio", "src", "AsyncWebServer", "AsyncTCP.cpp");
  const display = read("yoRadio", "src", "core", "display.cpp");

  assert.match(asyncHeader, /#define CONFIG_ASYNC_TCP_RUNNING_CORE 0/);
  assert.match(asyncSource, /##\[TASK\]# async_tcp core=%d/);
  assert.match(display, /#define\s+DSP_TASK_CORE_ID\s+0/);
  assert.match(display, /##\[TASK\]# DspTask core=%d/);
});

test("audio logs cross cores through a static non-blocking Telnet queue", () => {
  const telnetHeader = read("yoRadio", "src", "core", "telnet.h");
  const telnetSource = read("yoRadio", "src", "core", "telnet.cpp");

  assert.match(telnetHeader, /StaticQueue_t _logQueueControl/);
  assert.match(telnetHeader, /_logQueueStorage\[TELNET_LOG_QUEUE_LENGTH \* TELNET_LOG_ITEM_SIZE\]/);
  assert.match(telnetSource, /xQueueCreateStatic/);
  assert.match(telnetSource, /xQueueSend\(_logQueue, item, 0\)/);
  assert.match(telnetSource, /void Telnet::loop\(\) \{\s*drainLogQueue\(\)/);
});
