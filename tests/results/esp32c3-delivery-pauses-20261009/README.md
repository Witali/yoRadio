# Matched delivery pauses on ESP32-C3

See [the report](../../../docs/ESP32C3_DELIVERY_PAUSES_20261009.md).
This experiment reuses the two saved integer-clock firmware images from the
[preceding capacity trial](../esp32c3-flac-integer-20261009/README.md).
No firmware is rebuilt. `firmware-baseline.json` pins that archive's index;
its source overlays describe the binaries, while the current `sources/`
directory describes the server and test helpers used for this run.

`physical.py` installs applications through native app-only OTA in the order
4 / 8 / 4 compressed-input slots, verifies image identity, QIO 80 MHz and PDM
registers, and restores the previous quiet application and playback in
`finally`. Wi-Fi, playlist and settings snapshots remain private; only
equality checks are saved. The expanded phase also runs three minutes of
full-rate HE-AACv2 after stopping FLAC and checking settled memory recovery.

Each three-minute HTTPS FLAC run receives the same six host delivery pauses
at 3, 6, 9, 12, 15 and 18 million encoded bytes, requesting 50 / 100 / 200 ms
twice. The finite file resumes unpaced delivery after each pause. All phases
request the same 4096-byte host send buffer. Host writes and pauses are not
TCP acknowledgements or measurements of packet arrival at the board.

`review.py` preserves the original gates and independently checks complete
CPU, decoder, output and DMA windows. CPU has no pass ceiling. A separate
zero-DMA-event criterion is stricter than the original playback checks;
these counters do not measure exact acoustic gaps. `pause_review.py`
verifies the actual pause schedule and brackets each pause with observed
DMA counters, allowing a one-second tail for buffered data. Any other
events within the same bracket remain included, without causal attribution.

Replay without a board or network:

```powershell
python tests/results/esp32c3-delivery-pauses-20261009/replay.py --output NEW_DIRECTORY
```

Replay verifies both evidence archives, saved image/configuration identities,
test sources, restoration and the derived verdicts, including failed gates.
It does not turn a failed hardware check into a pass. Local controller paths
are retained as provenance; a new hardware run needs new output paths and
valid laboratory TLS trust. Private keys and credentials are excluded.
