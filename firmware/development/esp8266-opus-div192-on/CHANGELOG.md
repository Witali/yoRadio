# Single-reciprocal candidate rejected, 2026-09-10

Experimental raw Opus benchmark, NOT a production release. Source `ccfe023`,
app902208 bytes. Matches the control build in every manifest field except
`opus_div_once`, build time and binary identity/size. No runtime bitrate cap.
CPU160/QIO40; corpus12/24/64/128/192kbps; FIR/ICDF/word helpers ON, rotation
ASM and CELT decoder-only specialization OFF. OTA succeeded (`ota.json`).

Ten candidate and ten control attempts completed, no decode or observation
errors. No failed/slow attempt was excluded. All PCM hashes match fixtures
and control. Host verification also covered28 PCM scenarios plus five
vq.c ASan/UBSan cases. This does not claim whole-codec sanitization.

| Fixture | Control CPU median | Candidate CPU median | Time change |
|---|---:|---:|---:|
| mono12 | 23.192% | 23.153% | −0.17% |
| mono24 | 55.026% | 56.436% | +2.56% |
| stereo64 | 65.015% | 72.866% | +12.08% |
| stereo128 | 80.392% | 95.128% | +18.33% |
| stereo192 | 94.337% | 117.323% | +24.37% |

CPU budget = task time / decoded PCM duration. Packets are in RAM during
decode; no network audio, normalization or PDM. Wi-Fi/WebUI still run;
charged ISR/instrumentation remain in task time. This is sequential A/B,
not interleaved; raw wall timing, p95/max and snapshots are retained.
`comparison.json` passed/comparison_valid means comparable completed tests,
NOT improved performance or production/RAM qualification.

Final host/target regression suite:75 tests,71 passed,4 optional skipped,
0 failures (`host-tests.log`). Two tests also recheck archive hashes and
compiler-probe source identity. These JSON artifacts use Git eol=lf to keep
their raw SHA256 stable on Windows checkouts.

Minimum observed free DRAM6820→8012 bytes, lifetime free stack1660→1708 bytes.
Static DRAM/IRAM delta0; flash text−560 bytes. Dynamic free-memory differences
cannot be attributed to the decoder with an active network. Longest observed
192kbps call23409→31427us. Candidate is too slow for192kbps even without PDM.

GCC outlined rotation into a helper when the reciprocal became single-use.
This is a possible cause, not a proven explanation of the regression.
Compiler-only inlining probes do not provide board speed evidence.
**Keep `OpusDivOnce` OFF. Do not promote this artifact.**

Reproduction after building/flashing the two recorded manifest configurations:

```powershell
node tools/esp8266_opus_profile/compare_raw.cjs --reference firmware/development/esp8266-opus-div192-off --candidate firmware/development/esp8266-opus-div192-on --switch opus_div_once --runs 10 --output firmware/development/esp8266-opus-div192-on/comparison.json
```

After testing, application-only OTA restored the existing diagnostic radio
image `esp8266-opus-block-live` (source `ff49a46`), confirmed in
`restore-live.json`; `restored-stop.json` confirms playing=false, no reported
error and WebUI status available. SPIFFS/settings untouched; no serial reset,
UART commands or host Wi-Fi changes. This restored image still has known
Opus continuity defects and is not described as gap-free production firmware.
