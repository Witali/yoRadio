#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <errno.h>
#include "http_stream_protocol.h"

typedef uint32_t TickType_t;
typedef struct { int socket; TickType_t last_receive_tick; } http_stream_t;
typedef struct { unsigned mask; } fd_set;
struct timeval { long tv_sec, tv_usec; };
#define FD_ZERO(set) ((set)->mask = 0)
#define FD_SET(fd, set) ((set)->mask |= 1U << (fd))
#define pdMS_TO_TICKS(ms) (ms)
#define portTICK_PERIOD_MS 1U
#define STREAM_IDLE_TIMEOUT_MS 1000U
static uint32_t now, current_generation, advance, cancel_to, last_wait;
static int result, result_errno, select_calls, delay_calls;
static TickType_t xTaskGetTickCount(void) { return now; }
static bool generation_current(uint32_t generation) { return generation == current_generation; }
static void vTaskDelay(uint32_t ticks) {
    now += ticks; ++delay_calls; if (cancel_to) current_generation = cancel_to;
}
static int fake_select(int maxfd, fd_set *reads, void *writes, fd_set *errors,
                        struct timeval *timeout) {
    assert(maxfd == 4 && reads->mask == 8 && errors->mask == 8 && !writes);
    assert(timeout->tv_sec == 0 && timeout->tv_usec > 0);
    last_wait = (uint32_t)timeout->tv_usec / 1000U;
    ++select_calls; now += advance;
    if (cancel_to) current_generation = cancel_to;
    errno = result_errno; return result;
}
#define select fake_select
#include "stream_read_wait.h"

static http_stream_t reset(void) {
    now = 100; current_generation = 7; advance = cancel_to = last_wait = 0;
    result = 0; result_errno = EAGAIN; select_calls = delay_calls = 0;
    return (http_stream_t){3, 100};
}
int main(void) {
    http_stream_t s = reset();
    assert(stream_wait_after_empty(&s, 7, 0));
    assert(delay_calls == 1 && !select_calls && now == 101);
    s = reset(); cancel_to = 8;
    assert(!stream_wait_after_empty(&s, 7, 0) && errno == ECANCELED);
    s = reset(); current_generation = 8;
    assert(!stream_wait_after_empty(&s, 7, 25) && errno == ECANCELED && !select_calls);
    s = reset(); result = 1;
    assert(stream_wait_after_empty(&s, 7, 25) && last_wait == 25 && !delay_calls);
    s = reset(); advance = 25;
    assert(stream_wait_after_empty(&s, 7, 25) && s.last_receive_tick == 100);
    /* Repeated spurious wakeups must not renew inactivity deadline. */
    for (unsigned i = 0; i < 38; ++i) assert(stream_wait_after_empty(&s, 7, 25));
    assert(!stream_wait_after_empty(&s, 7, 25) && errno == ETIMEDOUT);
    s = reset(); now = 1093; advance = 7;
    assert(!stream_wait_after_empty(&s, 7, 25) && errno == ETIMEDOUT && last_wait == 7);
    s = reset(); now = 1100;
    assert(!stream_wait_after_empty(&s, 7, 25) && errno == ETIMEDOUT && !select_calls);
    s = reset(); result = -1; result_errno = EINTR; advance = 2;
    assert(stream_wait_after_empty(&s, 7, 25) && s.last_receive_tick == 100);
    s = reset(); result = -1; result_errno = EBADF;
    assert(!stream_wait_after_empty(&s, 7, 25) && errno == EBADF);
    s = reset(); result = 1; cancel_to = 8;
    assert(!stream_wait_after_empty(&s, 7, 25) && errno == ECANCELED);
    s = reset(); s.last_receive_tick = UINT32_MAX - 900; now = 50;
    assert(stream_wait_after_empty(&s, 7, 25) && last_wait == 25);
    now = 99;
    assert(!stream_wait_after_empty(&s, 7, 25) && errno == ETIMEDOUT);
    /* Readiness can become stale; return to recv instead of fabricating data. */
    s = reset(); result = 1;
    assert(stream_wait_after_empty(&s, 7, 25));
    result = 0; advance = 25;
    assert(stream_wait_after_empty(&s, 7, 25) && select_calls == 2);
    puts("Stream wait tests passed (13 scenarios)");
    return 0;
}
