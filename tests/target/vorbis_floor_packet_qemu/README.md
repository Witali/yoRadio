# Owned floor-packet and floor1-index tests

This test links only the owned five-unit component and minimal SDK runtime.
It captures audio-prefix parsing, floor0 amplitude/original affine LSPs,
floor1 raw/final Y and active flags, and the integer inverse-dB table indexes.
General floor0 gain is captured with internal composition checks; this stage
adds no independent general floating-point gain qualification. ABSENT and
order0 D=1 identities have separate checks. No residue, spectrum multiplication,
IMDCT, PCM, vendor/private ABI or production radio task is executed.

The coordinator uses core0; the worker uses core1 on ESP32 and core0 on C3,
priority3/stack16384. DIO40/4MB and CPU profiles are isolated test settings.
Production task affinities/configuration are unchanged. The fixture alone
uses guarded heap buffers sized from measured counts, exact immutable snapshots
and reused byte-identical setup contexts. The core allocates nothing.
Literal NULL storage is passed when global words/multiplicands require zero.
Native packets allow32768 BYTES, including the sparse131072-entry setup case.

Genuine floor EOP returns UNUSED, commits the last successfully read field/word
and sticky EOP, and publishes no partial arrays. INVALID/CAPACITY rolls the
whole floor back. Prefix EOP remains a separate fatal-prefix result. Explicit
host cut rows check every consumed floor prefix; native rows are the selected
original cases. Raw helpers also test full uint32 inputs beyond packet values.

From the repository worktree, run a fresh sanitized host campaign:

```powershell
python -B -X utf8 tests/test-vorbis-floor-packet.py --output .build/floor-packet-host-user-01
python -B -X utf8 tests/test-vorbis-floor-packet-protocol.py
```

For native capture, first activate the pinned ESP32 SDK6.0.2 or C3 SDK6.1.0
shell. Set FLOOR_QEMU and FLOOR_ROM to that target's QEMU executable and explicit
ROM directory. Use a fresh output and the generated host target-cases directory:

```powershell
$target = 'esp32' # use esp32c3 with its pinned SDK/toolchain
$cases = (Resolve-Path .build/floor-packet-host-user-01/target-cases).Path
$parts = @{ source='floor0.c'; header='include/native_vorbis_floor0.h'; 'quant-source'='quant.c'; 'quant-header'='include/native_vorbis_quant.h'; 'codebook-source'='codebook.c'; 'codebook-header'='include/native_vorbis_codebook.h'; 'setup-source'='setup.c'; 'setup-header'='include/native_vorbis_setup.h'; 'floor-packet-source'='floor_packet.c'; 'floor-packet-header'='include/native_vorbis_floor_packet.h'; component='CMakeLists.txt' }
$nativeArgs = @('--target',$target,'--output',".build/floor-packet-$target-user-01",'--cases',$cases,'--idf',$env:IDF_PATH,'--idf-tools',$env:IDF_TOOLS_PATH,'--powershell',(Get-Command pwsh).Source,'--sdk-python',(Join-Path $env:IDF_PYTHON_ENV_PATH 'Scripts/python.exe'),'--qemu',$env:FLOOR_QEMU,'--rom',$env:FLOOR_ROM)
foreach ($key in $parts.Keys) { $nativeArgs += @("--$key-sha256",(Get-FileHash -Algorithm SHA256 (Join-Path idf/components/native_vorbis_numeric $parts[$key])).Hash.ToLowerInvariant()) }
foreach ($item in @(@('cases',(Join-Path $cases 'cases.json')),@('cases-header',(Join-Path $cases 'cases.h')),@('qemu',$env:FLOOR_QEMU))) { $nativeArgs += @("--$($item[0])-sha256",(Get-FileHash -Algorithm SHA256 $item[1]).Hash.ToLowerInvariant()) }
python -B -X utf8 tests/run-vorbis-floor-packet-qemu.py @nativeArgs
```

The controller freezes all five C files, five headers, component CMake, fixture
and exact JSON/header inputs. It retains native compile/dependency/symbol
records and five `.su` files. Compiler frame estimates exclude callees/libm,
task high-water and physical timing. Chunked captures preserve conditional
UNUSED/error/raw-helper records. `CHECKED_FLOOR_PACKET_CAPTURED` means capture
only; the separate oracle comparison must qualify exact packet/index results.
Full decoder/PCM/device qualification does not follow from these finite tests.
