# ESP32-C3 retained TLS receive buffer experiment

The retained receive buffer remains **disabled by default**. It avoids repeated
large TLS allocations, but the physical tests still exhaust memory for smaller
network buffers. This experiment uses the published ESP-IDF `v6.1` tag and is
a control for the subsequent qualification of `release/v6.1` commit `9a97f6c54ec6`.

## Configuration

`CONFIG_YORADIO_TLS_RETAIN_RX_BUFFER=y` selects the SDK's
`HTTP_TLS_DYN_BUF_RX_STATIC` strategy for radio connections. The SDK allocates
the complete receive buffer after the TLS handshake and retains it until close.
Transmit buffers remain dynamic. The optional overlay is
`sdkconfig.tls-retain-rx.defaults`; it does not change codec precision or rates.

The saved laboratory image is
[`esp32c3-idf-6.1-memory-icy-tlslab-rx6-retain`](../firmware/development/esp32c3-idf-6.1-memory-icy-tlslab-rx6-retain/manifest.json),
ELF `0ba3b7bc5bc2ef035fe23eb06964bb93d6b3d19aa1b074d5a7eb88e20f31720d`.
It uses copied RX buffers, an 8,640-byte TCP receive window, compact PC19 AAC,
the HTTP fatal-read guard and the TLS EOF adapter. The test CA extends the
normal certificate roots. Certificate verification and the full 16 KiB TLS
record capacity remain enabled, consistent with
[RFC 5246 section 6.2.1](https://www.rfc-editor.org/rfc/rfc5246.html#section-6.2.1).

Both variants of the host connection test pass 37 cases, with the option
enabled and disabled, under ASan/UBSan. Linked audits confirm the AAC features,
the incoming EOF adapter, the SDK dynamic read wrapper, the post-handshake
retention call and buffer cleanup. These checks do not qualify memory headroom.

## Physical results

The eight TLS framing cases all reach full 44.1 kHz stereo HEv2 and the expected
terminal status, but all **fail** their runtime gate. The capture contains
181 allocation failures, with requests from 1,060 to 1,700 bytes. At allocation
failures, free memory reaches 4,876 bytes and the largest block reaches 704 bytes.
Those two minima need not belong to the same allocation.

The attempted 600-second alternating-record test ends early with a WebUI
`TimeoutError`, about 525.9 seconds into the case. It records another 51 failed
allocations of 1,512 or 1,700 bytes. Idle recovery passes: free heap returns to
about 143.5 kB (143,504–143,524 B), with a 110,592-byte largest
block. This is not a completed ten-minute playback qualification.

The original file matrix reports 44 status/EOF passes and one successful Stop.
A separate audit finds **165 allocation failures** in its serial capture.
The original results remain unchanged; they do not meet the stronger runtime
acceptance requirement. A host build overlapped part of this file matrix, so
its CPU measurements are not a matched performance comparison.

The public 60-second cases pass for AAC-LC 128 kbit/s and MP3 256 kbit/s.
HE-AAC 64 kbit/s fails the runtime gate; HE 32 and mono HE 16 kbit/s end in
WebUI timeouts. Both the public suite's idle recovery and settings checks pass.
These results reject the retained-buffer configuration for production use.

The control session restores the ordinary image by app-only OTA, verifies its
ELF identity and unchanged Wi-Fi, playlist and settings, and confirms saved
station playback in three observations over 15 seconds. A later session then
installs the latest-revision test image; this restoration describes the control
session's endpoint, not the board's state throughout subsequent work.

Original reports, filtered serial/status observations, source snapshots and
public test certificates are retained in
[`tests/results/esp32c3-retained-tls-rx-20261008`](../tests/results/esp32c3-retained-tls-rx-20261008/).
Its index hashes 142 files. Private keys and received broadcast audio are excluded.

## Acceptance change and next step

Positive file tests now reject captured memory, decoder, TLS, panic, watchdog,
reboot and serial failures. They explicitly record whether serial capture was
enabled. A regression test supplies correct HEv2 status and natural EOF while
injecting 14 different runtime faults; each must fail and stop playback.

Further firmware work targets the pinned latest revision of ESP-IDF 6.1.
Retaining a full TLS buffer alone is insufficient. Any replacement must preserve
full AAC LC/SBR/PS output, other codecs, certificate verification and full-sized
TLS records, while leaving enough memory for network and WebUI traffic.
