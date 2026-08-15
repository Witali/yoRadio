#pragma once

#include <Arduino.h>
#include <esp_err.h>

esp_err_t pdmOutputBegin(uint8_t port, uint8_t dataPin,
                         uint32_t sampleRate);
esp_err_t pdmOutputPrepare(uint8_t port, uint8_t dataPin);
esp_err_t pdmOutputEnd();
esp_err_t pdmOutputStart();
esp_err_t pdmOutputStop();
esp_err_t pdmOutputSetSampleRate(uint32_t sampleRate);
esp_err_t pdmOutputWriteSample(int16_t sample);
esp_err_t pdmOutputFlush();
esp_err_t pdmOutputClear();
