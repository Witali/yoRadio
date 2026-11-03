#include <stdint.h>
__attribute__((noinline,used)) uint8_t forbidden_byte(const volatile uint8_t *p){return *p;}
__attribute__((noinline,used)) void forbidden_half(volatile uint16_t *p,uint16_t bits){*p=bits;}
__attribute__((noinline,used)) float forbidden_float(const volatile float *p,float gain){return *p+gain;}
