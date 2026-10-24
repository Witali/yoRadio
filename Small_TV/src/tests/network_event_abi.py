"""Compile the production SDK's AP event layout without invoking guest functions."""
import argparse
import ctypes
from ctypes import wintypes
import hashlib
import json
import os
from pathlib import Path
import shlex
import struct
import subprocess

from elftools.elf.elffile import ELFFile


FIELDS = {
    'connected_id': 'WIFI_EVENT_AP_STACONNECTED',
    'disconnected_id': 'WIFI_EVENT_AP_STADISCONNECTED',
    'scan_done_id': 'WIFI_EVENT_SCAN_DONE',
    'connected_bytes': 'sizeof(wifi_event_ap_staconnected_t)',
    'connected_mac': 'offsetof(wifi_event_ap_staconnected_t,mac)',
    'mac_bytes': 'sizeof(((wifi_event_ap_staconnected_t *)0)->mac)',
    'connected_aid': 'offsetof(wifi_event_ap_staconnected_t,aid)',
    'disconnected_bytes': 'sizeof(wifi_event_ap_stadisconnected_t)',
    'disconnected_mac': 'offsetof(wifi_event_ap_stadisconnected_t,mac)',
    'disconnected_aid': 'offsetof(wifi_event_ap_stadisconnected_t,aid)',
    'disconnected_reason': 'offsetof(wifi_event_ap_stadisconnected_t,reason)',
    'reason_bytes': 'sizeof(((wifi_event_ap_stadisconnected_t *)0)->reason)',
}


def sha(file):
    """Identify the exact command metadata, compiler, SDK headers and object bytes."""
    return hashlib.sha256(file.read_bytes()).hexdigest()


def command_arguments(command):
    """Use Windows command-line decoding, preserving quoted C macro values."""
    if os.name != 'nt': return shlex.split(command)
    shell = ctypes.WinDLL('shell32', use_last_error=True)
    shell.CommandLineToArgvW.argtypes = [wintypes.LPCWSTR, ctypes.POINTER(ctypes.c_int)]
    shell.CommandLineToArgvW.restype = ctypes.POINTER(wintypes.LPWSTR)
    count = ctypes.c_int()
    pointer = shell.CommandLineToArgvW(command, ctypes.byref(count))
    if not pointer: raise ctypes.WinError(ctypes.get_last_error())
    try: return [pointer[index] for index in range(count.value)]
    finally:
        kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        kernel.LocalFree.argtypes = [ctypes.c_void_p]; kernel.LocalFree.restype = ctypes.c_void_p
        assert not kernel.LocalFree(ctypes.cast(pointer, ctypes.c_void_p))


def probe(root, output, dependency_root):
    """Reuse real target flags while replacing every original output/dependency path."""
    output = output.resolve(); output.mkdir(parents=True, exist_ok=False)
    build = root/'.build/small-tv-esp32c2'
    database = build/'compile_commands.json'
    commands = json.loads(database.read_text())
    rows = [row for row in commands if Path(row['file']).resolve() ==
            (root/'Small_TV/src/app/network/wifi.c').resolve()]
    assert len(rows) == 1
    original = command_arguments(rows[0]['command']); compiler = Path(original[0])
    flags = []; index = 1; saw_source = saw_output = False; production_object = None
    while index < len(original):
        value = original[index]; index += 1
        if value in ('-o', '-c', '-MF', '-MT', '-MQ'):
            assert index < len(original)
            if value == '-c':
                assert Path(original[index]).resolve() == Path(rows[0]['file']).resolve(); saw_source = True
            if value == '-o':
                assert not saw_output
                saw_output = True
                production_object = (Path(rows[0]['directory'])/original[index]).resolve()
            index += 1
        elif value not in ('-MD', '-MMD', '-MP'): flags.append(value)
    assert saw_source and saw_output
    source = output/'wire.c'; obj = output/'wire.o'
    source.write_text('#include <esp_wifi_types.h>\n#include <stddef.h>\n#include <stdint.h>\n'
        'const uint32_t tv_wifi_event_wire[] = {\n'+',\n'.join(FIELDS.values())+'\n};\n', encoding='utf-8')
    archive = root/'firmware/development/small-tv-esp32c2-reconstructed'
    manifest_file = archive/'manifest.json'; manifest = json.loads(manifest_file.read_text())
    app = archive/'app.bin'; elf_file = build/'small_tv_reconstructed.elf'
    assert sha(app) == next(row['sha256'] for row in manifest['images'] if row['file'] == 'app.bin')
    assert sha(elf_file) == manifest['elf_sha256'] == app.read_bytes()[176:208].hex()
    inputs = [Path(__file__), database, compiler, build/'config/sdkconfig.h', production_object,
        manifest_file, app, elf_file,
        dependency_root/'.idf/v6.1-9a97f6c54ec6/components/esp_wifi/include/esp_wifi_types.h',
        dependency_root/'.idf/v6.1-9a97f6c54ec6/components/esp_wifi/include/esp_wifi_types_generic.h']
    before = {str(file): sha(file) for file in inputs}
    command = [str(compiler), *flags, '-c', str(source), '-o', str(obj)]
    result = subprocess.run(command, cwd=rows[0]['directory'], capture_output=True, text=True,
        encoding='utf-8', errors='replace')
    (output/'compiler.log').write_text(result.stdout+result.stderr, encoding='utf-8')
    result.check_returncode()
    with obj.open('rb') as stream:
        elf = ELFFile(stream)
        assert elf['e_type'] == 'ET_REL' and elf['e_machine'] == 'EM_RISCV' and elf.elfclass == 32 and elf.little_endian
        symbols = [symbol for symbol in elf.get_section_by_name('.symtab').iter_symbols()
                   if symbol.name == 'tv_wifi_event_wire']
        assert len(symbols) == 1; symbol = symbols[0]
        assert symbol['st_size'] == 4*len(FIELDS)
        section = elf.get_section(symbol['st_shndx']); start = symbol['st_value']-section['sh_addr']
        data = section.data()[start:start+symbol['st_size']]
        wire = dict(zip(FIELDS, struct.unpack('<'+'I'*len(FIELDS), data)))
    assert wire['mac_bytes'] == 6 and wire['reason_bytes'] == 2
    assert 0 <= wire['connected_mac'] <= wire['connected_bytes']-6
    assert 0 <= wire['disconnected_mac'] <= wire['disconnected_bytes']-6
    assert 0 <= wire['disconnected_reason'] <= wire['disconnected_bytes']-2
    assert before == {str(file): sha(file) for file in inputs}
    report = dict(passed=True, wire=wire, inputs_sha256=before, object_sha256=sha(obj),
        app_sha256=sha(app), elf_sha256=sha(elf_file), production_object_unchanged=True,
        source_sha256=sha(source), command=command,
        scope='Compiled SDK ABI only; no association, RF, HTTP lifecycle or guest execution acceptance')
    (output/'layout.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8', newline='\n')
    return report


def main():
    """Generate a bounded read-only observer description from the matching build."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument('--dependency-root', type=Path, default=Path('C:/Work/yoRadio'))
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(); print(json.dumps(probe(args.root.resolve(), args.output, args.dependency_root)['wire']))


if __name__ == '__main__': main()
