#ifndef yoradio_fixedpoint_h
#define yoradio_fixedpoint_h

#include <stdint.h>

namespace fixedpoint {

inline uint32_t ratio(uint64_t numerator, uint64_t denominator,
                      uint32_t scale) {
  if (denominator == 0) return 0;
  return static_cast<uint32_t>((numerator * scale + denominator / 2U) /
                               denominator);
}

}  // namespace fixedpoint

#endif
