#pragma once

#include "esp_err.h"
#include "esp_http_server.h"
#include "native_state.h"

// Requires CONFIG_HTTPD_WS_SUPPORT=y, both HTTPD_WS_*_HANDSHAKE_CB_SUPPORT=y,
// HTTPD_QUEUE_WORK_BLOCKING=n and finite
// HTTPD send_wait_timeout. Two WS clients share one coalesced HTTPD work item.
// A WS-only send override completes short writes with a one-second application
// frame deadline, using lwip_select without enabling VFS select. A slow client
// can delay another client until that deadline; physical timing remains to test.
// Its recv override gives handler header/mask/payload reads one shared second.
// HTTPD reads the opcode before dispatch; that read and SDK control reads each
// receive a finite fallback budget. These are separate from the handler budget.
// A text message may span frames, with interleaved control frames. Its total
// payload is bounded to 96 bytes and its assembly deadline to five seconds.
// Register /ws before a matching wildcard route. No worker exists until start.
esp_err_t websocket_service_register(httpd_handle_t server, native_state_t *state);
esp_err_t websocket_service_start(void);

// Stop the polling producer before httpd_stop(). No HTTPD/session workspace is
// freed here. Call server_stopped only AFTER httpd_stop() has joined HTTPD.
// A timeout leaves all static state intact; retry stop before resetting it.
esp_err_t websocket_service_stop(void);
esp_err_t websocket_service_server_stopped(httpd_handle_t server);
void websocket_service_notify_playlist_changed(void);

// Supported text commands: ping/getindex/getsystem/getactive, play=N,
// stop/toggle/prev/next, smartstart=0|1, volume=0..254, balance=-16..16,
// normalization=0|1, normgain=0..20, normtarget=-20..0, normtime=100..10000.
// Commands without a parameter also accept =1 for shared WebUI compatibility.
// Unknown/invalid commands return commandError without changing settings.
