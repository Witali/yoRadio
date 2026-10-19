#pragma once

#include "esp_http_client.h"

/* Optional audited SDK extension. Same-task use only, after final synchronous
 * GET headers. Rejected states retain the buffer. Reuse keeps full TX capacity. */
esp_err_t yoradio_http_client_release_request_buffer(esp_http_client_handle_t client);
