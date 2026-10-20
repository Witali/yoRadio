# Qualified observations and limits

The final host campaign compiles the whole canonical early-MPI module and a
whole copy of the canonical CYD `app_main.c`. SDK, RTOS, display, GPIO names and
application services have explicit seams. The actual frozen board header
supplies task-stack values; GCC include traces demonstrate its use. Enabled and
disabled startups passed. Three exact ordering mutants, four invalid compile
profiles and seven CMake configurations were checked with strict compiler
warnings and ASan/UBSan. These host results establish ordering and configuration
behavior, not target mutex semantics.

The final target campaign uses the pinned ESP-IDF 6.0.2 checkout
`7101770dc6db2667b3c477cc31365dd1acd6db4e`, classic dual-core ESP32 QEMU, actual SDK
lock/queue/heap implementations and the frozen canonical module. Source pins,
tools/ROM hashes, compiler rows, images, external header identities and execution
bundles were captured before execution and checked afterward. Four variants
completed, with terminal exit status confirmed by the owning agent.

- The canonical minimal fixture observed no prior acquire of that MPI lock,
  a null initial handle and `lazy_at_fixture` allocation. Seventeen public
  acquire/release pairs preserved the same handle. Tasks pinned to cores 0 and 1
  completed 2000 protected increments with ownership and exclusion checks.
- The skip-acquire control produced exactly `warm_acquire_once`. Its separate
  public prewarm is explicitly control-only. The canonical fixture has no such
  prewarm. The skip-release control produced exactly `warm_release_once` and
  released the held lock only during fixture cleanup.
- The void-OOM fixture exhausted the actual `INTERNAL|8BIT` heap with real
  allocations. The real unmodified queue constructor returned null; its wrapper
  only observed the result. The runner required the actual SDK MPI-lock address,
  an abort resolving to `lock_init_generic` in `locks.c`, and the full expected
  acquire/prepare/`app_main` stack. A generic panic, timeout or missing completion
  was not accepted. This demonstrates the pinned SDK's fatal lazy-init failure
  in that isolated fixture, not successful OOM recovery.

The fixture invokes no cryptographic algorithm and has no network or physical
device interaction. Ordinary SDK boot initialization, including its existing
PSA/RNG initialization, remains unchanged; no claim is made that SDK boot itself
performs no cryptographic work. Reviews and archival verification executed no
cryptographic calculation.

The fixture's entry observation is not the actual radio's entry observation.
Production application exports and actual radio fresh-boot/pre-application
inspection remain pending. Physical OOM behavior, memory/fragmentation benefit,
latency, RF/DMA effects and board playback are unqualified. The feature remains
experimental and off by default. The earlier host01 board-profile claim and
prototype target reports do not supersede these final canonical scopes.
