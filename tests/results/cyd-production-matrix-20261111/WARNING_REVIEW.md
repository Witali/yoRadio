# Warning review

The CYD warning sets were compared by file, line, column, diagnostic and
multiplicity. The custom FLAC builds have the same warning sets as the
corresponding vendor builds. Continuous DAC has two fewer occurrences than PDM.
Legacy DAC removes three PDM occurrences and adds one warning at the I2S mode
initializer. The SDK defines master, TX and built-in DAC as bits 0, 2 and 4,
and its driver tests the individual bits. The resulting value 21 is valid for
this flags field. The GCC legacy-driver messages concern the three deprecated
SDK APLL calls. The earlier per-site review covers the inherited CYD sites.
[Prior CYD warning catalog](../cyd-transfer-pause-20261104/warning-triage.json)

- The C3 Wi-Fi JSON diagnostic reports a write past `action[5]`. The append
  guard requires `used < capacity` and `size < capacity - used` before the copy
  and terminator. Three new cases exercise an escaped valid four-byte action,
  a four-byte Unicode code point and a prefix followed by that code point.
  The Windows MSVC AddressSanitizer run passed 2,448 groups and 20,000
  deterministic malformed-input probes. WSL returned `Wsl/Service/E_UNEXPECTED`
  before starting GCC for this additional run. The C3 audio ASan/UBSan run had
  already completed. [Wi-Fi JSON cases](../../native/native_wifi_json_test.c)
- The C3 AAC reset warning follows recovery of the owning channel from a frame
  member pointer. The reset wrapper passes pointers to the actual left and
  right frame members. The alternate PS synthesis path is selected on the
  right channel after PS initialization, and the channel prefix offsets are
  asserted at build time. This review retains the existing private ABI design.
  [Reset wrapper](../../../idf/esp32c3-oled-native/main/aac_compact_owner.c)
- The HTTPD cleanup and bounded WebSocket handshake diagnostics also occur in
  the inherited CYD review. The generated C3 HTTPD files use the same audited
  overlay. The C3 report retains its SDK-specific file positions.
  [Current warning sites](clang-warnings.json)
