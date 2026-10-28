#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <limits>
#include <new>
#include <vector>

extern "C" void *__wrap__ZnwjRKSt9nothrow_t(std::size_t, const std::nothrow_t &) noexcept;
extern "C" void *__wrap__ZnajRKSt9nothrow_t(std::size_t, const std::nothrow_t &) noexcept;

static alignas(std::max_align_t) unsigned char arena[1024];
static std::vector<std::size_t> requests;
static std::vector<int> events;
static std::vector<void *> answers;
static std::new_handler current_handler;
static unsigned cases;

// Fail the process even when NDEBUG disables the C assertion macro.
static void require(bool condition)
{
    if (!condition) std::abort();
}

// Return a scripted allocation result and record the exact requested size.
void *smalltv_test_malloc(std::size_t bytes) noexcept
{
    requests.push_back(bytes); events.push_back(1);
    require(requests.size() <= answers.size());
    return answers[requests.size()-1];
}

// Re-read the currently installed handler after every failed allocation.
std::new_handler smalltv_test_get_new_handler() noexcept
{
    events.push_back(2); return current_handler;
}

// A returning handler leaves its callback installed for the successful retry.
static void returning_handler()
{
    events.push_back(3);
}

// A handler can decline further retries by removing itself before returning.
static void removing_handler()
{
    events.push_back(4); current_handler = nullptr;
}

// A handler can install another handler while the allocation still fails.
static void replacing_handler()
{
    events.push_back(5); current_handler = removing_handler;
}

// Reset all script state between the independent scalar and array cases.
static void reset(std::initializer_list<void *> result, std::new_handler handler = nullptr)
{
    requests.clear(); events.clear(); answers = result; current_handler = handler;
}

int main(int argc, char **argv)
{
    // Compile the production source separately; only malloc/get_new_handler
    // boundaries are substituted, not the allocation algorithm under test.
    require(argc == 2);
    const std::size_t sizes[] = {0,1,512,UINT32_MAX,std::numeric_limits<std::size_t>::max()};
    for (auto allocate : {__wrap__ZnwjRKSt9nothrow_t, __wrap__ZnajRKSt9nothrow_t})
    {
        for (std::size_t size : sizes)
        {
            reset({arena}); require(allocate(size,std::nothrow) == arena);
            require(requests == std::vector<std::size_t>{size ? size : 1});
            require(events == std::vector<int>{1}); ++cases;
            reset({nullptr}); require(allocate(size,std::nothrow) == nullptr);
            require(requests == std::vector<std::size_t>{size ? size : 1});
            require(events == std::vector<int>({1,2})); ++cases;
        }
        reset({nullptr,arena},returning_handler);
        require(allocate(512,std::nothrow) == arena);
        require(requests == std::vector<std::size_t>({512,512}));
        require(events == std::vector<int>({1,2,3,1})); ++cases;
        reset({nullptr,nullptr},removing_handler);
        require(allocate(0,std::nothrow) == nullptr);
        require(requests == std::vector<std::size_t>({1,1}));
        require(events == std::vector<int>({1,2,4,1,2})); ++cases;
        reset({nullptr,nullptr,nullptr},replacing_handler);
        require(allocate(7,std::nothrow) == nullptr);
        require(requests == std::vector<std::size_t>({7,7,7}));
        require(events == std::vector<int>({1,2,5,1,2,4,1,2})); ++cases;
    }
    FILE *report = nullptr; require(fopen_s(&report,argv[1],"wb") == 0 && report);
    std::fprintf(report,"{\"passed\":true,\"cases\":%u,\"pointer_bits\":%zu,\"exceptions_tested\":false}\n",
                 cases,sizeof(void *)*8);
    require(std::fclose(report) == 0);
    std::printf("PASS: %u nothrow allocation host cases\n",cases);
}
