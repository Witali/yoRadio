# C3 AAC memory investigation evidence

See [the analysis](../../../docs/ESP32C3_AAC_MEMORY_20260930.md) for conclusions,
scope, upstream links and reproduction commands.

- `provenance.json`: exact diagnostic application/ELF/map/library hashes and
  the restored production ELF identity.
- `diagnostic.sdkconfig`, `sections.json`: actual tested configuration and RAM
  sections. The DRAM dummy section aliases IRAM; do not count it twice.
- `report.json`, `status.json`, `performance.json`: real-board test outcomes,
  filtered technical status, boot/decoder heap snapshots and stack minima.
  LC passes. HE/v2 do not; v2 also encounters an HTTP request error.
- `upstream-layout.json`: pinned Android PacketVideo reference headers compiled
  for 32-bit RISC-V, including header hashes and member offsets. This is a
  structural reference, not Espressif's exact source or core structure.
- `binary-functions.json`: selected disassembly from the actual measured ELF.
  The 55,128-byte allocation, 25,792-byte channel stride and PS offsets match
  the reference. Decoder internal structure debug information is unavailable;
  the comparison does not establish complete source identity.

No Wi-Fi credentials, station names, NVS image or SPIFFS contents are retained.
No SBR allocation/layout optimization was installed. The no-sleep production
application was restored through WebUI OTA and its saved AAC 44.1 kHz stereo
station resumed.

Validation: diagnostic firmware builds and runs; all three native stream-format
host executables pass, 48 C3 Node checks pass, 14 acceptance-infrastructure Python
tests pass, and the saved layout tool reproduces all reported structure sizes.
Passing infrastructure checks do not turn the failed hardware cases into passes.
