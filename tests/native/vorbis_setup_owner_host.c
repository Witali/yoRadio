// Host entry point; the same lifecycle fixture can run under an SDK harness.
#include "vorbis_setup_owner_test.h"
#include <assert.h>
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void owner_test_poll(void) {}

static size_t case_index(const char *text) {
    size_t result = 0;
    assert(text && *text);
    for (const unsigned char *at = (const unsigned char *)text; *at; ++at) {
        assert(*at >= '0' && *at <= '9');
        size_t digit = (size_t)(*at - '0');
        assert(result <= (SIZE_MAX - digit) / 10);
        result = result * 10 + digit;
    }
    return result;
}

int main(int argc, char **argv) {
    if (argc == 1) {
        for (size_t i = 0; i < owner_test_case_count(); ++i) owner_test_run_case(i, true);
    } else {
        assert(argc == 3 && strcmp(argv[1], "--case") == 0);
        size_t index = case_index(argv[2]);
        assert(index < owner_test_case_count());
        owner_test_run_case(index, true);
    }
    owner_test_totals_t totals = owner_test_totals();
    printf("OWNER_PASS cases=%" PRIu64 " checks=%" PRIu64 " successes=%" PRIu64
        " parse_failures=%" PRIu64 " allocation_refusals=%" PRIu64 " live=0 bytes=0\n",
        totals.cases, totals.checks, totals.successful_opens, totals.parse_failures, totals.allocation_refusals);
    return 0;
}
