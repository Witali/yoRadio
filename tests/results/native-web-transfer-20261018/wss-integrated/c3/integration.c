#define TARGET_C3 1

#define INTEGRATION_TLS 1
#include "platform.h"
#include "psa/crypto.h"
#include "mbedtls/base64.h"
#include "native_httpd_headers.h"
#include "sdk-ws.inc"
#include "sdk-txrx.inc"
#include "sdk-parse.inc"
#include "sdk-sess.inc"
#include "sdk-uri.inc"
#include "application.inc"
#include "platform.c"
#include "tls_test.c"
