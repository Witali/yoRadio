# Quiet output health qualification

## Production observability

The staged PDM output exposes two lifetime `uint32_t` counters in the additive
`output` object of `/api/native/health` (schema 1):

- `completion_queue_drops`: the I2S driver discarded a completion notification
  before the output task consumed it. This indicates delayed service; it is
  **not an acoustic gap count**.
- `write_errors`: an attempted I2S write returned an error or accepted fewer
  bytes than requested. One failed attempt increments this counter once.

`available=true` means the staged backend implements these measurements.
The experimental direct-DMA backend returns `available=false`; zero counters
there must not qualify output continuity. Older schema-1 images without the
object remain readable for heap/watchdog checks but cannot pass output checks.

Only the overflow callback increments the queue counter. Only the output task
increments the write counter. Neither counter is reset by Stop/Play. Reads
are aligned words on the single-core C3; the two counters are not one atomic
snapshot. Differences use modulo-2^32 arithmetic, with boot identity and
uptime checked separately. Startup, idle and Stop can contribute queue events:
compare only explicitly selected sustained-play windows.

The new persistent state is two 32-bit words. There is no new task, allocation,
logging, timer read or per-completion callback; the interrupt callback runs only
when the existing driver reports queue overflow. The HTTP stack response buffer
grows from 384 to 512 bytes. Final placement/size must be checked in the ELF.

## Host verification

Run from the repository root with Python; the native tests use GCC via WSL on
Windows:

```text
python -B tests/test-production-health.py
python -B tests/test-production-health-native.py
python -B tools/codec_benchmark/run_output_dma_host.py --profile --output <new-result-directory>
```

The actual C handler is checked at maximum-width values with watchdog enabled
and disabled, using AddressSanitizer and UndefinedBehaviorSanitizer. Actual
output C is exercised for callback registration failure, ISR counter wrap,
successful/short/failed writes, and persistence across suspend/reinitialize.
The staged and direct backends, with and without profiling, retain identical
PCM and case metadata (864 rate/channel/volume/balance/normalization cases per
variant). Host tests do not establish physical interrupt timing.

The Python reader rejects malformed counters, filters unknown fields, accepts
older basic-health responses, and rejects absent/unavailable output telemetry
for output measurements. Window deltas exclude historical events and handle
counter wrap; reboots and zero-duration windows fail closed.

## Remaining physical work

Build a quiet QIO/80 MHz image with the previously listened nominal 48 kHz
fractional divider, unchanged codec arithmetic and public trust roots. Audit
the overflow ISR's IRAM placement and absence of helper calls. Save the image
under `firmware/development/` before testing it.

Measure HE-AAC over public HTTPS for a bounded ten-minute playback, separating
startup from sustained output, and preserve all queue/write, heap, watchdog,
format and transport failures. Restore and verify the exact listened image
after the campaign. No analog continuity or universal station compatibility
claim follows from these counters alone.
