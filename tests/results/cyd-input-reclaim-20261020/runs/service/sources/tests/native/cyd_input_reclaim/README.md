# CYD idle-input reclaim host service qualification

The runner freezes the complete production `native_input_reclaim.c/.h` and the
canonical shared `adaptive_input.c/.h` before compilation. The queue compiles as
a separate translation unit with explicit malloc/calloc/free substitutions;
the unmodified service and fixture compile as their own translation units.
No private registry, owner, pin, queue-slot or lifecycle state is written.

The original TLS allocator is an explicit host seam. Its failures are scripted,
and its successful results are ordinary libc calloc allocations released by
ordinary libc free. This proves wrapper forwarding/retry/zeroing/free ownership
against that seam, not actual SDK OOM, TLS traffic or target ABI. The artificial
non-NULL malformed-result case tests transparent forwarding of a real callee
result; it does not claim that the ESP-IDF allocator accepts overflow/zero.

Public queue leases protect real WRITING, READY and READING payloads, FIFO,
borrowed control storage and the current floor. A guarded heap ledger rejects
freeing any held lease before a sanitizer could turn it into a crash. Scripted
failure/recovery, unbound and ISR bypass, owner conflicts, explicit detach
retry, and admission/rebind denial are driven only through public APIs.

Pthread barriers pause existing pins before release, inside the queue's free
after unlocking, and inside the original retry callee. The lifecycle owner must
see BUSY until those calls drain; last-unpin does not clear a retiring owner.
A condition-variable barrier makes a separate producer restore the pool after
every retry. Even from a sparse resident pool, the frozen target-minus-minimum
budget is the only retry budget; repeated producer refill cannot extend it.
Another case concurrently transfers10000 checksummed FIFO packets while two
TLS callers fail/reclaim and the producer restores storage.

Every queue/registry critical entry rejects nesting/ISR access, and heap/free/
RTOS operations assert that neither production lock is held. Real pthread
mutexes model critical sections; they do not qualify ESP32 interrupt masking,
spinlock timing or hardware scheduling. ASan/UBSan positives and exact named
semantic mutants are required; crashes/timeouts never count as detected mutants.
Host tests do not prove native_health callback integration, startup publication,
actual SDK allocation failure, firmware linking/placement, DMA or board margin.
Those gates are separate. No numeric pool/TLS/headroom/IRAM policy is changed.
