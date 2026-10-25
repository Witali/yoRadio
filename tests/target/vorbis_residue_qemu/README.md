# Owned residue and exact inverse-coupling tests

This isolated test links the complete six-source owned component and minimal
SDK runtime. It captures all mapping submaps, forward-order presence propagation,
residue types0/1/2 and reverse-order inverse coupling. Samples retain exact
little-significance-first two's-complement limbs and a shared power-of-two
exponent. Zero-width spectra are implicit zeros, including when entropy still
has to be consumed. No floor application, IMDCT, PCM or production radio runs.

The coordinator uses core0. The worker uses core1 on ESP32 and core0 on C3,
priority3/stack16384. Production affinities stay unchanged. Only the fixture
allocates guarded buffers, sized from measured counts, with immutable source
snapshots and byte-identical setup-context reuse. The core has no heap or VLA.
Native cases allow32768-byte packets,512 active words,1024 multiplicands,
8192 configuration words,4096 output limbs and65536 classification bytes.
These finite test-resource ceilings do not restrict the public encoded format.

The packet begins at the residue portion, with supplied mapping/bins and
pre-propagation floor-present bytes. INVALID preserves cursor/output/state;
scratch may change after a sufficiently provisioned call starts. CAPACITY
precedes reads and writes. Genuine EOP publishes every earlier complete VQ word
and commits sticky EOP at the last full word. Host rows include explicit payload
bit cuts; the native matrix uses200 preselected original cases. A pre-existing
EOP with no entropy reads remains separate from a decoder stopped by EOP.

From this worktree, prepare a fresh sanitized host campaign and check the pure
protocol reader:

```powershell
python -B -X utf8 tests/test-vorbis-residue.py --output .build/residue-host-user-01
python -B -X utf8 tests/test-vorbis-residue-protocol.py
```

For native capture, activate the pinned ESP32 SDK6.0.2 or C3 SDK6.1.0 shell.
Set RESIDUE_QEMU and RESIDUE_ROM to the chosen target's QEMU executable and
explicit ROM directory. Use a fresh output and generated target cases:

```powershell
$target = 'esp32' # esp32c3 uses its own pinned SDK/toolchain
$cases = (Resolve-Path .build/residue-host-user-01/target-cases).Path
$parts = @{ source='floor0.c'; header='include/native_vorbis_floor0.h'; 'quant-source'='quant.c'; 'quant-header'='include/native_vorbis_quant.h'; 'codebook-source'='codebook.c'; 'codebook-header'='include/native_vorbis_codebook.h'; 'setup-source'='setup.c'; 'setup-header'='include/native_vorbis_setup.h'; 'floor-packet-source'='floor_packet.c'; 'floor-packet-header'='include/native_vorbis_floor_packet.h'; 'residue-source'='residue.c'; 'residue-header'='include/native_vorbis_residue.h'; component='CMakeLists.txt' }
$nativeArgs = @('--target',$target,'--output',".build/residue-$target-user-01",'--cases',$cases,'--idf',$env:IDF_PATH,'--idf-tools',$env:IDF_TOOLS_PATH,'--powershell',(Get-Command pwsh).Source,'--sdk-python',(Join-Path $env:IDF_PYTHON_ENV_PATH 'Scripts/python.exe'),'--qemu',$env:RESIDUE_QEMU,'--rom',$env:RESIDUE_ROM)
foreach ($key in $parts.Keys) { $nativeArgs += @("--$key-sha256",(Get-FileHash -Algorithm SHA256 (Join-Path idf/components/native_vorbis_numeric $parts[$key])).Hash.ToLowerInvariant()) }
foreach ($item in @(@('cases',(Join-Path $cases 'cases.json')),@('cases-header',(Join-Path $cases 'cases.h')),@('qemu',$env:RESIDUE_QEMU))) { $nativeArgs += @("--$($item[0])-sha256",(Get-FileHash -Algorithm SHA256 $item[1]).Hash.ToLowerInvariant()) }
python -B -X utf8 tests/run-vorbis-residue-qemu.py @nativeArgs
```

The controller freezes six C files, six headers, component CMake, this fixture
and the JSON/header corpus. It retains nine owned command receipts, explicit
ROM identities, native compile/dependency/symbol evidence and six `.su` files.
Stack records estimate individual compiler frames, excluding callees, task
high-water and physical timing. Guard checks are distinct from numerical
comparison. `CHECKED_RESIDUE_CAPTURED` records a completed capture; the separate
Fraction oracle must compare every exact limb before claiming numerical PASS.
These finite tests do not qualify a complete stream decoder or physical board.
