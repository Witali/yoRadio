# Complete upstream Xiph ESP32 evaluation

This isolated project compiles the complete unchanged base libvorbis1.3.7
library (20 C units) and libogg1.3.5 bitwise/framing (2 units). The component
manifest pins every imported source, license, platform type header and build
file. It uses public raw header/synthesis APIs, with the original three headers,
14 audio packets, packet numbers, granules and EOS flags for each of31 cases.
It adds no Ogg parser extension or production radio integration.

The coordinator uses core0 and the worker core1, priority3/stack16384. DIO40,
4MB flash and240MHz are fixture settings. Production task affinities and the
existing Espressif decoder remain unchanged. C3 is outside this first baseline.

PCM is drained after each block using pcmout/read, without lapout or a synthetic
extra packet. Finite float samples are multiplied by32768, explicitly rounded
to nearest with ties to even, clamped to signed16 and interleaved L/R. The
retained reference policy has no dithering, gain fitting, resampling or shifts.
Seventeen conversion controls check ties, signs, clipping and nonfinite refusal.
Typed signed16 storage has adjacent canaries; unused conversion-buffer bytes
and each copied raw packet are checked. These guards cover adapter-owned
storage, not every private upstream allocation.

Prepare the unchanged corpus and reference bytes in a fresh output directory:

```powershell
python -B -X utf8 tests/prepare-vorbis-xiph.py --output .build/xiph-prep-user-01
python -B -X utf8 tests/test-vorbis-xiph-protocol.py
```

Activate the pinned ESP-IDF6.0.2 shell, set XIPH_QEMU and XIPH_ROM to the
ESP32 QEMU executable and explicit ROM directory, and use a fresh campaign:

```powershell
$cases = (Resolve-Path .build/xiph-prep-user-01).Path
$nativeArgs = @('--target','esp32','--output','.build/xiph-esp32-user-01','--cases',$cases,'--idf',$env:IDF_PATH,'--idf-tools',$env:IDF_TOOLS_PATH,'--powershell',(Get-Command pwsh).Source,'--sdk-python',(Join-Path $env:IDF_PYTHON_ENV_PATH 'Scripts/python.exe'),'--qemu',$env:XIPH_QEMU,'--rom',$env:XIPH_ROM)
$pins = @{ 'component-manifest'='idf/components/native_vorbis_xiph/component-manifest.json'; cases=(Join-Path $cases 'cases.json'); 'cases-header'=(Join-Path $cases 'cases.h'); qemu=$env:XIPH_QEMU }
foreach ($key in $pins.Keys) { $nativeArgs += @("--$key-sha256",(Get-FileHash -Algorithm SHA256 $pins[$key]).Hash.ToLowerInvariant()) }
python -B -X utf8 tests/run-vorbis-xiph-qemu.py @nativeArgs
```

The capture retains all PCM chunks and API statuses, source/data/ROM/tool
identities, nine owned command receipts, native compile/dependency/symbol
evidence and22 compiler stack-usage files. It also writes per-case signed16
files under the campaign's pcm directory. CHECKED_XIPH_CAPTURED means a complete
capture; the separate test-vorbis-xiph-pcm.py comparison must qualify PCM and
all14 declared relations against the retained references. Numerical differences
remain measurable failures rather than changing conversion or acceptance.

free_before/free_open/free_after and largest-block values are snapshots.
minimum_free is the runtime's cumulative minimum; stack_before/stack_after are
the worker's cumulative minimum remaining stack in ESP-IDF bytes. They are not
per-case transient peaks. Compiler .su entries estimate individual frames and
do not bound full dynamic call trees. QEMU elapsed time, heap and stack values
do not establish physical performance, audio continuity or board acceptance.
