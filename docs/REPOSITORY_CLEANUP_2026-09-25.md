# Repository cleanup: 2026-09-25

The audit used `origin/main` at `b592edc626e92abd5bfa8ae8db07002d1c986de1`.
The default branch and push destination were verified as `main` and
`git@github.com:Witali/yoRadio.git`. The authenticated GitHub account is `Witali`.
No merge, remote-branch deletion, hardware access, flashing, or serial reset
was performed.

## Preserved and published work

The primary checkout is now on `codex/cleanup-preserve-local-work`.
Its existing useful uncommitted changes were saved separately:

| Commit | Preserved work | Validation |
| --- | --- | --- |
| `4b4f82c6` | Five Opus diagnostic firmware variants, low-RAM physical-test evidence, and the PLC/IRAM report | All five application SHA-256 values match their manifests; JSON files parse; the archived trace was inspected. The documented low-RAM physical result remains **0/10 qualified windows**. |
| `c84f28b9` | Existing WebRadio playback counters, diagnostic switches, test tools and fixtures, relocated source tests, and the existing development binary | All five WebRadio source tests pass. The saved binary matches the existing Arduino build output. No new firmware compilation or physical playback test was run. |

Both commits were pushed, including their Git LFS objects. The existing
23 local commits on `codex/esp8266-opus-asm` were also pushed; its verified
remote tip is `8c9ac87197261d4b0f6eb89fd5c0be38c46bf74f`.
Untracked experimental code and firmware inside that worktree were not
included in the push.

## Removed material

| Category | Count | Measured file bytes |
| --- | ---: | ---: |
| Completed linked worktrees | 2 | 163,262,983 |
| Generated host-test directories | 169 | 3,735,942 |
| Python cache directories | 3 | 298,380 |
| Temporary `probe` file | 1 | 6 |
| Total | | **167,297,311** |

This is about **159.5 MiB of file contents**, not a measurement of filesystem
allocation or Git object-store savings. Local and remote branch refs were retained.

Removed worktrees:

- `.worktree/merge-esp8266-main`, HEAD `9aa3317a`.
- `.worktree/esp8266audio-webradio`, detached HEAD `8db6399e`.

Both HEADs and all their HEAD reflog commits were already ancestors of
`origin/main`. Their tracked and untracked status was clean. Ignored contents,
real paths, and reparse points were checked before ordinary `git worktree remove`.
The old WebRadio build image exactly matched its committed firmware artifact.
The integration log exactly matched the retained
[360-test regression log](benchmarks/esp8266-main-merge-2026-09-06/host-tests.log).

The removed generated directories were 69 `http-response-test-*`,
50 `multipart-test-*`, and 50 `playlist-install-test-*` directories under
the root `.build/`. Their contents matched the files produced by the tracked
host-test runners. Python caches were removed from `tests/`,
`tools/esp8266_audio_profile/`, and `tools/radio_stream_collector/`.
`tmp/patch_probe.txt` contained only `probe` and a newline.
The exact local deletion inventory is in
`../.build/repository-cleanup-20260925/deleted-paths.json`.

## Retained worktrees and data

| Worktree or data | Reason retained |
| --- | --- |
| `esp32c3-deep-sleep-clock` | Published feature branch with two unique commits; opt-in firmware still needs physical sleep/wake/audio validation before adoption. |
| `esp8266-native-port` | Its committed history is integrated, but its index and working tree contain overlapping staged/unstaged HTTP/WebUI experiments. Their distinct versions were preserved. |
| `esp8266-output-baseline` | Its committed history is integrated. The timing counter improvement is already in current main, while the uncommitted SPI copy variant is a separate old experiment. It was not promoted into production or discarded. |
| `esp8266-stage-profile` | Committed history is integrated; the reported source modification has no substantive diff. Ignored SDK/toolchain trees, configuration, benchmark results, and inaccessible Linux environment entries still need a separate retention decision. |
| `esp8266-opus-asm` | Published experimental history, incomplete N3 unroll4 measurements, untracked flash-clock diagnostics, and untracked firmware variants remain useful for continuing investigation. |
| Root `.karadio-*.patch`, `.tmp_async_pdm/`, and remaining `tmp/` | Historical experiments and recovery data were retained. In particular, SPIFFS backups and extracted Wi-Fi configuration must not be treated as disposable or committed indiscriminately. |
| `.codex-remote-attachments/`, SDKs, local tools, radio captures, stashes, releases | User inputs, dependencies, recovery state, or retained artifacts; no demonstrated reason to delete them. |

There are five linked worktrees after cleanup, plus the primary checkout.
`git worktree prune --dry-run --verbose` reports no orphaned metadata.
The primary checkout has no tracked modifications; the retained untracked
material above remains intentionally visible in `git status`.

## Merge recommendations

| Branch | Recommendation |
| --- | --- |
| `codex/cleanup-preserve-local-work` | Review the preserved changes. The diagnostic evidence commit can be integrated as historical evidence. Before adopting the WebRadio behavior, compile its firmware and perform the documented playback checks; source tests alone do not establish physical correctness. |
| `codex/esp32c3-deep-sleep-clock` | Candidate for an opt-in feature merge after physical validation. `merge-tree` against the audited main is conflict-free. The actual RTC wake-stub host model passes I2C bytes, half-second boundaries, hour/day rollover, recovery, and elapsed-time drift checks. |
| `codex/esp8266-opus-asm` | Preserve the research branch, but do not merge the entire branch yet. Its 23 commits are a conflict-free continuation of audited main. Eight completed-result suites pass **38 tests**, but the N3 unroll4 result suite expects reports that do not exist yet, including `comparison.json` and `before-restore.json`. The corresponding plan explicitly leaves physical A/B measurements unfinished. |
| `codex/core-task-isolation` | Do not merge wholesale. This older branch is 939 commits behind audited main and has conflicts in firmware metadata and audio implementation. Reassess any still-useful idea against the current architecture. |

No PR was created and no branch was merged. The failed N3 unroll4 checks were
not skipped to claim the entire Opus branch passed. The separate completed-result
run is saved locally in
`../.build/repository-cleanup-20260925/opus-completed-results-tests.tap`.
