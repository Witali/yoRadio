# C3 public uint32-rate checkpoint archive

`pack.py` binds five independently completed C3 campaigns into separate source
namespaces; `verify.py` verifies the stored bytes offline with Python stdlib.
This source proposal has not packed or verified an archive. Only baseline was
known terminal during preparation (session94142/chunkde30cc, exit0); live and
not-yet-launched campaigns were not read or treated as successful evidence.
The packer requires all five completed reports and distinct final tool receipts.
Only a later offline verifier exit0 confirms an assembled archive.

The final location is `tests/results/c3-vorbis-uint32-rate-20261020/`. Root may
first assemble a fresh independent `.build` directory and promote the exact
verified bytes. Existing outputs, inputs and prep directories cannot be replaced.
Incomplete assembly is retained; neither script retries, deletes, launches a
process, touches Git/SDK state or accesses a device/network. The verifier does
not write into the archive; it disables bytecode writes before importing the
exact frozen pure C3 rate protocol.

## Explicit root-owned commands

Run only after all five reviewed terminal receipts and the canonical19 host
receipt/logs exist. These commands were not executed by this preparation:

```powershell
$rateRepo = (Get-Location).Path
$ratePrep = "$rateRepo/.build/c3-vorbis-uint32-rate-archive-prep-01"
$rateStage = "$rateRepo/.build/c3-vorbis-uint32-rate-archive-01"
$ratePython = 'C:/Work/yoRadio/.idf/python-3.12.10/tools/python.exe'
$rateArgv = @('--repository', $rateRepo, '--output', $rateStage)
foreach ($rateRole in @('baseline', 'acceptance', 'limited', 'validity-control', 'policy-control')) {
    $rateArgv += @("--$rateRole", "$rateRepo/.build/c3-vorbis-uint32-rate-$rateRole-01")
    $rateArgv += @("--$rateRole-terminal", "$rateRepo/.build/c3-vorbis-uint32-rate-source-01/$rateRole-terminal.json")
}
& $ratePython -B "$ratePrep/pack.py" @rateArgv
& $ratePython -B "$ratePrep/verify.py" $rateStage
```

Packing reports `COPIED_NOT_VERIFIED`. `OFFLINE_VERIFIED` requires a separate
successful verification. A nonzero exit is a failure; no PID, timeout fact or
outer command is reconstructed when it was not recorded.

## Independent C3 evidence

Each report input is checked against its own campaign snapshot, not the current
file at a historical absolute path. Baseline setup is
`83ce582554970e1a4bb70587e036c45af7bfb84519d3d7d87580eb4b9b1d38de`;
the complete fix is
`f3d8b3ff1cb8d2cef675eb742be35f3e6a4533b3e10fbd368aacd929a10fcac0`.
The raw CRLF source relation must contain only the explanatory comment and two
unsigned casts. Controls restore only their named signed guard. Output/ABI and
other candidate bytes remain identical across all five campaign snapshots.

Required protocol counts below are verifier assertions, not claims that pending
campaigns passed:

| Role | Required classification | Accepted/rejected | Pairs | PCM bytes | Native lines |
| --- | --- | ---: | ---: | ---: | ---: |
| baseline | REGRESSION_REPRODUCED | 14/2 | 952 | 3816960 | 988 |
| acceptance | UINT32_RATE_ACCEPTED | 16/0 | 1088 | 4362240 | 1124 |
| limited | LIMITED_POLICY_VERIFIED | 11/5 | 748 | 2999040 | 784 |
| validity-control | CONTROL_EFFECTIVE | 14/0 before exact failure | 952 | 3816960 | 985 |
| policy-control | CONTROL_EFFECTIVE | 11/3 before exact failure | 748 | 2999040 | 781 |

The frozen C3 protocol requires native `C3_VORBIS_RATE_` records and actual
coordinator0/worker0. All45 owned commands require exact terminal process flags
and raw log hashes. Separate direct-exec terminal witnesses bind each final
report/controller; baseline reproduction and effective controls never become
acceptance qualification.

The platform is **ESP32-C3/RV32, ELF243, SDK6.1 revision
9a97f6c54ec638111ce55cd36581b3c192f15207, 160MHz, unicore**. Actual generated
config, macro dump and compile row are checked, including ILP32, RISC-V32,
the selected rate policy and the four-line generated `@cflags`/picolibc.specs
context. No CYD 240MHz/SMP/Kconfig assertion is inherited. C3's raw wrapper
helper and output/ABI sources have their own frozen identities. Actual C3
compiler/nm/CMake/Ninja/QEMU/ROM and vendor archive pins are separate from CYD.
The flash recipe uses C3 offsets **0/0x8000/0x10000**, chip esp32c3 and QEMU's
single-core esp32c3 machine.

Retained evidence includes report-bound sources/headers, project/runner/protocol,
variant, generated config, compilation database, macro before/after inputs,
symbols, link/build/flash recipe, inner/outer SDK logs and compiler identities.
The SDK prep's actual23-method receipt has its own schema, list logs and seven
before/after source pins; it records no PID, and none is invented. The separate
canonical19 receipt retains the generic capture schema and its exact source/log
bindings. Both sets of test sources remain directly readable. No nonexistent
C3 sibling caller-prep is assumed.

Large text is gzip-compressed losslessly. Scripts and C headers stay direct;
raw and stored sizes/SHA256 and the exact file set are checked. Binary
ELF/app/flash/archive/tool/ROM bytes are hash-omitted, object caches are excluded.
An actual 64-byte ELF header captured during packing supports the ELF243 metadata
check. Omitted binary bytes cannot be rehashed or replayed offline; their recorded
identities do not substitute for stored contents. Historical-profile references
inside the retained prep are documentary context; current runtime proof comes
from these five campaign reports and their own terminal evidence.

CRLF normalization is restricted to decoded textual regex views (macro values,
symbols and host logs). Source relations and all raw hashes remain exact.
Raw-evidence attributes retain the reviewed whitespace exceptions. This isolated
public-rate checkpoint leaves full G6, production radio integration and physical
qualification false. It adds no Ogg/EOF/reset/OOM or unrelated codec claim.
