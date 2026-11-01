# Actual local TLS traffic checkpoint, 2026-11-01

The complete isolated host and ESP32/QEMU traffic campaign passed. The native
run completed seven verified 65,536-byte responses, each with four full
16,384-byte plaintext records and the exact synthetic body SHA-256. Two clients
were simultaneously live on cores 0 and 1 and exchanged data in four synchronized
rounds. One used the actual static RX reservation; the other used a distinct
heap buffer. This checkpoint does not enable a production default or qualify
physical devices, RF, radio/TFT load, physical headroom, throughput, or full TLS
conformance.

The original history is preserved without rewriting reports or outcomes:

| Attempt | Original result | Precise scope |
| --- | --- | --- |
| `peer01` | NONPASS | Initial host environment attempt; server listened but accepted zero connections. The exact client OS error was not recorded. |
| `peer02` | PASS | Actual Python TLS 1.2 clients: five complete responses, twenty full records, certificate/name refusals, close/truncation controls, two live clients and recovery. |
| `freeze01` | Unbuilt/unrun | Preparation passed; execution acceptance remains false. |
| `native01` | NONPASS | Genuine disk exhaustion at SDK archive creation, before any QEMU/MCU execution. Driver exit 1; actual SDK child exit 2. |
| `native02` | PASS | Actual SDK child and driver exit 0, QEMU exit 0 through QMP, seven complete responses and actual helper/pressure observations. |
| `syntax01` | NONPASS | Standalone observer incorrectly parsed escaped command-line macro quotes. It did not establish a C source defect. |
| `syntax02` | PASS syntax only | Correctly parsed original configured Xtensa recipe, unchanged C source, no SDK build or MCU execution. |

The target uses the pinned ESP-IDF 6.0.2 classic dual-core ESP32 configuration,
RX 16384/TX 4096, hardware MPI/AES/SHA, public ESP-TLS and PSA hash APIs, and the
canonical guarded build-local TLS overlay. Installed SDK sources are unchanged.
A disposable generated CA is included in the diagnostic certificate bundle,
and the guest clock is set to the recorded historically valid epoch. Hostname
and certificate verification remain enabled; no insecure skip or certificate
store installation is used. The actual guest logs include eight successful
bundle certificate validations, including the connection later truncated.

The public ELF-symbol transcript identifies `s_rx` as BSS address `0x3ffbbd98`,
size 16,717 bytes, including the SDK's record overhead. Ten genuine bundle
attaches and ten actual RX allocations/frees balance: nine static loans and one
heap fallback. Disassembly observations retain the actual SDK setup/free hooks
and the actual early-MPI call. Source snapshots, complete compile records and
all 1,718 actual compiler dependency fingerprints are bound. Unflagged dependency
bytes are included; flagged dependency payloads remain whole local omissions.
The checker authenticates those recorded identities rather than claiming to
reopen unpublished ELF/tool/credential payloads or rebuild their contents.
The original recorded tool hashes cover Python, PowerShell, QEMU, nm, objdump
and the ROMs. GCC compile recipes and CMake compiler/version records are retained;
a separate before/after hash of the GCC executable was not recorded and is not
manufactured by the offline checker.

The wrong-name native handshake reports `-0x2700`, the recorded X.509 verification
failure; the explicit handshake-close peer reports `-0x7280`. The independent
server sees the certificate-rejection alert and a real client hello before the
handshake-close control. Per-certificate native flags were not separately
captured, so they are not invented here. The truncated peer advertises a
16,408-byte encrypted application record but sends only 8,209 wire bytes. Native
read returns zero with zero response-body bytes. This proves rejection of an
incomplete response by the diagnostic; it is not presented as an observed TLS
alert. Subsequent complete verified requests succeed.

For pressure, the test keeps a real verified TLS connection and protected
READY/READING/WRITING input leases live, then exhausts actual allocator storage
using diagnostic pressure blocks. Forwarding wrappers observe one genuine
allocator NULL and one recovery; exactly one IDLE input slot is released within
the original budget of four. Resident bounds, lease counts, all retained byte
patterns and the live RX owner are asserted before pressure storage is restored.
The complete TLS body and a later reopen then pass. This is an explicit public
allocator pressure probe with live traffic state, not a claim that a particular
TLS-internal handshake allocation itself exhausted memory. No calloc-NULL result
is injected.

Original OpenETH diagnostics remain in the full guest transcript: unsupported
MAC multicast filtering (three associated messages) and one RX-frame drop
during parallel traffic. All seven complete bodies still match exactly. The
checker requires these original diagnostics to remain present; their removal
does not turn this into a warning-free, performance, or physical-network result.
QEMU uses normal OpenETH user NAT; it does not use or claim `restrict=on`. The
guest connects only to the explicit synthetic `10.0.2.2` endpoints, and host
listeners/QMP bind only to loopback. This does not claim NAT denies all possible
external routes.

`captures.zip` holds 2,192 untouched original logical files and seven explicitly
new selected-fields projections in 1,990 content-addressed blobs. It preserves
the full actual guest and independent server transcripts, compiler/config/source
records, disassembly, symbol metadata, and terminal child logs. Of the complete
3,812-original-file census, 1,620 whole payloads remain local: generated server
key, CA/certificates/bundle artifacts, diagnostic images, binaries/tools, and
186 raw-scan-flagged/contact-bearing logical payloads. Every omission retains
its original exact hash and size, with no alternate byte publication or semantic
privacy override. The CA signing key was never written by the material
generator; the server key remains in the ignored material directory.

Five original reports are published unchanged. The two original native reports
contain a personal-home executable path and therefore remain whole local
omissions. Their original hashes/sizes are retained. The clearly labeled new
literal projections carry selected terminal/source/config/tool/log fields and
the original report identities; they are not represented as original report
bytes. The public checker cross-checks their claims against the untouched actual
SDK-child records, guest/server transcripts, frozen inputs and compiler metadata.
It explicitly does not read the omitted originals or claim their unpublished
contents were independently reconstructed.

Run `python tests/results/cyd-tls-traffic-20261101/verify.py --self-test` for frozen
data authentication and forty contradictory evidence controls. These cover
source/driver/SDK failure, unrelated TLS refusals, body/hash/record mismatches,
fake pressure, premature RX release, lost input ownership, serialized traffic,
warning suppression and promotion of original nonpasses. The checker executes
no archived C/Python/PowerShell or native image and reads no omitted payload.
Default historical verification does not depend on current production, SDK,
certificate expiry, tools or files under `.build`. `--require-current` adds an
explicit optional check of the bound canonical diagnostic sources only; later
application changes do not invalidate the frozen checkpoint.

Primary setup references: [IDF 6.0.2 Ethernet](https://docs.espressif.com/projects/esp-idf/en/v6.0.2/esp32/api-reference/network/esp_eth.html)
and [Espressif QEMU Ethernet support](https://github.com/espressif/esp-toolchain-docs/tree/main/qemu/esp32#ethernet-support).
