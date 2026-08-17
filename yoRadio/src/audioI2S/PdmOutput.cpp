#include "../core/options.h"

#if I2S_INTERNAL && I2S_INTERNAL_OUTPUT == AUDIO_OUTPUT_PDM

#include "PdmOutput.h"

#include <esp_arduino_version.h>

#if ESP_ARDUINO_VERSION_MAJOR < 3
#error I2S PDM output requires ESP32 Arduino core 3.x or newer
#endif

#include <driver/gpio.h>
#include <driver/i2s_pdm.h>
#include <limits.h>

namespace {

// The network, decoder and display share the Arduino task.  Keep enough PCM
// queued in hardware to ride through an occasional long Wi-Fi/display pass
// without replacing part of the waveform with silence.  At 44.1 kHz this is
// about 93 ms, close to the input preroll and still short enough for controls.
constexpr size_t kDmaSamples = 512;
constexpr uint32_t kDmaDescriptors = 8;
constexpr uint32_t kBiasRampMs = 100;
constexpr uint32_t kBiasSettleMs = 2;

i2s_chan_handle_t outputChannel = nullptr;
uint8_t outputPort = I2S_NUM_0;
uint8_t outputPin = I2S_PDM_DOUT;
uint32_t outputSampleRate = 0;
bool outputRunning = false;
size_t bufferedSamples = 0;
int16_t sampleBuffer[kDmaSamples] = {};

uint32_t rampSamples(uint32_t sampleRate) {
  const uint64_t scaled = static_cast<uint64_t>(sampleRate) * kBiasRampMs;
  const uint32_t samples = static_cast<uint32_t>((scaled + 999U) / 1000U);
  return samples < 2U ? 2U : samples;
}

int16_t rampSample(uint32_t index, uint32_t count, bool rampUp) {
  const int32_t offset = static_cast<int32_t>(
      (static_cast<uint64_t>(index) * 32768U) / (count - 1U));
  return static_cast<int16_t>(rampUp ? INT16_MIN + offset : -offset);
}

esp_err_t writeBlock(const int16_t *samples, size_t count) {
  if (!outputChannel || !outputRunning) return ESP_ERR_INVALID_STATE;
  size_t written = 0;
  const size_t bytes = count * sizeof(*samples);
  const esp_err_t result = i2s_channel_write(
      outputChannel, samples, bytes, &written, 1000);
  return result == ESP_OK && written == bytes ? ESP_OK :
         result == ESP_OK ? ESP_FAIL : result;
}

void holdOutputLow() {
  gpio_reset_pin(static_cast<gpio_num_t>(outputPin));
  gpio_set_direction(static_cast<gpio_num_t>(outputPin), GPIO_MODE_OUTPUT);
  gpio_set_level(static_cast<gpio_num_t>(outputPin), 0);
}

esp_err_t releaseChannel(bool rampDown) {
  esp_err_t firstError = ESP_OK;
  if (outputChannel && outputRunning && rampDown && outputSampleRate) {
    esp_err_t result = pdmOutputFlush();
    if (firstError == ESP_OK && result != ESP_OK) firstError = result;

    const uint32_t count = rampSamples(outputSampleRate);
    uint32_t index = 0;
    while (index < count) {
      const size_t chunk = min(static_cast<size_t>(count - index),
                               kDmaSamples);
      for (size_t sample = 0; sample < chunk; ++sample) {
        sampleBuffer[sample] = rampSample(index + sample, count, false);
      }
      result = writeBlock(sampleBuffer, chunk);
      if (firstError == ESP_OK && result != ESP_OK) firstError = result;
      if (result != ESP_OK) break;
      index += chunk;
    }
    const uint32_t drainMs = static_cast<uint32_t>(
        ((kDmaDescriptors + 1U) * kDmaSamples * 1000ULL +
         outputSampleRate - 1U) / outputSampleRate);
    delay(kBiasRampMs + drainMs + kBiasSettleMs);
  }

  bufferedSamples = 0;
  if (outputChannel && outputRunning) {
    const esp_err_t result = i2s_channel_disable(outputChannel);
    if (firstError == ESP_OK && result != ESP_OK) firstError = result;
    outputRunning = false;
  }
  if (outputChannel) {
    const esp_err_t result = i2s_del_channel(outputChannel);
    if (firstError == ESP_OK && result != ESP_OK) firstError = result;
    outputChannel = nullptr;
  }
  holdOutputLow();
  outputSampleRate = 0;
  return firstError;
}

}  // namespace

esp_err_t pdmOutputPrepare(uint8_t port, uint8_t dataPin) {
  if (outputChannel) {
    const esp_err_t result = releaseChannel(true);
    if (result != ESP_OK) return result;
  }
  outputPort = port;
  outputPin = dataPin;
  outputSampleRate = 0;
  bufferedSamples = 0;
  holdOutputLow();
  return ESP_OK;
}

esp_err_t pdmOutputBegin(uint8_t port, uint8_t dataPin,
                         uint32_t sampleRate) {
  if (sampleRate < 8000U || sampleRate > 48000U) {
    return ESP_ERR_INVALID_ARG;
  }
  if (outputChannel) {
    const esp_err_t result = releaseChannel(true);
    if (result != ESP_OK) return result;
  }

  outputPort = port;
  outputPin = dataPin;
  outputSampleRate = sampleRate;
  bufferedSamples = 0;

  i2s_chan_config_t channelConfig = I2S_CHANNEL_DEFAULT_CONFIG(
      outputPort, I2S_ROLE_MASTER);
  channelConfig.dma_desc_num = kDmaDescriptors;
  channelConfig.dma_frame_num = kDmaSamples;
  // Unlike the HLV player, YoRadio feeds I2S with blocking writes and has no
  // on_sent callback to refill a completed descriptor immediately. Clear each
  // transmitted descriptor so a temporary decoder/network gap produces PCM
  // silence instead of repeating stale audio from the DMA ring.
  channelConfig.auto_clear_after_cb = true;
  channelConfig.auto_clear_before_cb = false;

  esp_err_t result = i2s_new_channel(&channelConfig, &outputChannel, nullptr);
  if (result != ESP_OK) {
    outputChannel = nullptr;
    holdOutputLow();
    return result;
  }

  // Track the decoded PCM rate with the official fixed-upsampling profile:
  // Fpdm = 128 * Fpcm.  The DAC helper instead requests a fixed 6.144 MHz
  // carrier through fp=960, fs=sampleRate/100.  The new IDF driver reduces
  // fp/fs to an integer before calculating BCLK, so that profile becomes
  // internally inconsistent at rates such as 44.1 kHz.  Keep the DAC
  // helper's higher-SNR divider while using the rate-consistent fp/fs pair.
  i2s_pdm_tx_clk_config_t pdmClockConfig =
      I2S_PDM_TX_CLK_DEFAULT_CONFIG(sampleRate);
  pdmClockConfig.bclk_div = 13;

  i2s_pdm_tx_config_t pdmConfig = {
      .clk_cfg = pdmClockConfig,
      .slot_cfg = I2S_PDM_TX_SLOT_DEFAULT_CONFIG(
          I2S_DATA_BIT_WIDTH_16BIT, I2S_SLOT_MODE_MONO),
      .gpio_cfg = {
          .clk = I2S_GPIO_UNUSED,
          .dout = static_cast<gpio_num_t>(outputPin),
          .invert_flags = {
              .clk_inv = false,
          },
      },
  };
  result = i2s_channel_init_pdm_tx_mode(outputChannel, &pdmConfig);
  if (result != ESP_OK) {
    releaseChannel(false);
    return result;
  }

  const uint32_t count = rampSamples(sampleRate);
  uint32_t index = 0;
  for (uint32_t descriptor = 0; descriptor < kDmaDescriptors; ++descriptor) {
    for (size_t sample = 0; sample < kDmaSamples; ++sample) {
      sampleBuffer[sample] = index < count
          ? rampSample(index++, count, true)
          : 0;
    }
    size_t loaded = 0;
    result = i2s_channel_preload_data(
        outputChannel, sampleBuffer, sizeof(sampleBuffer), &loaded);
    if (result != ESP_OK || loaded != sizeof(sampleBuffer)) {
      releaseChannel(false);
      return result == ESP_OK ? ESP_FAIL : result;
    }
  }

  result = i2s_channel_enable(outputChannel);
  if (result != ESP_OK) {
    releaseChannel(false);
    return result;
  }
  outputRunning = true;

  while (index < count) {
    const size_t chunk = min(static_cast<size_t>(count - index),
                             kDmaSamples);
    for (size_t sample = 0; sample < chunk; ++sample) {
      sampleBuffer[sample] = rampSample(index + sample, count, true);
    }
    result = writeBlock(sampleBuffer, chunk);
    if (result != ESP_OK) {
      releaseChannel(false);
      return result;
    }
    index += chunk;
  }
  delay(kBiasSettleMs);
  return ESP_OK;
}

esp_err_t pdmOutputEnd() {
  return releaseChannel(true);
}

esp_err_t pdmOutputStart() {
  if (!outputChannel) return ESP_ERR_INVALID_STATE;
  if (outputRunning) return ESP_OK;
  const i2s_pdm_tx_gpio_config_t gpioConfig = {
      .clk = I2S_GPIO_UNUSED,
      .dout = static_cast<gpio_num_t>(outputPin),
      .invert_flags = {
          .clk_inv = false,
      },
  };
  esp_err_t result = i2s_channel_reconfig_pdm_tx_gpio(
      outputChannel, &gpioConfig);
  if (result != ESP_OK) return result;
  result = i2s_channel_enable(outputChannel);
  if (result == ESP_OK) outputRunning = true;
  return result;
}

esp_err_t pdmOutputStop() {
  if (!outputChannel) return ESP_ERR_INVALID_STATE;
  if (!outputRunning) return ESP_OK;
  const esp_err_t result = i2s_channel_disable(outputChannel);
  if (result == ESP_OK) outputRunning = false;
  holdOutputLow();
  return result;
}

esp_err_t pdmOutputSetSampleRate(uint32_t sampleRate) {
  if (outputChannel && sampleRate == outputSampleRate) return ESP_OK;
  return pdmOutputBegin(outputPort, outputPin, sampleRate);
}

esp_err_t pdmOutputWriteSample(int16_t sample) {
  if (!outputChannel || !outputRunning) return ESP_ERR_INVALID_STATE;
  sampleBuffer[bufferedSamples++] = sample;
  if (bufferedSamples < kDmaSamples) return ESP_OK;
  const esp_err_t result = writeBlock(sampleBuffer, bufferedSamples);
  bufferedSamples = 0;
  return result;
}

esp_err_t pdmOutputFlush() {
  if (!bufferedSamples) return ESP_OK;
  for (size_t sample = bufferedSamples; sample < kDmaSamples; ++sample) {
    sampleBuffer[sample] = 0;
  }
  const esp_err_t result = writeBlock(sampleBuffer, kDmaSamples);
  bufferedSamples = 0;
  return result;
}

esp_err_t pdmOutputClear() {
  bufferedSamples = 0;
  memset(sampleBuffer, 0, sizeof(sampleBuffer));
  return writeBlock(sampleBuffer, kDmaSamples);
}

#endif
