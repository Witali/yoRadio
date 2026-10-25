# ESP8266 integration review — 2026-10-25

Reviewed against `main`/`origin/main` at
`51cd114f98b93cabd785e90676290dc6ff0ad62d`, after fetching `origin` without
pruning. The repository is `Witali/yoRadio`; no open pull requests were found.
This is a selective integration, not a merge of the complete research branch.

## Findings and selection

| Work | Evidence | Decision |
| --- | --- | --- |
| Native port `6008954b8`, output baseline `b47c0cd3b`, stage profile `10d1a8298`, Arduino WebRadio `8b600bcf2` | All tips are ancestors of current `main`; the earlier integration is documented in `docs/benchmarks/esp8266-main-merge-2026-09-06/README.md`. | Already integrated. |
| `codex/esp8266-opus-asm` at `80375a645` | 29 commits missing from `main`; changes are experimental recipes, artifacts, tests and research evidence. No newer ESP8266 firmware source commits were found on other local or origin branches. | Select the offline QEMU qualification tools. Retain the remaining research on its branch. |
| Offline LX106 harness `6006aefa1` | Executes the accepted linked decoder with exact PCM, guarded arenas, explicit OOM recovery and instruction traces. Uses accepted artifacts already in `main`. | Port with provenance, then incorporate reviewed phase/mixed-input and SILK-trace refinements from the research tip. |
| N3 finite differences/unroll4 | Unroll4 adds about 0.39% instructions at 192 kbit/s and removes about 1.95–2.06% at 320/510. These are QEMU instruction counts; board CPU and live output gates remain incomplete. | Retain as an experiment. |
| N4 prefix/uniform256 | Uniform256 removes about 0.37% instructions at 192 and 0.42% at 320, but adds about 0.58% at 128 and 0.12% at 510. No qualified hardware speed gain. | Retain as an experiment. |
| Binary/tree/packed-prefix/direct-word/in-place PVQ variants | Research records contain physical slowdowns and unresolved low-memory/outlier observations. | Do not promote into the accepted decoder chain. |
| Old uncommitted native-port HTTP/WebUI changes | Main now has bounded nonblocking HTTP sends and newer WebUI/audio ownership. The old patch is based on an earlier architecture and includes partially staged changes. | Preserve the original worktree and index. |
| Old uncommitted output-baseline changes | Invalid-timing accounting is already in main; the SPI proposal adds copying and stack use. | Preserve without porting. |
| Stage-profile `network_service.c` | No semantic diff after line-ending normalization. | No integration needed. |
| Untracked runtime flash-clock diagnostics | Standalone opt-in code without a completed integration/qualification record. | Preserve as unfinished work. |

## Resulting tools

`tools/esp8266_opus_qemu/` supplies the runner, original call0 harness and
dynamic trace parser. Its suite defaults to the accepted decoder only, so it
does not require unmerged N3/N4 firmware. It archives exact inputs and hashed
results, supports a valid empty CELT/PVQ trace for verified SILK-only packets,
and allows the first sanitizer-oracle build longer than a QEMU execution.

See [runner documentation](../tools/esp8266_opus_qemu/README.md) and
[qualification evidence](benchmarks/esp8266-main-integration-20261025/).

## Validation and limits

The qualification uses QEMU 9.2.2 `sim/lx106`, LX106 GCC 8.4 and the existing
vendored generic32 ASan/UBSan oracle. It checks the original independent PCM
fixtures plus extended phase, mixed-mode and long-packet cases. Dynamic trace
counts exclude callees and do not represent physical CPU cycles.

The verified suite passed all **24 exact PCM and OOM/recovery cases**, seven
instruction profiles, deterministic 192 kbit/s replay and the deliberate
negative canary. Decoder state is 6582 bytes; observed byte/word arena peaks
are 5968/15600 bytes, with a 2772-byte harness stack watermark. The mixed-mode
case reaches 5968 bytes; the original homogeneous fixtures peak at 5488.
These figures describe the isolated decoder, not complete firmware memory
headroom. The parser, archived evidence and production-profile regressions
passed **26 tests, with no failures or skips**; the
[TAP log](benchmarks/esp8266-main-integration-20261025/host-tests.tap) is retained.

The first suite attempt exhausted the original 60-second outer limit while
compiling the cold sanitizer oracle. Its log is retained in `qemu/`; the
subsequent verified run is in `qemu-verified/`. The suite now permits up to ten
minutes for extended host preparation; QEMU itself remains bounded at 60 seconds.

Production source, accepted ASM chain, build configuration, web assets and
firmware artifacts are unchanged by this integration. No new production
firmware build or board deployment is necessary for this tooling change.
Existing uncommitted work, stashes, firmware artifacts and temporary patches
remain untouched. No UART, reset or OTA operation was performed.
