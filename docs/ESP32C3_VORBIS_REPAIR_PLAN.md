# ESP32-C3 Vorbis audit and repair plan

Date: 2026-10-04. Reviewed checkout: `8db05fed` (`codex/aac-storage18`).

**Status: steps 1–3 completed; steps 4–7 remain pending.**
This review covers the native C3 audio service, the pinned Espressif Ogg/Vorbis
objects and retained playback evidence. It is not a complete audit of every
instruction in the decoder. No firmware was flashed during this review.

The [step-1 runtime report](ESP32C3_VORBIS_LIFECYCLE_20261004.md) adds 100 valid
decode/close cycles, 198 allocation-failure cases and four malformed-header cases
using the original objects in QEMU. Normal cycles restore all stream memory;
189 allocation failures and all four malformed cases crash. Three more
allocation failures silently return success with missing PCM. These failures
are preserved as the repair baseline, not treated as a successful qualification.

The [step-2 initialization report](ESP32C3_VORBIS_REPAIR_20261004.md) records
the repaired run: all 208 fault cases handled, 100 normal cycles, exact original
PCM and full heap recovery. The PC19 radio image builds and is retained; it has
not been flashed or qualified on hardware. The [step-3 retry/EOF report](ESP32C3_VORBIS_OUTPUT_20261005.md) supersedes
that old PCM reference: the original Ogg path omitted five final packets.
The physical fragmentation investigation remains pending.

The [RX ownership follow-up](ESP32C3_RX_OWNERSHIP_20261005.md) adds a diagnostic
compatible with the current PC19 image. A complete 160-second physical Vorbis
capture attributes roughly 14–18 KiB of settled live memory to netif RX buffers;
all tracked RX owners disappear after Stop and the 114,688-byte largest free
block returns. This does not reproduce or resolve the older persistent
fragmentation. Step 4 remains open; the original initial heap FAILs, an incomplete
MP3 ownership capture and an Opus WebUI latency FAIL remain visible.

## Conclusion

Vorbis already plays the tested 48 kHz stereo streams. The first repair should
make allocation failure and invalid-header cleanup safe. Static inspection
found a use-after-free/double-free path in the vendor open function and an
unchecked allocation in DSP creation. These are separate from the unresolved
post-stop fragmentation seen in one physical run; that run logged neither a
decoder error nor an allocation failure.

Keep the current DSP arithmetic while fixing ownership and retry behavior.
Then measure memory by owner before changing allocation layout or precision.

## Baseline and implementation

The component is `esp_audio_codec` **2.6.2**. Local archive SHA-256 values:

| Archive | SHA-256 |
| --- | --- |
| `libesp_audio_codec.a` | `311caa814095b098e476b28e46d55623ef70c26b0d73d69ba5832e154ec8d909` |
| `libesp_audio_simple_dec.a` | `232650ec81ae5e10ecbe1b2c86de2d1adf8f1b793f5ef343241c6e510db3e71f` |

The [saved static evidence](../tests/results/esp32c3-vorbis-audit-20261004/manifest.json)
identifies the ELF, application and disassembly files. The ELF hash matches the
[physical receive-credit image](ESP32C3_RECEIVE_CREDIT_20261004.md).

The C3 path is:

```text
HTTP / encoded ring
  -> audio_service.c: decoder_task
  -> esp_audio_simple_dec (Ogg parser + Ogg decoder wrapper)
  -> esp_vorbis_dec
  -> vorbis_dsp_* / codebooks / floor / residue / MDCT
  -> signed-16 PCM workspace -> PCM ring -> audio output
```

Symbols such as `tremor_oggpack_read`, `vorbis_dsp_create` and the work/history
layout match the **Tremor low-memory family**, an integer decoder. This is an
implementation-family identification, not a claim that the vendor archive is
identical to upstream. Compare the [Tremor DSP reference](https://android.googlesource.com/platform/external/tremor/+/0ad0141e864cfbb130db4f22e279d421832e7336/Tremor/dsp.c)
and [Xiph's Tremor description](https://wiki.xiph.org/Tremor).

The pinned README advertises mono/stereo, 16-bit output and rates 8, 11.025, 12,
16, 22.05, 24, 32, 44.1 and 48 kHz. Preserve this range. This is not a claim
of support for every channel count/rate permitted by the wider Vorbis format.
Preserve full-rate AAC/SBR/PS when switching codecs as well.

## Findings and confidence

### V1 — unsafe failed-open cleanup: confirmed in the linked binary

In `esp_vorbis_dec.c.obj:esp_vorbis_dec_open`, a failed identification/setup
parse branches to cleanup. After clearing/freeing `vorbis_info`, it frees the
wrapper, falls through to read its DSP pointer, and can free the wrapper again.

In the [linked function](../tests/results/esp32c3-vorbis-audit-20261004/linked-open.asm):

- `0x42045c96`: free the wrapper held in `s0`;
- `0x42045c9a`: read `0(s0)` after that free;
- `0x42045cb4`: another free of the same wrapper on the fall-through path.

These addresses identify this ELF only; they must **not** become patch addresses.
The relocatable member has the corresponding `.L52 -> .L49 -> .L57` path.
Step 1 now reproduces a crash in this invalid-header cleanup path. This is not
evidence that normal playback caused the observed fragmentation.

### V2 — DSP allocation failure is unchecked: confirmed in the linked binary

In [vorbis_dsp_create](../tests/results/esp32c3-vorbis-audit-20261004/linked-create.asm),
the 80-byte allocation at `0x42045e4c` is followed by `sw s3,0(a0)` at
`0x42045e58`, without testing the returned pointer. Later allocations create
channel pointer tables and work/history arrays; their failure paths also need
an exhaustive audit before declaring initialization safe.

The linked [media allocator](../tests/results/esp32c3-vorbis-audit-20261004/linked-calloc.asm)
delegates to `calloc`. The existing
[AAC allocation wrapper](../idf/esp32c3-oled-native/main/aac_compact_owner.c)
passes non-AAC allocations through; it does not supply Vorbis with a reserve
or make allocation infallible. Check `vorbis_info_init`, header/codebook unpack
and every floor/residue/mapping allocator in the same failure sweep.

### V3 — output-too-small retry repeats synthesis: reproduced and repaired in step 3

`esp_vorbis_dec_decode` calls `vorbis_dsp_synthesis` before comparing the required
PCM length with output capacity. If too small, it returns
`ESP_AUDIO_ERR_BUFF_NOT_ENOUGH` without draining PCM. The simple decoder caches
that compressed packet for retry; the C3 service grows the buffer and retries.
The second call therefore reaches synthesis again. Test whether this changes
history or duplicates/drops samples before choosing the repair.

The initial non-AAC PCM buffer is 12,288 bytes and can grow. Existing 48 kHz
fixtures do not establish that this branch is correct for larger legal blocks.
Do not apply the AAC-specific consumed-byte behavior to Ogg without measuring
the actual simple-decoder contract.

### V4 — audio-service terminal ownership needs correction/qualification

In [audio_service.c](../idf/esp32c3-oled-native/main/audio_service.c):

- Stop changes generation, closes the simple decoder, and normally frees its
  PCM workspace because the target becomes `AUTO`.
- If PCM preparation succeeds but `esp_audio_simple_dec_open` fails, both
  decoder handles can remain null. The later cleanup conditions PCM release
  on `had_simple_decoder`; it can retain the allocated PCM buffer after Stop.
  Release must follow buffer ownership, including partial initialization.
- EOF sends an output completion marker, but does not itself close the decoder.
  Terminal decode errors also retain it until a generation change. Define and
  test prompt release after queued PCM is safe, without truncating the tail or
  letting an old completion stop a newly selected station.
- Decoder registration results are currently ignored. Failed registration
  must become an explicit initialization error with defined cleanup.

The retained buffer after failed open is a different path from the successful
Vorbis playback followed by the 54 KiB loss of contiguous space.

### V5 — post-stop fragmentation: measured, owner unknown

The [retained physical results](ESP32C3_RECEIVE_CREDIT_20261004.md) distinguish:

| Vorbis run | Playback/load result | Post-stop memory |
| --- | --- | --- |
| Original 180 s paced run | Audio active; incomplete telemetry fails load gate | 146,124 B free / 114,688 B largest; recovery passes |
| Receive-credit 180 s paced run | Audio active; progressive-heap-loss gate fails | 145,876–145,880 B free / 59,392 B largest; recovery fails |
| Unpaced 60 s control after reboot | Load passes; CPU mean/peak 71.5/72.3% | 145,928–145,936 B free / 114,688 B largest; recovery passes |

In the failed recovery, the prior idle baseline was 145,964 / 114,688 bytes:
only 84–88 bytes of net free memory disappeared, while the largest free block
shrank by 55,296 bytes. Small surviving allocations can split a large region;
only tracing addresses and lifetimes can identify their owners. Network, WebUI,
runtime and codec allocations all remain candidates. These measurements alone
do not prove a Vorbis leak or prove that the short unpaced control fixed it.

## Ordered work plan

Each implementation step should be a separate focused commit with its tests
and retained results. Steps 1–3 are complete; steps 4–7 are **pending**.

### 1. Reproduce the failure paths without networking

**Completed 2026-10-04:** [results, owner ledger and reproduction commands](ESP32C3_VORBIS_LIFECYCLE_20261004.md).
The original decoder still fails the fault-handling gate. Coverage is the
successful allocation path of one fixture, one failure at a time, plus four
malformed-header cases; it is not an exhaustive malformed-stream test.

- Use the actual pinned RV32 objects in a QEMU harness. Register codecs once;
  exclude deliberate process-lifetime registration allocations from per-stream
  leak accounting, but record them separately.
- Decode the existing fixture, close, and repeat at least 100 times. Record
  live allocation addresses, requested/actual sizes, peak live bytes, largest
  block, free bytes, stack watermark and PCM hash/sample count.
- Fail each allocation/reallocation in turn during open, setup and decode.
  Include invalid identification/setup headers and partial initialization.
  Run potentially crashing original cases separately so later cases still run.
- Preserve the failing original result. A corrected run must return a defined
  error, leave no stream-owned blocks, keep the heap valid and successfully
  decode a valid stream immediately afterwards.

**Deliverable:** reproducible cases for V1/V2 and an owner ledger. No successful
physical playback result substitutes for these injected-failure tests.

### 2. Repair initialization and teardown — completed

- Replace the narrow affected wrapper/initializer routines with audited source
  and one cleanup path. Publish the handle only after complete initialization;
  free each owned allocation once, and tolerate partially built structures.
- Audit all callees that allocate: codebooks, floor, residue, mapping and DSP.
  An outer null check cannot repair a callee that dereferences allocation
  failure internally. Extend the source replacement where the tests require it.
- Cover the additional step-1 failures in simple-decoder initialization and
  Ogg header/packet error propagation. In particular, allocation failures 3,
  4 and 198 must not return success with missing PCM. Add registration failure
  tests separately from the per-stream sweep.
- Fix V4's PCM ownership on failed open and terminal paths. Keep generation
  guards and PCM queue ordering; add failed-open -> Stop -> valid Play tests.
- Use named structures/fields, `sizeof`/`offsetof` assertions and pinned archive
  hashes for any private ABI bridge. No raw numeric pointer arithmetic or
  absolute binary-address patches. Verify which definitions the final ELF uses.

**Pass:** all step-1 failures handled, no invalid/double free, no outstanding
stream allocations, unchanged valid-stream PCM and restored replay capability.

### 3. Make PCM retry and EOF behavior deterministic — completed

**Completed 2026-10-05:** [results and reproduction](ESP32C3_VORBIS_OUTPUT_20261005.md).
The seven-case matrix matches all 535 independently extracted audio packets,
including the tail previously lost by the streaming parser. The full allocation
failure regression passes; broader format/granule coverage remains step 5.

- Compare a sufficiently large output buffer with deliberately tiny buffers,
  repeated resize attempts, and injected resize failure. Capture complete PCM.
- If V3 reproduces, synthesize each packet once, retain/drain pending output,
  then admit the next packet; or calculate a safe required capacity before
  mutating DSP state. Preserve the parser's compressed-input ownership.
- Verify final sample count, overlap tail, repeated zero-length EOS calls and
  EOF status. Do not claim exact trimming from HTTP duration alone.

**Pass:** byte-identical PCM to the same decoder with ample output space,
identical sample count, no stalls and safe terminal cleanup.

### 4. Identify the physical fragmentation owner

- Add bounded address/lifetime capture compatible with **the current PC19 AAC
  image**. Existing `YORADIO_HEAP_LAYOUT_DIAGNOSTICS` excludes compact SBR; simply
  enabling it would change the experiment. Reuse the existing decoder stack
  for snapshots and report trace overflow; do not log inside heap locks.
- Capture idle, after Ogg headers, first PCM, steady playback, Stop, decoder
  close, socket close and settled idle. Include small allocations, frees and
  reallocations, not only allocations above 1 KiB.
- Repeat the exact MP3 -> Vorbis -> Opus sequence, Vorbis alone, paced/unpaced
  streams of equal duration, and with/without WebUI polling. Include warm-boot
  and fresh-boot runs. Keep buffer-filling observations separate from residual
  allocations after Stop.
- Attribute every allocation separating the formerly contiguous region. Fix
  its actual owner. Only consider a per-decoder pool/arena if ownership evidence
  supports it; a large permanent reserve can make TLS/OTA worse.

**Pass:** no unexplained retained stream allocations and no cumulative loss of
the idle largest block over repeated cycles. Preserve old failed reports.

### 5. Validate Ogg and Vorbis format boundaries

Use the [Vorbis specification](https://xiph.org/vorbis/doc/Vorbis_I_spec.html)
and [Ogg framing specification](https://xiph.org/ogg/doc/framing.html) as the
format references. Packets may cross pages; lacing, continuation, serial
changes and final granule positions need dedicated tests. Distinguish an
incomplete Ogg page from a complete, shortened Vorbis audio packet, which is
not automatically invalid under the Vorbis decoding rules.

Create a shared fixture corpus covering:

| Group | Required cases |
| --- | --- |
| Audio layouts | All nine advertised rates, mono/stereo, low/high bitrate, independent left/right content |
| Synthesis | Legal short/long blocks and transitions; include 8,192-sample blocks, silence, impulses and clipping |
| Setup | Different codebooks, floor 0/1 and residue modes; large valid setup/comments; malformed and truncated headers |
| Transport | One-byte/irregular HTTP chunks, multiple packets/page, continued packets, lacing lengths 0/254/255/256, CRC/sequence damage |
| Stream lifetime | EOF at complete packet and mid-page; chained logical streams with rate/channel changes; Stop during header/setup/output |

Audit the Ogg parser's additions/multiplications before allocation or copying.
Oversized input must produce a defined resource error rather than wrap a size
or corrupt memory. Do not impose an undocumented format restriction to make
the tests pass.

### 6. Measure memory opportunities after correctness

| Area | What is known | Experiment and condition |
| --- | --- | --- |
| Ogg identification/setup copies and packet cache | Separate allocations with cleanup in `esp_ogg_parse_free_extra` | Record lifetimes and high-water sizes; release obsolete header copies only after proving all consumers are finished |
| Codebooks/floor/residue/mapping setup | Allocated from stream configuration | Inventory each owner and reader; evaluate lossless table sizing/packing or grouped lifetimes, with CPU comparison |
| DSP work and retained overlap | `vorbis_dsp_create` allocates per channel | For long block `N`, work is `4*(N/2)` bytes/channel and retained history `4*(N/4)`; audit synthesis/MDCT consumers before reuse |
| Application PCM | Starts at 12,288 B for Ogg; grows as required | Correct ownership and retry first; test bounded draining to reduce peak output storage without changing sample count |
| Window constants | Already in Flash in this ELF | `vwin2048` at `0x3c14eb9c`, `vwin8192` at `0x3c148b9c`; do not count moving them as new RAM savings |

For stereo and `N=2048`, the two DSP sample-array groups total **12,288 bytes**;
for `N=8192`, **49,152 bytes**. These are allocation formulas, not measured
savings, and exclude pointer arrays, setup/codebooks, wrappers and allocator
overhead. AAC SBR/QMF compression cannot be assumed applicable to Vorbis MDCT
history. Start with lossless changes; any later precision experiment needs
separate PCM qualification within the established maximum **3 signed-16 LSB** budget.

### 7. Qualify quality, CPU and the complete radio

- First compare patched vs pinned decoder PCM: ownership-only changes require
  **zero** sample differences. Separately compare with a pinned Xiph
  libvorbis/Tremor reference; report baseline rounding differences, exact sample
  alignment/count, maximum error, RMSE and count above 3 LSB. Do not use arbitrary
  time alignment to hide missing or duplicated output. FFprobe metadata alone
  does not validate PCM quality.
- Use QEMU for correctness/instruction comparisons; measure wall-clock CPU on
  the real C3. Keep matched fixture, network, Flash/CPU settings and logging.
  Preserve current CPU/heap/latency gates, including the 85% CPU ceiling; also
  compare decode cost against baseline rather than accepting any regression
  below that ceiling.
- Run equal-duration 180 s paced/unpaced tests, at least 100 switches and a
  30-minute soak. Follow Vorbis with full-rate HE-AAC/PS over HTTPS and OTA
  while playing, then verify reboot, restored settings and playback.
- Confirm OLED/WebUI rate, channels, EOF/error states and actual sound. Record
  stack margins and total/contiguous heap. Trace-heavy images are diagnostic,
  not the final CPU qualification images.

**Promotion:** all required cases pass on the intended production image;
archive the build under `firmware/development/<variant>/app.bin`. Keep any
remaining failure visible and do not silently reduce rate, channels or format
support to obtain a PASS.

## Existing coverage and limits

- `qemu_codec_calibration.c` and the saved `qemu-vorbis.log` exercise the pinned
  fixture with deterministic instruction counts. They do not prove all failure
  paths, PCM fidelity, large-block retries or leak-free repeated lifetimes.
- `tests/ogg-codecs.test.js` checks the Arduino/minimal-IDF integration largely
  through source assertions. It is a compatibility reference, not a C3 decoder
  execution test. Its acceptance of `DATA_LACK`/`CONTINUE` must not be copied
  blindly over the pinned simple-decoder API contract.
- ESP8266's Ogg demux tests concern **Opus**. Reuse transport-test ideas and the
  device-independent HTTP server, but do not count those tests as Vorbis DSP
  coverage.
- `tests/test-esp32c3-receive-credit-evidence.py` checks the consistency of the
  retained measurements, including failures. No new physical or QEMU decoder
  run was performed for this static audit.

For reproduction, run `riscv32-esp-elf-objdump -d --disassemble=<symbol> <ELF>`
for the three symbols listed in the evidence manifest. For archive-level
inspection, extract `esp_vorbis_dec.c.obj`, `dsp.c.obj`, `info.c.obj`,
`codebook.c.obj` from the codec archive and `esp_audio_simple_dec.c.obj`,
`ogg_dec.c.obj`, `ogg_parser.c.obj` from the simple-decoder archive, then use
`objdump -dr`. Match the hashes above before interpreting offsets.
