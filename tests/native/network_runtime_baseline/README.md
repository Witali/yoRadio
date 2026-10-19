# Historical Wi-Fi runtime controls

Run from the repository with Python and a GCC/Linux host (WSL on Windows):

```text
python tests/run-network-runtime-baseline.py --out .build/network-runtime-baseline-01
```

`--revision` selects the historical commit; its default is the pre-runtime
`048a5c42df67a24b6e99396aae382f91d3b4ef49`. The runner obtains the original
source blobs from Git and freezes them, the harness and its host helper before
compilation. It never reads production files from the moving working tree.
`--target cyd` or `--target c3` narrows the campaign. Output must be a new folder.

These are executable negative controls, not positive tests of current firmware.
Actual historical startup, AP setup, callbacks and retry functions execute with
deterministic boundaries. Startup's wait seam invokes the actual GOT_IP handler
and the actual startup function returns before late failures are delivered.
The APSTA case executes the actual startup timeout and fallback path, then the
actual retry function; it observes AP removal before control returns to an HTTP
caller. No actual HTTP request or RF channel change is executed here.

Eight safety assertions must fail with exit code 42 and their exact named marker:
late fallback and manual retry on both boards; stale CLIENT/IP, failed config
publication, stale RSSI and failure to wrap from the last profile on C3. Build,
fixture precondition, timeout, sanitizer and unexpected process failures never
count as a detected defect. The C3 bool power API has a separate passing
characterization: an unowned later `false` replaces `true`. It does **not** execute
the audio generation race, and must not be cited as proof of its interleaving.

SDK result handling, netif state, events, state publication, timer/task admission,
loader results and driver acceptance are explicit host seams. C3's RSSI loop
executes until a controlled second delay. The profile loader supplies two
synthetic profiles; the test does not parse real credentials or log passwords.
`wifi_config_t` and state are field models, not target ABI replicas. ASan/UBSan
check the host execution, not target driver memory or SMP safety. No real SDK
event loop, RTOS scheduler, Wi-Fi binary, network, hardware or firmware image
is involved. Current runtime fixes require their own positive regression suite.
