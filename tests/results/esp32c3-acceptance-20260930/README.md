# Physical acceptance runs, 2026-09-30

ESP32-C3 SuperMini OLED, no deep sleep, internal RAM only. Each report records
the tested ELF hash, fixture hashes and test-source hashes. Status captures
contain technical fields only; raw Wi-Fi/playlist/settings files are not saved.

## Results

- `ota-negative-final.json`: all ten rejection/interruption cases and settings
  restoration pass. The earlier `ota-production.json` also records successful
  app0/app1 round trips, upload during playback and slow upload, with exact
  image verification and unchanged Wi-Fi, playlist and settings.
- Four failures in the **earlier** OTA report were client issues: sending a
  whole image after an early rejection produced connection-aborted exceptions;
  an oversized request with no body timed out. The corrected client sends a
  descriptor-sized prefix, receives the rejection, and passes all ten negatives.
  Keep the earlier report for provenance; those four are not firmware failures.
- `http-production`: 22 AUTO/explicit-codec cases. Eight non-HE fixtures decode
  at their expected layouts, but 15 of their 16 cases fail the finite-file EOF
  status check. Six HE/v2 cases fail full-rate/profile validation after SBR OOM.
  Only FLAC AUTO and board restoration pass the entire case.
- `production-scenarios`: Stop/Play replacement, stall recovery, HTTP 503
  recovery, WebSocket metadata/reconnection and restoration pass. AAC changes
  fail at HE/v2 phases; redirect/jitter fail EOF. The old drop test observed only
  seven seconds, shorter than the firmware watchdog deadline; its failure is
  inconclusive and the corrected 20-second test has not been rerun here.
  The TLS test timed out, so certificate rejection is **not verified**. The
  newer handshake-alert evidence requirement also still needs a hardware run.
- `diagnostic-load`: all seven 40-second codec cases fail acceptance. HEv2
  falls back to the core, LC/HE have HTTP timeouts, FLAC has a request error,
  and MP3/Vorbis/Opus exceed the two-second HTTP response budget. Serial data
  are retained; this is not a passing CPU-under-load benchmark. Restoration
  succeeds. Short earlier CPU calibration results remain separately scoped.

EOF failures mean the WebUI status stays active after a finite HTTP response;
these measurements do not establish that physical audio continues after EOF.
No acoustic, OLED visual, interrupt-latency, power-cut or hour-long soak result
is inferred from these records. Trusted HTTPS and Wi-Fi-placement latency A/B
still require their documented setups.

Production ELF `b0f5c3a1e55bc3b309f6f56f197b7d40bf0d3b4c1c1196de9b2c8288b72832f3`
was restored after the later RAM survey. The saved station resumes at AAC PCM
44.1 kHz stereo. See [testing instructions](../../../docs/ESP32C3_TESTING.md).
