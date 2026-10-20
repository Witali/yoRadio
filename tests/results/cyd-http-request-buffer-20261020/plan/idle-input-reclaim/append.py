"""Append frozen candidate2 preparation without changing any prior archive entry."""
import hashlib
import json
from pathlib import Path

OUT=Path(__file__).resolve().parent
ARCHIVE=OUT.parents[1]
ROOT=ARCHIVE.parents[2]
SOURCE=ROOT/'.build/cyd-idle-pool-lifetime-plan-01'


def sha(raw):return hashlib.sha256(raw).hexdigest()


def main():
    manifest_path=ARCHIVE/'manifest.json';previous_raw=manifest_path.read_bytes()
    assert sha(previous_raw)=='a8128bbedde171614f264d3f1e1409b8c058c3e9fd58332c87716c517d066c23'
    previous=json.loads(previous_raw);old_files=previous['files'].copy()
    for relative,expected in old_files.items():
        raw=(ARCHIVE/relative).read_bytes()
        assert len(raw)==expected['bytes'] and sha(raw)==expected['sha256'],relative
    assert not (OUT/'report.json').exists(),'Plan append already performed'
    raw_report=(SOURCE/'report.json').read_bytes()
    assert sha(raw_report)=='1d59c129bf12f0768eb79144300ed4f737da8f626c9660242ff9a5ee9d2ec611'
    report=json.loads(raw_report)
    assert report['status']=='preparation_only_not_implemented_or_qualified'
    assert len(report['input_sha256'])==35
    (OUT/'report.json').write_bytes(raw_report)
    (OUT/'previous-root-manifest.json').write_bytes(previous_raw)
    mapping={}
    for origin,digest in report['input_sha256'].items():
        source=SOURCE/report['snapshot_map'][origin];raw=source.read_bytes()
        assert sha(raw)==digest and not raw.startswith((b'MZ',b'\x7fELF'))
        target=OUT/'objects'/digest;target.parent.mkdir(exist_ok=True)
        if not target.exists():target.write_bytes(raw)
        mapping[origin]={'sha256':digest,'bytes':len(raw),'payload':target.relative_to(ARCHIVE).as_posix(),
                         'original_frozen_snapshot':report['snapshot_map'][origin]}
    (OUT/'snapshot-map.json').write_bytes((json.dumps({
        'schema':1,'status':'UNIMPLEMENTED preparation only; all host/target/board gates in report remain unrun',
        'raw_report_sha256':sha(raw_report),'frozen_inputs':mapping,
        'note':'Stored historical plan snapshots are checked, not current production-build inputs. No executable/tool payload is present.'},indent=2)+'\n').encode())
    (OUT/'README.md').write_bytes(b'''# Candidate2: idle-input reclaim plan (UNIMPLEMENTED)

[report.json](report.json) is the byte-identical frozen next-step plan. It is
preparation only: no candidate2 code, host tests, target builds, real OOM/SMP
qualification or board measurements were performed. It does not complete M13.
All host/actual-target/physical gates listed in the report remain **unrun**.

The proposed boundary is bind after successful READY commitment, before owner
notifications, with no rollback after binding; reclaim only existing IDLE
extras with a fixed per-allocation retry budget. The plan preserves the sole
native_health failed-allocation callback, current task/core ownership and all
numeric pool/TLS/headroom/IRAM settings. Checked detach/refpin and separate
ordinary queue/health-reader quiescence conditions are described for safe
lifetime handling. No runtime pool teardown feature is implemented or implied.

[snapshot-map.json](snapshot-map.json) maps all35 frozen source/SDK/config/test
context inputs to short content-addressed objects. These are plan provenance,
not a declaration that historical build configurations equal later exports.
The original archive README and all pre-existing entries are unchanged.
[previous-root-manifest.json](previous-root-manifest.json) preserves the root
manifest before this additive extension. Only its file table was extended;
the root verifier covers this addition as ordinary archived payloads.
''')
    added={path.relative_to(ARCHIVE).as_posix():{'sha256':sha(path.read_bytes()),'bytes':path.stat().st_size}
           for path in sorted(OUT.rglob('*')) if path.is_file()}
    assert not set(added)&set(old_files)
    previous['files'].update(added)
    assert all(previous['files'][name]==value for name,value in old_files.items())
    for relative,expected in old_files.items():assert sha((ARCHIVE/relative).read_bytes())==expected['sha256']
    assert sha((SOURCE/'report.json').read_bytes())==sha(raw_report)
    manifest_path.write_bytes((json.dumps(previous,indent=2)+'\n').encode())
    after=json.loads(manifest_path.read_bytes());before=json.loads(previous_raw)
    assert {k:v for k,v in after.items() if k!='files'}=={k:v for k,v in before.items() if k!='files'}
    print('Added',len(added),'files; all',len(old_files),'old manifest entries unchanged')
    print('Root manifest SHA256',sha(manifest_path.read_bytes()))


if __name__=='__main__':main()
