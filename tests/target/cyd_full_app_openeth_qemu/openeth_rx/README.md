# Diagnostic OpenETH RX allocation tests

The diagnostic-only SDK overlay allocates the received descriptor's actual length instead of `ETH_MAX_PACKET_SIZE` (1,522 bytes). It first requires a software-owned descriptor and a nonzero length no greater than both the Ethernet maximum and DMA buffer capacity. Zero and oversized lengths are dropped without allocating or reading payload; the descriptor returns to hardware and the cursor advances once. Valid packets retain the SDK receive capacity check, copy, retirement, and upper-layer ownership path. An allocation failure retains the descriptor and retries after the existing one-tick delay.

This affects the QEMU OpenETH diagnostic network. It changes no production CYD Wi-Fi source or configuration. Descriptor lengths include the model-supplied padding/FCS; the overlay forwards the same bytes and length as before.

Run from the repository root, using a fresh ignored output directory:

```powershell
python -B tests/run-cyd-openeth-rx-test.py --sdk C:/Work/yoRadio/.idf/v6.0.2 --output .build/openeth-rx-host
```

On Windows the runner uses GCC in WSL, matching the existing host-test workflow. Both variants compile with `-Wall -Wextra -Werror` and ASan/UBSan, with leak detection enabled. The runner extracts the actual generated SDK RX task and unchanged receive function, preserving their control flow. Only platform, descriptors, allocator pressure, and scheduling are host stubs; host descriptor layout and scheduling do not qualify QEMU or physical hardware timing.

The 18 cases cover a short frame with only 256 bytes available, no allocation for hardware-owned descriptors, a full frame's failed allocation/backoff/retry, six valid lengths including 1,522, four malformed lengths, unchanged receive capacity/ownership guards, cleanup after receive/upper-layer errors, exact payload copying, and ring wrap. The negative control executes the exact previous maximum-allocation task and cannot deliver the same short frame under the same pressure; its expected exit code is 17. The overall runner succeeds only when the candidate passes and the negative is rejected as expected.

`max-allocation-control.inc` preserves the prior task/receive excerpts and Espressif's original license notice. The runner reconstructs the complete prior overlay from the pinned SDK source and verifies SHA256 `77827f4605a712e9057484fe5999c8a3405e3e617f3f45e52ca8933d96be6cca`. The SDK guard remains SHA256 `b0526b76120abffe37ee8bd87b9e204880da18a5c02383e5d39b8e001bbcbb7d`; changed SDK bytes must be rejected, while CRLF normalization remains accepted. Generated candidate SHA256 is `e4808727b9a3a5a0e1617d57f0d39a11bdf85443b9e3556990ea4822cef60882`.

Each run preserves frozen source copies, extracted functions, compiler/test logs, source hashes, and `report.json`. Full diagnostic firmware builds and matched TLS/PCM/WebUI runs remain separate checks. Preserve the original fixed-size allocation runs when evaluating this new fixture; it changes the diagnostic image's allocation behavior and hash.
