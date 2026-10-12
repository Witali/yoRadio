#include "network.h"
#include "dns_packet.h"
#include <string.h>
#include <unistd.h>
#include "lwip/sockets.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static void dns_task(void *unused)
{
    /* Serve bounded captive-DNS replies only to peers on the setup subnet. */

    (void)unused;
    int socket_fd = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    if (socket_fd < 0)
    {
        vTaskDelete(NULL);
        return;
    }
    struct sockaddr_in address = {
        .sin_family = AF_INET, .sin_port = htons(53), .sin_addr.s_addr = htonl(INADDR_ANY)};
    if (bind(socket_fd, (struct sockaddr *)&address, sizeof(address)) < 0)
    {
        close(socket_fd);
        vTaskDelete(NULL);
        return;
    }
    for (;;)
    {
        uint8_t packet[512];
        struct sockaddr_in peer;
        socklen_t peer_length = sizeof(peer);
        int length =
            recvfrom(socket_fd, packet, sizeof(packet), 0, (struct sockaddr *)&peer, &peer_length);
        if (length < 0)
            continue;
        if (!network_ap_active() || (ntohl(peer.sin_addr.s_addr) & 0xffffff00u) != 0xc0a82b00u)
            continue;
        size_t response = captive_dns_reply(packet, length, sizeof(packet));
        if (response)
            sendto(socket_fd, packet, response, 0, (struct sockaddr *)&peer, peer_length);
    }
}

void dns_start(void)
{
    /* Start the setup network DNS responder task. */
    configASSERT(xTaskCreate(dns_task, "captive_dns", 3072, NULL, 2, NULL) == pdPASS);
}
