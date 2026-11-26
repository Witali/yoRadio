# TCP oversize disabled: isolated legacy A/B preparation

Status: **prepared only**. No compiler, QEMU, source/index change or publication
has occurred. The original source is frozen at
`f7dee344fb30ce109f2d30a01f0325d353e3b2eb`. A root-created release record is
required before `run-build.py` can start any child process.

## Why this is a justified first experiment

The completed continuous-DAC observation identifies all10 recorded failures
at `tcp_write`/`tcp_pbuf_prealloc`, with transport layer54, RAM type640,
length1440 and derived allocation1512. Legacy/PDM's first observer attempts
ended before EOF; this preparation does not claim a captured caller for them.

Pinned SDK sources are hashed in `preflight.json`:

- `components/lwip/Kconfig:789–808` provides the supported oversize choice.
- `port/include/lwipopts.h:639–646` maps the disabled choice to `TCP_OVERSIZE=0`.
- `port/include/lwipopts.h:748–765` defines `LWIP_NETIF_TX_SINGLE_PBUF=1`.
- `core/tcp_out.c:238–243` therefore reserves `max_length` when oversize is on;
  its usual Nagle/`MORE` heuristic is in the other compile-time branch.
- `core/tcp_out.c:276–278` uses the actual requested length when oversize is off.

Quarter-MSS remains nonzero and does not change this special single-pbuf branch.
With the current target pbuf16/alignment4/layer54, the RAM request formula is
`72 + align4(length)`:1440 requests1512, while a2-byte request would need76.
These smaller-request examples are source-derived predictions, not newly
observed allocations. Full-MSS writes can still request1512 and fail.

The exact expected effective configuration delta is only:

| Key | Before | Candidate |
| --- | --- | --- |
| `LWIP_TCP_OVERSIZE_MSS` | true | false |
| `LWIP_TCP_OVERSIZE_DISABLE` | false | true |

`LWIP_TCP_OVERSIZE_QUARTER_MSS` remains false. MSS1440, RX11520, mailbox10,
TX5760, TLS16384/4096, source-channel limit2, full JSON5120 and two clients,
the original dual-core audio bindings/stacks, watchdogs and every diagnostic
probe flag stay unchanged. The seed changes exactly the two choice lines;
the remaining bytes are preserved.

The SDK documents a performance/fragmentation tradeoff. Under
`LWIP_NETIF_TX_SINGLE_PBUF=1`, tcp_write's second chaining phase is also
compiled out (`tcp_out.c:518–586`); disabling spare capacity can produce
more short TCP segments rather than extending an existing reserved buffer.
This is not a promise of better throughput, arbitrary-load headroom or a
production-default recommendation. Long-lived fragmentation and small-write
latency still need evidence if the finite acceptance run improves.

## ABI and build isolation

Baseline actual DWARF says tcp_pcb168 bytes, with snd_buf104,
snd_queuelen106, unsent_oversize108, bytes_acked110, unsent112, unacked116.
`tcp.h:330–333` conditionally removes unsent_oversize. Source layout predicts
bytes_acked moves to108 while pointer padding may retain the total168 bytes.
The foundation checker requires actual candidate DWARF; no PCB-size saving
is claimed in advance. A fresh complete SDK build is required, not a copied
lwIP object or macro patched into a previously compiled image.

The new build path is `.build/coversize26/legacy/build`. No old cache is reused
or mutated. `preflight.json` pins61 sources,7 primary SDK files,324 protected
bindings, existing helper inputs, metadata and prepared experiment inputs.
The initial free-space observation was11.84GiB; the existing2GiB minimum is
checked again before a future build. No caches or directories are deleted.

The compile invocation retains the original PROJECT_VER and
SOURCE_DATE_EPOCH1795535394 for A/B descriptor matching. That metadata is
deliberately historical, not a new clean production release identity.
The candidate fixture is a fresh copy of the baseline fixture with only
application bytes and config JSON replaced. Old bootloader, partitions,
SPIFFS, OTA data and assets remain byte-identical. Fresh-build bootloader
bytes are retained and identified but are not used by this app-only A/B.

The old local TLS files remain unchanged. Their date validity has expired at
host time, but the frozen profile already has HAVE_TIME_DATE=false and
weak-verification=false. This experiment does not change that policy and
does not qualify certificate date enforcement. No private credential value
is copied into these preparation records.

## Explicit future release and commands

Root must first review the preparation and create `compile-release.json` with:

```json
{
  "allow_compile": true,
  "backend": "legacy",
  "source_commit": "f7dee344fb30ce109f2d30a01f0325d353e3b2eb",
  "preflight": {"bytes": "actual integer", "sha256": "actual preflight hash"}
}
```

Then, from the task worktree with the installed SDK Python:

```powershell
python -B .build/coversize26/run-build.py --shell 'C:/Program Files/PowerShell/7/pwsh.exe'
```

Use a correctly quoted installed shell path when invoking directly; the
default searches pwsh/powershell. The recipe reconfigures, verifies exactly
the two config changes, builds in the fresh directory, freezes outputs,
stages the controlled fixture and runs `qualify-foundation.py`. Every child
PID/exit is recorded, and failures retain their original logs. It does not
launch QEMU or write public/production output.

## Required qualification after the foundation

The foundation checks target image checksum/SHA/chip/OTA bounds, unchanged
descriptor metadata except ELF hash, full config/header delta, actual
tcp_pcb layout, fixed observer storage and source-unit count. Its record
explicitly leaves `final_qualification_passed=false`.

Before runtime root still needs:

1. Exact source/SDK/version and compiler-command comparison, normalizing only
   the separate build-root paths. Whole PCM/probe and SDK tcp_out/pbuf Clang
   must use the candidate configuration; retain system-header diagnostics.
2. New candidate-reference object provenance for linked calls. The frozen
   cpbuf24 verifier deliberately recognizes its old source CUs/cache profiles
   and old-config reference objects. Preserve it unchanged; a separately
   reviewed adapter/profile must tie new tcp_out/pbuf objects and commands to
   the new ELF. Prove every actual wrapped TCP call and the wrapper's single
   real allocator call; retain the same-object pbuf_clone blind spot.
3. Measured wrapper/dump/PCM frames and ordinary/RTC/heap-region deltas. The
   target task stacks are retained; static frames are not total-depth proof.
4. The unchanged strict full TLS/HE-AAC/614400-frame hash, all WebUI phases,
   two peers/pongs/close and final post-close allocation/error counters.
   Keep every original NONPASS. One promising legacy case is not sufficient
   for adoption; independently qualify PDM and continuous and retain any
   performance/fragmentation limitation.

This supported configuration experiment is cheaper and narrower than a new
serializer, but it is not selected as a fix until those measurements pass.
