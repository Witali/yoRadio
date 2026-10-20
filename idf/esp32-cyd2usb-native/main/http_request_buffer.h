#pragma once

#include "esp_http_client.h"

/* Audited SDK6.0.2 extension. Call only from the HTTP handle's owning task,
 * after accepting final synchronous GET headers. Rejected states retain their
 * buffer; later requests restore the original configured TX capacity. */
esp_err_t yoradio_http_client_release_request_buffer(esp_http_client_handle_t client);
