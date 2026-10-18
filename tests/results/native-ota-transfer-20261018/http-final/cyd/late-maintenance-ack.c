#include "host.h"
#include "web_ota.h"
#include "web_reboot.h"
#include "reboot.inc"
#define malloc host_malloc
#include "sdk-io.inc"
#undef malloc
#include "sdk-context.inc"
#include "sdk-cleanup.inc"
#include "native_ota_sink.c"
#include "native_ota_form.c"
#define calloc host_calloc
#include "native_ota_http.c"
#undef calloc
#include "late-maintenance-ack.inc"
#include "platform.c"
#include "test.c"
