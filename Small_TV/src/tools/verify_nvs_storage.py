"""Require the complete linked Storage closure and a consistent generated NVS component."""
import argparse
import json
from pathlib import Path

from patch_nvs_page import sha
from prepare_nvs_component import sources, report as overlay_report
from reverse.nvs_storage_linkage import archive_objects, ROOTS, EXTERNAL
from reverse.nvs_record_linkage import definitions
from reverse.nothrow_linkage import LinkedRuntime
from reverse.factory_nvs import native_address
from reverse.rv32_link_match import model, match


def verify(elf, app, archive, component, overlay, saved_overlay, commands):
    """Check every generated input and named algorithm call before archiving a build."""
    generated, original = sources(component)
    if saved_overlay != overlay_report(generated, original): raise ValueError('NVS overlay report differs')
    if {p.name for p in overlay.iterdir()} != set(generated) or any((overlay/name).read_bytes() != value for name, value in generated.items()):
        raise ValueError('NVS generated component differs')
    entries = [row for row in commands if '__idf_nvs_flash.dir' in row.get('command', '')]
    expected = {(overlay/name).resolve() for name in generated if Path(name).suffix in ('.c', '.cpp')}
    if len(entries) != len(expected) or {Path(row['file']).resolve() for row in entries} != expected:
        raise ValueError('NVS translation units mix original and generated headers')
    linked = LinkedRuntime(elf, app); objects = archive_objects(archive); available = definitions(objects)
    seen = {}; external = {}; queue = list(ROOTS); gp = linked.symbol('__global_pointer$')['st_value']
    while queue:
        name = queue.pop(0)
        if name in seen or name in external: continue
        if name not in available:
            if name not in EXTERNAL: raise ValueError('Unqualified Storage build algorithm: '+name)
            external[name] = native_address(linked, name); continue
        symbol, code = linked.body(name); rows = []
        for member in available[name]:
            try: row = match(model(objects[member], name), code, symbol['st_value'], gp)
            except ValueError: continue
            if row['linked_bytes'] != len(code): raise ValueError('Incomplete linked Storage build body')
            row.update(member=member, object_sha256=sha(objects[member]), code_sha256=sha(code)); rows.append(row)
        if not rows: raise ValueError('No complete Storage build source match: '+name)
        row = rows[0]
        for edge in row['symbol_bindings']:
            if edge['kind'] == 'call':
                if edge['address'] != native_address(linked, edge['name']): raise ValueError('Wrong Storage build callee')
                queue.append(edge['name'])
        # The full relocation match is performed above; keep build metadata concise.
        seen[name] = {key: row[key] for key in ('name', 'start', 'linked_bytes', 'member', 'object_sha256', 'code_sha256')}
    if external.get('esp_rom_crc32_le') != 0x400007fc: raise ValueError('Storage build CRC ROM changed')
    return dict(schema='small-tv-nvs-storage-linkage-v1', passed=True, elf_sha256=sha(elf), app_sha256=sha(app),
                archive_sha256=sha(archive), overlay=saved_overlay,
                source_objects={k: sha(v) for k, v in objects.items()}, functions=list(seen.values()), externals=external,
                local_translation_units=len(entries), complete_direct_init_read_closure=True,
                semantic_tests_executed=False, physical_hardware_tested=False)


def main():
    """Save qualification only for the exact linked ESP image and freshly checked overlay."""
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('elf', 'app', 'nvs', 'component', 'overlay', 'overlay-report', 'commands', 'output'):
        parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists(): raise ValueError('Preserve Storage linkage evidence')
    value = verify(args.elf.read_bytes(), args.app.read_bytes(), args.nvs.read_bytes(), args.component,
                   args.overlay, json.loads(args.overlay_report.read_bytes()), json.loads(args.commands.read_bytes()))
    args.output.write_text(json.dumps(value, indent=2)+'\n', encoding='utf8', newline='\n')
    print(json.dumps(dict(passed=True, functions=len(value['functions']), local_translation_units=value['local_translation_units'])))


if __name__ == '__main__': main()
