#include <cstdlib>
#include <new>

// This forced include affects only the wrapper translation unit in host tests.
// Keep production control flow intact while replacing its two SDK boundaries.
void *smalltv_test_malloc(std::size_t bytes) noexcept;
std::new_handler smalltv_test_get_new_handler() noexcept;
namespace std {
using ::smalltv_test_malloc;
using ::smalltv_test_get_new_handler;
}
#define malloc smalltv_test_malloc
#define get_new_handler smalltv_test_get_new_handler
