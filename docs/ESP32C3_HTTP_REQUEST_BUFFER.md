# Releasing the completed HTTP request buffer

## Design and ownership audit

Experimental build key: `CONFIG_YORADIO_HTTP_RELEASE_REQUEST_BUFFER=y`.
It is **off by default**. This saves the configured HTTP request/header buffer
(4,096 bytes), not a TLS record buffer or an audio packet. Full AAC/SBR/PS,
decoded precision and the original request capacity are unchanged.

Audited SDK: ESP-IDF revision `9a97f6c54ec638111ce55cd36581b3c192f15207`.
Normalized UTF-8/LF SHA-256 of `components/esp_http_client/esp_http_client.c`:
`152d658025205b1d0d090127a6d56d24726118c488d7d5bf5f85a98a15e87740`.
The generator rejects other source content. CMake replaces exactly one source
in the experimental build; the shared SDK and other projects are not modified.

All uses of `request->buffer` in that source were reviewed before adding release:

| Owner / function | Existing use | Rule after this change |
|---|---|---|
| `esp_http_client_init` | Allocates descriptor and full TX data | Unchanged; setup capacity stays available |
| `http_client_prepare_first_line` | Writes method, URL/query and HTTP version | Called only after full-capacity storage is present |
| `esp_http_client_request_send` | Header pagination and partial-send retries | Reallocates missing storage before a fresh request; retains in-progress storage |
| `esp_http_client_prepare` / perform reuse path | Resets first-line bookkeeping | Compatible with a fresh full-capacity allocation |
| `esp_http_client_send_post_data` / `esp_http_client_write` | Sends caller-owned body, separate from request header storage | Release rejects non-GET/body/async cases; these paths are unchanged |
| `esp_http_client_fetch_headers` / `esp_http_client_read` / parser callbacks | Uses response buffer and cached response data | No ownership change; no alias to freed request data |
| `esp_http_client_cleanup` | Frees request data and descriptor | The cleared pointer makes cleanup safe after release |

The added release API accepts only a synchronous GET with no body or pending
write, in `HTTP_STATE_RES_ON_DATA_START`. The stream task calls it only after
`open_stream` has accepted final 2xx headers; redirects have already completed.
Rejected states retain the buffer. Release is idempotent and clears the data
pointer and first-line flag. No numeric struct offsets or private layout copies
are used: the extension compiles inside the pinned SDK source.

Future requests allocate the original `buffer_size_tx`, preserving long request
lines and header pagination. Allocation failure returns `ESP_ERR_NO_MEM` without
writing or dereferencing NULL; stale `errno=EAGAIN` is cleared. An inconsistent
missing buffer with a prepared first line fails instead of discarding pending
request state. The application does not share the HTTP handle between tasks.

## Host verification

`tests/test-http-request-buffer.py --idf <SDK> --output <new-directory>` compiles
the actual patched SDK first-line/request sender and real SDK header/utilities
with ASan/UBSan. The transport and response-state transitions are scripted;
this is not a TLS integration test or a physical heap measurement.

36 cases passed, covering a 3,001-byte path, more than 8 KiB of paginated request
headers, partial writes, 20 identical repeated requests, double release,
reallocation failure and recovery, early release rejection, body/POST/async
rejection, transport failure and async leftover ownership. The allocator
records a 4,096-byte release and equal allocation/free counts. Unknown SDK
content is rejected; LF/CRLF normalization yields the same patch.

## Qualification

The quiet ESP-IDF 6.1 candidate builds successfully. Its only active configuration
change from `idf61-production-prefill1000` is this experimental key. Build/link
checks confirm unchanged contents for 18 codec objects (119 text/rodata sections),
the same public certificate bundle, and an application that fits the OTA slot.
These checks do not establish physical playback or HTTP lifecycle correctness.

This feature remains experimental until physical comparison, all-codec and
HTTP lifecycle regression, and OTA checks pass. A 4,096-byte freed allocation
does not promise a 4,096-byte increase in the largest free block: allocator
coalescing and subsequent network/decoder allocations determine that result.
No production default is changed by this experiment.
