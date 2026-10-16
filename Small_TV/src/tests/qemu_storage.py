"""Check the live block backend before treating a flash file as evidence of guest writes."""
from pathlib import Path


def direct_flash_backing(qmp, folder):
    """Require the owned raw image, excluding a hidden -snapshot QCOW overlay."""
    expected = (Path(folder)/'flash.bin').resolve()
    matches = []
    for device in qmp.execute('query-block'):
        inserted = device.get('inserted', {})
        if inserted.get('drv') == 'raw' and not inserted.get('ro', True):
            filename = inserted.get('file')
            if filename and Path(filename).resolve() == expected:
                matches.append(inserted)
    return len(matches) == 1
