#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "lwip/api.h"
#include "lwip/sockets.h"
#include "lwip/priv/sockets_priv.h"
#include "lwip/priv/tcp_priv.h"
#include "lwip/tcpip.h"
#include "lwip/stats.h"
#include "lwip/ip4.h"
#include "arch/sys_arch.h"

/* Delay the peer's final ACK for the LAST_ACK regression. All TCP state
 * transitions still come from real packets through the unmodified input API. */
static int hold_ack;
static struct pbuf *held_packet;
static struct netif *held_netif;
void __real_tcp_input(struct pbuf *, struct netif *);
void __wrap_tcp_input(struct pbuf *p, struct netif *netif) {
    struct tcp_hdr *header = p->payload;
    if (hold_ack && lwip_ntohs(header->dest) == 8080 && TCPH_FLAGS(header) == TCP_ACK) {
        assert(!held_packet);
        assert(pbuf_add_header(p, IP_HLEN) == 0);
        held_packet = p;
        held_netif = netif;
        return;
    }
    __real_tcp_input(p, netif);
}

unsigned int lwip_port_rand(void) { return 12345; }
static int pump_wait(sys_sem_t *sem, sys_mbox_t *mbox) {
    (void)sem; (void)mbox;
    assert(tcpip_thread_poll_one());
    return 0;
}
static void pump(void) {
    unsigned n = 0;
    while (tcpip_thread_poll_one()) assert(++n < 10000);
}
static struct tcp_pcb *pcb_of(int fd) {
    struct lwip_sock *sock = lwip_socket_dbg_get_socket(fd);
    assert(sock && sock->conn);
    return sock->conn->pcb.tcp;
}
int main(int argc, char **argv) {
    assert(argc == 2);
    int expire = strstr(argv[1], "expire") != NULL;
    int unread = strstr(argv[1], "unread") != NULL;
    int lastack = strcmp(argv[1], "lastack") == 0;
    int full = strcmp(argv[1], "full") == 0;
    setbuf(stdout, NULL);
    tcpip_init(NULL, NULL);
    /* Upstream's single-thread test OS requires explicit semaphore setup. */
    sys_arch_netconn_sem_alloc();
    test_sys_arch_wait_callback(pump_wait);
    int listener = lwip_socket(AF_INET, SOCK_STREAM, 0);
    assert(listener >= 0);
    struct sockaddr_in address = { .sin_family = AF_INET,
        .sin_port = PP_HTONS(8080), .sin_addr = { PP_HTONL(INADDR_LOOPBACK) } };
    assert(lwip_bind(listener, (struct sockaddr *)&address, sizeof(address)) == 0);
    assert(lwip_listen(listener, 4) == 0);
    int client = lwip_socket(AF_INET, SOCK_STREAM, 0);
    assert(client >= 0);
    assert(lwip_fcntl(client, F_SETFL, O_NONBLOCK) == 0);
    assert(lwip_connect(client, (struct sockaddr *)&address, sizeof(address)) == -1);
    assert(errno == EINPROGRESS);
    pump();
    int server = lwip_accept(listener, NULL, NULL);
    assert(server >= 0);
    assert(pcb_of(server)->state == ESTABLISHED);
    assert(lwip_send(server, "400 Bad Request", 15, 0) == 15);
    pump();
    if (lastack) {
        assert(lwip_shutdown(client, SHUT_WR) == 0);
        pump();
        assert(pcb_of(server)->state == CLOSE_WAIT);
        hold_ack = 1;
    }
    if (full) assert(lwip_close(server) == 0);
    else assert(lwip_shutdown(server, SHUT_WR) == 0);
    pump();
    char data[64];
    assert(lwip_recv(client, data, sizeof(data), 0) == 15);
    assert(memcmp(data, "400 Bad Request", 15) == 0);
    assert(lwip_recv(client, data, sizeof(data), 0) == 0);
    if (lastack) {
        assert(held_packet);
        assert(pcb_of(server)->state == LAST_ACK);
        assert(lwip_recv(server, data, sizeof(data), MSG_DONTWAIT) == 0);
        hold_ack = 0;
        assert(ip4_input(held_packet, held_netif) == ERR_OK);
        held_packet = NULL;
        pump();
        /* In the unfixed SDK, delayed close frees a PCB still owned by this
         * socket. Closing it below reproduces the board's double-release. */
    }
    if (unread) {
        assert(lwip_send(client, "remaining upload", 16, 0) == 16);
        pump();
    }
    assert(lwip_close(client) == 0);
    pump();
    if (!unread && !lastack && !full)
        assert(lwip_recv(server, data, sizeof(data), MSG_DONTWAIT) == 0);
    if (expire) {
        tcp_ticks += 2 * TCP_MSL / TCP_SLOW_INTERVAL + 1;
        tcp_slowtmr();
        assert(!tcp_tw_pcbs);
    }
    int holders[MEMP_NUM_TCP_PCB];
    struct tcp_pcb *owned[MEMP_NUM_TCP_PCB];
    for (unsigned i = 0; i < MEMP_NUM_TCP_PCB; ++i) {
        holders[i] = lwip_socket(AF_INET, SOCK_STREAM, 0);
        assert(holders[i] >= 0);
        owned[i] = pcb_of(holders[i]);
    }
    if (unread) {
        assert(lwip_recv(server, data, 16, MSG_DONTWAIT) == 16);
        assert(memcmp(data, "remaining upload", 16) == 0);
        assert(lwip_recv(server, data, sizeof(data), MSG_DONTWAIT) == 0);
    }
    if (!full) assert(lwip_close(server) == 0);
    pump();
    for (unsigned i = 0; i < MEMP_NUM_TCP_PCB; ++i) {
        assert(pcb_of(holders[i]) == owned[i]);
        assert(owned[i]->callback_arg == lwip_socket_dbg_get_socket(holders[i])->conn);
        assert(lwip_close(holders[i]) == 0);
    }
    assert(lwip_close(listener) == 0);
    pump();
    while (tcp_tw_pcbs) tcp_abort(tcp_tw_pcbs);
    assert(lwip_stats.memp[MEMP_TCP_PCB]->used == 0);
    netconn_thread_cleanup();
    printf("PASS: %s response/data/EOF/ownership and no retained TCP PCBs\n", argv[1]);
}
