#include "../core/options.h"

#if DSP_MODEL==DSP_SSD1306_72X40

#include "SSD1306_72x40.h"
#include <cstring>

SSD1306_72x40::SSD1306_72x40(TwoWire* wire, uint32_t clock)
    : Adafruit_GFX(kWidth, kHeight), wire_(wire), clock_(clock), address_(0x3c) {
  clearDisplay();
}

bool SSD1306_72x40::begin(uint8_t address) {
  address_ = address;
  wire_->setClock(clock_);

  // EastRising 72x40 initialization from the U8g2 SSD1306 driver.
  static const uint8_t init[] = {
      0xae, 0xd5, 0x80, 0xa8, 0x27, 0xd3, 0x00, 0xad, 0x30,
      0x8d, 0x14, 0x40, 0xa6, 0xa4, 0x20, 0x00, 0xa1, 0xc8,
      0xda, 0x12, 0x81, 0xaf, 0xd9, 0x22, 0xdb, 0x20, 0x2e,
      0xaf};
  commands(init, sizeof(init));
  clearDisplay();
  display();
  return true;
}

void SSD1306_72x40::commands(const uint8_t* values, size_t count) {
  while (count != 0) {
    const size_t chunk = count > 24 ? 24 : count;
    wire_->beginTransmission(address_);
    wire_->write(0x00);
    wire_->write(values, chunk);
    wire_->endTransmission();
    values += chunk;
    count -= chunk;
  }
}

void SSD1306_72x40::command(uint8_t value) { commands(&value, 1); }

void SSD1306_72x40::clearDisplay() { std::memset(buffer_, 0, sizeof(buffer_)); }

void SSD1306_72x40::drawPixel(int16_t x, int16_t y, uint16_t color) {
  if (x < 0 || x >= kWidth || y < 0 || y >= kHeight) return;
  uint8_t& pixel = buffer_[x + (y / 8) * kWidth];
  const uint8_t mask = static_cast<uint8_t>(1U << (y & 7));
  if (color == WHITE) pixel |= mask;
  else if (color == BLACK) pixel &= static_cast<uint8_t>(~mask);
  else pixel ^= mask;
}

void SSD1306_72x40::writePixel(int16_t x, int16_t y, uint16_t color) {
  drawPixel(x, y, color);
}

void SSD1306_72x40::writeFillRect(int16_t x, int16_t y, int16_t w, int16_t h,
                                  uint16_t color) {
  if (w <= 0 || h <= 0) return;
  const int16_t x0 = x < 0 ? 0 : x;
  const int16_t y0 = y < 0 ? 0 : y;
  const int16_t x1 = (x + w) > kWidth ? kWidth : (x + w);
  const int16_t y1 = (y + h) > kHeight ? kHeight : (y + h);
  for (int16_t yy = y0; yy < y1; ++yy) {
    for (int16_t xx = x0; xx < x1; ++xx) drawPixel(xx, yy, color);
  }
}

void SSD1306_72x40::display() {
  for (uint8_t page = 0; page < kPages; ++page) {
    const uint8_t column = kColumnOffset;
    const uint8_t pageCommands[] = {
        static_cast<uint8_t>(0x10 | (column >> 4)),
        static_cast<uint8_t>(column & 0x0f),
        static_cast<uint8_t>(0xb0 | page)};
    commands(pageCommands, sizeof(pageCommands));

    const uint8_t* data = buffer_ + page * kWidth;
    for (uint8_t sent = 0; sent < kWidth; sent += 24) {
      const uint8_t chunk = static_cast<uint8_t>(
          (kWidth - sent) > 24 ? 24 : (kWidth - sent));
      wire_->beginTransmission(address_);
      wire_->write(0x40);
      wire_->write(data + sent, chunk);
      wire_->endTransmission();
    }
  }
}

void SSD1306_72x40::invertDisplay(bool inverted) {
  command(inverted ? 0xa7 : 0xa6);
}

void SSD1306_72x40::setContrast(uint8_t percent) {
  if (percent > 100) percent = 100;
  const uint8_t controllerContrast = static_cast<uint8_t>(
      (static_cast<uint16_t>(percent) * 255U + 50U) / 100U);
  const uint8_t values[] = {0x81, controllerContrast};
  commands(values, sizeof(values));
}

void SSD1306_72x40::setFlip(bool flipped) {
  const uint8_t values[] = {
      static_cast<uint8_t>(flipped ? 0xa0 : 0xa1),
      static_cast<uint8_t>(flipped ? 0xc0 : 0xc8)};
  commands(values, sizeof(values));
}

#endif
