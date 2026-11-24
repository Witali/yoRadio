# Full-application controls after the QEMU START correction

These are the preserved complete outcomes of a bounded experiment, not a claim
that every prior intermittent failure is explained. Firmware stays at the
current shared-scheduler source `b65437a1b`: RTC on, normal TCP 11520/10/5760,
fixed TLS 16384/4096, unchanged watchdogs, two CPUs and original audio bindings.
Only the selected QEMU executable changes in the quiet comparisons.

The [register regression and one-line correction](../cyd-i2s-dma-start-20261124/README.md)
establish hardware START semantics independently. The old and fixed relays have
matched retained inputs; this does not prove START caused the historical native
[continuous-DAC timeout](../cyd-ws-shared-scheduler-20261124/README.md).

## Unmodified controller, compiler-quiet controls

All five runs use the original full-app controller without QMP pause. Own GCC,
Clang and model compilation were terminal before the campaign. Every run delivers
all 614,400 decoder PCM frames, the complete HE-AAC TLS stream, and WebUI after EOF.
Two live WebSocket peers require fresh idle/playing/EOF status, application pongs
and normal close. Existing memory/PCM/asset gates are unchanged.

| Case | Result | Minimum heap | Allocation failures | Driver timeouts | Completion queue drops |
| --- | --- | ---: | ---: | ---: | ---: |
| [quiet-baseline-continuous-01](quiet/quiet-baseline-continuous-01/report.json) | PASS | 5612 | 0 | 0 | None |
| [quiet-fixed-continuous-01](quiet/quiet-fixed-continuous-01/report.json) | PASS | 5520 | 0 | 0 | None |
| [quiet-fixed-continuous-02](quiet/quiet-fixed-continuous-02/report.json) | PASS | 5932 | 0 | 0 | None |
| [quiet-fixed-legacy-01](quiet/quiet-fixed-legacy-01/report.json) | NONPASS | 1912 | 1 | 0 | None |
| [quiet-fixed-pdm-01](quiet/quiet-fixed-pdm-01/report.json) | PASS | 2500 | 0 | 0 | 2 |

The fixed continuous image passes both preselected runs and PDM passes. Legacy
remains **NONPASS**: one recovered 1522-byte DEFAULT|INTERNAL allocation fails,
despite complete PCM/EOF/WebUI and zero driver errors. This must not be relabeled
as success. The PDM completion queue drop counter is retained as recorded; decoder
PCM and driver-write gates do not measure physical DMA timing or analog quality.
The baseline continuous pass also prevents attributing native causality solely
to the successful fixed runs. RTC-off default HE-AAC/two-peer memory qualification
is a separate unpassed gate; these opt-in passes do not supersede it.

## Paused diagnostic controls, including all failures

| Case | Controller result | Minimum heap | Allocation failures | Driver timeouts | Completion queue drops |
| --- | --- | ---: | ---: | ---: | ---: |
| [reference-01](diagnostic/reference-01/report.json) | PASS | 5496 | 0 | 0 | None |
| [reference-02](diagnostic/reference-02/report.json) | NONPASS | 17472 | 0 | 53 | None |
| [reference-followup-01](diagnostic/reference-followup-01/report.json) | PASS | 2296 | 0 | 0 | None |
| [timeout-01](diagnostic/timeout-01/report.json) | PASS | 5584 | 0 | 0 | None |
| [timeout-02](diagnostic/timeout-02/report.json) | NONPASS | 4052 | 2 | 0 | None |
| [timeout-03](diagnostic/timeout-03/report.json) | PASS | 2356 | 0 | 0 | None |

These six runs overlap production compilation and are not compiler-quiet timing
qualification. Reference-01 has a controller PASS but an independent snapshot
failure from the original monitor-command spelling; it is preserved. Reference-02
captures a healthy state, then fails with output timeouts after a 31 ms observation.
The later 47 ms reference also captures a healthy state and passes. This is not proof
that every pause causes the original failure. Timeout-02 retains two 1522-byte
allocation failures despite complete PCM. The three timeout-triggered runs did
not produce a timeout snapshot; absence of a capture is not proof of absence of
the original issue.

Snapshots read only validated DAC registers/control metadata, never audio or TLS
buffers. `diagnostic/latest-dac-qmp.py` is the final helper revision. Each run pins
the helper/controller it actually used when a per-attempt binding is available;
the first reference predates these extra bindings. Earlier helper versions are
not all embedded, and are not claimed identical to the final helper. Program-counter
queries in the final monitor returned unavailable. Frozen ELF-derived layout and
per-backend artifact/translation-unit identities accompany the reports. These are
selected bindings, not a complete compiler dependency closure.

No private key, full TLS fixture, flash image, physical Wi-Fi/audio, listening or
sleep/wake qualification is included. The original raw NONPASS reports remain
immutable. The 1522-byte allocation owner is investigated separately; neither
increasing waits nor weakening the zero-allocation gate is an accepted fix.
