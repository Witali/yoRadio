/* Compile the actual audio_service.c connect helpers. Only lwIP, time and
 * command state are mocked; no real network, decoder or target build. */
#define _POSIX_C_SOURCE 200809L
#include <errno.h>
#include <fcntl.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/select.h>
#include <sys/time.h>
#include <netdb.h>

#define CHECK(expr) do { if (!(expr)) { \
    fprintf(stderr, "line %d: %s\n", __LINE__, #expr); exit(1); \
} } while (0)
#define ESP_LOGE(...) ((void)0)
/* DEFINES */
typedef struct {
    int socket_error, get_flags_error, set_flags_error, connect_error;
    int select_error, so_error, getsockopt_error;
    int64_t ready_delay;
    bool error_only, ready_error;
} socket_plan_t;
static socket_plan_t plans[3];
static struct addrinfo addresses[3];
static struct sockaddr endpoints[3];
static unsigned address_count, socket_calls, close_calls, dns_calls, frees;
static unsigned connect_calls, waits, option_reads, option_writes, error_reads;
static unsigned interrupted_waits;
static bool always_interrupt, cancel_in_connect, cancel_in_dns, pause;
static int dns_error, active_fd, flags[3];
static bool live[3];
static int64_t now, connect_started[3], dns_delay, cancel_at, pause_at, max_wait;
static uint32_t s_generation;
static char s_host[96] = "radio.invalid";
static bool generation_current(uint32_t generation) { return generation == s_generation; }
static bool audio_web_pause_requested(void) { return pause; }
static int64_t esp_timer_get_time(void) { return now; }
static void advance_to(int64_t next) {
    now = next;
    if (cancel_at >= 0 && now >= cancel_at) { ++s_generation; cancel_at = -1; }
    if (pause_at >= 0 && now >= pause_at) { pause = true; pause_at = -1; }
}
static unsigned fd_index(int fd) {
    CHECK(fd >= 3 && fd < 6 && live[fd - 3]); return (unsigned)(fd - 3);
}
static int mock_getaddrinfo(const char *host, const char *port,
                           const struct addrinfo *hints, struct addrinfo **result) {
    CHECK(strcmp(host, s_host) == 0 && strcmp(port, "8765") == 0);
    CHECK(hints->ai_family == AF_INET && hints->ai_socktype == SOCK_STREAM);
    ++dns_calls; advance_to(now + dns_delay);
    if (cancel_in_dns) ++s_generation;
    if (dns_error) return dns_error;
    *result = address_count ? addresses : NULL; return 0;
}
static void mock_freeaddrinfo(struct addrinfo *result) {
    CHECK(result == (address_count ? addresses : NULL)); ++frees;
    errno = ERANGE; /* Cleanup must not replace the connection failure. */
}
static int mock_socket(int family, int type, int protocol) {
    CHECK(family == AF_INET && type == SOCK_STREAM && protocol == IPPROTO_TCP);
    unsigned index = socket_calls++;
    CHECK(index < address_count);
    if (plans[index].socket_error) { errno = plans[index].socket_error; return -1; }
    live[index] = true; active_fd = (int)index + 3; return active_fd;
}
static int mock_fcntl(int fd, int command, int value) {
    unsigned index = fd_index(fd);
    if (command == F_GETFL) {
        if (plans[index].get_flags_error) { errno = plans[index].get_flags_error; return -1; }
        return flags[index];
    }
    CHECK(command == F_SETFL && value == (O_RDWR | O_NONBLOCK));
    if (plans[index].set_flags_error) { errno = plans[index].set_flags_error; return -1; }
    flags[index] = value; return 0;
}
static int mock_connect(int fd, const struct sockaddr *address, socklen_t length) {
    unsigned index = fd_index(fd);
    CHECK(flags[index] & O_NONBLOCK); /* This is the regression's essential ordering. */
    CHECK(address == &endpoints[index] && length == sizeof(endpoints[index]));
    ++connect_calls; connect_started[index] = now;
    if (cancel_in_connect) ++s_generation;
    if (plans[index].connect_error) { errno = plans[index].connect_error; return -1; }
    return 0;
}
static int mock_select(int nfds, fd_set *read_set, fd_set *write_set,
                       fd_set *error_set, struct timeval *timeout) {
    unsigned index = fd_index(active_fd);
    CHECK(nfds == active_fd + 1 && !read_set);
    CHECK(FD_ISSET(active_fd, write_set) && FD_ISSET(active_fd, error_set));
    int64_t wait_us = timeout->tv_sec * 1000000LL + timeout->tv_usec;
    CHECK(wait_us > 0 && wait_us <= SOCKET_CONNECT_POLL_MS * 1000LL);
    if (wait_us > max_wait) max_wait = wait_us;
    ++waits;
    FD_ZERO(write_set); FD_ZERO(error_set);
    if (always_interrupt || interrupted_waits) {
        if (interrupted_waits) --interrupted_waits;
        advance_to(now + (wait_us < 1000 ? wait_us : 1000));
        errno = EINTR; return -1;
    }
    if (plans[index].select_error) { errno = plans[index].select_error; return -1; }
    int64_t next = now + wait_us;
    if (cancel_at >= 0 && cancel_at < next) next = cancel_at;
    if (pause_at >= 0 && pause_at < next) next = pause_at;
    int64_t ready_at = connect_started[index] + plans[index].ready_delay;
    bool ready = plans[index].ready_delay >= 0 && ready_at <= next;
    if (ready && ready_at > now) next = ready_at;
    advance_to(next);
    if (!ready) return 0;
    if (!plans[index].error_only) FD_SET(active_fd, write_set);
    if (plans[index].error_only || plans[index].ready_error) FD_SET(active_fd, error_set);
    return 1;
}
static int mock_getsockopt(int fd, int level, int option, void *value, socklen_t *length) {
    unsigned index = fd_index(fd);
    CHECK(level == SOL_SOCKET && option == SO_ERROR && *length == sizeof(int));
    ++error_reads;
    if (plans[index].getsockopt_error) { errno = plans[index].getsockopt_error; return -1; }
    *(int *)value = plans[index].so_error; return 0;
}
static int mock_setsockopt(int fd, int level, int option, const void *value, socklen_t length) {
    (void)fd_index(fd);
    CHECK(level == SOL_SOCKET && length == sizeof(struct timeval));
    const struct timeval *timeout = value;
    int64_t ms = timeout->tv_sec * 1000LL + timeout->tv_usec / 1000;
    if (option == SO_RCVTIMEO) { CHECK(ms == SOCKET_READ_TIMEOUT_MS); ++option_reads; }
    else { CHECK(option == SO_SNDTIMEO && ms == SOCKET_WRITE_TIMEOUT_MS); ++option_writes; }
    return 0;
}
static int mock_close(int fd) {
    unsigned index = fd_index(fd);
    live[index] = false; ++close_calls; errno = EIO; return 0;
}
#define getaddrinfo mock_getaddrinfo
#define freeaddrinfo mock_freeaddrinfo
#define socket mock_socket
#define fcntl mock_fcntl
#define connect mock_connect
#define select mock_select
#define getsockopt mock_getsockopt
#define setsockopt mock_setsockopt
#define close mock_close
/* CONNECT_IMPLEMENTATION */

static void reset(unsigned count) {
    CHECK(count <= 3);
    memset(plans, 0, sizeof(plans)); memset(addresses, 0, sizeof(addresses));
    memset(live, 0, sizeof(live));
    address_count = count; socket_calls = close_calls = dns_calls = frees = 0;
    connect_calls = waits = option_reads = option_writes = error_reads = 0;
    interrupted_waits = 0; always_interrupt = cancel_in_connect = cancel_in_dns = pause = false;
    dns_error = 0; active_fd = -1; now = dns_delay = max_wait = 0;
    cancel_at = pause_at = -1; s_generation = 42; errno = 0;
    for (unsigned i = 0; i < count; ++i) {
        flags[i] = O_RDWR;
        addresses[i].ai_family = AF_INET; addresses[i].ai_socktype = SOCK_STREAM;
        addresses[i].ai_protocol = IPPROTO_TCP; addresses[i].ai_addr = &endpoints[i];
        addresses[i].ai_addrlen = sizeof(endpoints[i]);
        addresses[i].ai_next = i + 1U < count ? &addresses[i + 1U] : NULL;
        plans[i].ready_delay = -1;
    }
}
static void failed(int error, unsigned opened) {
    CHECK(connect_http(8765, 42) == -1);
    CHECK(errno == error && close_calls == opened && frees == 1);
    CHECK(option_reads == 0 && option_writes == 0);
    for (unsigned i = 0; i < 3; ++i) CHECK(!live[i]);
}
static void success_cases(void) {
    reset(1);
    CHECK(connect_http(8765, 42) == 3);
    CHECK(live[0] && close_calls == 0 && waits == 0 && error_reads == 0 && frees == 1);
    CHECK(option_reads == 1 && option_writes == 1);
    static const int pending[] = {EINPROGRESS, EWOULDBLOCK, EALREADY};
    for (unsigned i = 0; i < sizeof(pending)/sizeof(pending[0]); ++i) {
        reset(1); plans[0].connect_error = pending[i]; plans[0].ready_delay = 125000;
        CHECK(connect_http(8765, 42) == 3);
        CHECK(now == 125000 && waits == 3 && error_reads == 1 && close_calls == 0 && frees == 1);
        CHECK(option_reads == 1 && option_writes == 1 && (flags[0] & O_NONBLOCK));
    }
    reset(2); plans[0].connect_error = ECONNREFUSED;
    CHECK(connect_http(8765, 42) == 4);
    CHECK(close_calls == 1 && !live[0] && live[1] && socket_calls == 2);
    reset(2); plans[0].socket_error = ENOMEM;
    CHECK(connect_http(8765, 42) == 4);
    CHECK(close_calls == 0 && socket_calls == 2 && live[1]);
    reset(1); plans[0].connect_error = EINPROGRESS; plans[0].ready_delay = 12000;
    interrupted_waits = 3;
    CHECK(connect_http(8765, 42) == 3 && now == 12000 && waits == 4);
}
static void failures(void) {
    reset(1); plans[0].socket_error = ENOMEM; failed(ENOMEM, 0);
    reset(1); plans[0].get_flags_error = EBADF; failed(EBADF, 1); CHECK(connect_calls == 0);
    reset(1); plans[0].set_flags_error = ENOSYS; failed(ENOSYS, 1); CHECK(connect_calls == 0);
    reset(1); plans[0].connect_error = ECONNREFUSED; failed(ECONNREFUSED, 1); CHECK(waits == 0);
    for (unsigned i = 0; i < 3; ++i) {
        reset(1); plans[0].connect_error = EINPROGRESS; plans[0].ready_delay = 10000;
        plans[0].so_error = ECONNRESET;
        plans[0].error_only = i == 1; plans[0].ready_error = i == 2;
        failed(ECONNRESET, 1); CHECK(error_reads == 1 && now == 10000);
    }
    reset(1); plans[0].connect_error = EINPROGRESS; plans[0].select_error = EBADF;
    failed(EBADF, 1); CHECK(error_reads == 0);
    reset(1); plans[0].connect_error = EINPROGRESS; plans[0].ready_delay = 1000;
    plans[0].getsockopt_error = ENOBUFS; failed(ENOBUFS, 1);
    reset(1); plans[0].connect_error = EINPROGRESS; plans[0].ready_delay = 1000;
    plans[0].error_only = true; failed(ECONNABORTED, 1);
    reset(0); failed(EHOSTUNREACH, 0);
    reset(1); dns_error = EAI_FAIL;
    CHECK(connect_http(8765, 42) == -1 && dns_calls == 1 && frees == 0 && socket_calls == 0);
}
static void deadlines(void) {
    reset(2); plans[0].connect_error = EINPROGRESS;
    failed(ETIMEDOUT, 1);
    CHECK(now == SOCKET_CONNECT_TIMEOUT_MS * 1000LL && socket_calls == 1);
    CHECK(waits == SOCKET_CONNECT_TIMEOUT_MS / SOCKET_CONNECT_POLL_MS);
    reset(2); plans[0].connect_error = plans[1].connect_error = EINPROGRESS;
    plans[0].ready_delay = 1234000; plans[0].so_error = ECONNREFUSED;
    failed(ETIMEDOUT, 2); CHECK(now == SOCKET_CONNECT_TIMEOUT_MS * 1000LL);
    reset(1); plans[0].connect_error = EINPROGRESS; always_interrupt = true;
    failed(ETIMEDOUT, 1); CHECK(now == SOCKET_CONNECT_TIMEOUT_MS * 1000LL);
    reset(1); plans[0].connect_error = EINPROGRESS;
    plans[0].ready_delay = SOCKET_CONNECT_TIMEOUT_MS * 1000LL;
    failed(ETIMEDOUT, 1); /* Readiness exactly at deadline is not published. */
    reset(1); dns_delay = 17000000; plans[0].connect_error = EINPROGRESS;
    failed(ETIMEDOUT, 1);
    CHECK(now == dns_delay + SOCKET_CONNECT_TIMEOUT_MS * 1000LL); /* DNS documented separately. */
}
static void cancellation(void) {
    reset(1); ++s_generation;
    CHECK(connect_http(8765, 42) == -1 && errno == ECANCELED && dns_calls == 0);
    reset(1); pause = true;
    CHECK(connect_http(8765, 42) == -1 && errno == ECANCELED && dns_calls == 0);
    reset(2); cancel_in_dns = true; failed(ECANCELED, 0); CHECK(socket_calls == 0);
    reset(2); cancel_in_connect = true; failed(ECANCELED, 1); CHECK(socket_calls == 1);
    reset(2); plans[0].connect_error = EINPROGRESS; cancel_at = 120000;
    failed(ECANCELED, 1); CHECK(now == 120000 && waits == 3 && socket_calls == 1);
    reset(2); plans[0].connect_error = EINPROGRESS; pause_at = 120000;
    failed(ECANCELED, 1); CHECK(now == 120000 && waits == 3 && socket_calls == 1);
    reset(1); plans[0].connect_error = EINPROGRESS; plans[0].ready_delay = 120000;
    cancel_at = 120000; failed(ECANCELED, 1); CHECK(error_reads == 0);
}
int main(void) {
    success_cases(); failures(); deadlines(); cancellation();
    puts("actual HTTP connect lifecycle PASS: nonblocking, SO_ERROR, deadline, EINTR, cancel, ownership");
    return 0;
}
