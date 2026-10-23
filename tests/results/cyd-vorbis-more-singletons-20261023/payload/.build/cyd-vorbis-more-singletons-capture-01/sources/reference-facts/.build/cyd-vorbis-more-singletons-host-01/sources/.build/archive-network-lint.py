from pathlib import Path
import hashlib
import json
import shutil

root = Path(__file__).resolve().parents[1]
dest = root / 'tests/results/cyd-network-runtime-20261019'
hash_file = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
reports = {}
for mode in ['vendor', 'custom']:
    source = root / '.build' / ('lint-cyd-network-' + mode + '-final')
    report = json.loads((source / 'report.json').read_text(encoding='utf-8'))
    assert report['complete'] and report['errors'] == 0 and report['analysis_exit'] == 0
    assert report['all_inputs_unchanged_after_analysis']
    verification = json.loads((source / 'post-analysis-verification.json').read_text(encoding='utf-8'))
    assert verification['passed'] and all(verification['inputs'].values())
    for path in source.rglob('*'):
        if not path.is_file() or '__pycache__' in path.parts:
            continue
        assert path.suffix.lower() not in {'.exe', '.obj', '.o', '.a', '.bin', '.pyc'}, path
        target = dest / ('lint-' + mode) / path.relative_to(source)
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            assert target.read_bytes() == path.read_bytes(), target
        else:
            shutil.copyfile(path, target)
    reports[mode] = {'units': report['units'], 'warnings': report['warnings'],
                     'errors': report['errors'], 'report_sha256': hash_file(source / 'report.json'),
                     'frozen_inputs': len(verification['inputs'])}
qualification = dest / 'qualification.json'
data = json.loads(qualification.read_text(encoding='utf-8'))
data['lint'] = reports
qualification.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
print(json.dumps(reports, indent=2))
