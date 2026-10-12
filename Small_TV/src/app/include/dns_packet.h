#pragma once
#include <stddef.h>
#include <stdint.h>
size_t captive_dns_reply(uint8_t *packet,size_t length,size_t capacity);
