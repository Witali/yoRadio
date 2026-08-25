const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const root = path.resolve(__dirname, "..");
const native = path.join(root, "idf", "esp32c3-oled-native");
const read = (...parts) => fs.readFileSync(path.join(native, ...parts), "utf8");

test("native encoder profile is optional and has conflict-safe board pins", () => {
  const defaults = read("sdkconfig.defaults");
  const encoderDefaults = read("sdkconfig.encoder.defaults");
  const kconfig = read("main", "Kconfig.projbuild");
  const source = read("main", "encoder_input.c");

  assert.match(defaults, /# CONFIG_YORADIO_ROTARY_ENCODER is not set/);
  assert.match(encoderDefaults, /CONFIG_YORADIO_ROTARY_ENCODER=y/);
  assert.match(encoderDefaults, /GPIO_A=0/);
  assert.match(encoderDefaults, /GPIO_B=1/);
  assert.match(encoderDefaults, /BUTTON_GPIO=4/);
  assert.match(kconfig, /config YORADIO_ROTARY_ENCODER_STEPS[\s\S]*range 1 4/);
  assert.match(source, /pin_is_reserved[\s\S]*BOARD_OLED_SDA[\s\S]*BOARD_AUDIO_LEFT_DATA[\s\S]*BOARD_BOOT_BUTTON/);
  assert.match(source, /CONFIG_YORADIO_AUDIO_LEVEL_LED_GPIO/);
});

test("native encoder uses the proven Arduino quadrature state table", () => {
  const source = read("main", "encoder_input.c");
  const match = source.match(/s_transition_table\[16\] = \{([\s\S]*?)\};/);
  assert.ok(match);
  const table = [...match[1].matchAll(/-?\d+/g)].map(([value]) => Number(value));
  assert.deepEqual(table, [0, -1, 1, 0, 1, 0, 0, -1, -1, 0, 0, 1, 0, 1, -1, 0]);

  function movement(sequence) {
    let previous = 3;
    return sequence.reduce((sum, phase) => {
      const delta = table[(previous << 2) | phase];
      previous = phase;
      return sum + delta;
    }, 0);
  }
  assert.equal(movement([1, 0, 2, 3]), 4);
  assert.equal(movement([2, 0, 1, 3]), -4);
});

test("encoder ISR only queues work and task callbacks control radio", () => {
  const encoder = read("main", "encoder_input.c");
  const app = read("main", "app_main.c");

  const phaseIsr = encoder.match(/encoder_phase_isr[\s\S]*?^}/m)?.[0] || "";
  assert.match(phaseIsr, /xQueueSendFromISR/);
  assert.doesNotMatch(phaseIsr, /native_audio_output|radio_control/);
  assert.match(encoder, /xQueueReceive\(s_event_queue/);
  assert.match(encoder, /runtime_settings_get_encoder_acceleration/);
  assert.match(encoder, /BOARD_TASK_STACK_ROTARY_ENCODER/);
  assert.match(app, /encoder_rotate_volume[\s\S]*native_audio_output_set_volume/);
  assert.match(app, /encoder_toggle_playback[\s\S]*radio_control_toggle/);
  assert.match(app, /encoder_input_start\(&encoder_callbacks\)/);
});

test("encoder acceleration is persisted and exposed only for enabled hardware", () => {
  const settings = read("main", "runtime_settings.c");
  const websocket = read("main", "websocket_service.c");

  assert.match(settings, /SETTINGS_NVS_ENCODER_ACCELERATION "encacc"/);
  assert.match(settings, /nvs_get_u16\(handle, SETTINGS_NVS_ENCODER_ACCELERATION/);
  assert.match(settings, /save_u16\(SETTINGS_NVS_ENCODER_ACCELERATION/);
  assert.match(websocket, /runtime_settings_get_encoder_acceleration\(\)/);
  assert.match(websocket, /strcmp\(command, "encacc"\)/);
  assert.match(websocket, /runtime_settings_set_encoder_acceleration/);
  assert.match(websocket, /#ifdef CONFIG_YORADIO_ROTARY_ENCODER[\s\S]*"\\"group_encoder\\","/);
});
