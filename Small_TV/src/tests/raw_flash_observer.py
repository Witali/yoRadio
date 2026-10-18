"""Read public synthetic settings while a disposable VM persists its raw sector."""


def read_stored_key(path, offset):
    """Return pending for erased/partly programmed fields; never decode 0xff as text."""
    with path.open('rb') as stream:
        stream.seek(offset)
        data = stream.read(20)
    if len(data) != 20 or b'\0' not in data:
        return None
    value = data.split(b'\0',1)[0]
    if not value or any(byte < 0x20 or byte > 0x7e for byte in value):
        return None
    return value.decode('ascii')


def persistence_complete(read_key, expected, read_dirty=None):
    """Require native esp_flash_write completion before accepting host image bytes.

    The flag is read before and after the file. The outer caller retains its
    bounded timeout, so a permanent write failure still fails the test.
    Factory firmware has no proven equivalent flag: it uses the raw key only.
    """
    if read_dirty is not None and read_dirty() != b'\0':
        return False
    if read_key() != expected:
        return False
    return read_dirty is None or read_dirty() == b'\0'
