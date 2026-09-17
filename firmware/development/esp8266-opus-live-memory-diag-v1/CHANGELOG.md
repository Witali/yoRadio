# 2026-09-17: diagnostic memory/TCP radio

Experimental C-backend radio only; not production and not a speed improvement.
Adds diagnostic `/api/native/audio?memory=1`, nonblocking owner-task TCP
snapshot with explicit age, heap fragmentation, and existing SDK RX counters.
Full config/image identities are in manifest.json and evidence/.

Ten live starts retained,42 observation request failures,9 final decoder-init
errors and1 still reconnecting.39 closing-only TCP snapshots retain OOO data.
No CPU/continuity qualification; scratch and4096-B reserve unchanged.
10 regression tests PASS. See docs/ESP8266_OPUS_LIVE_TCP_MEMORY.md.

Prior radio image restored by OTA; saved station, WebSocket and playlist
verified. Do not distribute this diagnostic app as the accepted ASM build.
