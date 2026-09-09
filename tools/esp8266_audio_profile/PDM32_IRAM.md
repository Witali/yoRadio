# Experimental PDM32 IRAM placement

`-DYORADIO_ESP8266_PDM32_IRAM=ON` is a separate, default-OFF CMake
experiment for standard I2S PDM32 only. It changes placement, not arithmetic:

- `i2s_pdm_pack32` moves from mapped flash to IRAM.
- Only `libgcc.a:_moddi3` moves from IRAM to mapped flash, including its
  literals. The exact original library object is linked; it is not replaced.
- All codec arena capacities remain unchanged, including the shared 16384-byte
  arena. No PCM, task-stack or DMA buffer sizes change.
- OFF registers no additional linker fragment and leaves the original layout.
  RCPDM, PDM64 and other output modes reject ON at configuration time.

## Why this object can move

The audited `esp8266-opus-live-join` map places `__moddi3` at `0x40101180`:
959 bytes of text plus 8 bytes of literals. Its only linked callers are
`sntp_sync_time` (`0x4025d830`) and `adjtime` (`0x4026c968`). Both already
execute from flash. `adjtime` masks interrupts, but neither caller disables
the flash cache. It is therefore not a cache-off helper on these call paths.
Do not generalize this mapping to all libgcc objects: PHY code uses others.

The automated guard checks the reference build's map cross-reference table,
the actual caller object relocations and flash addresses, and the SDK caller
sources for cache-disable operations. A newly linked caller fails this audit
rather than silently inheriting the exemption. These checks cover linked
code, not undocumented ROM callers or arbitrary future SDK changes.

Shrinking the arena is not an equivalent alternative. Native AAC needs two
8192-byte word allocations (`coef` and persistent `overlap`). Reducing capacity
by 512 bytes would spill the whole second allocation to DRAM: +8192 bytes.
Fixed target-aligned requirements are 15640 bytes for Helix MP3 and 11152
bytes for libmad; Opus's 22-case corpus peaks at 15600 bytes, which is a
measured corpus limit, not a universal bound for all possible packets.

## Reproduce without building firmware

```powershell
node --test tests/esp8266-pdm32-iram.test.js tests/esp8266-i2s-pdm-output.test.js
node tools/esp8266_audio_profile/check_pdm32_iram.cjs .build/esp8266-opus-live-join
```

The tool uses the existing build's SDK, configuration, library inventory and
linker fragments, then runs the real `ldgen.py` into a separate diagnostic
directory. It compiles the packer extracted verbatim from the production
source and links a minimal ELF using the generated script and original
libgcc archive. It does not compile firmware, generate an application image,
modify the reference build, flash, reset or contact a board.

Measured with pinned Xtensa GCC 8.4:

| Isolated link | OFF | ON |
|---|---:|---:|
| Packer instructions | 164 | 164 |
| Packer stack frame | 0 | 0 |
| IRAM span including probe/vector layout | 1084 B | 576 B |
| DRAM, including test-only globals | 24 B | 24 B |

The isolated net IRAM saving is **508 bytes**, including linker alignment.
The instruction/register sequence is identical except the relocated literal
address; the packer has no function calls. Full firmware alignment and free
heap must still be checked in the eventual ON map and on the board.

Host GCC/UBSan executes the real packer body in both modes: all 65536 PCM
values with six integrator seeds, then 100000 continuous randomized samples.
All **493216 output words and integrator states per mode** match the original
branching reference. The section attribute is exercised on the host too;
this is not merely a copied JavaScript model.

No physical speed improvement is claimed by these checks. Keep the option
OFF until a controlled output/stream A/B establishes CPU, underrun, heap and
reconnect behavior for the intended firmware.

## Independent builder switches

`build_i2s_pdm_production.ps1 -Diagnostic -Pdm32Iram` selects this placement.
The separate `-Pdm32Batch` switch selects
`YORADIO_ESP8266_PDM32_BATCH=ON` for the DMA-span batching experiment. It also
requires `-Diagnostic` and does not imply `-Pdm32Iram` or `-EnableOpus`.
Both switches default OFF and the builder explicitly passes their ON/OFF
values on every invocation, including after an earlier ON build. Manifests
record independent boolean `pdm32_iram` and `pdm32_batch` fields. Keep other
switches identical and vary only one experiment at a time for physical A/B.
