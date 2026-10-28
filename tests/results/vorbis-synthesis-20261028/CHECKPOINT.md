# Stateful packet-to-PCM synthesis on host and both ESP32 architectures

The [owner API](../../../idf/components/native_vorbis_synthesis/include/native_vorbis_synthesis.h)
and [design](../../../docs/CYD_VORBIS_SYNTHESIS_DESIGN.md) connect shared
granule/EOS timing, retained per-channel right halves, exact window products
and one final S16 rounding. The shared fixture executes actual public setup,
frame, floor0/floor1 spectrum, reused IMDCT and synthesis APIs. Captured gain,
spectrum, transform and PCM are never supplied as decoder input.

The original corpus contract is unchanged:

- All31 streams,434 raw audio packets and738560 PCM bytes are retained.
  Host compares every sample at zero lag to both the saved Xiph output and
  original FFmpeg8.1.1 libvorbis bitexact references. Maximum absolute S16
  error is2 against each, within the original bound2; all14 relations pass.
- SDK6.0.2/LX6 and SDK6.1.0/RV32IMC execute the same complete public pipeline
  in QEMU. Every native PCM byte equals the host output and the other ISA.
  The native parser directly checks the original FFmpeg/libvorbis references;
  complete host equality supplies the saved Xiph lineage as well.
- Complete concatenated PCM SHA256 is
  `b9df479b6cb6ac07b2aff2049f05bb8ba98ef9ce4fdc72acf40a333f47e01d75`.
  Equality is checked on actual bytes, not inferred from digests alone.
- Input API bytes total7376: identification930, setup3007 and audio3439.
  Another1798 comment bytes remain in the original JSON; the setup API has
  no comment operation. The corpus is stereo with short64/256 and long256/2048.
  It does not qualify target memory use for8192 blocks or255 channels.

Host03 GCC13.3 ASan/UBSan passes the full corpus plus ownership checks:

- All864 saved overlap DATA rows produce598992 exact PCM values. All17962
  prior nonzero underflow witnesses, including13767 with exponent>=1074,
  retain their original identities before the final sum.
- All20019 timing actions drive the actual owner. The fixture asserts each
  of14788558 actual timing PCM values is zero and captures its exact zero-run
  length; supplementary FNV64 is not the numerical oracle.
- Every channel count1..255 is exercised, with765 pushes/2440724 actual
  interleaved values and73 front-trim/119 end-trim rows. The total owner run
  has20447 successful pushes/17828274 values.
- All50 failure/retry controls and46359453 owner guard checks pass, including
  late source/history/factor corruption on channel255, malformed timing,
  null/capacity errors and init/reset. Byte snapshots cover state, history,
  exponents, descriptors, source, output and result. All owned children are
  terminal/reaped. Nineteen damaged host captures are rejected by replay.

Native fixtures preserve watchdog and idle-task checks. Their priority3 worker
has16384 stack bytes on ESP32/core1 or C3/core0. Every successful report retains
six completed command receipts plus the SDK child's exit0. All3450 protocol
lines are parsed strictly; eleven malformed transcript controls are rejected
for each target. Per-stream allocations balance and live tracked bytes end at0.
Maximum tracked helper payload is128970 bytes with28 concurrent allocations.
Minimum free worker stack is10876 ESP32/11048 C3 bytes. Emulator heap minima
are155940/192268 bytes. These isolated observations are not radio/TLS heap,
physical real-time performance or a transient-allocation peak measurement.
No private decoder is executed; the already reused Xiph IMDCT kernel remains
unchanged. Production core bindings, priorities, stacks and selection stay as
before: stream core0 and decode/output core1 on CYD, C3 core0.

Source-only GCC15.2 C/C++17 profiles produce four ELF32 objects for LX6/RV32IMC.
The owner has zero Clang warnings/errors. Its own -O2/-fno-inline stack frames
in bytes, ESP32/C3, are measure80/80, init112/96, reset96/80, push160/160 and
publish_pcm176/160; these exclude callees and task high-water. Fixture/helper
lint retains17 reviewed warnings and zero errors: three ordinary C void-pointer
conversions, thirteen deliberate byte snapshots and one bounded count widening.
No custom suppression or weaker lint configuration was added.

All attempts remain visible. Host01 stops at sandbox WSL activation before
compilation; host02 passes full31 and host03 adds the owner campaign without
changing its primary capture. ESP32-01 stops during sandbox SDK activation;
ESP32-02 and C3-01 find an overstrict fixture size comparison under32-bit GCC.
The shared helper then uses a checked uint64 argument on both architectures,
retaining the host64 overflow check. ESP32-03 and C3-02 pass. Protocol01 stops
on a mistaken total including unconsumed comments before native execution;
protocol02/C3-01 then pass nine controls, protocol03 and both successful native
runs freeze all eleven. No production numeric source or reference bound changes
during these fixture repairs. No previously deferred controller is executed.

`captures.zip` SHA256:
`1b9937ee9009e5b1a48cd2435651f8cd26af0b3e565b2f3c0e2c1fb3c5b45877`.
ZIP bytes:20331925. `manifest.json` SHA256:
`9601d8ba02962e89a7916c6d30ffa43195c1c7023efcf1f9c25d542a4414545b`.
The archive holds424 physical SHA256 blobs/193778896 decoded bytes representing
all1487 logical files/209071195 logical bytes. Rebuildable host executables and
SDK/build scratch are omitted with3604 identities/316099377 bytes recorded.
Every reported build output is retained or explicitly bound to an omission;
the22 own objects per successful native target, images, ELF/map/configuration,
compile commands, sources, receipts, UART logs and all PCM/reference files remain.
These images are diagnostic fixtures, not production firmware handoff builds.

The [pure verifier](../../verify-vorbis-synthesis-checkpoint.py) uses pinned live
readers, validates all physical/logical bytes, replays saved host/owner data and
native UART logs, and checks complete cross-ISA equality. It extracts and executes
no archived code and starts no child commands. `replay.json` preserves that
numerical replay; `verification.json` is separate root artifact/receipt checking
without a second numerical campaign.

The first pure replay finishes all host/owner checks and nineteen damaged-capture
controls, then stops on an anchored symbol regex applied to Windows CRLF text.
Its [terminal failure receipt](vorbis-synthesis-checkpoint-replay-20261028-01-failure.json)
and exact `vorbis-synthesis-checkpoint-replay-20261028-01-failed-source.py`
snapshot remain alongside this archive. Three text reads (symbols, sdkconfig and
compiled configuration) now normalize CRLF before anchored matching, as the
qualified native controller already did. The fresh complete replay is recorded
in `replay.json`; C, SDK and QEMU campaigns were not repeated for this repair.

This closes full original31/bound2/all14 packet-to-PCM qualification and the
stateful granule/history owner for this candidate, including native execution.
Universal floor0 gain accuracy, wider/precision routes, actual raw/Ogg/audio-task
integration, OOM/backpressure and production resource/performance qualification
remain open. The existing production Ogg/Vorbis backend already works; this
candidate is not selected by it. All earlier deferred records remain unchanged.
Physical-board acceptance still awaits the user's board connection.
