#pragma once
#include <stdio.h>
#include <stdlib.h>
#define LWIP_PLATFORM_DIAG(message) do { printf message; } while (0)
#define LWIP_PLATFORM_ASSERT(message) do { fprintf(stderr, "%s\n", message); abort(); } while (0)
