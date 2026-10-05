"""Check linked Vorbis repair callbacks and retain a PC19 radio candidate.

The AAC verifier separately checks its existing layouts and patched calls.
This build gate does not assert playback, timing or hardware qualification.
"""
import argparse
import json
from pathlib import Path
import re
import shutil
import struct
import subprocess

from elftools.elf.elffile import ELFFile
from verify_aac_network_build import sha, verify as verify_aac

ROOT = Path(__file__).resolve().parents[2]
CALLS = {
    'decoder_register_codecs': ('__wrap_esp_vorbis_dec_register', 'esp_audio_simple_dec_register_default'),
    'decoder_task': ('__wrap_esp_audio_simple_dec_open', '__wrap_esp_audio_simple_dec_process'),
    '__wrap_esp_vorbis_dec_register': ('esp_audio_dec_register',),
    'process_checked': ('esp_audio_simple_dec_process',),
    '__wrap_esp_audio_simple_dec_process': ('process_checked',),
    '__wrap_esp_vorbis_dec_decode': ('esp_vorbis_dec_decode',),
}
OPS = ('__wrap_esp_vorbis_dec_open', '__wrap_esp_vorbis_dec_decode',
       'esp_vorbis_dec_reset', 'esp_vorbis_dec_close')
WRAPPERS = (*OPS, '__wrap_esp_ogg_parse_frame', '__wrap_esp_es_parse_frame',
            '__wrap_media_lib_module_realloc')
RX_CALLS = {
    'wlanif_input': '__wrap_esp_pbuf_allocate',
    'esp_pbuf_free': '__wrap_esp_netif_free_rx_buffer',
    '__wrap_esp_pbuf_allocate': 'esp_pbuf_allocate',
    '__wrap_esp_netif_free_rx_buffer': 'esp_netif_free_rx_buffer',
    'decoder_task': 'rx_buffer_diagnostic_poll',
}


def verify(build, objdump, output):
    result = verify_aac(build, objdump)
    if 'CONFIG_YORADIO_VORBIS_REPAIR=y' not in (build/'sdkconfig').read_text():
        raise ValueError('Vorbis repair disabled')
    elf_path = build/'yoradio_esp32c3_oled_native.elf'
    with elf_path.open('rb') as stream:
        elf = ELFFile(stream)
        symbols = [s for s in elf.get_section_by_name('.symtab').iter_symbols()
                   if s['st_shndx'] != 'SHN_UNDEF']
        named = {s.name: s for s in symbols}
        if any(name not in named for name in WRAPPERS):
            raise ValueError('Missing repaired/original callback')
        expected = struct.pack('<4I', *(named[n]['st_value'] for n in OPS))
        matched = []
        for symbol in symbols:
            if not symbol.name.startswith('operations.') or symbol['st_size'] != len(expected):
                continue
            section = elf.get_section(symbol['st_shndx'])
            start = symbol['st_value'] - section['sh_addr']
            if section.data()[start:start+len(expected)] == expected:
                matched.append(symbol.name)
        if len(matched) != 1:
            raise ValueError('Missing/ambiguous repaired Vorbis callback table')
        result['vorbis_operations'] = dict(table=matched[0], callbacks=list(OPS))
        result['sections'] = {s.name: s['sh_size'] for s in elf.iter_sections()
                              if s.name in ('.iram0.text', '.dram0.data', '.dram0.bss',
                                            '.flash.text', '.flash.rodata')}
        result['tls_sections'] = {s.name: s['sh_size'] for s in elf.iter_sections()
                                  if s['sh_flags'] & 0x400}
    output.mkdir(parents=True, exist_ok=True)
    for caller, callees in CALLS.items():
        code = subprocess.check_output([str(objdump), '-d', '--disassemble='+caller,
                                        str(elf_path)], text=True)
        for callee in callees:
            if not re.search(r'\b(?:j|jal|jalr)\s+[^\n]*<'+re.escape(callee)+r'>', code):
                raise ValueError('Missing linked call: '+caller+' -> '+callee)
        (output/(caller+'.asm')).write_text(code)
    result['vorbis_linked_calls'] = CALLS
    result['source_sha256'] = {}
    main = ROOT/'idf/esp32c3-oled-native/main'
    sources = [main/name for name in ('CMakeLists.txt', 'Kconfig.projbuild', 'audio_service.c',
               'vorbis_repair_abi.h', 'decoder_registration.c', 'decoder_registration.h', 'decoder_resources.h')]
    sources += sorted((main/'vorbis_repair').glob('*'))
    sources += [ROOT/path for path in (
        'idf/esp32c3-oled-native/components/custom_flac/custom_flac_adapter.cpp',
        'idf/esp32c3-oled-native/components/custom_flac/custom_flac_adapter.h',
        'idf/components/custom_legacy_codecs/custom_legacy_adapter.cpp',
        'idf/components/custom_legacy_codecs/custom_legacy_adapter.h',
        'yoRadio/src/audioI2S/flac_decoder/flac_decoder.cpp',
        'yoRadio/src/audioI2S/flac_decoder/flac_decoder.h',
        'yoRadio/src/audioI2S/CodecMemoryArena.cpp')]
    if 'CONFIG_YORADIO_RX_BUFFER_DIAGNOSTICS=y' in (build/'sdkconfig').read_text():
        for caller, callee in RX_CALLS.items():
            code = subprocess.check_output([str(objdump), '-d', '--disassemble='+caller,
                                            str(elf_path)], text=True)
            if not re.search(r'\b(?:j|jal|jalr)\s+[^\n]*<'+re.escape(callee)+r'>', code):
                raise ValueError('Missing RX ownership hook: '+caller+' -> '+callee)
            (output/(caller+'.asm')).write_text(code)
        result['rx_ownership_calls'] = RX_CALLS
        sources += [main/'rx_buffer_diagnostic.c', main/'rx_buffer_diagnostic.h']
    for source in sources:
        name = source.relative_to(ROOT)
        destination = output/'sources'/name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
        result['source_sha256'][name.as_posix()] = sha(source)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build', type=Path, required=True)
    parser.add_argument('--objdump', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--artifact', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or args.artifact.exists():
        raise ValueError('Choose new evidence and development artifact directories')
    if not args.artifact.resolve().is_relative_to((ROOT/'firmware/development').resolve()):
        raise ValueError('Artifact must be under firmware/development')
    result = verify(args.build, args.objdump, args.output)
    result.update(evidence=args.output.as_posix(), qualification='Build verified; hardware not tested')
    payload = json.dumps(result, indent=2)+'\n'
    (args.output/'build.json').write_text(payload)
    args.artifact.mkdir(parents=True)
    for source, destination in [('yoradio_esp32c3_oled_native.bin','app.bin'), ('sdkconfig','sdkconfig')]:
        shutil.copyfile(args.build/source, args.artifact/destination)
    (args.artifact/'manifest.json').write_text(payload)
    print(json.dumps({k: result[k] for k in ('app_bytes','sections','tls_sections','vorbis_operations')}))


if __name__ == '__main__':
    main()
