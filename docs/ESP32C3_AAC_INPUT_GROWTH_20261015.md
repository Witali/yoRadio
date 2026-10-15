# Bounded AAC input-capacity experiment

## Purpose and status

The [controlled TLS pause](ESP32C3_AAC_TLS_PAUSES_20261015.md) exhausted buffered
audio at 1.51 seconds with four resident input slots. Output-task checkpoints
remained recent. This experiment adds capacity after native AAC initialization,
without changing DSP, sampling rates, DMA scheduling or the TLS RX reservation.
It is implemented and host-tested. The first physical trial did **not** activate
growth for AAC-LC: the queue remained at four slots and repeated the output
failure. Physical benefit and all-codec safety are not established. Production
defaults remain unchanged.

`CONFIG_YORADIO_AAC_INPUT_EXTRA_SLOTS` accepts 0–8, default **0**. The planned
first trial requests four extra slots, capped by the user's saved target.
At the observed packet capacity of 2,060 bytes, four resident slots add
8,240 requested heap bytes, plus allocator overhead. Measure actual resident
count and heap use; a requested extra count does not prove allocation.

## Ownership and memory conditions

- Only the stream task restores slots, once per connection after successful
  native AAC output. FLAC and AAC share the existing bounded expansion helper.
- The decoder signals readiness only if the configured compact SBR/PS owner is
  allocated or reserved and no scoped allocation failure was recorded. The
  AAC-LC low-memory fallback may discard that reservation; it does not signal
  readiness. No decoder pointer is transferred to another task.
- Before each extra allocation, leave 32 KiB of advisory internal-heap
  headroom. This is not a reservation or a guarantee against concurrent or
  later allocations. The 17,058-byte TLS RX reserve remains intact.
- Existing adaptive-queue limits, allocation-pressure reclamation and lease
  rules apply. Only idle slots are reclaimed. Stop/EOF/next-connection cleanup
  lowers the limit, and busy extra slots retire when their leases end.
- Both FLAC and AAC still obey the saved user buffer target. No NVS settings
  change and no new full-frame buffer or codec data structure is introduced.

The owner check protects the largest pre-reserved AAC block; it does not prove
that every later allocation succeeds. Same-connection rate/channel/profile
changes, late SBR/PS, reopening and codec-family transitions remain mandatory
physical tests before enabling the option by default.

## Host evidence

Seven ASan/UBSan allocator variants pass: four original configurations,
FLAC expansion only, AAC expansion only, and both. Each variant performs
8,000 concurrent TLS allocations. Growth variants cover low headroom, partial
allocation failure, headroom changes between allocations, a live TLS reservation,
producer/consumer leases across shrink and preparation, retained floor buffers,
FIFO data integrity, complete release and target-capacity clamping.

The actual adaptive queue also passes 60,000 concurrent packet transfers,
ownership/FIFO checks, deferred-limit changes, allocation races/faults,
TLS pressure, tick wrap and separate control-slot storage.

[Retained sources, logs and reports](../tests/results/esp32c3-aac-input-growth-20261015/host/)
use pthread/heap stubs. They do not qualify target scheduling or actual TLS/PCM.

## Physical acceptance still required

1. Build/audit the local-CA diagnostic image with four requested extra slots.
2. Repeat the exact 0.5/1.0/1.5-second TLS pause schedule, source, host buffer
   and cipher; compare resident slots, heap and output/phase counters.
3. Run full-rate AAC-LC/HE-AAC/HE-AACv2, late SBR/PS and same-connection
   codec/rate/channel transitions; verify all allocations and settled recovery.
4. Check other codecs, Stop/replacement/EOF, TLS pressure and OTA on the final
   quiet candidate. Retain failed controls and do not infer public-stream
   causality merely from a passing local pause experiment.

## First physical trial: expansion did not activate

The audited `idf61-aacin4-20261015` image has application SHA-256
`edbadada673b8509e1aae11a3a55e89f2168cd6a3b19a0bf609aebd21144f37a`.
Its configuration differs from the preceding local-CA diagnostic only by the
new extra-slot option, set to four (absent in the baseline, equivalent to zero).
Linked AAC/HTTP/allocator checks and the ISR/timer IRAM audit pass.

| Measurement | Baseline | Requested four extra AAC slots |
| --- | ---: | ---: |
| Actual resident / minimum / limit | 4 / 4 / 4 | 4 / 4 / 4 |
| Actual longest host pause | 1.510316 s | 1.513596 s |
| New DMA completion-queue drops | 48 | 48 |
| Output write errors | 0 | 0 |
| Allocation / decoder / watchdog faults | 0 / 0 / 0 | 0 / 0 / 0 |
| Minimum sampled free heap / largest block | 59,152 / 32,768 B | 59,308 / 32,768 B |
| Passed campaign checks | 10 / 11 | 10 / 11 |

Both use the same owned AAC-LC fixture, TLS cipher, pacing, 4-KiB host send
buffer and pause offsets. The new run has 106 health observations on one boot.
The shorter pauses introduce no new completion drops. The final pause produces
all 48 increments; the retained events have all three pipeline wait flags.
After Stop, median free heap returns from 138,924 to 138,928 B; the largest
block remains 110,592 B and task count stays at 16. Original production firmware
and private settings are verified restored, with playback stopped.

### Why the feature did not activate

`native_aac_decoder_process()` deliberately discards an unused pending SBR
owner after the first successful PCM output. For pure LC, no active SBR owner
exists. The caller then asks `native_aac_decoder_input_growth_ready()`, whose
owner requirement is false. The stream task never receives the readiness
generation. This is a lifecycle mismatch in the proposed LC experiment, not
evidence that a larger queue provides no benefit. No additional resident queue
storage was observed.

The actual adapter ASan/UBSan test now enables the extra-slot option and checks
eligibility after LC, output retry, late SBR, reopen and allocation failure.
It confirms false after LC and true once SBR owns its storage. The caller only
signals inside its first-frame block, so later eligibility alone does not
activate growth in an already-running LC stream. DSP is mocked in this host
test; the physical evidence supplies the real LC lifecycle observation.

Do not remove the owner guard merely to force this test to pass: extra occupied
input leases cannot be reclaimed on demand when a later SBR allocation needs
memory. Retaining the full pending owner would also have a separate RAM cost
and must be measured with late-profile transitions.

### Next experiment

First compare the existing bounded startup-prefill setting at two seconds
against the one-second baseline, with extra AAC slots disabled and the same
TLS schedule. This isolates startup lead without inventing additional reserved
RAM. Check start latency, Stop/replacement responsiveness and output counters;
a longer prefill does not guarantee that a live server can supply that lead.
Then revisit safe queue growth with explicit owner lifetime and late-SBR tests.
Neither experiment qualifies public-source failures or the final production
image by itself.

The [two-second prefill trial](ESP32C3_AAC_PREFILL2_20261015.md) is now complete:
50 completion drops versus 48 in the control, without allocation/decoder faults.
It does not justify a production delay increase; guarded real-capacity growth
remains the next memory-lifetime experiment.

[Build evidence](../tests/results/esp32c3-aac-input-growth-20261015/build/),
[physical run and restoration](../tests/results/esp32c3-aac-input-growth-20261015/physical/),
and [adapter eligibility regression](../tests/results/esp32c3-aac-input-growth-20261015/adapter-eligibility/)
are retained, including the failed output check.
