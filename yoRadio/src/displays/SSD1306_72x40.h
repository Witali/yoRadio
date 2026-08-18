#ifndef SSD1306_72X40_H
#define SSD1306_72X40_H

#include <Adafruit_GFX.h>
#include <Wire.h>

#ifndef BLACK
#define BLACK 0
#endif
#ifndef WHITE
#define WHITE 1
#endif
#ifndef INVERSE
#define INVERSE 2
#endif

class SSD1306_72x40 : public Adafruit_GFX {
 public:
  explicit SSD1306_72x40(TwoWire* wire, uint32_t clock = 400000UL);

  bool begin(uint8_t address = 0x3c);
  void clearDisplay();
  void display();
  void drawPixel(int16_t x, int16_t y, uint16_t color) override;
  void writePixel(int16_t x, int16_t y, uint16_t color) override;
  void writeFillRect(int16_t x, int16_t y, int16_t w, int16_t h,
                     uint16_t color) override;
  void invertDisplay(bool inverted);
  void setFlip(bool flipped);
  void command(uint8_t value);

 private:
  static constexpr uint8_t kWidth = 72;
  static constexpr uint8_t kHeight = 40;
  static constexpr uint8_t kPages = kHeight / 8;
  static constexpr uint8_t kColumnOffset = 28;

  void commands(const uint8_t* values, size_t count);

  TwoWire* wire_;
  uint32_t clock_;
  uint8_t address_;
  uint8_t buffer_[kWidth * kPages];
};

#endif
