"""Config/image/ABI foundation only; does not claim final SDK/runtime acceptance."""
import hashlib
import json
import runpy
from elftools.elf.elffile import ELFFile
from esptool.bin_image import LoadFirmwareImage
from common import BASE, ROOT, PROFILE, guard, load, pin, write_new
from common_reviewed import config_proof

def main():
    p = guard()
    compiled, fixture = PROFILE / 'compiled', PROFILE / 'fixture'
    config = config_proof(compiled)
    assert (fixture / 'config/sdkconfig.json').read_bytes() == (compiled / 'config/sdkconfig.json').read_bytes()
    before_image = ROOT / '.build/cpbuf24/sdk/legacy/fixture/yoradio_cyd2usb_native.bin'
    image_path = fixture / 'yoradio_cyd2usb_native.bin'
    body = image_path.read_bytes(); image = LoadFirmwareImage('esp32', body)
    assert image.chip_id == image.ROM_LOADER.IMAGE_CHIP_ID and image.calculate_checksum() == image.checksum
    assert image.append_digest and image.stored_digest == image.calc_digest and len(body) == image.data_length + 32
    assert body[:24] == before_image.read_bytes()[:24], 'Chip/header geometry changed'
    elf_path = compiled / 'yoradio_cyd2usb_native.elf'
    assert image.segments[0].data[144:176].hex() == pin(elf_path)['sha256']
    old_image = LoadFirmwareImage('esp32', before_image.read_bytes())
    new_desc, old_desc = bytearray(image.segments[0].data[:256]), bytearray(old_image.segments[0].data[:256])
    new_desc[144:176] = old_desc[144:176] = bytes(32)
    assert new_desc == old_desc, 'A/B descriptor version/date metadata changed'
    exporter = runpy.run_path(str(ROOT / 'tools/export_cyd_production.py'))
    slots = exporter['partition_slots']((fixture / 'partition_table/partition-table.bin').read_bytes(), 4 * 1024**2)
    assert len(slots) == 2 and all(slot['bytes'] == 0x1b0000 and len(body) < slot['bytes'] for slot in slots)
    layouts = set()
    with elf_path.open('rb') as stream:
        elf = ELFFile(stream)
        assert elf['e_machine'] == 'EM_XTENSA' and elf.elfclass == 32 and elf.little_endian
        for cu in elf.get_dwarf_info().iter_CUs():
            for die in cu.iter_DIEs():
                attrs = die.attributes
                if die.tag != 'DW_TAG_structure_type' or 'DW_AT_name' not in attrs or attrs['DW_AT_name'].value != b'tcp_pcb' or 'DW_AT_byte_size' not in attrs: continue
                members = {}
                for child in die.iter_children():
                    a = child.attributes
                    if child.tag != 'DW_TAG_member' or 'DW_AT_name' not in a: continue
                    name = a['DW_AT_name'].value.decode()
                    if name in ('snd_buf', 'snd_queuelen', 'unsent_oversize', 'bytes_acked', 'unsent', 'unacked'):
                        members[name] = a['DW_AT_data_member_location'].value
                layouts.add((attrs['DW_AT_byte_size'].value, tuple(sorted(members.items()))))
        predicted = p['predicted_candidate_tcp_pcb']
        assert layouts == {(predicted['bytes'], tuple(sorted(predicted['members'].items())))}, 'Candidate tcp_pcb ABI differs from the predicted source layout; retain and investigate'
        table = elf.get_section_by_name('.symtab')
        owners = {}
        for name, size in (('s_pbuf_failures', 128), ('s_pbuf_failure_lock', 8)):
            symbol, = table.get_symbol_by_name(name)
            section = elf.get_section(symbol['st_shndx'])
            assert symbol['st_size'] == size and section.name == '.dram0.data'
            owners[name] = dict(bytes=size, address=symbol['st_value'], section=section.name)
        value = lambda name: table.get_symbol_by_name(name)[0]['st_value']
        assert value('_rtc_slow_length') == 104
        geometry = dict(rtc_used_bytes=104, rtc_reserved_bytes=24, rtc_free_bytes=8064,
                        heap_start=value('_heap_start'), dram_data_bytes=elf.get_section_by_name('.dram0.data')['sh_size'],
                        dram_bss_bytes=elf.get_section_by_name('.dram0.bss')['sh_size'])
    old_commands = load(PROFILE / 'baseline/compile_commands.json')
    commands = load(compiled / 'compile_commands.json')
    assert len(commands) == len(old_commands), 'Unexpected compilation unit count'
    write_new(PROFILE / 'foundation-qualification.json', dict(
        foundation_passed=True, final_qualification_passed=False, source_commit=p['source_commit'], backend='legacy',
        physical_tested=False, native_run=False, image=pin(image_path), elf=pin(elf_path), config=config,
        tcp_pcb_layout=dict(bytes=predicted['bytes'], members=predicted['members'], unsent_oversize_absent=True, measured=True),
        owners=owners, geometry=geometry, ota_slots=slots, source_units=len(commands),
        pending=['Whole candidate PCM/probe and SDK tcp_out/pbuf Clang checks with exact configuration',
                 'Actual linked allocator-call proof using candidate SDK reference objects, not frozen old-config references',
                 'Static wrapper/dump/PCM frame and heap-region comparison against baseline',
                 'Strict full TLS/HE-AAC/PCM/WebUI/two-peer run including final post-close health',
                 'If legacy is promising, independently build/qualify PDM and continuous before adoption'],
        scope='Finite diagnostic A/B foundation. No production-default promotion or throughput/fragmentation claim.'))
    print(json.dumps(dict(foundation_passed=True, final_qualification_passed=False, image_bytes=len(body))))

if __name__ == '__main__':
    main()
