# ESP32-C3 flash-cache trace experiment

This test executes the actual Espressif RISC-V AAC decoder in QEMU and feeds
its flash accesses into three cache models. It measures **modelled traffic**,
not hardware cache misses, stall cycles or CPU utilization. It does not change
the saved empirical CPU coefficients.

## Models and measurement boundaries

- One unified, read-only 16 KiB cache, eight ways, 32-byte lines, 64 sets. Geometry
  follows [ESP32-C3 Datasheet, section 4.1.2.3](https://documentation.espressif.com/esp32-c3_datasheet_en.html).
- MMU writes at `0x600c5000` establish the shared IROM/DROM mapping. The plugin
  converts aliases to flash offsets and uses `physical_line % 64` as the set
  index. Physical tagging/indexing is a model assumption, not a verified
  reconstruction of the silicon's cache tag implementation.
- `continuous_lru` retains contents across calls, including flash accesses by
  the harness, logging, fixture copying and interrupts. One complete decode
  precedes the two measured passes. This is a warmed workload, not an all-hit
  cache; the decoder's working set can still cause replacement.
- `continuous_fifo` sees the same access sequence with FIFO replacement. LRU
  and FIFO are sensitivity scenarios; neither is asserted to be the hardware
  replacement policy, and they are not guaranteed bounds for other policies.
- `cold_call_lru` starts with an empty model before **every decoder call**,
  including parser-only calls. This is a synthetic full-eviction scenario,
  not a cache flush performed by the guest and not a guaranteed worst-case
  timing bound. It receives the same accesses inside each interval.
- Only instruction fetches and flash reads allocate lines. SRAM, ROM and MMIO
  bypass the model. PCM and the 2,048-byte input chunks are in internal RAM.
  Copying the fixture from flash warms the continuous models outside the
  measured interval. This differs from the earlier direct-flash 997-byte AAC
  microbenchmark and does not replace its saved instruction counts.
- RISC-V `addi x0,x0,imm` markers select cases (`0x6a0..0x6a2`), begin/end a
  call (`0x6b0/0x6b1`), and finish a pass (`0x6bf`). The counted interval includes
  counter reads, the end-marker fetch and a few harness instructions around the
  decoder. The begin-marker fetch is outside the interval. It excludes
  PCM checks, logging, input copying and voluntary sleeps. Tick interrupts
  inside the interval remain included. Line accesses count each touched line,
  including a fetch/read crossing a line boundary; they are not hardware bus
  transaction counters.
- Prefetch, cache locking, speculative fetch, bus arbitration, invalidation
  commands, overlapping refills and early restart are not simulated. MMU
  mapping changes clear the models conservatively. Firmware during the measured
  intervals does not intentionally change mappings or cache configuration.
- A miss adds a 32-byte model refill, immediately available. It adds **no delay
  to QEMU**. Evicting a C3 read-only line creates no writeback. The model must
  not be reused for a PSRAM writeback cache without target-specific changes.

This small emulator image has its own linker layout. Cache conflicts depend on
code/constant addresses, so its counts are not claims about the shipping image.
Wi-Fi/TLS traffic and physical audio-output activity are absent. The cold-call
scenario explores sensitivity; it does not reconstruct those missing tasks.

The plugin follows [QEMU's TCG plugin callbacks](https://www.qemu.org/docs/master/devel/tcg-plugins.html)
for executed instructions and successful memory accesses. It is single-vCPU,
RV32 system-emulation only, and uses the QEMU 9.2 plugin API. Compile it against
the headers of the QEMU binary used to run it.

## Build and repeat

1. In PowerShell, from `idf/esp32c3-oled-native`, create a separate emulator
   configuration. Enable Espressif AAC with AAC Plus, `YORADIO_QEMU_AAC_TEST`
   and `YORADIO_QEMU_CACHE_TEST`; leave `YORADIO_QEMU_AAC_PROFILE` disabled:

   ```powershell
   .\build-qemu.ps1 -BuildDirectory build-qemu-cache `
     -Sdkconfig build-qemu-cache/sdkconfig menuconfig
   .\build-qemu.ps1 -BuildDirectory build-qemu-cache `
     -Sdkconfig build-qemu-cache/sdkconfig
   .\run-qemu.ps1 -SkipBuild -BuildDirectory build-qemu-cache `
     -QemuExecutable C:\path\to\qemu-system-riscv32.exe `
     -QemuBiosDirectory C:\path\to\qemu\share\qemu
   ```

   Add `-DependencyRoot C:\Work\yoRadio\.idf` when sharing the SDK from another
   worktree. The last command creates `build-qemu-cache/qemu-flash.bin` and checks
   the workload with ordinary QEMU. It requires `QEMU_CACHE_PASS`, plus the
   existing OLED/audio/storage smoke checks. There is no device I/O or flashing.

2. Build a Linux/WSL copy of the yoRadio QEMU fork with SSD1306 and PCM support
   and `--enable-plugins`. The tested source revision is
   `413834d79a1ac46570cdf4839f136e3b9a8e6ffd`. Prepare its submodules as for a
   normal QEMU source build. Linux requires LF shell scripts and actual Git
   symlinks; a Windows checkout may represent symlinks as text files. Use a
   separate source/build directory, preserving the installed Windows emulator.

   With GCC, make, Ninja, Python, pkg-config, GLib and libslirp development headers
   installed, run from an empty build directory (replace source path):

   ```sh
   /path/to/qemu-source/configure --target-list=riscv32-softmmu \
     --enable-plugins --disable-docs --disable-tools --disable-guest-agent \
     --enable-slirp --disable-sdl --disable-gtk --disable-vnc --disable-curses \
     --disable-werror --disable-capstone --disable-rust
   ninja -j8 qemu-system-riscv32
   ```

   Keep the fork's ESP32-C3 ROM files available through `-L`/`--bios`; upstream
   QEMU without these custom devices cannot run this workload.

3. In Linux/WSL, from the yoRadio repository root, build the plugin and run twice:

   ```sh
   sh tools/codec_benchmark/cache/build-plugin.sh \
     /path/to/qemu-source .build/cache-plugin
   python3 tools/codec_benchmark/cache/run.py \
     --qemu /path/to/qemu-build/qemu-system-riscv32 \
     --bios /path/to/qemu/share/qemu \
     --plugin .build/cache-plugin/esp32c3_cache.so \
     --flash idf/esp32c3-oled-native/build-qemu-cache/qemu-flash.bin \
     --qemu-source-revision 413834d79a1ac46570cdf4839f136e3b9a8e6ffd \
     --output .build/cache-trace
   ```

   Use `/mnt/c/...` for Windows paths in WSL. The supplied revision is recorded
   provenance: obtain it from the source checkout with `git rev-parse HEAD`.
   The runner saves two serial logs, two plugin traces, summaries, waveform
   smoke output, exact commands and SHA-256 hashes. It rejects incomplete
   windows, lost MMU mappings, invalid counters and failed firmware checks.
   These are emulator-only images; do not flash them to a board.

4. Recheck saved evidence without rebuilding QEMU:

   ```sh
   python3 tests/test-esp32c3-cache-trace.py
   python3 tools/codec_benchmark/cache/analyze.py \
     --log tests/results/esp32c3-cache-qemu-20260930/run-1.log \
     --trace tests/results/esp32c3-cache-qemu-20260930/run-1.json \
     --output .build/cache-summary.json
   ```

`build-plugin.sh` also compiles and runs the cache-model unit checks: LRU/FIFO
replacement, shared instruction/data lines, crossing line boundaries, cold
reset, MMU aliases, invalid mappings, and SRAM/ROM/MMIO exclusion.

## Using the result

`refill_bytes = 32 * (instruction_misses + data_misses)` is model traffic. It
cannot be divided by nominal flash bandwidth to obtain CPU stalls: critical
word first, early restart and overlapping accesses matter. Host run duration
only describes the cost of tracing on the PC.

Use the continuous/cold difference to identify sensitivity to interference and
to design future board tests. A cache correction to the CPU estimate still
needs hardware reference and target stall measurements, or a separately
validated effective penalty model. The empirical coefficient already includes
the old workload's physical cache stalls; adding a full cache penalty to it
would count that cost twice. See the
[calibration report](../../../docs/ESP32C3_QEMU_CALIBRATION_20260930.md#cache-refill-and-eviction-costs).
