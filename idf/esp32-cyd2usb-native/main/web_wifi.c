#include "web_wifi.h"

#include <stdatomic.h>
#include "native_wifi_http.h"
#include "network_service.h"
#include "web_reboot.h"

static atomic_bool s_wifi_active;
typedef struct { web_reboot_lease_t reboot; } wifi_edit_context_t;

void web_wifi_activate(void) { atomic_store(&s_wifi_active, true); }
void web_wifi_deactivate(void) { atomic_store(&s_wifi_active, false); }

static esp_err_t wifi_admit(void *opaque) {
    wifi_edit_context_t *context = opaque;
    if (!atomic_load(&s_wifi_active)) return ESP_ERR_INVALID_STATE;
    return web_reboot_reserve(&context->reboot);
}
static void wifi_finished(void *opaque, bool committed) {
    wifi_edit_context_t *context = opaque;
    if (committed) (void)web_reboot_commit(&context->reboot, 750);
    else if (context->reboot.epoch) (void)web_reboot_cancel(&context->reboot);
}

esp_err_t web_wifi_edit_handler(httpd_req_t *request) {
    wifi_edit_context_t context = {0};
    const native_wifi_http_config_t config = {
        .edit = network_service_wifi_edit, .admit = wifi_admit,
        .finish = wifi_finished, .context = &context,
    };
    return native_wifi_http_edit(request, &config);
}
esp_err_t web_wifi_info_handler(httpd_req_t *request) {
    if (!atomic_load(&s_wifi_active)) {
        httpd_resp_set_hdr(request, "Cache-Control", "no-store");
        httpd_resp_set_status(request, "503 Service Unavailable");
        return httpd_resp_sendstr(request, "Wi-Fi service unavailable");
    }
    return native_wifi_http_info(request, network_service_wifi_metadata);
}
