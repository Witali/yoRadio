#pragma once
/* Real pinned esp-lwIP TCP/netconn/socket code; deterministic upstream test OS. */
#define NO_SYS 0
#define SYS_LIGHTWEIGHT_PROT 0
#define TCPIP_THREAD_TEST
#define LWIP_TESTMODE 1
#define LWIP_TCPIP_CORE_LOCKING 0
#define LWIP_NETCONN 1
#define LWIP_SOCKET 1
#define LWIP_COMPAT_SOCKETS 0
#define LWIP_NETCONN_FULLDUPLEX 1
#define LWIP_NETCONN_SEM_PER_THREAD 1
#define LWIP_SO_LINGER 0
#define LWIP_SO_SNDTIMEO 1
#define LWIP_SO_RCVTIMEO 1
#define LWIP_HAVE_LOOPIF 1
#define LWIP_NETIF_LOOPBACK 1
#define LWIP_IPV6 0
#define LWIP_DNS 0
#define LWIP_DHCP 0
#define LWIP_UDP 0
#define LWIP_RAW 0
#define LWIP_ARP 0
#define LWIP_ETHERNET 0
#define IP_REASSEMBLY 0
#define IP_FRAG 0
#define MEM_ALIGNMENT 8
#define MEM_LIBC_MALLOC 1
#define MEMP_MEM_MALLOC 1
#define MEMP_OVERFLOW_CHECK 0
#define MEMP_NUM_TCP_PCB 16
#define MEMP_NUM_NETCONN 32
#define TCP_MSS 1460
#define TCP_WND (8 * TCP_MSS)
#define TCP_SND_BUF (4 * TCP_MSS)
#define LWIP_STATS 1
#define MEMP_STATS 1
#define ESP_LWIP 1
