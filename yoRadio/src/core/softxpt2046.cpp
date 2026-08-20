#include "softxpt2046.h"

namespace {
constexpr int16_t kPressureThreshold = 300;
constexpr uint32_t kMinimumReadIntervalMs = 3;
}

SoftXPT2046Touchscreen::SoftXPT2046Touchscreen(
    uint8_t csPin, uint8_t clockPin, uint8_t misoPin, uint8_t mosiPin)
    : _csPin(csPin),
      _clockPin(clockPin),
      _misoPin(misoPin),
      _mosiPin(mosiPin) {}

bool SoftXPT2046Touchscreen::begin() {
  pinMode(_csPin, OUTPUT);
  pinMode(_clockPin, OUTPUT);
  pinMode(_mosiPin, OUTPUT);
  pinMode(_misoPin, INPUT);
  digitalWrite(_csPin, HIGH);
  digitalWrite(_clockPin, LOW);
  digitalWrite(_mosiPin, LOW);
  return true;
}

void SoftXPT2046Touchscreen::setRotation(uint8_t rotation) {
  _rotation = rotation & 3U;
}

bool SoftXPT2046Touchscreen::touched() {
  update();
  return _z >= kPressureThreshold;
}

SoftXPT2046Point SoftXPT2046Touchscreen::getPoint() {
  update();
  return SoftXPT2046Point(_x, _y, _z);
}

uint8_t SoftXPT2046Touchscreen::transfer8(uint8_t value) {
  uint8_t input = 0;
  for (uint8_t mask = 0x80; mask; mask >>= 1) {
    digitalWrite(_mosiPin, (value & mask) ? HIGH : LOW);
    digitalWrite(_clockPin, HIGH);
    input = static_cast<uint8_t>((input << 1) | (digitalRead(_misoPin) ? 1 : 0));
    digitalWrite(_clockPin, LOW);
  }
  return input;
}

uint16_t SoftXPT2046Touchscreen::transfer16(uint16_t value) {
  const uint16_t high = transfer8(static_cast<uint8_t>(value >> 8));
  const uint16_t low = transfer8(static_cast<uint8_t>(value));
  return static_cast<uint16_t>((high << 8) | low);
}

int16_t SoftXPT2046Touchscreen::bestTwoAverage(
    int16_t a, int16_t b, int16_t c) {
  const int16_t ab = abs(a - b);
  const int16_t ac = abs(a - c);
  const int16_t bc = abs(b - c);
  if (ab <= ac && ab <= bc) return (a + b) >> 1;
  if (ac <= ab && ac <= bc) return (a + c) >> 1;
  return (b + c) >> 1;
}

void SoftXPT2046Touchscreen::update() {
  const uint32_t now = millis();
  if (now - _lastReadMs < kMinimumReadIntervalMs) return;

  int16_t samples[6] = {0, 0, 0, 0, 0, 0};
  digitalWrite(_csPin, LOW);
  transfer8(0xB1);  // Z1
  const int16_t z1 = static_cast<int16_t>(transfer16(0xC1) >> 3);  // Z2
  int16_t pressure = z1 + 4095;
  const int16_t z2 = static_cast<int16_t>(transfer16(0x91) >> 3);  // X
  pressure -= z2;

  if (pressure >= kPressureThreshold) {
    transfer16(0x91);  // First X sample is noisy.
    samples[0] = static_cast<int16_t>(transfer16(0xD1) >> 3);
    samples[1] = static_cast<int16_t>(transfer16(0x91) >> 3);
    samples[2] = static_cast<int16_t>(transfer16(0xD1) >> 3);
    samples[3] = static_cast<int16_t>(transfer16(0x91) >> 3);
  }
  samples[4] = static_cast<int16_t>(transfer16(0xD0) >> 3);
  samples[5] = static_cast<int16_t>(transfer16(0) >> 3);
  digitalWrite(_csPin, HIGH);
  digitalWrite(_mosiPin, LOW);

  if (pressure < 0) pressure = 0;
  if (pressure < kPressureThreshold) {
    _z = 0;
    _lastReadMs = now;
    return;
  }

  const int16_t x = bestTwoAverage(samples[0], samples[2], samples[4]);
  const int16_t y = bestTwoAverage(samples[1], samples[3], samples[5]);
  _z = pressure;
  _lastReadMs = now;

  switch (_rotation) {
    case 0:
      _x = 4095 - y;
      _y = x;
      break;
    case 1:
      _x = x;
      _y = y;
      break;
    case 2:
      _x = y;
      _y = 4095 - x;
      break;
    default:
      _x = 4095 - x;
      _y = 4095 - y;
      break;
  }
}
