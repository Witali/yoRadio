#pragma once
#include <stddef.h>
typedef unsigned socklen_t;
struct timeval {long tv_sec, tv_usec;};
#define SOL_SOCKET 0xffff
#define SO_RCVTIMEO 0x1006
#define SHUT_RD 0
#define getsockopt test_getsockopt
#define setsockopt test_setsockopt
#define shutdown test_shutdown
int test_getsockopt(int socket, int level, int option, void *value, socklen_t *size);
int test_setsockopt(int socket, int level, int option, const void *value, socklen_t size);
int test_shutdown(int socket, int how);
