# Aligned eBands EXTUI experiment — 2026-09-17

- Against accepted eBands-final; six helpers save one instruction per call,
  five contiguous cross entries remain at parent+16. No executed padding.
- 401280 numeric verification cases;24 host PCM cases
  through510kbps/120ms,20 local regressions PASS, no RAM/stack increase.
- App903216B, SHA256
  `09a03d89865399c0222e57175d22b62ba0ecaad825c18c3ca8489c53c1b4c5c8`.
- All30 physical A/B/A2 retained. CPU19277.875625/77.859187/77.879229%;
  CPU12870.385687/70.404708/70.372021%. Both acceptance gates FAIL.
  Not promoted. Candidate exists only for reproducing the experiment.
- Max19219.949/20.980/20.771ms, minDRAM2940/5184/7484B, stack1660B.
  A2/run2 mono12 task>wall2615us retained, no empty-loop subtraction.
- Ordinary accepted ASM restored OTA; station167/stopped, playlist/settings
  retained, HTTP/WS observed. No live I2S continuity claim.
- [Full report](../../../docs/ESP8266_OPUS_ASM_EBANDS_U16_ALIGNED.md).
