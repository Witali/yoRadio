# CELT band-stage diagnostic, 2026-09-13

Separate C fixed-point profiling image, CPU160/QIO40. Selected stage8
measures quant_all_bands inclusive wall time; the outer decoder task counter
remains separate. Five own12/24/64/128/192kbps raw fixtures; no network audio
or physical PDM output during the benchmark. Wi-Fi/WebUI/OTA stay enabled.

Use only after the current uninstrumented ASM comparison finishes. This
build is for locating costs, not claiming a speedup against an uninstrumented
image. Stage timings must pass stage_profile_result.cjs clock/scope checks.
Source revision, parameters and SHA256 are retained in manifest.json.
Image903632B. Not yet flashed or physically measured at archival time.
