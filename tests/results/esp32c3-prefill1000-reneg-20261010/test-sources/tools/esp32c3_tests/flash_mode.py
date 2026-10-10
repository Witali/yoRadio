"""Validate a full-radio boot probe against the exact firmware image."""
import hashlib
import re
import zlib

# ESP32-C3 SPI_MEM_CTRL fields, verified against the pinned SDK spi_mem_reg.h.
FREAD_QIO = 1 << 24
FREAD_DIO = 1 << 23
FREAD_QUAD = 1 << 20
FREAD_DUAL = 1 << 14
MODE_MASK = FREAD_QIO | FREAD_DIO | FREAD_QUAD | FREAD_DUAL
CLOCK_EQUAL_SYSTEM = 1 << 31
CLOCK_DIVIDER_SHIFT = 16
CLOCK_DIVIDER_MASK = 255
READ_PASSES = 4


def rows(log, tag):
    return [dict(re.findall(r'(\w+)=([^\s]+)', line))
            for line in log.splitlines() if line.startswith(tag + ' ')]


def validate(log, binary, mode):
    if mode not in ('dio', 'qio'):
        raise ValueError('Unsupported flash mode')
    env = rows(log, 'FLASH_PROBE_ENV')
    read = rows(log, 'FLASH_PROBE_READ')
    passed = rows(log, 'FLASH_PROBE_PASS')
    if len(env) != 1 or len(passed) != 1 or 'FLASH_PROBE_FAIL' in log:
        raise ValueError('Missing, duplicate or failed boot probe')
    e = env[0]
    ctrl, clock = int(e['ctrl'], 0), int(e['clock'], 0)
    divider = 1 if clock & CLOCK_EQUAL_SYSTEM else (
        (clock >> CLOCK_DIVIDER_SHIFT) & CLOCK_DIVIDER_MASK) + 1
    expected = FREAD_QIO if mode == 'qio' else FREAD_DIO
    if (e['expected'] != mode or ctrl & MODE_MASK != expected or
            int(e['source_mhz']) != 80 or int(e['divider']) != divider or
            divider != 1 or int(e['actual_mhz']) != 80 or
            int(e['cpu_hz']) != 160000000 or
            int(e['physical_bytes']) != 4 * 1024 * 1024 or
            int(e['jedec'], 0) != 0x464016):
        raise ValueError('Wrong actual flash mode, clock or board')
    if (len(read) != READ_PASSES or
            [int(r['pass']) for r in read] != list(range(1, READ_PASSES + 1))):
        raise ValueError('Incomplete or duplicate mapped reads')
    offsets = {int(r['offset'], 0) for r in read}
    if len(offsets) != 1 or not offsets <= {0x10000, 0x1e0000}:
        raise ValueError('Wrong running partition')
    crc = zlib.crc32(binary)
    if len(binary) <= 16384 or any(int(r['bytes']) != len(binary) or
                                 int(r['crc32'], 0) != crc for r in read):
        raise ValueError('Flash read differs from saved application')
    return dict(result='PASS', mode=mode, environment=e, read_passes=len(read),
                image_bytes=len(binary), read_bytes=len(read) * len(binary),
                app_sha256=hashlib.sha256(binary).hexdigest(), crc32=f'0x{crc:08x}')
