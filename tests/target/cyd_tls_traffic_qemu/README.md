# Isolated actual TLS traffic diagnostic

This new target exercises the unchanged CYD static RX reservation, adaptive
input reclaim and early hardware-MPI preparation against a synthetic host
loopback TLS1.2 peer. It is separate from production selection and from the
earlier isolated registry/setup tests that have no TCP traffic.

The target uses ESP-IDF 6.0.2, classic dual-core ESP32, OpenETH/generic PHY,
RX 16384/TX 4096, hardware MPI/AES/SHA and a guarded build-local TLS overlay. A
fresh disposable CA is added to the diagnostic certificate bundle; the guest
uses its recorded valid clock, public ESP-TLS APIs and actual certificate/name
verification. There is no insecure verification fallback or store installation.

The host peer generates four actual 16384-byte plaintext TLS records per 65536-byte
response. Cases cover cleanup/reopen, wrong-name/handshake-close/truncated-record
refusal, recovery, two simultaneously live connections with synchronized data
rounds and distinct static/heap RX owners, and real public allocator exhaustion
with a live TLS connection and protected READY/READING/WRITING input leases.
Pressure never injects calloc-NULL; predicates are captured before releasing
diagnostic pressure blocks. This explicit allocator pressure probe is separate
from a claim that a particular TLS handshake allocation itself exhausted heap.
Panics, unknown refusals, timeouts and partial transfers remain NONPASS.

`create-test-material.ps1` writes only a fresh ignored campaign; the CA private
key stays in memory, and the generated server key remains local-only. Never
publish generated keys, unreviewed certificate bundles, or images containing
unreviewed material. Full payload omissions must retain exact hashes and sizes.

Run `tests/test-cyd-tls-traffic-peer.py` first to qualify actual Python TLS1.2
clients, including unknown-CA and wrong-name certificate refusals. Use
`tests/run-cyd-tls-traffic-qemu.py --preflight-only` or `--freeze-only` for source
preparation without SDK/target execution. A fresh controller run builds only
after the heavy SDK slot is available. Its QEMU arguments use normal user NAT
with OpenETH and the guest connects only to explicit synthetic 10.0.2.2 ports.
They do not use or claim `restrict=on`. QMP is bound to127.0.0.1 solely to quit
the owned emulator cleanly after the complete marker. No physical device, RF,
external endpoint, radio/TFT load, hardware headroom or MCU timing is qualified.

Primary setup documentation: [IDF 6.0.2 Ethernet](https://docs.espressif.com/projects/esp-idf/en/v6.0.2/esp32/api-reference/network/esp_eth.html)
and [Espressif QEMU Ethernet](https://github.com/espressif/esp-toolchain-docs/tree/main/qemu/esp32#ethernet-support).
