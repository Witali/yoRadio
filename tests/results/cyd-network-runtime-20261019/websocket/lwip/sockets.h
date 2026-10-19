#pragma once
#include <sys/types.h>
#include <sys/select.h>
#define SHUT_RDWR 2
#define MSG_DONTWAIT 8
#define MSG_PEEK 2
int shutdown(int,int);
ssize_t lwip_send(int,const void *,size_t,int);
ssize_t lwip_recv(int,void *,size_t,int);
int lwip_select(int,fd_set *,fd_set *,fd_set *,struct timeval *);
