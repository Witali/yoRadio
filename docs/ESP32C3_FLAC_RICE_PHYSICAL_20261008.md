# FLAC Rice reader: physical ESP32-C3 comparison — 2026-10-08

## Scope

This follows the [host and RV32 hot-loop study](ESP32C3_FLAC_HOTLOOPS_20261008.md).
GPT-6.1 Sol prepared the isolated Rice experiment; the parent independently
reviewed the reader state, bounds, exact PCM comparisons and compiled code.
These measurements test whether the host improvement transfers to the actual
ESP32-C3 while Wi-Fi, WebUI and PDM output are active.

`CONFIG_YORADIO_FLAC_BYTEWISE_RICE` is an experimental, **default-off** option
for the custom FLAC decoder. The optional
`sdkconfig.flac-bytewise-rice.defaults` overlay enables it. The ordinary scalar
reader remains available. No LPC arithmetic or PCM precision changes here.

## Matched builds and linked code

Both fresh builds use pinned ESP-IDF revision
`9a97f6c54ec638111ce55cd36581b3c192f15207`, the same full compact AAC path,
copied network RX, six-segment TCP receive window, dynamic TLS, early 17,058-byte
RX-only reserve, adaptive input minimum four blocks, and staged-output/CPU
diagnostics. Tick period is 1 ms; output/decode/stream priorities are 8/7/5.
Deep sleep and TLS path profiling are off. Normal public roots and TLS
certificate verification remain enabled; these laboratory builds also trust
the private test CA.

The semantic sdkconfig comparison contains exactly one difference: the Rice
switch. Embedded project-version labels intentionally identify the variants.
Both AAC, HTTP and TLS reserve link audits pass.

| Linked measurement | Scalar control | Bytewise Rice | Difference |
| --- | ---: | ---: | ---: |
| Application image | 1,618,096 B | 1,617,920 B | −176 B |
| `.flash.text` | 1,158,788 B | 1,158,602 B | −186 B |
| `.iram0.text` | 47,690 B | 47,690 B | 0 |
| `.dram0.data` | 12,856 B | 12,856 B | 0 |
| `.dram0.bss` | 45,664 B | 45,664 B | 0 |

Every other allocated section has the same size and address. The candidate
does not add static RAM or a lookup table. Final image savings differ from
relocatable-object savings because of linking and alignment. The scalar reader
is inlined into `decodeResiduals`; the candidate has a separate 354-byte
`readRiceSignedInt` function. Its leading-zero operation calls ROM `__clzsi2`:
it is not a native CLZ instruction on this target.

## Physical method

Native application OTA installs each image and verifies its exact ELF identity.
There are four cases per variant:

- 60 seconds: Bossa Beyond, FLAC maximum LPC32, HTTP.
- 60 seconds: Groove Salad, FLAC maximum LPC12, HTTP.
- 60 seconds: the retained demanding 48 kHz stereo 16-bit FLAC fixture, HTTPS.
- 90 seconds: full-rate 44.1 kHz stereo HE-AACv2, alternating 1,024/16,384-byte
  TLS plaintext records, as a cross-codec regression control.

The two radio cases run in reverse order on the candidate. Variant order remains
control then candidate, with one observation per case; this is a screening
comparison, not a statistical guarantee of a small speed difference. Radio
sources are the same retained recordings as the host study. Broadcast audio
and private TLS keys are excluded from Git.

Original playback, runtime, heap and Stop-recovery gates are retained. CPU
percentage is informational. Runtime faults remain failures even when decoded
audio advances approximately in real time. The controller continues after a
failed benchmark to preserve the rest of the comparison; it records every exit
code and restores the previous quiet image in its finalization path.

### Interpreting timing and completeness

Measurements exclude the first ten seconds. CPU averages are weighted by full
firmware profiling intervals; decoder elapsed time includes descheduling and
is not decoder CPU time. Serial arrival timestamps place intervals within the
test window, so capture delay can affect boundary placement. CPU, decoder and
DMA counters have separately reported observation durations and coverage.

DMA byte counters are after resampling: the hardware output is fixed at
48,000 frames/s, stereo, 16 bits, even for a 44.1 kHz source. Queue overruns
indicate delayed descriptor reuse; they are **not an acoustic gap count**.
No microphone or digital-output capture was performed, so uninterrupted sound
cannot be certified solely from these diagnostics.

Telemetry completeness and original acceptance are separate results. Missing
or malformed samples, interrupted capture, counter resets and excessive gaps
cannot silently turn into a complete comparison. Zero decoded audio is recorded
without dividing by zero. Canonical runtime checks also retain watchdog,
allocation, decoder, TLS, assertion and reboot failures.

## Results and decision

**Keep bytewise Rice disabled.** This implementation was smaller but did not
improve the physical screening. All three FLAC cases took more elapsed decoder
time per audio second, and the demanding cases had more delayed DMA descriptor
reuse. These observations do not establish that ROM CLZ alone causes the
regression: the linked call boundaries, register spills, caches and scheduling
also differ. A separate CLZ microbenchmark is the next experiment.

| FLAC case | Elapsed decode ms / audio s, scalar → Rice | Change | Decoder-task CPU, scalar → Rice | DMA overruns, scalar → Rice |
| --- | ---: | ---: | ---: | ---: |
| Groove Salad, LPC12, HTTP | 262.12 → 280.45 | +6.99% | 24.94% → 26.57% | 0 → 0 |
| Bossa Beyond, LPC32, HTTP | 433.13 → 444.74 | +2.68% | 38.92% → 39.97% | 61 → 107 |
| Demanding 48 kHz FLAC, HTTPS | 198.71 → 218.77 | +10.10% | 19.92% → 21.21% | 118 → 229 |

DMA observations span about 45.1 seconds per FLAC run. Total CPU for Bossa is
90.94% in both variants; Groove is 72.26% → 73.86%; demanding HTTPS is 100%
in both. This is why total CPU alone cannot measure a decoder improvement.
Decoded-audio/wall ratios are 1.00153 → 1.00153 for Groove,
0.98708 → 0.97668 for Bossa, and 0.97323 → 0.94756 for demanding HTTPS.
The latter is materially below real-time progress despite remaining inside
the existing coarse 0.9–1.1 gate. Both HTTPS variants record **11 watchdog
events**, so neither is accepted.

Original case results, including adverse and incomplete observations:

| Case | Scalar control | Bytewise Rice |
| --- | --- | --- |
| Bossa LPC32 HTTP | Original gates pass; 61 DMA overruns remain | Heap-trend failure; 107 DMA overruns |
| Groove LPC12 HTTP | Heap-trend failure | Original gates pass; zero DMA overruns |
| Demanding FLAC HTTPS | Runtime watchdog failure | Runtime watchdog failure |
| HE-AACv2 alternating TLS records | 90 s pass; zero DMA overruns | Interrupted around 73 s by WebUI request timeout; **incomplete** |

In the failed AAC candidate run the exception chain is `URLError` →
`TimeoutError`; the captured codec/runtime check itself passes and records no
DMA overruns. The interrupted run is still a failure, not a 90-second pass or
evidence of an AAC speed improvement. Its partial metrics remain in the raw
summary. The request trace retains the transport phase timings. No retry was
performed merely to replace an unfavorable outcome.

Steady heap medians fall by 2,180 B in the control Groove case and 2,240 B in
the candidate Bossa case, exceeding the unchanged 2,048-byte gate. All eight
settled Stop-recovery checks pass. Median RSSI ranges from −61 to −57 dBm;
sequential ordering and network variation limit precise causal attribution.
Seven observations have complete telemetry; the interrupted AAC observation
does not. The pair is **NOT_QUALIFIED** for production.

The previous quiet image was restored through native OTA and verified by exact
ELF SHA, three successful playback observations, and unchanged Wi-Fi, settings
and playlist snapshots. Full-rate AAC playback resumed. No NVS/filesystem
rewrite or serial recovery was needed.

## Reproduction

The retained evidence includes exact build recipes, source snapshots, compile
commands, linked reader disassembly, complete sanitized case reports,
performance/status records, controller exit codes, and restoration checks.
Application binaries and sdkconfig files are under:

- `firmware/development/esp32c3-idf-6.1-r9a97-flac-rice-control/`
- `firmware/development/esp32c3-idf-6.1-r9a97-flac-rice-bytewise/`

These are laboratory artifacts, not production releases. Reproduction requires
fresh output/build directories, the recorded SDK revision, accessible local
fixtures, an awake C3, and a valid laboratory certificate for the host address.
Never reuse or publish a private test key. `physical.py` documents the exact
runner arguments; adjust board/host/serial paths to the local setup.

The [archive index](../tests/results/esp32c3-flac-rice-physical-20261008/index.json)
hashes every retained input/result. Replay from the repository root:

```text
python tests/test-flac-rice-physical-evidence.py
python tests/test-flac-hotloops-evidence.py
```

The physical replay also injects missing CPU samples, damaged markers,
interrupted observations, sparse DMA samples, zero decoded audio, and canonical
runtime failures into saved data to test the report's rejection behavior.
