# Candidate2: idle-input reclaim plan (UNIMPLEMENTED)

[report.json](report.json) is the byte-identical frozen next-step plan. It is
preparation only: no candidate2 code, host tests, target builds, real OOM/SMP
qualification or board measurements were performed. It does not complete M13.
All host/actual-target/physical gates listed in the report remain **unrun**.

The proposed boundary is bind after successful READY commitment, before owner
notifications, with no rollback after binding; reclaim only existing IDLE
extras with a fixed per-allocation retry budget. The plan preserves the sole
native_health failed-allocation callback, current task/core ownership and all
numeric pool/TLS/headroom/IRAM settings. Checked detach/refpin and separate
ordinary queue/health-reader quiescence conditions are described for safe
lifetime handling. No runtime pool teardown feature is implemented or implied.

[snapshot-map.json](snapshot-map.json) maps all35 frozen source/SDK/config/test
context inputs to short content-addressed objects. These are plan provenance,
not a declaration that historical build configurations equal later exports.
The original archive README and all pre-existing entries are unchanged.
[previous-root-manifest.json](previous-root-manifest.json) preserves the root
manifest before this additive extension. Only its file table was extended;
the root verifier covers this addition as ordinary archived payloads.
