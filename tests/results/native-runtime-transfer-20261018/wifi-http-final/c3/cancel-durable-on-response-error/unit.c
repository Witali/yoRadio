#define TARGET_C3 1
#include "host.h"
#include "web_wifi.h"
#include "websocket_service.h"
#include "native_wifi_file.h"
#include "native_wifi_json.h"
#include "native_wifi_http.h"
#include "web_file_form.h"
#include "reboot.inc"
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
#define malloc response_malloc
#include "sdk-io.inc"
#undef malloc
#include "sdk-context.inc"
#include "sdk-cleanup.inc"
#define calloc workspace_calloc
#define free workspace_free
#include "native_wifi_request_io.c"
#include "native_wifi_http.c"
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
#ifdef TARGET_C3
#include "native_wifi_public.h"
#include "static.inc"
#endif
#include "platform.c"
#include "test.c"
