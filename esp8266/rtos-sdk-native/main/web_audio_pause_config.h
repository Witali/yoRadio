#pragma once

/* CMake selects exactly one policy; other boards/builds retain old behavior. */
#ifndef YORADIO_ESP8266_WEB_AUDIO_PAUSE
#define YORADIO_ESP8266_WEB_AUDIO_PAUSE 0
#endif
#if YORADIO_ESP8266_WEB_AUDIO_PAUSE < 0 || YORADIO_ESP8266_WEB_AUDIO_PAUSE > 2
#error Invalid WebUI audio pause policy
#endif
#define WEB_AUDIO_PAUSE_ACK_MS 1000U
#define WEB_AUDIO_PAUSE_HOLD_MS 250U
#define WEB_AUDIO_PAUSE_IDLE_POLL_MS 20U
