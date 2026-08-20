#ifndef softxpt2046_h
#define softxpt2046_h

#include <Arduino.h>

struct SoftXPT2046Point {
  SoftXPT2046Point() : x(0), y(0), z(0) {}
  SoftXPT2046Point(int16_t px, int16_t py, int16_t pz) : x(px), y(py), z(pz) {}

  int16_t x;
  int16_t y;
  int16_t z;
};

/*
 * Minimal software-SPI XPT2046 reader.  CYD2USB wires its display, touch
 * controller and SD socket to three different pin groups, but ESP32 has only
 * two general-purpose hardware SPI hosts.  Touch traffic is tiny, so moving
 * it to bit-banged SPI leaves HSPI for the display and VSPI for microSD.
 */
class SoftXPT2046Touchscreen {
 public:
  SoftXPT2046Touchscreen(uint8_t csPin, uint8_t clockPin,
                        uint8_t misoPin, uint8_t mosiPin);

  bool begin();
  bool touched();
  SoftXPT2046Point getPoint();
  void setRotation(uint8_t rotation);

 private:
  void update();
  uint8_t transfer8(uint8_t value);
  uint16_t transfer16(uint16_t value);
  static int16_t bestTwoAverage(int16_t a, int16_t b, int16_t c);

  uint8_t _csPin;
  uint8_t _clockPin;
  uint8_t _misoPin;
  uint8_t _mosiPin;
  uint8_t _rotation = 1;
  int16_t _x = 0;
  int16_t _y = 0;
  int16_t _z = 0;
  uint32_t _lastReadMs = 0x80000000UL;
};

#endif
