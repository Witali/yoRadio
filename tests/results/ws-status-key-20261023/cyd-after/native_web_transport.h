#pragma once
#include "esp_http_server.h"
#include <sys/types.h>
ssize_t native_web_transport_send(httpd_handle_t,int,const void *,size_t,int,bool *);
ssize_t native_web_transport_recv(httpd_handle_t,int,void *,size_t,int,bool *);
void native_web_transport_shutdown(httpd_handle_t,int,bool);
