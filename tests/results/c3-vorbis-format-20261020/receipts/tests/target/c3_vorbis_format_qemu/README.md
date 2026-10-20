# ESP32-C3 public raw Vorbis format regression

This isolated SDK6.1/RV32 project checks public `esp_vorbis_dec_open/decode/close`
against the same actual vendor synthesis. It compiles only the candidate's
`vorbis_repair/setup.c`, `vorbis_repair/output.c` and C3 ABI header. The caller
keeps decoder handles opaque. It does not use the radio application, simple/Ogg
parser, reset/EOF cases, allocator injection, private AAC or hardware audio.

`main.c` and `fixture.h` are byte-identical to the reviewed C3 baseline caller.
The fixture SHA256 is
`839febe9f12d7bc33e6afd8a9f0b16ee799f12d6c8ecb88188537b7ae8349378`.
Coordinator and worker are CPU0. Every packet requires complete consumption,
public rate/channel/bits (including priming), 16-byte output canaries and exact
PCM bytes against the original vendor decoder. The vendor must first decode all
68 high-rate8192 packets with nonzero PCM and 66 full-size outputs.

Run the eight synthetic host protocol tests from the repository root:

```powershell
& $hostPython -B tests/test-c3-vorbis-format-protocol.py
```

`tests/c3_vorbis_format_protocol.py` reads native `C3_VORBIS_FORMAT_` lines directly;
it never translates captured logs. `validate_log(log, scope, control, header,
returncode=actual_returncode, timed_out=actual_timeout_flag)` requires both
keyword-only process facts. It returns observations, not a qualification.
Feed both retained stdout and stderr. An interrupted/unknown/timeout/nonzero
process, panic, incomplete or out-of-order protocol is a nonpass.

| scope / control | build rejection flag | lines | paired packets | interpretation |
|---|---:|---:|---:|---|
| baseline / None | 1 | 285 | 204 | REGRESSION_REPRODUCED; acceptance false |
| acceptance / None | 0 | 421 | 340 | Full counted candidate-format acceptance |
| acceptance / old-guard | 0 | 279 | 204 | Exact legal_candidate_open_required after all prerequisites |

Both header-error groups require public `ESP_AUDIO_ERR_FAIL` and a null handle;
`header_error=1` attests that check. Any other control failure/panic/timeout fails.
The old-guard control changes only frozen setup.c, restoring the inherited
restriction exactly. Independently compare baseline/candidate/control bytes;
never patch a live source or relabel a baseline diagnostic as acceptance.

## Durable manual rerun

Use a fresh `.build/<campaign>` and freeze this project, validator, public headers,
three candidate files and tool/archive identities before execution. Pin the
reviewed setup SHA explicitly with `FORMAT_SETUP_SHA256`; do not derive an
unreviewed expected value from a live file. Output/ABI and the two C3 archives
remain fixed in main/CMakeLists.txt. `C3_VORBIS_CANDIDATE` must name the frozen
variant directory containing `vorbis_repair/{setup,output}.c` and
`vorbis_repair_abi.h`. Keep sources/tools unchanged through terminal review.

The actual baseline used SDK commit
`9a97f6c54ec638111ce55cd36581b3c192f15207` at
`C:/Work/yoRadio/.idf/v6.1-9a97f6c54ec6`, tools directory
`C:/Work/yoRadio/.idf/tools-v6.1`, and the pinned installed codec component
`C:/Work/yoRadio/.idf/esp-adf-libs/esp_audio_codec`. The direct compiler is
`tools/riscv32-esp-elf/esp-15.2.0_20251204/riscv32-esp-elf/bin/riscv32-esp-elf-gcc.exe`
under that tools directory, SHA256
`9a96e8e77c263d4f7f16c084e8a2dfe89dfa8598c31fd3f9b152db35ccbb2a74`.
Activate that SDK, require its clean/reviewed source and actual RV32 tools, disable
component downloads and ccache, then invoke its Python/idf.py with the frozen
project and fresh build/config paths. The meaningful idf.py arguments are:

```text
-C <campaign>/sources/project -B <campaign>/build --no-ccache
-D IDF_TARGET=esp32c3 -D IDF_TOOLCHAIN=gcc
-D SDKCONFIG=<campaign>/sdkconfig
-D SDKCONFIG_DEFAULTS=<campaign>/sources/project/sdkconfig.defaults
-D FORMAT_EXPECT_LOW_RATE_REJECTION=<1 baseline; 0 acceptance/control>
-D FORMAT_SETUP_SHA256=<separately reviewed frozen setup SHA256> build
```

Retain bounded owned-command receipts, exact argv/cwd/environment, SDK child
stdout/stderr, generated config, compile database, link/symbol evidence and
source/tool hashes. After build require ELF machine243 (RISC-V), C3/one-core
config, only the two raw wrappers and this isolated source list.

For setup.c's actual compile-database row, reuse `windows_argv` from
`tests/windows_compile_command.py` (CommandLineToArgvW). Do not pass C3 through
that helper's CYD-only six-line response validator. The established manual C3
procedure verifies the direct compiler/source/cwd, exactly one outer `-c` and
`-o`+operand, removes only those options, appends `-E -dM`, and leaves every
remaining argument, including the original `@.../build/toolchain/cflags`, intact.
Accept exactly one such response at that build path, with precisely four lines:

```text
-march=rv32imc_zicsr_zifencei
-mtune=esp-base
"-specs=<same-build>/specs/picolibc.specs"
-D__PICOLIBC_ERRNO_FUNCTION=__errno
```

Reject arbitrary/nested/additional response inputs. Snapshot/hash both cflags
and nonempty same-build picolibc.specs before/after the probe, together with the
actual row/argv, config and compiler identity. Require successful macro output
with ESP_PLATFORM and CONFIG_IDF_TARGET_ESP32C3 enabled and LIMIT_TO_64kHz absent;
checking only the harness translation unit is insufficient.

Require actual flasher_args.json to match DIO/4MB/40m and exactly bootloader0x0,
partition table0x8000, factory app0x10000 before a separate local merge. A changed
recipe needs review. Produce a separate 4MiB fullflash; never overwrite firmware.
The proven emulator executable is
`C:/Work/QEMU-ESP32/bin/qemu-system-riscv32.exe`, SHA256
`a74f3324430b306618aa88a52649dbb93c32eac6d0b87926d335754346abbf0b`.
Its C3 ROM SHA256 is
`0de1e65020e803bea0d7443dca149d61895e01fca3bb9c82d073234eebd73f99`.
Use a bounded owned process (120s limit), raw stdout/stderr and terminal receipt:

```text
qemu-system-riscv32.exe -audiodev none,id=quiet -M esp32c3,audiodev=quiet
-smp 1 -L C:/Work/QEMU-ESP32/share/qemu -display none -monitor none
-serial stdio -no-reboot -snapshot -nic none
-drive file=<campaign>/qemu-flash.bin,if=mtd,format=raw
```

On timeout/interruption stop/reap only the owned process and preserve a nonpass.
A zero exit alone never qualifies a result. Validate the whole counted native
protocol using the actual owned-process facts, then recheck all frozen inputs.
This gate concerns public raw format support on the pinned C3 vendor/SDK/ABI;
it makes no radio, Ogg, physical board, network, resource or CYD claim.
