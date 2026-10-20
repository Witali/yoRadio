# CYD public uint32-rate checkpoint archive

This bundle preserves five completed CYD public raw uint32-rate campaigns, their
exact source versions, command receipts and logs. `pack.py` copies evidence only.
`verify.py` reads the finished archive using Python
stdlib only; it launches no process, performs no network operation, imports only
the pinned pure protocol module and disables bytecode writes. Both take explicit
paths and work independently of the caller's working directory. Only an offline
verifier exit code 0 confirms the stored archive. The scripts' source-only
preparation checks are recorded separately in `source-checks.json`.

The final durable location is
`tests/results/cyd-vorbis-uint32-rate-20261020/`. Root may first assemble a fresh
independent directory beneath `.build`, run the offline verifier from outside it,
and then promote the exact reviewed bytes. Existing directories are rejected.
No original campaign, canonical source or installed SDK is changed.

## Root-owned assembly and verification

To assemble from the retained campaign directories, use the following from the
repository root in PowerShell:

```powershell
$rateRepo = (Get-Location).Path
$ratePrep = "$rateRepo/.build/cyd-vorbis-uint32-rate-archive-prep-02"
$rateStage = "$rateRepo/.build/cyd-vorbis-uint32-rate-archive-01"
$ratePython = 'C:/Work/yoRadio/.idf/python-3.12.10/tools/python.exe'
$rateArgv = @('--repository', $rateRepo, '--output', $rateStage)
foreach ($rateRole in @('baseline', 'acceptance', 'limited', 'validity-control', 'policy-control')) {
    $rateArgv += @("--$rateRole", "$rateRepo/.build/cyd-vorbis-uint32-rate-$rateRole-01")
    $rateArgv += @("--$rateRole-terminal", "$rateRepo/.build/cyd-vorbis-uint32-rate-source-01/$rateRole-terminal.json")
}
& $ratePython -B "$ratePrep/pack.py" @rateArgv
& $ratePython -B "$ratePrep/verify.py" $rateStage
```

Packing prints `COPIED_NOT_VERIFIED`. Only a successful independent verifier run
prints `OFFLINE_VERIFIED`; a nonzero exit is a failure. Partial assembly is
preserved for inspection, and there is no automatic retry, deletion or restart.
The verifier prints to stdout and does not write into the archive.

## Exact scope and retained evidence

Five campaign namespaces preserve the source version consumed by each campaign.
Every report input is bound to its campaign's frozen snapshot and SHA256, never
to the current file at an old absolute canonical pathname. Baseline setup is
`b7e1999c349f9353a5690eaf5b05a0387db1bcad365d7f079c4a6c52ae493156`;
the complete fix is
`d23fd5cb2ad7d8c3a87ebcda2197421245f571dea5724de3d328058264e491c2`.
Only one comment and two unsigned casts distinguish them. Each control restores
only its named signed guard in the isolated variant.

| Campaign | Classification | Accepted/rejected | Paired packets | PCM bytes | Native lines |
| --- | --- | ---: | ---: | ---: | ---: |
| baseline | REGRESSION_REPRODUCED | 14/2 | 952 | 3816960 | 988 |
| acceptance | UINT32_RATE_ACCEPTED | 16/0 | 1088 | 4362240 | 1124 |
| limited | LIMITED_POLICY_VERIFIED | 11/5 | 748 | 2999040 | 784 |
| validity-control | CONTROL_EFFECTIVE | 14/0 before failure | 952 | 3816960 | 985 |
| policy-control | CONTROL_EFFECTIVE | 11/3 before failure | 748 | 2999040 | 781 |

These are actual root-owned results from the five bound reports; root also
revalidated all five pure protocols (tool chunk `533a15`). They are distinct from
verification of the stored archive. Controls end at exactly
`legal_unsigned_rate_open_required` or `limited_rate_rejection_required`, as
enforced by the frozen strict protocol. Neither a reproduced baseline nor an
effective control is classified as successful acceptance.

The bundle retains all 45 owned command rows and their exact stdout/stderr,
separate direct-exec terminal witnesses, actual frozen caller/fixture/protocol,
project/runner, input headers, variant sources, source audit and fix relation.
It includes actual config, compile database, macro context, six-line Xtensa
`@cflags` and specs, generated-input before/after identities, symbols, flash
recipe, linker map/build recipe, SDK inner/outer logs and compiler identities.
The caller's actual host-tests02 and canonical nineteen-method receipts/logs,
their exact pure sources and the pinned capture utility are retained too.

The manifest records both raw and stored sizes/SHA256. Large text is losslessly
gzip-compressed; Python/scripts/C headers stay directly readable/importable.
The exact stored file set is checked. ELF/app/flash images, generated archives,
tools, ROMs and vendor archive bytes are omitted with their actual size/SHA256;
object caches are excluded entirely. ELF records include an explicitly captured
64-byte ELF32 header and machine94 metadata, read during packing. The verifier
checks that captured header, not absent ELF bytes. Omitted binaries cannot be
rehashed or replayed offline; binary sizes/hashes are identity records bound to
the qualified reports, not a substitute for retained binary contents.

Verification rehashes stored/decompressed bytes, validates all command process
flags and log hashes, independently runs the exact pinned protocol parser for
all five logs using their real recorded QEMU facts, and checks source versions,
guard controls, actual compile/macro/config context, SDK6.0.2 revision/clean logs,
vendor archive pins and CYD offsets 0x1000/0x8000/0x10000. It never reads an
installed SDK or an obsolete original source path. This public raw rate
checkpoint does not qualify full G6, production radio integration, physical
hardware, target Ogg, EOF/reset/OOM behavior or unrelated codecs. Those scope
flags remain false.
