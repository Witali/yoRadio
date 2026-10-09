# Integer-clock cross-codec and long TLS qualification

See [the report](../../../docs/ESP32C3_INTEGER_QUALIFICATION_20261009.md).
The unchanged `idf61-flac-int4` diagnostic firmware is tested with the
high-resolution host-clock helpers from `cc23e8e7`. It is not the separately
built quiet production candidate. `firmware-baseline.json` pins the original
firmware archive and its source overlays; `sources/` here freezes the helpers.

The HTTPS matrix and transition/switch suites pass. The ten-minute HE-AACv2
test retains one initial-idle TCP connect timeout, missing qualified recovery
baseline, and 11 delayed-DMA notification events. No runtime fault or DMA write
error is recorded. These counters do not measure acoustic gaps. All original
failed gates remain failed; a successful replay does not mean acceptance.

`review.py` independently replays saved REST formats, memory checkpoints,
runtime and sustained telemetry. WebSocket/generation assertions remain the
original runner's results. `event_review.py` brackets the eleven events and
overlapping input/output wait windows, without assigning a causal timestamp.
The exact quiet image, settings and three playing observations are restored.

Replay without a board or network:

```powershell
python tests/results/esp32c3-integer-qualification-20261009/replay.py --output NEW_DIRECTORY
```

Local controller/build paths are retained for provenance, not direct reuse.
Use fresh output paths and valid laboratory certificates for another run.
The archived host logs also retain initial sandbox socket/temp failures and
their successful authorized reruns. Public certificates are included; no TLS
private key or board Wi-Fi settings are included.
