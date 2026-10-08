import hashlib, json
from pathlib import Path
from elftools.elf.elffile import ELFFile

root = Path(__file__).resolve().parent
path = Path('idf/esp32c3-oled-native/build-idf-6.1-r9a97f6c54ec6-rx6-reserve-floor/yoradio_esp32c3_oled_native.elf')
with path.open('rb') as stream:
    elf = ELFFile(stream)
    sections = {s.name: s['sh_size'] for s in elf.iter_sections()
                if s.name.startswith(('.iram0.', '.dram0.'))}
payload = sum(sections.get(n, 0) for n in ('.iram0.text', '.dram0.data', '.dram0.bss'))
physical = sum(n for k, n in sections.items() if k != '.dram0.dummy')
result = dict(variant='rx6-reserve-floor', elf_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
              sections=sections, static_payload_bytes=payload,
              static_sram_with_padding_bytes=physical,
              note='.dram0.dummy aliases IRAM and is excluded to avoid counting the same SRAM twice.')
(root/'memory-layout.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result, indent=2))
