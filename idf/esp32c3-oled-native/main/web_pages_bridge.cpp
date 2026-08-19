#define YORADIO_WEB_PAGES_ONLY
#define PROGMEM
#include "../../../yoRadio/src/core/netserver.h"

#include "web_pages_bridge.h"

extern "C" const char *yoradio_index_html(void) {
    return index_html;
}

extern "C" const char *yoradio_emptyfs_html(void) {
    return emptyfs_html;
}

extern "C" const char *yoradio_emergency_form(void) {
    return emergency_form;
}
