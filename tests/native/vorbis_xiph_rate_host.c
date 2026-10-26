/* Metadata-only unsigned sample-rate regression entry point. */
#include <assert.h>
#include <stdio.h>
#include "vorbis_xiph_alloc.h"

extern int xiph_rate_tests(void);

int main(void) {
  assert(!xiph_port_test_live() && !xiph_port_test_bytes());
  int count = xiph_rate_tests();
  assert(count > 0 && !xiph_port_test_live() && !xiph_port_test_bytes());
  printf("RATE_PASS scenarios=%d live=%zu bytes=%zu\n", count,
         xiph_port_test_live(), xiph_port_test_bytes());
  return 0;
}
