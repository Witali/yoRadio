# C3 public raw uint32 rate proposal

This is an independent SDK6.1/RV32 source proposal. No C compiler, SDK, QEMU, reference codec, Git or device operation was executed here. The synthetic host tests and Python/PowerShell source parsers add no target result. Canonical C3 source and all existing campaigns remain unchanged; the generic17-case SDK proposal is untouched.

The caller/protocol/controller derive from the qualified standalone CYD uint32-rate source in `.build/cyd-vorbis-uint32-rate-sdk-prep-01`. The C3 profile comes from the audited standalone raw8192 project, its completed `.build/c3-vorbis-format-baseline-01` records, and `tests/target/c3_vorbis_format_qemu`. Source diffs expose each adaptation. CYD/Xtensa qualification is evidence for the inherited algorithm, not a C3 result.

## Preserved test and C3 changes

The exact fixture SHA256 is `839febe9f12d7bc33e6afd8a9f0b16ee799f12d6c8ecb88188537b7ae8349378`; the canonical C3 and CYD fixture bytes match. All16 rates and their original order remain:48000,44100,32000,24000,22050,16000,12000,11025,8000,1,63999,64000,192000,2147483647,2147483648,4294967295. Every accepted case uses68 complete raw packets at S256/L2048 and a fresh original public vendor192000Hz golden handle plus a fresh checked handle.

Persistent public metadata is checked on every packet including primer, with exact rate/channel2/bits16, full consumption, exact expected PCM byte counts, per-packet vendor/checked byte equality,16-byte output guards, nonzero total PCM and checked close results. Zero rate requires the public header error separately. Handles remain opaque. The native prefix is `C3_VORBIS_RATE_`; coordinator and pinned worker are both actual CPU0, witnessed by xPortGetCoreID(), including every packet. Captured C3 logs are never translated into CYD logs.

The only caller algorithm deltas are the prefix, worker core assertion and worker affinity/error label. All19 protocol-test methods are retained with native C3/core0 expectations; the core method additionally rejects wrong-core priming and final packet witnesses. Four separate pure Windows argv/response methods exercise the C3 compiler context. The retained host gate ran23 methods and exited0; exact command, input hashes before/after, logs and exit facts are in `host-tests.command.json`. There is no compiler invocation in those tests. Synthetic response models are retained under `host-models/`; their compiler pathnames do not name created executables.

## Separate modes and controls

| CLI | Expected complete result | Acceptance flag |
|---|---|---|
| `--mode baseline` |14 decoded/2 unsigned rejects;952 packet pairs; `REGRESSION_REPRODUCED` | false |
| `--mode acceptance` |16 decoded;1088 packet pairs; `UINT32_RATE_ACCEPTED` | true only after an actual complete run |
| `--mode limited` |11 decoded/5 policy rejects;748 packet pairs; `LIMITED_POLICY_VERIFIED` | false; policy flag only |
| `--mode acceptance --control signed-validity` | exact `legal_unsigned_rate_open_required` at2147483648 after14 decoded prerequisites | false |
| `--mode limited --control signed-policy` | exact `limited_rate_rejection_required` at2147483648 after11 decoded +3 prior policy rejections | false |

Baseline requires each exact original signed guard once:

```c
  if(vi->rate>=64000 || ci->blocksizes[1]>4096)goto err_out;
  if(vi->rate<1)goto err_out;
```

Acceptance, limited and either control require the complete unsigned fix before a frozen control is made:

```c
  if((uint32_t)vi->rate>=64000 || ci->blocksizes[1]>4096)goto err_out;
  if((uint32_t)vi->rate<1)goto err_out;
```

The unchanged `rate_variant` function rejects mixed/unfixed/duplicated/unknown forms. A control restores only its named guard in the fresh frozen setup copy. The source projection changes no canonical file or ABI type. Limited mode adds `LIMIT_TO_64kHz=1` to the actual setup translation unit; normal modes require absence. The signed-validity expected failure requires the public `ESP_AUDIO_ERR_FAIL`/null-handle witness, so an allocation or generic nonzero result cannot substitute. No panic, interruption, timeout, arbitrary failure or partial protocol passes.

At source assembly the canonical C3 setup is still unsigned-rate-unfixed. Root must first execute/review the signed baseline, then separately integrate/review the two casts and own all acceptance/policy/control qualifications. No automatic canonical fix is present in this prep. Normal/controls use the selected candidate's frozen setup bytes and record their SHA; fixed output.c and C3 ABI identities remain pinned independently.

## Independent C3 profile

| Item | Required profile |
|---|---|
| SDK |6.1.0, commit `9a97f6c54ec638111ce55cd36581b3c192f15207`, tracked source clean before/after |
| Default SDK/tools | `C:/Work/yoRadio/.idf/v6.1-9a97f6c54ec6`, `C:/Work/yoRadio/.idf/tools-v6.1` |
| Compiler | RV32 GCC15.2.0_20251204, SHA `9a96e8e77c263d4f7f16c084e8a2dfe89dfa8598c31fd3f9b152db35ccbb2a74` |
| Target | ESP32-C3, ELF machine243, RV32,32-bit long/pointers,160MHz, unicore |
| Codec archive | `311caa814095b098e476b28e46d55623ef70c26b0d73d69ba5832e154ec8d909` |
| Simple archive identity guard | `232650ec81ae5e10ecbe1b2c86de2d1adf8f1b793f5ef343241c6e510db3e71f` |
| QEMU | `qemu-system-riscv32.exe`, SHA `a74f3324430b306618aa88a52649dbb93c32eac6d0b87926d335754346abbf0b` |
| ROM | `share/qemu/esp32c3-rom.bin`, SHA `0de1e65020e803bea0d7443dca149d61895e01fca3bb9c82d073234eebd73f99` |
| Flash recipe | DIO/40m/4MB; bootloader0x0, partition table0x8000, factory app0x10000 |

`platform-facts.json` retains the exact old source/terminal-record hashes behind these reused facts. Those earlier raw8192 records do not qualify the uint32 rates. The new controller checks the C3 compiler/nm, Python, CMake, Ninja, QEMU, ROM and both archive hashes before execution, captures compiler/build-tool identity before build, checks actual compiler/output identities afterward, and rechecks inputs/tools/config/image bytes at completion.

Top-level `set(COMPONENTS main)` precedes the SDK project include. The project builds only the public caller plus canonical C3 setup.c/output.c and its ABI, using the standalone raw helper and only raw open/decode wrappers. There is no canonical C3 enable helper to replace. The new project includes its own helper directly; it does not use the full C3 application or add simple/Ogg/AAC hooks. The helper preserves SDK/target/archive/output/ABI guards from the earlier C3 project and checks the frozen selected setup SHA passed by the controller's launcher. C3 output SHA remains `7e7a49a1ba68b2417514ab4b0adb37c9ed31e2d1b65032fa06dbf4b2830c25e2`; ABI SHA remains `dd26a294cf3887853e12174f3958ea9cccdaa9425ff6a7b21d46faa350bde61c`.

The C3-specific Windows helper is a copy, not an edit to the shared CYD helper. It uses CommandLineToArgvW, requires one direct compiler/source and exactly one outer `-c` and `-o` operand, removes only those output/compile flags and appends `-E -dM`. It preserves exactly one original @cflags argument. Only these observed four generated lines are accepted:

```text
-march=rv32imc_zicsr_zifencei
-mtune=esp-base
"-specs=<same-build>/specs/picolibc.specs"
-D__PICOLIBC_ERRNO_FUNCTION=__errno
```

Both cflags and nonempty same-build specs are snapshotted and hashed before/after the actual setup.c macro probe. Missing/arbitrary/nested/extra response files and wrong-architecture flags are rejected. Actual setup macros must attest C3/RV32/32-bit ABI, unicore160MHz, explicit0/1 mode flags and the expected cap presence/absence. Exactly one frozen caller and two candidate raw compile rows, ELF243 and public wrapper/vendor symbols are required.

SDK child stdout/stderr are asynchronously copied to retained files; all commands remain bounded and owned. Timeout/interruption invokes taskkill only for the owned process tree, then direct-child kill/reap fallback. QEMU uses `esp32c3,audiodev=quiet`, one CPU, the pinned ROM directory, headless display/monitor, none audio backend, `-nic none`, snapshot flash and stdio logs. The actual C3 flash recipe and chip must match before merge. Process success and exact native protocol are both required; timeout alone is never success.

## Root-owned commands

The meaningful pure host suite, already executed here, can be repeated from this prep:

```powershell
python -B -m unittest -v test_rate_protocol test_windows_compile_command
```

After source review, root may launch a **new** campaign from the task checkout with the pinned host Python; these are future invocations, not executed target results:

```powershell
python -B .build/c3-vorbis-uint32-rate-sdk-prep-01/run-c3-vorbis-uint32-rate-qemu.py --mode baseline --output .build/c3-vorbis-uint32-rate-baseline-01
python -B .build/c3-vorbis-uint32-rate-sdk-prep-01/run-c3-vorbis-uint32-rate-qemu.py --mode acceptance --output .build/c3-vorbis-uint32-rate-acceptance-01
python -B .build/c3-vorbis-uint32-rate-sdk-prep-01/run-c3-vorbis-uint32-rate-qemu.py --mode limited --output .build/c3-vorbis-uint32-rate-limited-01
python -B .build/c3-vorbis-uint32-rate-sdk-prep-01/run-c3-vorbis-uint32-rate-qemu.py --mode acceptance --control signed-validity --output .build/c3-vorbis-uint32-rate-validity-control-01
python -B .build/c3-vorbis-uint32-rate-sdk-prep-01/run-c3-vorbis-uint32-rate-qemu.py --mode limited --control signed-policy --output .build/c3-vorbis-uint32-rate-policy-control-01
```

`--candidate` defaults to canonical `idf/esp32c3-oled-native/main`; SDK/tool/codec/QEMU/PowerShell options remain explicit when needed. Keep the selected candidate, all input files and tools frozen through each actual terminal result. These are isolated public raw rate tests only: no hardware/audio/radio/network, target Ogg EOF/reset/ownership, allocator failure/OOM, AAC or private-state testing. FullG6 remains open.
