# CYD public raw Vorbis format probe

This isolated ESP32 harness uses only public codec open/decode/close APIs and
opaque handles. It feeds 68 complete raw packets with ample output buffers.
It exercises actual 8192 MDCT blocks without target Ogg parsing, EOF/flush,
reset, OOM injection, private-state access, radio integration or physical audio.

The original vendor public decoder must first open and decode all 68 packets
at 192000 Hz / 8192 blocks, with correct public metadata, consumed lengths,
overlap sizes, nonzero PCM and output canaries. Only then may the checked bridge
be compared against that synthesis byte for byte, per packet. Metadata failures
print public output fields before the unchanged assertions; they remain nonpass.
Each metadata output is initialized once per opened handle and retained across
that handle's decode calls. Every packet, including the zero-output priming
packet, must have the expected sample rate, channel count and bit depth. Counted
packet lines include these actual fields; pair lines also include both expected
rates and expected channel/bit values, all checked by the host validator.

`main/fixture.h` SHA256 is
`839febe9f12d7bc33e6afd8a9f0b16ee799f12d6c8ecb88188537b7ae8349378`.
Its setup payload SHA256 is
`ddf96884253b58b0449734cb874e21b8465625303c01bb5645012eb761cfcf43`;
concatenated audio SHA256 is
`4e7aee5fa90add769e2dc95d8c2e0fab858b07d176932fdc581d12608799c8cc`.
There are two floor1 floors, one short-mode and 67 long-mode packets. Expected
raw stereo 16-bit PCM is 1089792 bytes at 8192 blocks, including 66 full
16384-byte outputs. The 48000 Hz / 2048 ordinary control yields 272640 raw bytes.

The fixture derives from an installed libvorbis encode at 192000 Hz with
256/2048 blocks. Only its identification long exponent was enlarged to 8192;
all setup/audio packet bytes were preserved. Independent FFmpeg-native Vorbis
and libvorbis decoded nonzero audio at rates 192000, 64000, 63999 and 48000.
Within each independent decoder those rate variants were byte-identical.
Their container output was 1089280 bytes because the carrier discards 128 final
samples/channel. The raw target oracle does not apply container trimming or
compare floating host PCM with fixed-point vendor PCM.

The retained host proof is `.build/cyd-vorbis-format-prep-01/reference/report.json`,
SHA256 `6e1ed5c881851878b40882d5888af7f9089b3a49eff1ac0e85bb588bee7cfbf6`.
Preparation never implies the installed target vendor decoder has passed its
prerequisite. The first two root-owned target campaigns stopped at their
`vendor_high8192_metadata` assertion and remain NONPASS. Diagnostic output
showed packet0 consumed32/decoded0 with rate192000/channel2/bits16, then packet1
consumed111/decoded8448 with zero fields after the harness cleared the metadata
output again. Those observations exposed the per-packet-reset assumption in
the harness. They did not establish full vendor decode or format qualification.
Baseline02 then built successfully but the prep02 runner rejected the generated
`@toolchain/cflags` argument before macro/nm/QEMU. Its original report remains
NONPASS. Root separately retained/froze that same build's cflags/specs, preserved
the original response argument, and completed macro/nm/merge/QEMU without a
rebuild. `manual-qualification.json` records REGRESSION_REPRODUCED: vendor68
packets/1089792 PCM bytes, three exact pairs/204 packets, both low-rate header
rejections and four invalid-header rejections. Format acceptance remains false.

The later canonical acceptance run completes five exact pairs (340 packet
comparisons, 4631808 PCM bytes): 8192 blocks at 192000, 64000, 63999 and 48000 Hz,
plus the ordinary 48000 Hz / 2048 control. All four malformed headers still
reject. The separate old-guard control restores the original setup bytes and
fails exactly at `legal_candidate_open_required` after its vendor/high/ordinary
prerequisites. Both controllers exit0 with their distinct expected results.
See the [qualification archive](../../results/cyd-vorbis-format-20261020/README.md).

[Vorbis I, section 4.2.2](https://xiph.org/vorbis/doc/Vorbis_I_spec.html) allows
8192 blocks independently of the positive sample rate. The fix removes only
the default branch's rate/block coupling; the optional `LIMIT_TO_64kHz` branch
and the ordinary header checks are retained. This selected floor1 raw fixture
does not close the full format, Ogg, integration or physical qualification gates.

The runner has explicit scopes:

- `--scope baseline`: require unchanged low-rate rejections plus all vendor,
  ordinary, high-rate and invalid-header prerequisites. Exit0 means diagnostic
  reproduction; `passed=false` and `format_acceptance_qualified=false` remain.
- `--scope acceptance`: require all legal rates accepted with exact vendor PCM,
  metadata, packet counts and canaries. Only this mode can qualify the format.
- `--scope acceptance --control old-guard`: add the old default restriction only
  to the frozen `setup.c` variant. Require the exact
  `legal_candidate_open_required` failure after all vendor/ordinary/high-rate
  prerequisites. Panic, timeout, an earlier failure or mere nonzero exit cannot
  establish the control. The supplied source must already be repaired so this
  is a distinct mutation, rather than an ineffective control.

Baseline low-rate rejections and the four malformed-identification controls
require specifically the public `ESP_AUDIO_ERR_FAIL` result and a null handle.
Their counted lines retain the numeric result and attest `header_error=1`;
an allocation failure cannot satisfy a header-rejection expectation.

The runner defaults to canonical CYD sources; `--candidate` may select
a source directory within the repository for reviewed frozen candidates.
It never edits those inputs. Use a fresh output strictly inside `.build`.

```powershell
python -B tests/run-cyd-vorbis-format-qemu.py --scope acceptance `
  --output .build/cyd-vorbis-format-acceptance-next `
  --qemu C:/Work/QEMU-ESP32/bin/qemu-system-xtensa.exe
```

The SDK launcher snapshots the actual compiler/nm identities before compilation.
It captures the actual idf.py child's stdout/stderr in `sdk-build.stdout.log`
and `sdk-build.stderr.log` using two concurrent asynchronous stream copies,
started before waiting and both awaited before stream disposal. The runner
records these log hashes after successful or failed builds; missing logs remain
explicitly missing. No child logs are reconstructed for the older campaigns.
The runner records input/tool hashes, compiler rows, original and transformed
Windows argv, actual setup-TU macro dump, linker symbols, flash recipe, ELF/app
and execution hashes. `LIMIT_TO_64kHz` must be absent in the setup macro dump;
ESP32 and bridge enable macros must be present. The helper uses
`CommandLineToArgvW`, preserves cwd and all non-output arguments, and removes
exactly one `-c` and `-o` operand pair. The original `@` argument remains intact
for GCC. Its only supported response is the same build's `toolchain/cflags`,
with exactly the five reviewed literal flags and a quoted reference to that
build's `specs/picolibc.specs`. Both files are captured byte for byte, frozen,
bound before/after the macro probe and checked again at completion. Arbitrary,
duplicate or nested responses and other output contexts are explicit errors.

Flash settings must already be DIO/4MB/40m with exactly the expected factory
layout before merge. QEMU uses two cores, snapshot mode, no NIC/display/monitor
or host audio. Owned processes have bounded capture and PID-tree cleanup on
timeout/interruption, with direct-child kill/reap fallback. Every failure or
interruption leaves a nonpass report; no retry is automatic. Qualification
requires the complete ordered BEGIN/vendor/per-packet/case/completion protocol,
successful process exit and unchanged source/tool/build hashes.
