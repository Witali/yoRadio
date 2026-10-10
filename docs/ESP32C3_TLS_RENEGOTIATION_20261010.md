# TLS renegotiation during HE-AAC playback

## Physical result: output service failure reproduced

The first quiet-image campaign passes **17/18** checks. HE-AAC with 1 KiB
records has four I2S completion-queue drops; HE-AACv2 has none. A second
campaign on the same application repeats HE-AAC with 1 KiB and 16 KiB records:
**16/18**, with 13 and 23 drops respectively. No I2S write errors, allocation
failures, watchdog events or reboots are recorded. Each campaign contains
161 health observations. All four full TLS handshakes finish and playback
status continues at the expected 44.1 kHz stereo format.

| Campaign / stream | Handshake, ms | Output drops / errors | Min free / largest, B | Max status + health, ms |
| --- | ---: | ---: | ---: | ---: |
| physical / he-44100-stereo:small | 486.7 | 4 / 0 | 32,552 / 24,576 | 1132 |
| physical / hev2-44100-stereo:small | 599.0 | 0 / 0 | 32,660 / 24,576 | 349 |
| physical-comparison / he-44100-stereo:small | 592.2 | 13 / 0 | 29,784 / 22,528 | 462 |
| physical-comparison / he-44100-stereo:large | 445.5 | 23 / 0 | 22,048 / 11,776 | 405 |

The deltas cover the steady interval after the first 15 seconds and before
Stop. Every observed in-playback queue-drop increase is in the sample
interval surrounding/following the renegotiation request. `correlation.json`
retains exact before/after sample times relative to that request; these
sampled counters cannot establish the exact interrupt time or analog waveform.
Sampled free/largest blocks remain above the existing 16/8 KiB budgets.
SDK lifetime minimum free heap, including unobserved transients, is
19,992 B for the initial campaign and
16,912 B for the comparison.

There are three failed output gates across four playback cases; all four
handshakes themselves complete. Both reports preserve
their failures, and offline replay reproduces them without converting them
to PASS. Each controller restores the exact listened image and verifies
Wi-Fi, playlist, settings and stopped state before returning.

## Server and acceptance evidence

The saved application is the unchanged laboratory `idf61-quiet-growth-tls`,
SHA-256 `7871681aef75c9bb89caffab97f073eabe62b272ff8dc20f710cb4473c56b6fd`.
It has the same full compact AAC and 17,058-byte RX reservation as the prior
quiet tests, four input slots, and a 250..500 ms initial prefill. The test CA
extends normal roots, verification remains enabled, and no UART or optional
runtime profiler is used. No new firmware is compiled for these baseline runs.

The host server uses pyOpenSSL 26.4.0 / OpenSSL 4.0.3. TLS 1.2 and
`ECDHE-RSA-AES128-GCM-SHA256` are fixed, and session tickets and the session
cache are disabled. The same verified connection carries audio before and
after the request at 30 seconds. Delivery remains paced at 1.0 audio seconds
per wall second. No cipher, certificate check or AAC feature is removed.

Host tests check the real encrypted transfer against the original bytes and
a negative case where the client refuses renegotiation. OpenSSL emits a
HANDSHAKE_DONE callback for HelloRequest while renegotiation is pending;
the verifier requires a later callback with pending=false, the completed
renegotiation counter, and subsequent audio writes. That intermediate callback
alone is not proof of a handshake. The initial host-test failure identified
this distinction and is retained alongside the corrected passing tests.
See the [pyOpenSSL connection API](https://www.pyopenssl.org/en/stable/api/ssl.html#OpenSSL.SSL.Connection.renegotiate)
and [TLS 1.2 HelloRequest](https://www.rfc-editor.org/rfc/rfc5246.html#section-7.4.1.1).

## Interpretation and next experiment

This narrows the memory concern: the tested late handshakes fit with the full
HE-AAC/HE-AACv2 decoders alive. It does not establish a universal bound for
different certificates, groups, simultaneous clients or larger AAC frames.
The earlier 7,424-byte largest-block case remains separate evidence.

An output service interruption is now reproducible, rather than merely a
small-memory warning. Input starvation is a hypothesis: HE-AACv2 survives a
longer handshake at lower encoded bitrate, but both small and large HE-AAC
record modes fail. Those results do not prove that short records alone cause
the problem, or rule out scheduling/crypto effects.

`prefill_encoded_input()` retains the first decoder lease and waits at most
500 ms. It can exit once all input slots are occupied after only 250 ms;
occupation does not establish that every packet contains 2,048 audio bytes.
The SDK HTTP reader may return partial data (including data before a timeout).
The next isolated experiment sets only the minimum prefill to 500 ms, retaining
the current maximum, queue sizes, TLS record support, decoder precision and
stream-read timeouts. It is not a production-default change. Require new
measurements before attributing the failure to this mechanism or adopting it.

[Frozen baseline measurements and replay](../tests/results/esp32c3-tls-renegotiation-20261010/README.md).
