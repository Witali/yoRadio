# CYD public raw uint32 rate SDK proposal

Source-only proposal, not an executed SDK campaign. No codec, compiler, SDK, QEMU, Git, reference decoder or target process was run during assembly. Python and PowerShell source parsing adds no build/runtime result. Root owns the first actual baseline and all later qualification.

The controller is adapted from `.build/cyd-vorbis-block-sdk-prep-01/run-cyd-vorbis-blocks-qemu.py` (SHA256 `0fa8a346a114e7ccf368cdd0957b1425a9d1e20369018ecbb1d81552fcd76a40`). `runner-adaptation.diff` records the exact source delta. The Windows compilation-command helper, raw-only CMake helper, isolated defaults/partition table and Kconfig are byte-identical copies of that audited infrastructure. `launcher-adaptation.diff` and the two CMake diffs expose the remaining project changes.

The caller/protocol are exact frozen copies from `.build/cyd-vorbis-uint32-rate-caller-prep-01`: main SHA256 `3d97389d3e8befd2ebf6642172cbe9f285d12954aed0b0bd8168d832ba3d7483`, protocol `53a9c81ae3293e99c0ea0fe9ef48b62ee2b78fde184fd080151b83f34dc9da79`. That prep's synthetic host gate02 recorded19 methods/exit0; no host tests were rerun here. Its source pins SHA256 is `9db2b55d3931e7d4e498a7e131f6d6e17b9d40716e0f0d87826a58c56fad74a5`. The copied test source is retained for review, not target qualification.

## Fixed inputs and scope

`target/cyd_vorbis_uint32_rate_qemu/main/fixture.h` is the exact canonical `tests/target/cyd_vorbis_format_qemu/main/fixture.h`, SHA256 `839febe9f12d7bc33e6afd8a9f0b16ee799f12d6c8ecb88188537b7ae8349378`. The controller requires both that canonical source and its frozen project copy to match. It also freezes and checks the exact `AUDIT.md`/`sources.json` bytes in `.build/cyd-vorbis-public-header-audit-01`. That source audit is context for the rate field, not a new decoding or reference result; its historical setup identity need not equal a later candidate's setup bytes.

The public caller preserves the16-rate order from its independent prep: the nine advertised rates48000..8000, then1,63999,64000,192000,2147483647,2147483648,4294967295. Every accepted case compares the fixed S256/L2048 packets against a fresh original public vendor handle at192000Hz, using fresh checked handles, persistent per-handle metadata checked every packet including primer, complete consumption, expected PCM sizes, exact PCM and16-byte output guards. Rate0 is rejected separately. It witnesses actual coordinator0/worker1. The signed-validity control requires the public header-error witness, so another nonzero error cannot substitute for the restored rate guard.

Only the canonical setup.c/output.c and pinned ABI are used. The frozen variant replaces the canonical enable helper with the audited raw-only helper, which compiles those two files and wraps only public raw open/decode. The original canonical helper is frozen unchanged in `sources/candidate`; no canonical helper is edited. There is no simple decoder, target Ogg, EOF/reset/ownership hook, allocator fault injection, AAC, radio, network, physical device or audio-output qualification.

## Explicit modes and controls

| CLI | Required candidate guards before variant | Expected semantic result |
|---|---|---|
| `--mode baseline` | both original signed forms | `REGRESSION_REPRODUCED`,14 decoded/2 unsigned rejections,952 packet pairs |
| `--mode acceptance` | both complete unsigned fixes | `UINT32_RATE_ACCEPTED`,16 decoded,1088 packet pairs |
| `--mode limited` | both complete unsigned fixes | `LIMITED_POLICY_VERIFIED`,11 decoded/5 policy rejections,748 packet pairs |
| `--mode acceptance --control signed-validity` | both complete unsigned fixes | restores only validity guard; exact `legal_unsigned_rate_open_required` at2147483648 after all14 prior rates |
| `--mode limited --control signed-policy` | both complete unsigned fixes | restores only optional-cap comparison; exact `limited_rate_rejection_required` at2147483648 after11 decoded +3 prior policy rejections |

The original guards are exactly:

```c
  if(vi->rate>=64000 || ci->blocksizes[1]>4096)goto err_out;
  if(vi->rate<1)goto err_out;
```

The complete fix required for acceptance/limited/control sources is exactly:

```c
  if((uint32_t)vi->rate>=64000 || ci->blocksizes[1]>4096)goto err_out;
  if((uint32_t)vi->rate<1)goto err_out;
```

Each must occur once. Mixed, duplicated, differently spelled or unfixed acceptance/control sources are rejected before SDK execution. A control changes only its named guard in the frozen copy, never canonical source. The two restored control failures are expected diagnostic results only when the strict protocol and actual zero-exit terminal process both match. `rate_acceptance_qualified` is true only for normal acceptance; baseline, policy-only and controls cannot set it. No mode closes fullG6.

## Root-owned launch

From the task checkout, use a fresh campaign for each invocation. The SDK/tool/QEMU options have the same defaults as the audited block controller; supply explicit installed paths when they are absent from PATH. These are proposed commands, **not executions recorded by this prep**:

```powershell
python -B .build/cyd-vorbis-uint32-rate-sdk-prep-01/run-cyd-vorbis-uint32-rate-qemu.py --mode baseline --output .build/cyd-vorbis-uint32-rate-baseline-01
python -B .build/cyd-vorbis-uint32-rate-sdk-prep-01/run-cyd-vorbis-uint32-rate-qemu.py --mode acceptance --output .build/cyd-vorbis-uint32-rate-acceptance-01
python -B .build/cyd-vorbis-uint32-rate-sdk-prep-01/run-cyd-vorbis-uint32-rate-qemu.py --mode limited --output .build/cyd-vorbis-uint32-rate-limited-01
python -B .build/cyd-vorbis-uint32-rate-sdk-prep-01/run-cyd-vorbis-uint32-rate-qemu.py --mode acceptance --control signed-validity --output .build/cyd-vorbis-uint32-rate-validity-control-01
python -B .build/cyd-vorbis-uint32-rate-sdk-prep-01/run-cyd-vorbis-uint32-rate-qemu.py --mode limited --control signed-policy --output .build/cyd-vorbis-uint32-rate-policy-control-01
```

`--candidate` defaults to canonical `idf/esp32-cyd2usb-native/main`; an explicit candidate must remain inside the repository. Other options are `--idf`, `--idf-tools`, `--codec`, `--qemu`, `--powershell`. Complete the signed baseline before integrating the two unsigned casts. Keep canonical source frozen throughout each actual campaign. The controller snapshots inputs before building and rejects any changed input/tool/variant/config/log/image byte before recording success.

Top-level `set(COMPONENTS main)` precedes `project.cmake`, limiting the standalone closure to main and its declared dependencies. The mode check follows `idf_component_register`, respecting ESP-IDF's early requirements scan. The launcher passes explicit RATE_MODE; target definitions are explicit0/1. Limited mode adds `LIMIT_TO_64kHz=1` to the component containing the actual candidate setup.c. No other mode adds it.

The controller preserves SDK6.0.2 commit `7101770dc6db2667b3c477cc31365dd1acd6db4e`, clean SDK checks before/after, both audited ESP32 archives, runtime/ROM/tool/header snapshots, compiler/nm identity before/after build, ELF machine94, public wrapper symbols, the exact single frozen caller compile row and exactly two candidate translation units. The actual setup compile command is parsed with CommandLineToArgvW. The original six-line generated `@toolchain/cflags` argument remains intact for GCC; its exact reviewed flags/quoted specs path and picolibc.specs bytes are bound before/after macro probing. Actual macros must show ESP32/repair,240MHz, two cores, correct mode values, and cap presence1 only for limited mode.

The flash recipe must be DIO/40m/4MB with exactly bootloader0x1000, partition table0x8000 and factory app0x10000 before merge. QEMU uses two cores, snapshot flash, headless display/monitor, `-nic none`, and a none audio backend. Each command owns its PID/logs and is bounded; timeout/interruption retains failure and invokes taskkill only on that owned tree, with direct-process kill/reap fallback. SDK child stdout/stderr are captured concurrently to separate retained files. The final validator receives actual QEMU returncode/timeout/interruption facts and the unmodified native protocol; any other failure/panic/partial protocol remains NONPASS.
