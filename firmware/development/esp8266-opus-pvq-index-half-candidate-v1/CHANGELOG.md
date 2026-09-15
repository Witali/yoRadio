# 2026-09-15: phase-specialized PVQ signed index

Independent immutable overlay over accepted index-word v2, not a default.
BBCI selects lower/upper signed halfword; original return-store ordering
restored without touching a0/SAR.25 live bytes/35 patched bytes, RAM/frame0.
Exact137792 linked signed/table cases and24 sanitized host PCM/state cases.
Candidate app903216 B, SHA2560d76ec891f194e58e385339f1777e38c187b1bd0616a3c3bc8dfce91a033468e.
Speed/80%/20second I2S-WebUI gate pending. Ordinary restore required after A/B/A.

Initial ADDI.N-2 preview failed; replaced by supported ADDI-2 before packaging.
Host registration initially missing after oversized patch command; fixed
with a narrow edit. Both failed-run logs retained; no failed firmware flashed.
Full160 related preflight PASS/0skip,258.95seconds; complete log retained.

Completed30 A/B/A:CPU19280.05594 /80.01998 /80.04450%,
CPU12872.06458 /72.00285 /72.02125%; both speed gates pass.
Max19229877 /20371 /22845us; minDRAM1044 /8020 /8176 B,stack1660 B.
Two A observation timeouts preserved; B mono12 task>wall279us preserved.
No decoder errors. Accepted experimental baseline80.01998%, not80%/live.
Ordinary C radio restored OTA, stopped167/playlist/HTTP/WS unchanged.
Root HTTP200/27249 gzip bytes/103.15ms;heap27628 B,min24748 B,RSSI-61dBm.
Final165 related regressions PASS/0skip,346.60seconds; full log retained.
Two independent Git evidence-line-ending regressions also PASS.
