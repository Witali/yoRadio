#include <cstdlib>
#include <new>

#ifdef ESP_PLATFORM
#include "sdkconfig.h"
#include "esp_idf_version.h"
#if !CONFIG_IDF_TARGET_ESP32C2 || ESP_IDF_VERSION_MAJOR != 6 || ESP_IDF_VERSION_MINOR != 1
#error "Requalify the C2 nothrow allocation ABI for this target/SDK"
#endif
#if CONFIG_COMPILER_CXX_EXCEPTIONS || defined(__cpp_exceptions)
#error "Requalify nothrow handler exception propagation before enabling C++ exceptions"
#endif
#if CONFIG_HEAP_ABORT_WHEN_ALLOCATION_FAILS
#error "Nothrow allocation requires malloc to return NULL on allocation failure"
#endif
static_assert(sizeof(std::size_t) == 4, "The wrapped allocation symbols use RV32 size_t");
#endif

static void *allocate_nothrow(std::size_t bytes) noexcept
{
    /* Preserve malloc/free ownership, zero-size new and returning new-handler
     * retries without calling the SDK's throwing new implementation.
     * FIXED_FACTORY: 0x420a3a0a (native old ELF 0x420a413e) calls throwing
     * array new; with exceptions disabled, OOM reaches the abort-only exception
     * allocator instead of its null-result landing pad. Keep this correction
     * local to the two ordinary nothrow overloads in this no-exceptions build. */
    if (bytes == 0)
        bytes = 1;
    for (;;)
    {
        if (void *result = std::malloc(bytes))
            return result;
        std::new_handler handler = std::get_new_handler();
        if (handler == nullptr)
            return nullptr;
        /* A returning handler may free memory or replace/remove itself. Read
         * the current handler again after the next failed allocation. A
         * nonreturning handler retains its deliberate nonreturning behavior. */
        handler();
    }
}

extern "C" void *__wrap__ZnwjRKSt9nothrow_t(std::size_t bytes, const std::nothrow_t &) noexcept
{
    /* FIXED_FACTORY: use the shared null-on-failure path for scalar nothrow new. */
    return allocate_nothrow(bytes);
}

extern "C" void *__wrap__ZnajRKSt9nothrow_t(std::size_t bytes, const std::nothrow_t &) noexcept
{
    /* FIXED_FACTORY: array allocation must return null before any construction. */
    return allocate_nothrow(bytes);
}
