# Pure host qualification for mono21 and map2-eight

This source proposal prepares `qualify.py`; it has **not** qualified either
campaign. Root owns later execution. The program only reads existing source,
tool, receipt, carrier and WAV bytes. It launches no decoder, process, SDK, QEMU,
Git operation or network request, and writes only a fresh qualification output.

The two profiles pin the exact completed reports and outer receipts:

| Profile | Cases | Owned reference commands | Original outer status | Required derived support |
| --- | ---: | ---: | ---: | --- |
| mono21 | 21 | 42 | exit0 | Both references on all21; no refusals |
| map2-eight | 8 | 16 | exit1 | Xiph all8; native8 lookup2 refusals |

These are actual root-reported campaign outcomes used to define the proposal,
not newly executed qualification results. Mono21 includes one/two channels at
the advertised nine rates, 294 raw packets and 464640 PCM bytes. Map2-eight has
stereo/192000 Hz, 112 raw packets and 225280 PCM bytes. The map2 original dual
NONPASS stays false for qualification; a separate Xiph-qualified result can
succeed only after all eight references and all four Xiph PCM pair equalities
are recomputed from actual bytes.

## Root-owned invocation

From the repository root, after reviewing these sources:

```powershell
python -B .build/cyd-vorbis-new-format-host-qualification-prep-01/qualify.py `
  --profile mono21 --repository . `
  --campaign .build/cyd-vorbis-mono-mapping-host-01 `
  --outer .build/cyd-vorbis-mono-mapping-host-01-command.json `
  --output .build/cyd-vorbis-mono-mapping-qualified-01

python -B .build/cyd-vorbis-new-format-host-qualification-prep-01/qualify.py `
  --profile map2-eight --repository . `
  --campaign .build/cyd-vorbis-map2-regression-host-01 `
  --outer .build/cyd-vorbis-map2-regression-host-01-command.json `
  --output .build/cyd-vorbis-map2-regression-qualified-01
```

Outputs must be fresh independent directories under the repository's `.build`.
Failures/interruption retain partial `qualification.json` before returning
nonzero (KeyboardInterrupt130). There is no automatic retry, deletion, stream
fallback or modification of original reports. A map2 qualification exit0 means
`XIPH_QUALIFIED_DUAL_NONPASS`, not that the original dual-reference run succeeded.

## Checks performed if root runs it

- Rehash every actual original input and frozen snapshot, including source MD
  provenance, plus the original/new driver and exact adaptation diff. Rehash both
  actual tool executables before and after qualification without running them.
- Validate actual outer and owned process receipts, tool/capture identities and
  both streams' size/SHA. A terminal nonzero native refusal is accepted only for
  map2, exactly3199971767 plus its documented lookup2 diagnostic. No failed WAV
  is used as a successful decode.
- Independently parse Ogg page CRC/sequence/header order and exact raw/carrier
  correspondence, full identification fields, all14 packets, neighbor flags,
  primer0, natural granules/EOS and overlap counts.
- Read each actual WAV and require exact sample rate, channel count, S16 width,
  frame/byte totals. Validate every framemd5 PTS/duration/size and MD5 against the
  corresponding WAV PCM segment. Recompute both byte nonzero counts and each
  channel's nonzero samples for SS/SL/LS/LL.
- Recompute signed-S16 crossreference maximum error from every sample with equal
  full lengths. The predeclared project policy is <=2 LSB; it is never fitted to
  the result. Recompute every matrix-declared same/different PCM relationship for
  each available decoder and require all Xiph relations. Derive support flags
  from these observations, then compare them with the preserved report flags.
- Rehash every consumed file once more before completing the qualification.

`carrier.py` contains exactly three pure definitions from the previously pinned
public carrier parser; `pins.json` records their source relation. No parser driver
or decoder entry point is imported or executed. `prepare.py` only assembled
these definitions and pins. Source checks do not run either qualification or
interpret actual PCM.

The optional support distinctions and <=2 crossreference policy are bounded
engineering evidence. Standard conformance, full G6, target execution,
production changes and physical qualification remain false. This work neither
changes the existing numeric01 adapter nor qualifies any new target campaign.
