"""Create this evidence archive once from historical ignored qualification outputs.

No SDK, firmware source, Git index or existing evidence artifact is modified.
The bundle stores long dependency paths through content-addressed payloads.
"""
import datetime
import hashlib
import json
from pathlib import Path
import struct

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
ARTIFACTS={
    'audit':'cyd-memory-transfer-audit-01',
    'host':'cyd-http-tx-release-01',
    'target':'cyd-http-tx-target-01',
    'integration':'cyd-http-tx-integration-02',
    'failed/integration-01':'cyd-http-tx-integration-01',
}
EXPECTED={
    'audit/report.json':'2a9eab5d44b055dd5350b200397a5e4c7c7f7e8157c92e8baeb7f0b5119c1ec9',
    'host/report.json':'08c2a41a11ac8156b147f44142998f355f5aed5648051ee9209a2c49fc3fe32b',
    'target/report.json':'27a04ac78c3737d23ecdff46357403f46ac6eed411f69ecc8fbb36763b85703a',
    'integration/report.json':'87467071a8828570d58964051819f97bec96f916da07f443cc6cf779f5c244d6',
}


def sha(raw):return hashlib.sha256(raw).hexdigest()


def write(relative,raw):
    target=OUT/relative;target.parent.mkdir(parents=True,exist_ok=True)
    if not target.exists() or target.read_bytes()!=raw:target.write_bytes(raw)


def json_file(relative,value):write(relative,(json.dumps(value,indent=2)+'\n').encode())


def binary(raw):
    if raw[:2]==b'MZ':return 'Windows PE executable/tool payload',None
    if raw[:4]==b'\x7fELF':
        endian='<' if raw[5]==1 else '>'
        kind,machine=struct.unpack_from(endian+'HH',raw,16)
        identity={'class':32 if raw[4]==1 else 64,'type':kind,'machine':machine}
        if kind==1 and machine==94:return None,identity
        return 'Host executable/binary payload (not Xtensa ET_REL)',identity
    return None,None


def main():
    assert not (OUT/'manifest.json').exists(),'Archive already frozen; do not overwrite'
    catalog=[];captured={};report_hashes={}
    for label,name in ARTIFACTS.items():
        source=ROOT/'.build'/name;assert source.is_dir()
        for path in sorted(source.rglob('*')):
            if not path.is_file():continue
            relative=path.relative_to(source).as_posix();raw=path.read_bytes();digest=sha(raw)
            captured[str(path)]=digest
            omitted,elf=binary(raw)
            payload=None
            if not omitted:
                # Root reports/commands/logs and the actual target object remain
                # immediately readable; all nested paths are flattened/deduped.
                payload=label+'/'+relative if '/' not in relative else 'objects/'+digest
                write(payload,raw)
            item={'artifact':label,'relative_path':relative,'source':path.relative_to(ROOT).as_posix(),
                  'sha256':digest,'bytes':len(raw),'payload':payload,'omitted_reason':omitted}
            if elf:item['elf']=elf
            catalog.append(item)
            if relative=='report.json':report_hashes[label+'/report.json']=digest
    for relative,expected in EXPECTED.items():assert report_hashes[relative]==expected,relative
    target=json.loads((OUT/'target/report.json').read_bytes())
    stored={item['source']:item for item in catalog}
    # Validate frozen input snapshots, not current firmware/SDK trees. They are
    # historical after intentional production integration and telemetry edits.
    for origin,digest in target['input_sha256'].items():
        relative=Path(target['snapshot_map'][origin]).as_posix()
        record=stored['.build/'+ARTIFACTS['target']+'/'+relative]
        assert record['sha256']==digest,(origin,relative)
    assert len(target['input_sha256'])==264
    external=json.loads((OUT/'integration/report.json').read_bytes())['cmake_tool_sha256']
    json_file('catalog.json',{'schema':1,'layout':'Original artifact-relative names map to short content-addressed payloads. Raw reports retain original historical absolute paths and hashes unchanged.',
              'files':catalog,'external_tools_reported_hash_only':external,
              'external_tool_note':'Integration report records CMake/Ninja/Python executable hashes; those executable payloads were never frozen in its original artifact. Host GCC is identified by the retained compiler version log, not a fabricated retrospective executable hash.'})
    json_file('failed-attempts.json',{
        'target_initial_import':{'raw_report':'target/attempt-00-report.json','outcome':'Snapshot-module import failed before any compiler/tool command. Preserved by the original target report; no separate raw traceback file was captured.'},
        'target_postcompile_crlf_validation':{'raw_report':'target/attempt-01-completed-compile-report.json','outcome':'Whole target compile and nm succeeded. A Windows CRLF regex assertion failed in the initial validator. The finalizer validates split lines without changing source, flags or object; target/report.json preserves this completion history. No separate raw traceback file was captured.'},
        'integration_missing_wsl_cmake':{'raw_report':'failed/integration-01/report.json','error_evidence_original_relative':'cmake/enabled-absolute/configure.log','outcome':'31 enabled and31 disabled cases plus6 semantic controls passed; configure then failed because cmake was absent in WSL. The fresh integration02 uses installed Windows CMake/Ninja and completes all9 helper scenarios. Original failed output tree is archived with the same binary omission policy.'}})
    write('.gitattributes',b'* -text\n')
    write('README.md',b'''# CYD request-buffer release qualification (2026-10-20)

This archive records the M13 C3-to-CYD memory-policy audit and bounded HTTP
request TX-buffer release candidate for pinned ESP-IDF 6.0.2. The audit is a
historical snapshot: production integration and output telemetry intentionally
changed some live firmware/configuration inputs afterward. Its original
"unchanged after" fields describe the original run, not today's checkout.

- [Memory audit](audit/report.json): donor/current configuration, SDK source
  comparisons, map-symbol observations, ownership risks and measured-policy gates.
- [SDK-source host proof](host/report.json): 17 cases and 8 exact semantic
  controls under ASan/UBSan, with selected actual SDK functions/header utilities.
- [Whole SDK Xtensa object compile](target/report.json): exact existing CYD
  compile row, unchanged flags/includes/config, 248 dependencies captured before
  compile and 264 total recorded inputs; exit0, no compiler diagnostics.
  [Retained object](target/esp_http_client.c.obj) is ELF32 ET_REL EM_XTENSA94;
  `nm` defines the new API once. This is not a linked production application.
- [Radio/CMake integration proof](integration/report.json): 31 enabled plus31
  disabled actual `open_stream` cases, identical observable HTTP traces,
  6 exact semantic controls and 9 configure-time helper scenarios.
- [Failed attempt metadata](failed-attempts.json) retains the precompiler import,
  postcompile CRLF validator and missing WSL CMake failures without recasting them
  as successful test runs.

The radio config requests **4096 TX payload bytes**. This is neither a measured
usable allocation size nor a guaranteed 4096-byte free-heap gain. No physical
heap, fragmentation, TLS runtime, audible playback or performance result is
claimed. The installed SDK was not modified: the exact-source patch is used on
a build-local copy and preserves unrelated SDK bytes. Other TLS reserve/IRAM
configuration changes from C3 remain separate candidates with measurement gates.

The bounded production integration is present in the captured integration
snapshot, default-enabled behind `CONFIG_YORADIO_HTTP_REQUEST_BUFFER_RELEASE`.
The production application build/link/placement gate is pending separate parent
evidence and is not bound by this archive. No firmware image or device test is
included here. See [HOST.md](HOST.md) for seams and replay limits.

Run `python -B verify.py` from this directory. [manifest.json](manifest.json)
hashes every archived payload and metadata file except itself; publish its own
SHA256 alongside the bundle. [catalog.json](catalog.json) maps original artifact
paths to short `objects/<sha256>` payloads or explicit binary omissions. Reports
and root commands/logs keep their original bytes. Long dependency/source paths
are flattened; Windows tool executables and Linux host binaries have hashes and
sizes only. Actual Xtensa relocatable objects are retained. `.gitattributes`
disables text conversion so Git preserves the byte hashes.
''')
    write('HOST.md',b'''# Scope, seams and stored evidence

The raw audit, host, target and integration reports are byte-identical to their
original ignored outputs. Input hashes and snapshot maps in those reports are
historical run provenance. The archive verifier checks stored bytes and does
not assert that historical repository/SDK input hashes equal the live checkout.

## SDK-source host proof

The actual request generator, body sender, cached response reader and request
cleanup spans run with actual SDK header/utilities. Private client layout,
transport, allocation accounting and scripted auth/redirect/response-state
preparation are host seams. Tests cover reuse capacities4096/8192, OOM retry,
state/body/async admission, retained borrowed pointers and cached reads. They
are not the full SDK auth/redirect/parser/TLS state machine. Semantic controls
must exit80 at their expected named assertion; sanitizer crashes are not a pass.

## Whole target translation unit

The complete patched SDK6.0.2 `esp_http_client.c` was compiled to an Xtensa object
using the existing `build-c3-transfer` row. Only source/output paths were
replaced; compiler flags, headers and generated configuration were preserved.
The target report stores the original row/raw command, response-file/specs,
before/after hashes, all248 dependency paths/snapshots, GCC/cc1/as/nm identities,
SDK commit/clean-status logs and object/symbol checks. Its264 recorded inputs
include report/validator context as well as compiler inputs. The finalizer was
captured after compile and is identified as such; it corrected the CRLF report
check without rebuilding. PE tool payloads are omitted by policy, with hashes
retained. Their DLL closure was not certified. This object proves compilation
against real target private structs/headers; it proves neither linked firmware
placement nor runtime memory ownership under actual TLS traffic.

## Radio and configure integration

The unchanged extracted production `open_stream` runs with explicit HTTP,
clock and release-result seams. The SDK release implementation is tested in
the separate host proof, not substituted as real in the radio fixture.
Enabled/disabled traces agree for response status, redirect, timeout and ICY
metadata behavior. Rejected release retains the request buffer and playback;
redirect/error/deadline/invalid-header paths do not request release.

The actual CMake helper is exercised against a copied SDK input and a mock
component target with source/include/options properties. No CMake SDK library
is built by these tests. Enabled absolute/relative source replacement, disabled
and early expansion, exact1 source, version/source drift/already-patched
rejections and configure dependencies are checked. Installed Windows
CMake/Ninja/Python tool hashes are recorded, not their executable payloads.

## Layout and reproduction

`catalog.json` covers every original artifact file, including failed integration
attempt01. For each entry, `payload` is a direct archive path or a short
content-addressed object; null means the explicit executable omission policy.
The retained runner/fixture/source snapshots and commands are accessible through
this mapping. Original absolute paths in commands and raw reports are retained
as provenance, so replay elsewhere requires restoring a fresh local layout and
reviewing tool/SDK paths; no one-command portable runtime replay is claimed.

The archive contains raw compiler/configure/test logs, generated function spans,
stubs, dependency files, source/config snapshots, audit SDK comparisons/map
observations and the actual Xtensa object. It contains no board measurement or
successful production application build. Keep those qualification gates separate
when updating the parent transfer plan.
''')
    assert all(sha(Path(name).read_bytes())==digest for name,digest in captured.items()),'Original artifacts changed during archive'
    files={p.relative_to(OUT).as_posix():{'sha256':sha(p.read_bytes()),'bytes':p.stat().st_size} for p in sorted(OUT.rglob('*')) if p.is_file() and p.name!='manifest.json'}
    json_file('manifest.json',{'schema':1,'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'scope':'Historical M13 audit and bounded HTTP qualification, without current-live-input or physical/application qualification claim.',
              'files':files,'raw_report_sha256':report_hashes,'original_artifact_files':len(catalog),
              'kept_artifact_files':sum(item['payload'] is not None for item in catalog),
              'omitted_executable_files':sum(item['payload'] is None for item in catalog),
              'original_artifact_bytes':sum(item['bytes'] for item in catalog),
              'omitted_executable_bytes':sum(item['bytes'] for item in catalog if item['payload'] is None),
              'original_artifacts_unchanged_during_archive':True,'original_artifact_currentness_note':'Only ignored artifact files were compared before/after. Historical source inputs are not asserted live-current.'})
    print('Archived',len(catalog),'original files into',len(files),'verifiable archive files')
    print('manifest SHA256',sha((OUT/'manifest.json').read_bytes()))


if __name__=='__main__':main()
