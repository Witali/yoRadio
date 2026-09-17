# Wi-Fi TX completion diagnostics

2026-09-17. Diagnostic-only addition to `YORADIO_ESP8266_SDK_RX_DIAG`.

An accepted `ieee80211_output_pbuf` enqueue does not prove that the radio
transmission succeeded. The pinned SDK's `low_level_send_cb` exposes
`wifi_tx_status_t` in `aio->ret`. Observe it before the unchanged SDK code
releases its pbuf. No payload inspection, new allocation, blocking, logging,
retry policy or ownership change is introduced. The installed SDK is not edited.

`GET /api/native/audio?wifi=1` returns lifetime modulo-2^32 counters:

- `tx_completed`: all observed Wi-Fi TX completions;
- `tx_failed`: completions other than SDK `TX_STATUS_SUCCESS`;
- `tx_src`, `tx_lrc`: sums of the SDK short/long retry status fields.

Use differences between snapshots. These are not TCP retransmission counts,
not audio-only counts, and do not measure receive-frame loss inside the closed
Wi-Fi driver. This endpoint is separate from normal health to preserve its
bounded response size. Four maximum-width uint32 values produce less than128
JSON bytes. It uses the existing serialized HTTP scratch, not a new buffer.

Total counter backing storage is48 bytes (previously32). All twelve words are
copied in one short critical section. With diagnostics disabled there is no
counter storage or SDK interception. The source-overlay test removes inserted
lines and checks that every original SDK byte remains unchanged; the real
generated completion callback is exercised under ASan/UBSan, including pbuf
release on both successful and failed completions and concurrent snapshots.

This adds observability, not a demonstrated fix for live playback stalls.
