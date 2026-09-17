# 2026-09-17: exact qn v+1 flash lookup

Experimental frozen-layout ASM candidate; not production/default radio.
13->11 executed instructions with identical GPR/SAR at the old join.
Same903216-B app, RAM, IRAM, stack and outside addresses. New260-B table
occupies decoder-inaccessible bytes, replacing the superseded32-B table.
No bitrate limitation or change to C fallback.

3904 linked arithmetic cases and24 exact host PCM/state/PLC/reset/OOM cases
pass, including510kbps and120ms. Four ASM regression tests PASS.
Exploratory30 A/B/A at accidental1.5s HTTP polling completed:
CPU19279.949958/80.139354/79.940083%, slower against both controls.
Retained separately in high-poll, not eligible for the established15s protocol.
New30 A/B/A at explicit15s completed: CPU19279.611521/79.836104/79.646708%.
Candidate slower0.282099/0.237795% against A/A2; rejected, defaults unchanged.
Exact PCM, static RAM/stack unchanged. All observations/maxima retained,
including one mono12 task-vs-wall accounting excess1948us. No75% or live pass.
Qualified-series min sampled DRAM8352/8168/8196B, stack free1660B.
Max192 wall call21.871/19.761/19.993ms; zero observation/decoder errors.
Three mono12 task>wall values retained:119/1206/231us, no outlier filtering.
All60 distinct attempts archived; only30 at15s qualify for the raw protocol.
7 result/attribute tests PASS; related27 tests PASS. Goal75% still not met.
Prior ordinary C radio restored again by OTA; saved controls/playlist/WS verified.
RSSI-59dBm, stopped, free heap27448B. Not visual/live qualification.
