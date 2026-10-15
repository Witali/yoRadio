import collections,gzip,hashlib,json,struct
from pathlib import Path
archive=Path('tests/results/esp32c3-idf61-revision-20261008')
index=json.loads((archive/'index.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
saved=json.loads((archive/'qemu/pcm-comparison.json').read_text())
run=json.loads((archive/'qemu/report.json').read_text())
assert run['passed'] and run['idf']=='6.1-9a97f6c54ec6'
assert Path('idf/esp32c3-oled-native/idf-revision.txt').read_text().strip().startswith('9a97f6c54ec6')
result={'scope':'Recompute retained pinned-SDK PCM; not a new emulator run or an all-input bound.',
        'inputs':{},'comparisons':[]}
for name in ('qemu/pcm-comparison.json','qemu/report.json','qemu/late.pcm.gz','qemu/gaps.pcm.gz'):
    path=archive/name;assert sha(path)==index[name]['sha256']
    result['inputs'][path.as_posix()]=sha(path)
for row in saved['comparisons']:
    candidate=gzip.decompress((archive/'qemu'/(row['case']+'.pcm.gz')).read_bytes())
    path=Path(row['reference']);reference=gzip.decompress(path.read_bytes())
    assert hashlib.sha256(candidate).hexdigest()==row['candidate_sha256']
    assert hashlib.sha256(reference).hexdigest()==row['reference_sha256']
    assert len(candidate)==len(reference) and len(reference)>0
    errors=collections.Counter(abs(a[0]-b[0]) for a,b in zip(struct.iter_unpack('<h',reference),struct.iter_unpack('<h',candidate)))
    assert {str(k):v for k,v in sorted(errors.items())}==row['histogram']
    assert max(errors)==row['max_error_lsb']<=row['limit_lsb']
    result['inputs'][path.as_posix()]=sha(path)
    result['comparisons'].append(dict(case=row['case'],reference=row['reference'],
        samples=sum(errors.values()),peak_lsb=max(errors),limit_lsb=row['limit_lsb']))
result['passed']=True
Path('.build/c3-raw-tail-quiet-20261015/evidence-audit/sdk-pcm.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result['comparisons']))
