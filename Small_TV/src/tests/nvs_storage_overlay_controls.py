"""Reject inconsistent vendor/generated sources, mixed TUs and unsafe overlay outputs locally."""
from copy import deepcopy
from pathlib import Path
import subprocess
import sys

from prepare_nvs_component import sources
from verify_nvs_storage import verify


def run(native, app, archive, old_app, old_archive, component, overlay, saved, commands, output):
    """Mutate private copies only, first proving the copied fixture is accepted unchanged."""
    output.mkdir(parents=True, exist_ok=False); generated, vendor = sources(component)
    local_component, local_overlay = output/'component', output/'overlay'
    for name, raw in vendor.items():
        target = local_component/name; target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(raw)
    local_overlay.mkdir()
    for name, raw in generated.items(): (local_overlay/name).write_bytes(raw)
    copied_commands = deepcopy(commands)
    for row in copied_commands:
        if '__idf_nvs_flash.dir' in row.get('command', ''):
            row['file'] = str(local_overlay/Path(row['file']).name)
    assert verify(native, app, archive, local_component, local_overlay, saved, copied_commands)['passed']
    rejected = []
    def reject(name, operation):
        """Use the same checker as the real build; require an effective rejection."""
        try: operation()
        except (ValueError, AssertionError): rejected.append(name)
        else: raise AssertionError('Invalid Storage overlay accepted: '+name)
    def checked():
        """Recheck actual source/header bytes and source-object linkage after each mutation."""
        return verify(native, app, archive, local_component, local_overlay, saved, copied_commands)
    header = local_component/'src/nvs_storage.hpp'; original = header.read_bytes()
    try:
        header.write_bytes(original+b'\n'); reject('changed-vendor-header', checked)
    finally: header.write_bytes(original)
    extra = local_component/'src/unexpected.cpp'
    try:
        extra.write_text('// private control\n'); reject('added-vendor-source', checked)
    finally: extra.unlink()
    header = local_overlay/'nvs_storage.hpp'; original = header.read_bytes()
    try:
        changed = original.replace(b'esp_err_t eraseOrphanDataBlobs(', b'void eraseOrphanDataBlobs(')
        assert changed != original; header.write_bytes(changed); reject('inconsistent-private-return-type', checked)
    finally: header.write_bytes(original)
    row = next(row for row in copied_commands if '__idf_nvs_flash.dir' in row.get('command', ''))
    original = row['file']
    try:
        row['file'] = str(local_component/'src'/Path(original).name); reject('mixed-translation-unit', checked)
    finally: row['file'] = original
    reject('wrong-app-elf-pair', lambda: verify(native, old_app, archive, local_component, local_overlay, saved, copied_commands))
    reject('old-source-archive', lambda: verify(native, app, old_archive, local_component, local_overlay, saved, copied_commands))
    inventory = {str(p.relative_to(local_component)): p.read_bytes() for p in local_component.rglob('*') if p.is_file()}
    tool = Path(__file__).resolve().parents[1]/'tools/prepare_nvs_component.py'
    for name, target, reports in (('source-output-alias', local_component/'src', output/'reports'),
                                  ('reports-inside-sdk', output/'unused-overlay', local_component)):
        result = subprocess.run([sys.executable, '-B', str(tool), '--component', str(local_component),
                                 '--output', str(target), '--reports', str(reports)], capture_output=True)
        assert result.returncode != 0, 'Unsafe overlay output accepted'
        assert inventory == {str(p.relative_to(local_component)): p.read_bytes() for p in local_component.rglob('*') if p.is_file()}
        rejected.append(name)
    return dict(passed=True, rejected=rejected, original_sdk_modified=False, original_overlay_modified=False,
                positive_copied_fixture_passed=True)
