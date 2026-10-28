"""Qualify the actual linked NVS recovery closure and its exact build-local source patch."""
import argparse
import json
from pathlib import Path

from patch_nvs_page import FIXES, patch, sha
from reverse.nvs_record_linkage import archive_objects, definitions, EXTERNAL
from reverse.factory_nvs import TABLE, native_address
from reverse.nothrow_linkage import LinkedRuntime
from reverse.rv32_link_match import model, match


def verify(elf, app, library, original, generated, report):
    """Require complete source-object matches and resolve every named algorithm call."""
    if generated != patch(original):
        raise ValueError('Generated NVS source differs from the qualified corrections')
    expected = dict(schema='small-tv-nvs-recovery-v1', source_sha256=sha(original),
                    generated_sha256=sha(generated), generator_sha256=sha(Path(__file__).with_name('patch_nvs_page.py').read_bytes()),
                    fixes=list(FIXES), shared_sdk_modified=False)
    if report != expected:
        raise ValueError('NVS patch report differs from source')
    linked = LinkedRuntime(elf, app); parts = archive_objects(library)
    available = definitions(parts); functions = {}; external = {}; queue = [TABLE]
    gp = linked.symbol('__global_pointer$')['st_value']
    while queue:
        name = queue.pop(0)
        if name in functions or name in external:
            continue
        if name not in available:
            if name not in EXTERNAL:
                raise ValueError('Unqualified NVS recovery algorithm: '+name)
            external[name] = native_address(linked, name)
            continue
        symbol, code = linked.body(name); accepted = []
        for member in available[name]:
            try:
                row = match(model(parts[member], name), code, symbol['st_value'], gp)
            except ValueError:
                continue
            if row['linked_bytes'] != symbol['st_size']:
                raise ValueError('Incomplete linked NVS body')
            row.update(member=member, object_sha256=sha(parts[member]), code_sha256=sha(code))
            accepted.append(row)
        if not accepted:
            raise ValueError('No full source-object match for NVS body: '+name)
        row = accepted[0]; row['matching_members'] = sorted(r['member'] for r in accepted)
        functions[name] = row
        for edge in row['symbol_bindings']:
            if edge['kind'] != 'call':
                continue
            if edge['address'] != native_address(linked, edge['name']):
                raise ValueError('NVS call reaches an unexpected symbol')
            queue.append(edge['name'])
    if external.get('esp_rom_crc32_le') != 0x400007fc:
        raise ValueError('NVS CRC ROM entry changed')
    return dict(passed=True, schema='small-tv-nvs-recovery-linkage-v1', elf_sha256=sha(elf),
                app_sha256=sha(app), archive_sha256=sha(library), patch=expected,
                objects={k: sha(v) for k, v in parts.items()},
                functions=list(functions.values()), externals=external,
                complete_direct_recovery_call_closure=True, semantic_tests_executed=False)


def main():
    """Run after linking and before archiving the candidate firmware."""
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('elf', 'app', 'nvs', 'source', 'generated', 'patch-report', 'output'):
        parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('Preserve previous NVS linkage evidence')
    result = verify(args.elf.read_bytes(), args.app.read_bytes(), args.nvs.read_bytes(),
                    args.source.read_bytes(), args.generated.read_bytes(), json.loads(args.patch_report.read_bytes()))
    args.output.write_text(json.dumps(result, indent=2)+'\n', encoding='utf8', newline='\n')
    print(json.dumps(dict(passed=True, functions=len(result['functions']))))


if __name__ == '__main__':
    main()
