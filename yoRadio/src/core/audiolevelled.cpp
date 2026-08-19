#include "Arduino.h"
#include "audiolevelled.h"
#include "options.h"
#include "config.h"
#include "player.h"

namespace audioLevelLed {

#if AUDIO_LEVEL_LED_PIN != 255
namespace {
uint32_t lastUpdateMs = 0;
uint8_t envelope = 0;
uint8_t lastBrightness = UINT8_MAX;
bool pwmReady = false;

uint8_t peakLevel() {
  if(!player.isRunning() || config.vuThreshold == 0) return 0;

  const uint16_t packed = player.get_VUlevel(255);
  const uint8_t leftInverse = static_cast<uint8_t>(packed >> 8);
  const uint8_t rightInverse = static_cast<uint8_t>(packed);
  const uint8_t strongestInverse = min(leftInverse, rightInverse);
  return static_cast<uint8_t>(255U - strongestInverse);
}

void writeEnvelope() {
  if(!pwmReady) return;
  const uint8_t brightness = static_cast<uint8_t>(
      (static_cast<uint16_t>(envelope) * AUDIO_LEVEL_LED_MAX_BRIGHTNESS + 127U) / 255U);
  if(brightness == lastBrightness) return;

  lastBrightness = brightness;
  ledcWrite(AUDIO_LEVEL_LED_PIN, 255U - brightness);
}
} // namespace
#endif

void begin() {
#if AUDIO_LEVEL_LED_PIN != 255
  pwmReady = ledcAttach(AUDIO_LEVEL_LED_PIN, AUDIO_LEVEL_LED_PWM_HZ, 8);
  if(!pwmReady) {
    Serial.println("##ERROR#:\tAudio level LED PWM initialization failed");
    return;
  }
  envelope = 0;
  lastBrightness = UINT8_MAX;
  writeEnvelope();
#endif
}

void loop() {
#if AUDIO_LEVEL_LED_PIN != 255
  const uint32_t now = millis();
  if(now - lastUpdateMs < AUDIO_LEVEL_LED_UPDATE_MS) return;
  lastUpdateMs = now;

  const uint8_t target = peakLevel();
  if(target >= envelope) {
    envelope = target;
  } else if(envelope > AUDIO_LEVEL_LED_DECAY_STEP) {
    envelope -= AUDIO_LEVEL_LED_DECAY_STEP;
  } else {
    envelope = 0;
  }
  writeEnvelope();
#endif
}

} // namespace audioLevelLed
