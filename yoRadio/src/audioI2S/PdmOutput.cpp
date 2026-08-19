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
// without replacing part of the waveform with silence. At the fixed 48 kHz
// output rate this is about 85 ms, still short enough for controls.
constexpr size_t kDmaFrames = 512;
constexpr uint32_t kDmaDescriptors = 8;
constexpr uint32_t kBiasRampMs = 100;
constexpr uint32_t kBiasSettleMs = 2;
constexpr uint32_t kPdmOutputSampleRate = 48000;
constexpr uint32_t kPdmCarrierRate = 6144000;
constexpr uint32_t kInterpolationScale = 32768;

i2s_chan_handle_t outputChannel = nullptr;
uint8_t outputPort = I2S_NUM_0;
uint8_t outputLeftPin = I2S_PDM_DOUT;
uint8_t outputRightPin = I2S_PDM_DOUT2;
uint32_t outputSampleRate = 0;
uint32_t inputSampleRate = 0;
bool outputRunning = false;
size_t bufferedFrames = 0;
int16_t sampleBuffer[kDmaFrames * 2] = {};
bool resamplerHasPrevious = false;
int16_t resamplerPreviousLeft = 0;
int16_t resamplerPreviousRight = 0;
uint32_t resamplerNextPhase = 0;

bool stereoOutput() {
  return outputRightPin != 255;
}

size_t outputChannels() {
  return stereoOutput() ? 2U : 1U;
}

void resetResampler() {
  resamplerHasPrevious = false;
  resamplerPreviousLeft = 0;
  resamplerPreviousRight = 0;
  resamplerNextPhase = 0;
}

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

esp_err_t writeBlock(const int16_t *samples, size_t frames) {
  if (!outputChannel || !outputRunning) return ESP_ERR_INVALID_STATE;
  size_t written = 0;
  const size_t bytes = frames * outputChannels() * sizeof(*samples);
  const esp_err_t result = i2s_channel_write(
      outputChannel, samples, bytes, &written, 1000);
  return result == ESP_OK && written == bytes ? ESP_OK :
         result == ESP_OK ? ESP_FAIL : result;
}

esp_err_t queueOutputFrame(int16_t left, int16_t right) {
  const size_t offset = bufferedFrames * outputChannels();
  sampleBuffer[offset] = left;
  if (stereoOutput()) sampleBuffer[offset + 1U] = right;
  ++bufferedFrames;
  if (bufferedFrames < kDmaFrames) return ESP_OK;
  const esp_err_t result = writeBlock(sampleBuffer, bufferedFrames);
  bufferedFrames = 0;
  return result;
}

void holdOutputLow() {
  const uint8_t pins[] = {outputLeftPin, outputRightPin};
  for (const uint8_t pin : pins) {
    if (pin == 255) continue;
    gpio_reset_pin(static_cast<gpio_num_t>(pin));
    gpio_set_direction(static_cast<gpio_num_t>(pin), GPIO_MODE_OUTPUT);
    gpio_set_level(static_cast<gpio_num_t>(pin), 0);
  }
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
                               kDmaFrames);
      for (size_t frame = 0; frame < chunk; ++frame) {
        const int16_t value = rampSample(index + frame, count, false);
        const size_t offset = frame * outputChannels();
        sampleBuffer[offset] = value;
        if (stereoOutput()) sampleBuffer[offset + 1U] = value;
      }
      result = writeBlock(sampleBuffer, chunk);
      if (firstError == ESP_OK && result != ESP_OK) firstError = result;
      if (result != ESP_OK) break;
      index += chunk;
    }
    const uint32_t drainMs = static_cast<uint32_t>(
        ((kDmaDescriptors + 1U) * kDmaFrames * 1000ULL +
         outputSampleRate - 1U) / outputSampleRate);
    delay(kBiasRampMs + drainMs + kBiasSettleMs);
  }

  bufferedFrames = 0;
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
  inputSampleRate = 0;
  resetResampler();
  return firstError;
}

}  // namespace

esp_err_t pdmOutputPrepare(uint8_t port, uint8_t leftPin, uint8_t rightPin) {
#if SOC_I2S_PDM_MAX_TX_LINES < 2
  if (rightPin != 255) return ESP_ERR_NOT_SUPPORTED;
#endif
  if (outputChannel) {
    const esp_err_t result = releaseChannel(true);
    if (result != ESP_OK) return result;
  }
  outputPort = port;
  outputLeftPin = leftPin;
  outputRightPin = rightPin;
  outputSampleRate = 0;
  inputSampleRate = 0;
  bufferedFrames = 0;
  resetResampler();
  holdOutputLow();
  return ESP_OK;
}

esp_err_t pdmOutputBegin(uint8_t port, uint8_t leftPin, uint8_t rightPin,
                         uint32_t sampleRate) {
  if (sampleRate < 8000U || sampleRate > 48000U) {
    return ESP_ERR_INVALID_ARG;
  }
#if SOC_I2S_PDM_MAX_TX_LINES < 2
  if (rightPin != 255) return ESP_ERR_NOT_SUPPORTED;
#endif
  if (outputChannel) {
    const esp_err_t result = releaseChannel(true);
    if (result != ESP_OK) return result;
  }

  outputPort = port;
  outputLeftPin = leftPin;
  outputRightPin = rightPin;
  outputSampleRate = kPdmOutputSampleRate;
  inputSampleRate = sampleRate;
  bufferedFrames = 0;
  resetResampler();

  i2s_chan_config_t channelConfig = I2S_CHANNEL_DEFAULT_CONFIG(
      static_cast<i2s_port_t>(outputPort), I2S_ROLE_MASTER);
  channelConfig.dma_desc_num = kDmaDescriptors;
  channelConfig.dma_frame_num = kDmaFrames;
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

  i2s_pdm_tx_config_t pdmConfig = {
      // Run the hardware PCM-to-PDM converter at a fixed 48 kHz. The samples
      // are linearly resampled below, keeping the high-SNR PDM carrier at
      // exactly 6.144 MHz for every supported source rate.
      .clk_cfg = I2S_PDM_TX_CLK_DAC_DEFAULT_CONFIG(kPdmOutputSampleRate),
      .slot_cfg = I2S_PDM_TX_SLOT_DAC_DEFAULT_CONFIG(
          I2S_DATA_BIT_WIDTH_16BIT,
          stereoOutput() ? I2S_SLOT_MODE_STEREO : I2S_SLOT_MODE_MONO),
      .gpio_cfg = {
          .clk = I2S_GPIO_UNUSED,
          .dout = static_cast<gpio_num_t>(outputLeftPin),
#if SOC_I2S_PDM_MAX_TX_LINES > 1
          .dout2 = stereoOutput()
              ? static_cast<gpio_num_t>(outputRightPin) : I2S_GPIO_UNUSED,
#endif
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

  const uint32_t count = rampSamples(outputSampleRate);
  uint32_t index = 0;
  for (uint32_t descriptor = 0; descriptor < kDmaDescriptors; ++descriptor) {
    for (size_t frame = 0; frame < kDmaFrames; ++frame) {
      const int16_t value = index < count
          ? rampSample(index++, count, true) : 0;
      const size_t offset = frame * outputChannels();
      sampleBuffer[offset] = value;
      if (stereoOutput()) sampleBuffer[offset + 1U] = value;
    }
    size_t loaded = 0;
    const size_t preloadBytes =
        kDmaFrames * outputChannels() * sizeof(sampleBuffer[0]);
    result = i2s_channel_preload_data(
        outputChannel, sampleBuffer, preloadBytes, &loaded);
    if (result != ESP_OK || loaded != preloadBytes) {
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

  log_i("PDM %s L=GPIO%d R=GPIO%d: input %lu Hz -> PCM %lu Hz, carrier %lu Hz",
        stereoOutput() ? "stereo" : "mono", outputLeftPin, outputRightPin,
        static_cast<unsigned long>(inputSampleRate),
        static_cast<unsigned long>(outputSampleRate),
        static_cast<unsigned long>(kPdmCarrierRate));

  while (index < count) {
    const size_t chunk = min(static_cast<size_t>(count - index),
                             kDmaFrames);
    for (size_t frame = 0; frame < chunk; ++frame) {
      const int16_t value = rampSample(index + frame, count, true);
      const size_t offset = frame * outputChannels();
      sampleBuffer[offset] = value;
      if (stereoOutput()) sampleBuffer[offset + 1U] = value;
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
      .dout = static_cast<gpio_num_t>(outputLeftPin),
#if SOC_I2S_PDM_MAX_TX_LINES > 1
      .dout2 = stereoOutput()
          ? static_cast<gpio_num_t>(outputRightPin) : I2S_GPIO_UNUSED,
#endif
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
  if (outputChannel && sampleRate == inputSampleRate) return ESP_OK;
  return pdmOutputBegin(
      outputPort, outputLeftPin, outputRightPin, sampleRate);
}

esp_err_t pdmOutputWriteFrame(int16_t left, int16_t right) {
  if (!outputChannel || !outputRunning) return ESP_ERR_INVALID_STATE;
  if (!inputSampleRate) return ESP_ERR_INVALID_STATE;

  // Preserve the 48 kHz path bit-for-bit and without interpolation overhead.
  if (inputSampleRate == kPdmOutputSampleRate) {
    return queueOutputFrame(left, right);
  }

  // The first source sample establishes the left endpoint and is emitted
  // immediately. Subsequent samples interpolate all 48 kHz output instants
  // that fall in the interval [previous, current]. The integer phase is exact
  // for rates such as 44.1, 32, 24, 22.05, 16 and 8 kHz and cannot drift.
  if (!resamplerHasPrevious) {
    resamplerHasPrevious = true;
    resamplerPreviousLeft = left;
    resamplerPreviousRight = right;
    resamplerNextPhase = inputSampleRate;
    return queueOutputFrame(left, right);
  }

  uint32_t phase = resamplerNextPhase;
  const int32_t deltaLeft =
      static_cast<int32_t>(left) - resamplerPreviousLeft;
  const int32_t deltaRight =
      static_cast<int32_t>(right) - resamplerPreviousRight;
  while (phase <= kPdmOutputSampleRate) {
    // Q15 keeps this 48 kHz hot path entirely in 32-bit arithmetic. Even the
    // worst-case 16-bit delta times 32768 remains inside int32_t.
    const uint32_t fraction =
        (phase * kInterpolationScale + kPdmOutputSampleRate / 2) /
        kPdmOutputSampleRate;
    int32_t scaledLeft = deltaLeft * static_cast<int32_t>(fraction);
    scaledLeft += scaledLeft >= 0 ? kInterpolationScale / 2
                                  : -static_cast<int32_t>(kInterpolationScale / 2);
    int32_t scaledRight = deltaRight * static_cast<int32_t>(fraction);
    scaledRight += scaledRight >= 0 ? kInterpolationScale / 2
                                    : -static_cast<int32_t>(kInterpolationScale / 2);
    const int16_t interpolatedLeft = static_cast<int16_t>(
        static_cast<int32_t>(resamplerPreviousLeft) +
        scaledLeft / static_cast<int32_t>(kInterpolationScale));
    const int16_t interpolatedRight = static_cast<int16_t>(
        static_cast<int32_t>(resamplerPreviousRight) +
        scaledRight / static_cast<int32_t>(kInterpolationScale));
    const esp_err_t result =
        queueOutputFrame(interpolatedLeft, interpolatedRight);
    if (result != ESP_OK) return result;
    phase += inputSampleRate;
  }
  resamplerNextPhase = phase - kPdmOutputSampleRate;
  resamplerPreviousLeft = left;
  resamplerPreviousRight = right;
  return ESP_OK;
}

esp_err_t pdmOutputFlush() {
  if (!bufferedFrames) return ESP_OK;
  for (size_t frame = bufferedFrames; frame < kDmaFrames; ++frame) {
    const size_t offset = frame * outputChannels();
    sampleBuffer[offset] = 0;
    if (stereoOutput()) sampleBuffer[offset + 1U] = 0;
  }
  const esp_err_t result = writeBlock(sampleBuffer, kDmaFrames);
  bufferedFrames = 0;
  return result;
}

esp_err_t pdmOutputClear() {
  bufferedFrames = 0;
  resetResampler();
  memset(sampleBuffer, 0, sizeof(sampleBuffer));
  return writeBlock(sampleBuffer, kDmaFrames);
}

#endif
