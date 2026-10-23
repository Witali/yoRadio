from pathlib import Path

root = Path(__file__).resolve().parents[1]
tasks = [
    ('run-network-power-lint-configure.ps1', 'run-n5-lint-configure.ps1', [
        ('build-lint-network-power-final02', 'build-lint-network-n5-01'),
        ('network-power-lint-configure-', 'network-n5-lint-configure-')]),
    ('run-network-power-lint.py', 'run-n5-lint.py', [
        ('build-lint-network-power-final02', 'build-lint-network-n5-01'),
        ('-network-power-final', '-network-n5-01'),
        ('run-network-power-lint-configure.ps1', 'run-n5-lint-configure.ps1')]),
]
for source, target, replacements in tasks:
    data = (root / '.build' / source).read_text(encoding='utf-8')
    for old, new in replacements:
        assert old in data, old
        data = data.replace(old, new)
    destination = root / '.build' / target
    assert not destination.exists(), destination
    destination.write_text(data, encoding='utf-8')
print('Prepared independent N5 Clang configuration and frozen-input analysis helpers')
