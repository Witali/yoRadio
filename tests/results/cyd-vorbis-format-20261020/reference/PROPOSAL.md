# CYD public raw Vorbis 8192-block format regression

Prepared on 2026-10-20. Host reference work is executed; the SDK build, vendor
probe, and target execution are **not executed**. Production sources and images
are unchanged. This is the narrow G6 format case, with complete raw packets and
ample output capacity. It does not use target Ogg parsing, EOF/flush/reset/OOM
cases, or decoder-private state.

## Format defect and retained inputs

`idf/esp32-cyd2usb-native/main/vorbis_repair/setup.c:954-958` rejects a legal
8192 long block below 64000 Hz in the normal branch. [Vorbis I 4.2.2](https://xiph.org/vorbis/doc/Vorbis_I_spec.html)
allows positive rates and powers-of-two block sizes from 64 through 8192,
with the short size no larger than the long size; it adds no such rate coupling.

`candidate-pins.json` records six byte-identical canonical source snapshots in
`frozen-main/`. The setup source SHA256 is
`26a294fd703bf9e8f120c869efc354a8ff6f35f010393ff01349fc8af3512cb2`.
`reference/report.json` pins current source inputs, original fixture/parser,
public codec headers, host tools, and both installed ESP32 archives:

| Input | SHA256 |
|---|---|
| libesp_audio_codec.a | 92ba997358f50994d41422438c78bf2d7ee86dc1efc265f5356a66e221ae2e58 |
| libesp_audio_simple_dec.a | ca3b95dfc83b6984ae91c509bf859e4334fcc74654d2fe8b68bfc34f06126cc6 |
| FFmpeg 8.1.1 executable | 09948d4cdd0650da6ff5a87577469f2a218dc2615ae379f8f734d24c49de0f73 |
| FFprobe 8.1.1 executable | a6618e99bb58869ded3c6f37b53aa1a8d701c3591dbb7b5b317d47369c112be2 |
| Executed prepare_reference.py | 75faabf34ceaecb1dff62955451338f6c6c684aa5b49a6413253672f40b7b211 |

## Executed independent reference proof

`prepare_reference.py` generated deterministic, nonzero stereo audio with the
installed libvorbis encoder at 192000 Hz. The encoder naturally chose 256/2048
blocks. The encoder output remains separately retained as
`reference/encoder-192000.ogg`; it is not called an encoder-produced 8192 stream.

The candidate fixture changes the identification long exponent to 13 (8192),
updates its carrier's final granule and affected CRCs, and preserves the entire
setup packet and every audio packet byte. The public bitstream reader found
42 codebooks, two floor1 floors, two valid residue2 configurations, and modes
`[short,long]`. Of 68 audio packets, 67 select the actual long mode. There is no
floor0 rate-dependent setup to reinterpret.

The 192000/64000/63999/48000 Hz 8192 variants differ only in identification rate
and that page's CRC. Both independent FFmpeg-native `vorbis` and `libvorbis`
decoders accepted every variant with `-err_detect explode`, producing nonzero
PCM with equal counts. Within each independent decoder all four variants are
byte-identical. Cross-decoder PCM hashes differ and are not an exact oracle.
The native decoder emitted 65 full 4096-sample frames, proving more than header
acceptance. `normal2048-rate48000.ogg` is also independently decoded as a
positive ordinary-block control.

| Retained object | SHA256 |
|---|---|
| 8192 / 192000 Hz Ogg fixture | 7511b210c385395ab0d7eec97d39da3996a98b3877827874ed39006872b0a6b2 |
| 8192 / 64000 Hz Ogg fixture | 3d1e4f74b058330801963f81d28be29f38ab5a6d05223677557a8f5df7f7f56e |
| 8192 / 63999 Hz Ogg fixture | 159f28baa208297f0fa4824e9db1b3815b976ea9ec8383820a22430386091bb6 |
| 8192 / 48000 Hz Ogg fixture | 6f548bc9c5013df7e2e4b84b9d457f6e8d06bdc1ef9eb0dcc149449abe1acaab |
| Setup payload | ddf96884253b58b0449734cb874e21b8465625303c01bb5645012eb761cfcf43 |
| Concatenated 68 audio packets | 4e7aee5fa90add769e2dc95d8c2e0fab858b07d176932fdc581d12608799c8cc |
| Native decoder PCM, each rate | 8ec759b5cbdb7dde94aa36bf0435b0308d9ef536dbce661133b42ac9eafb8bf4 |
| libvorbis PCM, each rate | 4fc1e5c9ff7c220410a5d89deb47fae309c71a6fecb6c49acd5d87b3b08291b1 |

All argv, tool versions, exit status and stdout/stderr hashes are retained in
`reference/report.json` and `preparation.json`, with the actual log files.
The executed host commands were:

```powershell
$prep = 'C:/Work/yoRadio/.worktree/esp32-cyd-c3-review/.build/cyd-vorbis-format-prep-01'
$hostPython = 'C:/Users/rudol/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $hostPython -B "$prep/prepare_reference.py" --ffmpeg (Get-Command ffmpeg).Source --ffprobe (Get-Command ffprobe).Source
& $hostPython -B "$prep/finish_preparation.py"
```

These prepare fresh outputs and are intentionally not overwrite/re-run commands.

## Container count accounting

The raw overlap sum for all 68 complete 8192 packets is 272448 samples/channel,
or 1089792 PCM bytes. The host container decoders emit 272320 samples/channel,
or 1089280 bytes. `frame-accounting.stdout.log` explains the exact difference:
the initial priming packet has nominal duration 128 but produces no PCM; the
first returned frame has 2112 samples, 65 middle frames have 4096, and the final
frame has 3968. The final packet explicitly reports `skip_samples=0` and
`discard_padding=128`. This is final carrier trimming, not an initial PCM skip.

[Vorbis I Appendix A.2](https://xiph.org/vorbis/doc/Vorbis_I_spec.html) allows a
final granule to shorten the last returned audio. FFmpeg's tagged
[Ogg packet handling](https://github.com/FFmpeg/FFmpeg/blob/n8.1.1/libavformat/oggparsevorbis.c#L528-L543)
sets that final trimming from page granule accounting. The executed preparer's
comment about removing the final crop is imprecise: the retained trace proves
128 samples are still trimmed. No original reference artifacts were overwritten.
The target expectation uses full raw-packet overlap only; it never equates the
container byte count with the public raw decoder byte count.

## Source-only target probe

`project/main/main.c` includes only public codec/RTOS/system headers and generated
packet bytes. Handles stay opaque. Its only codec operations are public
open/decode/close; `__real_` aliases select the installed original public codec
implementation through the same linker wrapping used by the canonical bridge.

The ordered prerequisites and cases are:

1. Original vendor public open **and full decode** at 192000/8192. Require all
   68 complete packets consumed, exact public overlap sizes, nonzero PCM and
   66 real 16384-byte stereo output packets. An unsupported result or panic is
   a nonpass; the vendor oracle must not be weakened or assumed from source.
2. Pair original 192000/8192 synthesis with checked 192000, 64000, 63999 and
   48000 Hz / 8192. Compare result, consumption, output size and every PCM byte
   per packet, with expected public metadata for each rate. Float host PCM is
   not compared with the vendor fixed-point PCM.
3. Pair original/checked 48000/2048 for the ordinary positive control.
4. Checked open must reject zero rate, short=32, long=16384, and short>long.
   These are header validity controls, without OOM injection or private state.

Each 16384-byte output has 16-byte canaries before and after it, reset/checked
around every decode. Pair buffers receive different initial fill bytes so stale
output cannot pass byte comparison. The coordinator asserts core0 and all codec
work asserts core1. No output undersizing, retry, reset, flush, or EOF is used.

`FORMAT_EXPECT_LOW_RATE_REJECTION=1` reproduces the unchanged defect. It emits
`CYD_VORBIS_FORMAT_BASELINE ...` only after all prerequisites/controls and both
legal low-rate rejections. A controller may report `regression_reproduced=true`
for this diagnostic, but **must report format acceptance/qualification false**.

After reviewing that result, a separate frozen candidate may remove only the
normal branch's rate/block-size guard. Keep the optional `LIMIT_TO_64kHz` branch
and all ordinary checks. `FORMAT_EXPECT_LOW_RATE_REJECTION=0` then requires
all legal rates accepted with exact vendor PCM and emits
`CYD_VORBIS_FORMAT_COMPLETE ...`. There is no proposed production edit yet.

## Proposed next execution, not run

Use a fresh `.build/cyd-vorbis-format-baseline-01` campaign with the existing
pinned IDF6.0.2 launcher pattern from `tests/target/cyd_vorbis_qemu/sdk-build.ps1`.
Copy this `project/` and the unmodified `frozen-main/` into that campaign, retain
input/source hashes, and select the explicit CMake cache variable below. The
SDK/tool paths are `C:/Work/yoRadio/.idf/v6.0.2`,
`C:/Work/yoRadio/.idf/tools-v6.0.2`, and the codec component is
`C:/Work/yoRadio/.idf/esp-adf-libs/esp_audio_codec`.

After that existing launcher activates its SDK environment, the build argv is:

```text
C:/Work/yoRadio/.idf/tools-v6.0.2/python_env/idf6.0_py3.12_env/Scripts/python.exe
  C:/Work/yoRadio/.idf/v6.0.2/tools/idf.py
  -C <fresh-campaign>/project -B <fresh-campaign>/build --no-ccache
  -D IDF_TARGET=esp32 -D SDKCONFIG=<fresh-campaign>/sdkconfig
  -D SDKCONFIG_DEFAULTS=<fresh-campaign>/project/sdkconfig.defaults
  -D FORMAT_EXPECT_LOW_RATE_REJECTION=1
  -D CMAKE_JOB_POOLS=compile=2;link=1
  -D CMAKE_JOB_POOL_COMPILE=compile -D CMAKE_JOB_POOL_LINK=link build
```

Set `CYD_VORBIS_CANDIDATE=<fresh-campaign>/frozen-main` and
`YORADIO_AUDIO_CODEC_COMPONENT` to the pinned component. Verify actual consumed
compile rows point to all three frozen bridge TUs, and linked symbols include
original and wrapped public open/decode. For the actual `setup.c` row, retain
the compiler argv/response files, remove only compile/output options and run
`-E -dM` in its original directory/context. Require `LIMIT_TO_64kHz` absent in
that macro dump; the harness TU's `#error` alone does not establish this.

Merge actual `build/flasher_args.json` inputs with esptool in DIO/40m/4MB mode
and pad to 4MB, retaining the recipe and output SHA. Expected layout is
bootloader 0x1000, partition table 0x8000, factory app 0x10000; check the actual
recipe rather than inventing missing build outputs. The emulator argv is:

```text
C:/Work/QEMU-ESP32/bin/qemu-system-xtensa.exe
  -audiodev none,id=quiet -M esp32,audiodev=quiet -smp 2
  -L C:/Work/QEMU-ESP32/pc-bios -display none -monitor none -serial stdio
  -no-reboot -snapshot -nic none
  -drive file=<fresh-campaign>/qemu-flash.bin,if=mtd,format=raw
```

Use bounded stdout/stderr capture with a 120-second timeout; terminate the
process tree on timeout and retain the partial log as nonpass. Require the
exact expected completion marker once, all prior case markers and counts, no
failure/panic/assert/corruption marker, successful process completion and
unchanged input hashes. Exit0 or timeout alone cannot establish any result.
No board, host network, physical audio or production-radio coverage is implied.
C3 would need its own RISC-V/vendor qualification.
