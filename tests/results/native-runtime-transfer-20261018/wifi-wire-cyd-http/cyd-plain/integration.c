#include "model.h"
#include "crypto.inc"
#include "native_httpd_headers.h"
#include "web_wifi.h"
#include "web_reboot.h"
#include "native_wifi_file.h"
#include "native_wifi_json.h"
#include "native_wifi_http.h"
#include "native_wifi_request_io.h"
#include "web_file_form.h"
#include "web_upload.h"
#include "network_service.h"
#include "platform-declarations.h"
#include "platform.c"
#include "reboot.inc"
#include "sdk-ws.inc"
#define httpd_req_recv sdk_req_recv
#include "sdk-txrx.inc"
#undef httpd_req_recv
int httpd_req_recv(httpd_req_t *r,char *data,size_t size) {if(request_deletes&&!workspace)++purge_receives;return sdk_req_recv(r,data,size);}
#define malloc response_malloc
#include "sdk-response.inc"
#undef malloc
#define httpd_req_delete sdk_req_delete
#include "sdk-parse.inc"
#undef httpd_req_delete
esp_err_t httpd_req_delete(struct httpd_data *hd) {++request_deletes;return sdk_req_delete(hd);}
#include "sdk-sess.inc"
#include "sdk-uri.inc"
#define stat(...) mapped_stat(__VA_ARGS__)
#define remove(...) mapped_remove(__VA_ARGS__)
#define rename(...) mapped_rename(__VA_ARGS__)
#include "file_transaction.c"
#define fopen(...) mapped_open(__VA_ARGS__)
#include "native_wifi_store.c"
#include "native_wifi_file.c"
#include "network.inc"
#undef fopen
#undef rename
#undef remove
#undef stat
#include "native_wifi_json.c"
#define calloc workspace_calloc
#define free workspace_free
#define native_web_transport_prepare_close observed_prepare_close
#include "native_wifi_request_io.c"
#include "native_wifi_http.c"
#undef native_web_transport_prepare_close
#undef free
#undef calloc
#include "target.inc"
#define fopen(...) mapped_open(__VA_ARGS__)
#define open(...) mapped_fd_open(__VA_ARGS__)
#define remove(...) mapped_remove(__VA_ARGS__)
#define native_wifi_erase observed_upload_erase
#include "upload.inc"
#undef native_wifi_erase
#undef remove
#undef open
#undef fopen
#include "native_wifi_public.h"
#include "static.inc"
#include "test.c"
