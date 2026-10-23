import hashlib
import json
from pathlib import Path

root=Path(__file__).resolve().parents[1]
archive=root/'tests/results/native-runtime-transfer-20261018'
manifest=json.loads((archive/'archive-manifest.json').read_text())
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def relative_path(value): return Path(value.replace('\\','/'))
files=manifest['files']
for relative,sha in files.items():
    assert digest(archive/relative)==sha,relative
source_count=sdk_count=unit_count=0
for name,item in manifest.items():
    if name=='files': continue
    for filename,sha in item['reports'].items():
        report_path=archive/name/filename
        assert digest(report_path)==sha
        report=json.loads(report_path.read_text())
        for relative,expected in report.get('source_sha256',{}).items():
            if not isinstance(expected,str): continue
            assert digest(archive/name/'sources'/relative_path(relative))==expected,(name,relative)
            source_count+=1
        for relative,expected in report.get('sdk_sha256',{}).items():
            candidates=[archive/name/'sdk-sources'/relative_path(relative),
                        archive/name/'composed/sdk-sources'/relative_path(relative)]
            candidate=next((path for path in candidates if path.is_file()),None)
            assert candidate is not None and digest(candidate)==expected,(name,relative)
            sdk_count+=1
        for relative,expected in report.get('generated_unit_sha256',{}).items():
            assert digest(archive/name/relative)==expected,(name,relative)
            unit_count+=1
        if 'foundation_report_sha256' in report:
            assert digest(archive/name/'foundation-report.json')==report['foundation_report_sha256']
        if 'historical_git_blob_sha256' in report:
            assert digest(archive/name/'historical-source.c')==report['historical_git_blob_sha256']
        for unit in report.get('results',[]):
            if not isinstance(unit,dict) or 'source_sha256' not in unit: continue
            assert digest(archive/name/'sources'/relative_path(unit['file']))==unit['source_sha256'],(name,unit['file'])
            source_count+=1
        source_manifest=archive/name/'source-manifest.json'
        if source_manifest.is_file():
            sources=json.loads(source_manifest.read_text())
            for field in ['units','dependencies']:
                for relative,expected in sources.get(field,{}).items():
                    if isinstance(expected,dict): expected=expected['sha256']
                    assert digest(archive/name/'sources'/relative_path(relative))==expected,(name,relative)
                    source_count+=1
print('PASS',len(files),'archive files,',source_count,'source hashes,',sdk_count,'SDK hashes,',unit_count,'generated units')
