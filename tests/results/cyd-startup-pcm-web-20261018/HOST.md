# CYD startup, PCM and native WebUI host qualification

Hardware was not flashed or measured. This report qualifies production functions
with explicit RTOS/driver/socket/flash seams; SDK builds and physical acceptance
are separate. Focused implementation commits: startup `b261e301`, PCM
`8693a921`, WebUI `2852dc44`, explicit web boundaries `420bc2bc`.

| Block | Evidence | Result |
| --- | --- | --- |
| Checked startup, registry and gated tasks | [startup/report.json](startup/report.json) | 228 scenarios, eight ring/adaptive/vendor/custom variants; all allocation/registration/task creation failures, concurrent controls, rollback and retry |
| Signed packed PCM and resampler | [pcm/report.json](pcm/report.json) | PDM 1359 / DAC 1358 / legacy 1358 stream cases; 721152 conversion checks each; 1278222 PDM interpolation checks, maximum 2 LSB against independent rational reference |
| Existing gain and normalizer | [gain/report.json](gain/report.json), [normalizer/report.json](normalizer/report.json) | Existing 16-bit output remains exact; normalizer 239/240/239 packet cases |
| Integrated decoder/output lifetime | [lifecycle/report.json](lifecycle/report.json) | Six variants; all supported PCM depths publish aligned packets; other depths/zero channels rejected before publication; generation, completion, 2000 concurrent controls |
| HTTP/ICY/status/settings | [http/report.json](http/report.json) | 50 stream scenarios and 80 settings requests; permanent stream-buffer OOM moved to synchronous startup coverage |
| Static dispatch and embedded page | [static-page/report.json](static-page/report.json) | Bounded queue and two workers, gated startup/rollback, raw/gzip and read/send failures; five executed JavaScript scenarios including reconnect and two-tab settings updates |
| WebSocket core and transport | [websocket/report.json](websocket/report.json) | 38 fixture groups; two clients, at most one queued status work item, fd reuse, full short-write/read handling and timeouts; JSON maximum 4828/5120 bytes |

Every C campaign above uses ASan/UBSan; UI JavaScript runs in Node with DOM,
fetch and socket seams. Sources and logs are saved beside each report. The
[negative controls](pcm-negative/) run original `900e009c` configure functions
and reproduce lost PDM tail and failed DAC priming retries. The direct source
checks for settings/clock also [pass 13 cases](source-checks.log).

The native root page is embedded in flash and works without SPIFFS assets. It
uses the existing REST controls and receives coherent status/radio/settings over
`/ws`. `/api/native/capabilities` advertises implemented features. Uploads, OTA,
Wi-Fi profiles, EQ, SD and display controls are not advertised yet. Arbitrary
SPIFFS data files, including Wi-Fi credentials, are not exposed by static GET.

HTTPD uses five client sockets and three internal sockets in the existing
10-descriptor lwIP profile; the radio stream leaves one additional descriptor.
Two workers each reserve 4096 stack bytes; the WS producer reserves 2048, with
5120 bytes of static status workspace. These are allocations/configuration,
not measured free heap or stack high-water. Application WS send frames and
receive-handler reads each share a one-second deadline. SDK opcode/control
reads have separate finite per-read budgets. Real TCP scheduling, complete
browser rendering and concurrent physical audio/WS/download timing remain open.
The in-app browser could not reach the local preview server; no visual-browser
pass is claimed. The temporary server was stopped.

Successful output/LED initialization intentionally persists through failed
pipeline starts; task/queue/registry resources are rolled back. The application
currently attempts startup once; callers may safely retry the public API.

Full static checks at this checkpoint: CYD 24 units / 8 warnings / 0 errors
([report](../native-lint-20261018/cyd-startup-web-pcm-final/report.json)); C3
50 units / 97 warnings / 0 errors
([report](../native-lint-20261018/c3-startup-web-pcm/report.json)). All new web
units have zero warnings after six explicit comparison/queue-boundary fixes.
The remaining C3 finding multiset exactly matches its previous full baseline.
The user's follow-up requests prioritizing dangerous remaining warnings; that
review is a separate ongoing change, not completion of every lint finding.
