#define TARGET_C3 1
#include "host.h"
#include "web_ota.h"
#include "websocket_service.h"
#include "reboot.inc"
#define malloc host_malloc
#include "sdk-io.inc"
#undef malloc
#include "sdk-context.inc"
#include "sdk-cleanup.inc"
#include "native_ota_sink.c"
#include "target-policy.inc"
#define calloc host_calloc
#include "native_ota_http.c"
#undef calloc
#include "target.inc"
#include "ota_upload.c"
#include "platform.c"
#include "test.c"
