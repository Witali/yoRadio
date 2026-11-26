# Pbuf observer: original native matrix

All three original controller verdicts remain **NONPASS**. The collection
wrapper's terminal exit zero means it collected all three reports, not that
the resource workload passed. No absent EOF or post-close sample is created.

| Backend | Original stopping reason | PCM EOF / pbuf attribution |
| --- | --- | --- |
| Legacy DAC | WebUI connection closed without a response | EOF and attribution unavailable |
| PDM | WebUI/health response could not be decoded as JSON | EOF and attribution unavailable |
| Continuous DAC | Nonzero allocation-failure count | Exact 614,400-frame PCM; ten attributed pbuf NULL calls |

Legacy and PDM stop before an EOF probe dump. Their pbuf snapshot is null,
not a zero-failure observation. Available health snapshots are preserved
separately; a zero in an earlier snapshot does not cover an unobserved later
interval. The independent gates use true/false/null rather than promoting
missing information to a passing result. Later last-reachable health is never
substituted for the missing post-close health gate.

Continuous DAC completes the full 102,420-byte TLS/HE-AAC peer response and
614,400 stereo PCM16 frames at 48 kHz, hash
`44d9a67ecc2e6a6d382951442fb7bdf687510c784e2e9137036cbe0a38b6f362`.
Its EOF prefix has one bucket: layer 54, full-width type 640 (PBUF_RAM), length
1440, derived allocation 1,512 bytes, count 10, no overflow or saturation. The
captured instruction is the exact qualified `tcp_write` call through the
wrapper (inlined `tcp_pbuf_prealloc` line 266 / tcp_write line 613). Global
allocation counts are 10 during the captured WebUI interval, at EOF and in the
last-reachable snapshot. The prefix and later snapshots are separately labeled
observations; they are not an atomic common window or a post-close resource
pass. The original zero-allocation assertion remains unchanged and fails.

Raw reports, UART, terminal logs, input bindings and parser analyses retain
their original bytes. The three frozen observer images/configurations and
exact linked ELFs are identified by the root release, completed static audit
and per-run bindings. Binaries, object archives, private keys and certificate
bodies remain local. Complete TLS peer transmission is a separate gate from
guest PCM/ordered EOF consumption. QEMU is intentionally stopped after the
observations; exit status 1 is not a clean guest exit or an observed guest crash.

Certificate-date checking was already **disabled** in these unchanged
profiles (`MBEDTLS_HAVE_TIME_DATE=false`). The old disposable CA/server
certificate dates were expired at the recorded host time. The retained date
policy records metadata only, no key or certificate body; it makes no
configuration/credential change and does not claim validity-date enforcement.
The original signature/chain/hostname policy was retained, but these results
must never be described as proving certificate-date validation.

The root release's initial header-path assumption and its correction remain
recorded separately. Standard fixtures contain config JSON; their headers
are in compiled snapshots. Parser control recipes and prior parser versions
are retained with their own source hashes, including the actual ELF/tool
witness and negative correspondence/counter controls. Recipe copies depend
on original private paths and are review evidence, not standalone launch
instructions from this public directory. Old SDK/host manifests and every
referenced published body are verified and left untouched.
