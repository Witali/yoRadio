# Checked Vorbis initialization

Enabled by `CONFIG_YORADIO_VORBIS_REPAIR` (default on). The CMake integration
refuses archives other than the two pinned Espressif 2.6.2 ESP32-C3 libraries.
This is an ownership/initialization repair; the original synthesis, MDCT,
windowing, floor/residue decode and PCM arithmetic remain linked.

## Source and ABI

`setup.c` adapts the setup routines from Xiph.Org Tremor, with its BSD license
retained in `COPYING`. Reference revision:
[Android Tremor 0ad0141e864cfbb130db4f22e279d421832e7336](https://android.googlesource.com/platform/external/tremor/+/0ad0141e864cfbb130db4f22e279d421832e7336/Tremor/).
The original files are `codebook.c`, `floor0.c`, `floor1.c`, `res012.c`,
`mapping0.c`, `info.c`, and `dsp.c`. The pinned vendor archive is not assumed
identical to that reference. Its consumers and cleanup routines were checked
against disassembly/decompilation before introducing the typed bridge.

Private structures in `../vorbis_repair_abi.h` and `simple.c` have compile-time
size/offset assertions for RV32. Calls are redirected by symbol, never by
absolute addresses. Wrapping registration is necessary because the original
Vorbis registration routine stores its own open callback from the same object.

## Ownership changes

- Allocate zeroed structures; check each allocation before use. Publish a
  decoder handle only after both headers and the DSP state are ready.
- Clear partially initialized codebooks, floor, residue, mapping and DSP
  arrays through one owner chain. Temporary setup arrays use checked heap
  allocations instead of unbounded stack allocations.
- Keep Huffman table/workspace sizing based on **used** entries, as in the
  pinned library. Validate each node against the actual allocated capacity.
  Unused entries do not consume tree nodes (Vorbis I specification, section 3).
- Check the Ogg simple-decoder allocation before initializing it. Other
  simple-decoder types still use their original initialization routine.
- Preserve Ogg `NO_MEM` and failed packet/header reallocations through a
  task-local failure scope around one process call. The vendor's outer parser
  can otherwise swallow the inner Ogg error. A four-byte TLS pointer isolates
  tasks; restoring the previous scope supports nesting. On captured failure,
  report `ESP_AUDIO_ERR_MEM_LACK` and publish no PCM from that call. The caller
  must close the failed handle, as the audio service now does.
- Registration rollback and the independent PCM owner are shared with the
  firmware via `decoder_registration.c` and `decoder_resources.h`.

The simple-decoder process/close implementation and packet-state machine are
unchanged. Output resize/retry and exact EOF trimming are separate plan steps.
This is not a complete malformed-input audit or a physical-radio qualification.

## Tests

Use the original lifecycle overlay for the retained unmodified baseline;
append `sdkconfig.qemu-vorbis-repair.defaults` for this implementation. Run
`tools/codec_benchmark/run_vorbis_lifecycle.py` with the resulting build.
The suite checks 100 decode/close cycles, every allocation on the fixture's
successful path, four malformed headers, registration rollback, and failed
open followed by repeated release and a valid decode. It compares PCM bytes,
sample count and SHA-256 with the retained original decoder output.

These cases do not cover all legal codebooks, rates, channel layouts, malformed
inputs or network schedules; see `docs/ESP32C3_VORBIS_REPAIR_PLAN.md`.
