# Function-profile pilot, 2026-09-13

Diagnostic raw-only Opus GCC-ASM, CPU160/QIO40. Not ordinary radio and not
a release. Source4c35dc6f; exact image/configuration hashes in manifest.json.
Application-only OTA succeeded; Wi-Fi/SPIFFS/playlist unchanged.

Three pilot attempts retained in pilot-reports. PCM exact, device error0.
Attempt3 failed the host outer/nested wall-window check: those windows used
different SDK time sources. The series stopped; no pilot data are included
in the final performance tables. Superseded by functions-192-v2, which uses
one coherent runtime clock for both windows. Keep pilots as failure evidence.
