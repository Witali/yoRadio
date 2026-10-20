"""Archive the completed standalone target FLAC gate without rewriting evidence."""
import datetime
import hashlib
import json
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parents[1]
RUN=ROOT/'.build/cyd-custom-flac-qemu-tracked-02'
ARCHIVE=ROOT/'tests/results/cyd-flac-qemu-20261020'


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


report=json.loads((RUN/'report.json').read_text())
bundle=json.loads((RUN/'execution-bundle.json').read_text())
assert report['passed'] and report['all_bound_inputs_current']
assert len(report['exact_pcm_cases'])==520 and report['guards']==48
assert report['execution_bundle_sha256']==sha(RUN/'execution-bundle.json')
assert all(row['exit_status']==0 for row in report['commands'])


def verify_live():
    results={}
    for group in ('frozen_sources_sha256','fixture_sha256','artifact_sha256'):
        results[group]={name:sha(RUN/name)==digest for name,digest in bundle[group].items()}
    for group,values in [('runtime_sha256',bundle['runtime_sha256']),('live_source_sha256',report['source_sha256'])]:
        results[group]={name:sha(Path(name))==digest for name,digest in values.items()}
    assert all(value for values in results.values() for value in values.values())
    return results


before=verify_live()
ARCHIVE.mkdir(parents=True,exist_ok=False)
mapping={}


def copy(source,relative):
    target=ARCHIVE/relative
    assert target.resolve().is_relative_to(ARCHIVE.resolve())
    target.parent.mkdir(parents=True,exist_ok=True)
    data=source.read_bytes();target.write_bytes(data)
    assert source.read_bytes()==data and target.read_bytes()==data
    mapping[str(relative).replace('\\','/')]={'source':str(source),'sha256':sha(target),'bytes':len(data)}


for name in ('report.json','execution-bundle.json'):
    copy(RUN/name,name)
for group in ('frozen_sources_sha256','fixture_sha256','artifact_sha256'):
    for name,digest in bundle[group].items():
        relative=Path(name);copy(RUN/relative,relative)
        assert sha(ARCHIVE/relative)==digest
for source in sorted(RUN.glob('*.log')):
    copy(source,source.name)
history=ROOT/'.build/cyd-custom-flac-qemu-tracked-01'
for name in ('report.json','execution-bundle.json'):
    copy(history/name,Path('history/tracked-01')/name)
preflight=ROOT/'.build/cyd-custom-flac-qemu-preflight-02'
for name in ('report.json','runner.diff'):
    copy(preflight/name,Path('history/preflight-02')/name)
copy(Path(__file__).resolve(),Path('archival/archive.py'))
history_readme='''# Historical records

`tracked-01/` preserves the first successful tracked-harness report and bundle.
Its frozen runner predates the narrow output-directory guard fix. It remains
historical evidence and does not describe the current runner bytes. Its full
old source/fixture/image set is not included here; use the final root bundle.

`preflight-02/` records two synthetic portable-tool destinations. Both were
rejected for overlap before missing-dependency lookup, without creating output.
`runner.diff` shows only the added PowerShell and overridden Python parent roots.

Original report and bundle bytes are retained unchanged. The root report/bundle
are the final actual tracked-02 execution and authoritative case evidence.
'''
(ARCHIVE/'history/README.md').write_text(history_readme,encoding='utf-8')
readme='''# CYD custom FLAC: ESP32 SDK/QEMU adapter and core

The final standalone Windows harness passed **520 unique exact PCM16 cases**
and **48 guard/recovery checks** using pinned ESP-IDF 6.0.2 and the installed
Xtensa QEMU. A single actual SDK decoder owner runs on core 1; its coordinator
runs on core 0. Every callback compares all PCM bytes against a separately
FFmpeg-verified oracle and validates depth, channels, rate, alignment and bounds.

There are 120 small fixtures and 10 fixtures with an 8192-frame block plus short
tail. Tested source depths are 4, 8, 12, 16, 20 and 24 bits, with mono, independent
stereo and three side-channel assignments. Each fixture runs with whole-input,
1-byte, 127-byte and 2048-byte schedules. Encoded source depth and delivered
PCM16 depth are checked separately. QEMU must produce every unique case and
the complete marker and terminate with exit zero; timeout/panic/watchdog,
heap failure, missing/duplicate cases and mismatches fail the gate.

The additional guards are 42 truncated STREAMINFO prefixes (0–41 bytes),
invalid signature, 65537-byte metadata, 65537-byte frame window, callback abort,
separate zero-byte EOF and clean reopen: 48 checks. Destruction must leave zero
core workspace and valid SDK heap integrity. The explicit oversized-metadata
error in `qemu.log` is an expected negative-input guard.

## Evidence map

| Path | Meaning |
| --- | --- |
| `report.json` | Unmodified final runner report and all 520 parsed cases. |
| `execution-bundle.json` | Unmodified source/fixture/tool/ROM/config/ELF/image hash bundle written before QEMU. |
| `sources/harness/` | Frozen target project, SDK build helper and harness README. |
| `sources/runner/` | Frozen actual Python runner. |
| `sources/repository/` | Unchanged production adapter/core/compatibility and fixture generator bytes. |
| `fixtures/`, `fixture-manifest.json`, `fixtures.bin` | Actual encoded fixtures, independent PCM16 oracles and the exact data-partition blob. |
| `build/`, `sdkconfig`, `qemu-flash.bin` | Bound standalone test ELF/app, compiler database, partition/config metadata and disposable 4 MiB flash image. |
| `*.log` | Original build, merge, version, SDK-state and emulator stdout logs. |
| `qualification.json` | Archive map and before/after live/bound-input hash verification. |
| `history/` | Clearly historical tracked-01 report/bundle and portable-tool preflight-02. |
| `archival/archive.py` | Archive procedure; original evidence is copied byte-for-byte. |
| `manifest.json` | Size and SHA-256 of every archive file except this self-index. |

Runtime executable and ROM bytes are deliberately not copied: their exact hashes
and version logs are retained. Absolute paths in original evidence identify the
run environment; archived bundle-relative paths retain the same byte content.
The archive binds SDK commit `7101770dc6db2667b3c477cc31365dd1acd6db4e`, real
Xtensa ELF/image identity, nonoverlapping factory/data partitions, bootloader
offset `0x1000` and a checked 4 MiB merged flash. These are standalone test images,
not production firmware and not intended for automatic flashing.

## Scope and remaining gates

This executes the shared adapter/core with real SDK FreeRTOS/heap/timers in an
emulator. It does **not** run the actual CYD `decoder_task` or its maintenance/
queue lifecycle, inject OOM, execute deliberate semantic-mutant target controls,
or qualify physical vendor/custom A/B, RF, DMA/I2S, full-radio resource margins,
power or physical timing/stack behavior. Those gates remain open. The six tested
depths are not all 21 possible integer depths from 4 through 24. No full FLAC
CRC/MD5/malformed-stream standard conformance is claimed. Debug guards and
DIO/40 MHz flash settings belong only to this isolated test profile; emulator
heap/stack observations do not establish production budgets or performance.
'''
(ARCHIVE/'README.md').write_text(readme,encoding='utf-8')
after=verify_live()
assert before==after
archived={}
for group in ('frozen_sources_sha256','fixture_sha256','artifact_sha256'):
    archived[group]={name:sha(ARCHIVE/name)==digest for name,digest in bundle[group].items()}
assert all(value for values in archived.values() for value in values.values())
assert all(sha(ARCHIVE/name)==info['sha256'] for name,info in mapping.items())
qualification={'passed':True,'archived_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'scope':'Standalone target adapter/core 520 PCM cases and 48 guards only; actual CYD decoder task/OOM/semantic-mutant target controls/physical gates remain open.',
    'original_report_sha256':sha(RUN/'report.json'),'original_execution_bundle_sha256':sha(RUN/'execution-bundle.json'),
    'original_bytes_preserved':True,'source_to_archive':mapping,'live_inputs_before':before,
    'live_inputs_after':after,'archived_bundle_inputs':archived,
    'runtime_and_rom_bytes_copied':False,'all_processes_terminal':True}
(ARCHIVE/'qualification.json').write_text(json.dumps(qualification,indent=2)+'\n',encoding='utf-8')
entries={path.relative_to(ARCHIVE).as_posix():{'bytes':path.stat().st_size,'sha256':sha(path)}
    for path in sorted(ARCHIVE.rglob('*')) if path.is_file() and path!=ARCHIVE/'manifest.json'}
(ARCHIVE/'manifest.json').write_text(json.dumps({'scope':'All archive files except manifest.json',
    'files':entries},indent=2)+'\n',encoding='utf-8')
assert all((ARCHIVE/name).stat().st_size==info['bytes'] and sha(ARCHIVE/name)==info['sha256'] for name,info in entries.items())
print('PASS archive',len(entries),'indexed files;',sum(info['bytes'] for info in entries.values()),
      'bytes; manifest SHA256',sha(ARCHIVE/'manifest.json'))
