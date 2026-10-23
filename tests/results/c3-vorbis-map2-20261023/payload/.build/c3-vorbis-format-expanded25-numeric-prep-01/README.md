# C3 complete25 numeric adapter source proposal

This directory prepares an offline numerical adapter for a future **complete
actual C3** checked-only capture: 25 cases, 350 packets, 623360 PCM bytes, and 778
protocol events. The order remains original books8, additional map2 books8, and
original floor9. There is no subset CLI. Preparation does not inspect the live C3
baseline, PCM, references, or an actual C3 target result.

The source starts from the CYD complete25 numeric adapter at
`2fe6ca486c0031101f15c787a84c39c419840b914ae0c829c95bd4095ec37a08`.
`pcm_metrics.py` and `policy25.py` are ordinary byte-identical copies at
`a2c600f8e19f3b48baaa12c559e60d0105401cba12362ce0250836c23b319f8f` and
`32ef721fa8a812684e83be296d7b74f90a12414644639f74ea353eef862d3dd6`.
No prepared adapter, metric, policy, protocol, SDK, compiler, emulator, reference,
or test code has been imported or executed during this preparation. Canonical
production sources, campaign inputs, and Git state are untouched.

## Exact adaptation

The adapter changes three runtime pins to the reviewed C3 prep02 sources:

- Runner: `e00a30172c3b4291f080b2eee937214108adda7b6a03178e2f9833cb44d92034`.
- Protocol: `961b0050f5881e5000116cbf7a598a122407420b0a52da0805d060c7b7e3f7ba`.
- Caller: `8c6aff4bb6d43c6b034db799477653e89fff4c9e65ac0b805d99f257672e9f03`.

Contract, model, corrected data header, descriptor header, source map, reference
binding, and binding-helper identities stay unchanged. `adapter-adaptation.diff`
contains the complete literal diff. `source-relation.json` binds its source and
runtime inputs. `check_source.py` checks only ASTs and raw source/JSON bytes.

New platform checks require `esp32c3`, SDK revision
`9a97f6c54ec638111ce55cd36581b3c192f15207`, ELF machine 243, and coordinator and
worker core 0. They verify both actual SDK-head command logs, ILP32/RV32,
160 MHz/unicore/ESP32C3 compile macros, and the retained little-endian ELF32/RISC-V
build image against its report hash. This adapter therefore requires the actual
ELF and compile-command JSON to remain available until measurement completes.

The setup identity is dynamic: the report's `selected_setup_sha256` must bind its
single frozen candidate setup source, actual compiled variant setup, reported
variant identity, actual compile row, and macro-context row. The result records
that exact hash. It never assumes that C3 and CYD source or binaries are equal,
and does not substitute current production source for a historical snapshot.
Windows build/variant keys are normalized through the existing strict relative
path function; duplicate normalized keys are rejected. The pinned C3 protocol
independently checks core 0 on every native event.

The existing complete25 command/outer-terminal/log/PCM gates remain intact. All
nine actual target commands and the direct-tool terminal must complete with
exit 0 and no timeout/interruption. A partial or NONPASS capture is rejected
before any target/reference PCM is read or recovered. The native PCM_HEX stream
must exactly match all 25 named persisted PCM files and every packet boundary.

The actual old17 and additional8 Xiph reference scopes remain separately bound
to their original reports, qualifications, receipts, raw inputs, WAVs, and
framemd5 logs. Their original dual-reference NONPASS results and native lookup2
refusals stay preserved. No aggregate25 reference command is invented.

The optional predeclared project bound remains exactly 2 S16 LSB, default None.
It is an engineering regression policy, not a normative Vorbis tolerance.
Alignment is diagnostic only; comparison uses the original zero-lag L/R samples
without trim, channel swap, gain correction, or resampling. The named books16
subgroup is reported only after complete25 capture and measurement and cannot
override the full25 result. Every failing case and relation stays reported.

## Root-owned future invocation

After source review and a complete actual C3 full25 capture, the root may run:

```powershell
& 'C:/Work/yoRadio/.idf/python-3.12.10/tools/python.exe' -B -X utf8 .build/c3-vorbis-format-expanded25-numeric-prep-01/compare_capture25.py --repository 'C:/Work/yoRadio/.worktree/esp32-cyd-c3-review' --target '<complete actual C3 full25 directory>' --target-report-sha256 '<reviewed report SHA256>' --target-terminal '<actual direct-tool terminal JSON>' --output '<fresh independent checkout .build output>' --max-abs-error 2
```

Omitting `--max-abs-error 2` measures without assigning a tolerance. All future
execution and actual receipts belong to the root. This source-only preparation
does not claim numeric, format-conformance, full G6, radio-integration, or
physical-device qualification.

## Preparation history

The first create-only source assembly stopped before writing outputs because its
text anchor incorrectly expected CRLF in the LF base source (actual terminal
exit 1, chunk `ceb162`). That script is preserved as
`prepare_adapter01-failed.py`. The corrected LF-only assembly completed with
exit 0, chunk `858764`, producing initial adapter hash
`e96ce72dffe783cef9158e021607afab18bb243736f512496508737a1a27cbf6`.
Review then added Windows-path normalization to the assembly template and its
generated adapter before freezing either. The final AST closure verifies those
sources and the exact permitted changes. Neither assembly invocation executed
prepared code or accessed a target capture.
