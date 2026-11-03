"""Bind the BSS length guard to the actual C2 association and registration paths."""
import argparse
import io
import json
from pathlib import Path

from elftools.elf.elffile import ELFFile
from elftools.elf.relocation import RelocationSection
from audit_factory_xrefs import sha
from reverse.elf_archive import members
from reverse.nothrow_linkage import LinkedRuntime
from reverse.bss_assoc import complete_association, return_sites, selected
from reverse.wifi_producers import NET_SHA

SDK_NAME = 'ieee80211_set_bss_max_idle_period'
REPLACEMENT = 'small_tv_wifi_set_bss_max_idle_period'


def verify(elf, app, libraries, own):
    """Reject bypasses, changed SDK inputs and incomplete code/data bindings."""
    linked = LinkedRuntime(elf, app)
    replacement = linked.symbol(REPLACEMENT)
    aliases = [s for s in linked.symbols if s.name == SDK_NAME and s['st_value']]
    if len(aliases) != 1 or aliases[0]['st_value'] != replacement['st_value']:
        raise ValueError('BSS definition redirect is not active')
    net = (libraries / 'libnet80211.a').read_bytes()
    if sha(net) != NET_SHA['native']:
        raise ValueError('Requalify the BSS SDK archive')
    parts = dict(members(net))
    references = []
    for archive in sorted(libraries.glob('*.a')):
        for member, data in members(archive.read_bytes()):
            if data[:4] != b'\x7fELF':
                continue
            obj = ELFFile(io.BytesIO(data))
            for section in obj.iter_sections():
                if not isinstance(section, RelocationSection):
                    continue
                if not obj.get_section(section['sh_info'])['sh_flags'] & 2:
                    continue
                symbols = obj.get_section(section['sh_link'])
                for r in section.iter_relocations():
                    if symbols.get_symbol(r['r_info_sym']).name == SDK_NAME:
                        references.append(dict(archive=archive.name, member=member,
                            section=obj.get_section(section['sh_info']).name,
                            offset=r['r_offset'], type=r['r_info_type']))
    if len(references) != 1 or any((r['archive'], r['member'], r['section'], r['type']) !=
            ('libnet80211.a', 'ieee80211_sta.o', '.text.sta_recv_assoc', 18) for r in references):
        raise ValueError('Requalify additional BSS setter references')
    locals_ = {}
    association = complete_association(linked, parts['ieee80211_sta.o'], 'sta_recv_assoc', locals_)
    setter = complete_association(linked, own, REPLACEMENT, locals_)
    setter['name'] = SDK_NAME
    getter = complete_association(linked, parts['ieee80211_sta.o'], 'sta_is_bss_max_idle_enabled', locals_)
    management = complete_association(linked, parts['ieee80211_sta.o'], 'sta_recv_mgmt', locals_)
    registration = complete_association(linked, parts['ieee80211_api.o'], 'net80211_funcs_init', locals_)
    target = replacement['st_value']
    if selected(association['symbol_bindings'], SDK_NAME)['address'] != target:
        raise ValueError('Association bypasses the BSS guard')
    for owner in (management, registration):
        if selected(owner['symbol_bindings'], 'sta_recv_assoc')['address'] != int(association['start'], 0):
            raise ValueError('Wrong association ingress')
    feature = [b for b in getter['symbol_bindings'] if b['kind'] == 'data']
    if len(feature) != 1:
        raise ValueError('Ambiguous BSS feature word')
    table = linked.symbol('g_wifi_osi_funcs')['st_value']
    if int.from_bytes(linked.read(table, 4), 'little') != 9:
        raise ValueError('Requalify the BSS OSI ABI')
    noop = int.from_bytes(linked.read(table + 412, 4), 'little')
    code = linked.read(noop, 4, True)
    if code != bytes.fromhex('01458280') or linked.symbol('coex_wifi_release_wrapper')['st_value'] != noop:
        raise ValueError('Requalify association coexistence backend')
    noop_row = dict(name='osi-412-noop', start=hex(noop), end=hex(noop + 4),
                    linked_bytes=4, linked_code_sha256=sha(code))
    layout = dict(functions=[association, setter, getter, management, registration, noop_row],
        gp=linked.symbol('__global_pointer$')['st_value'], menuconfig=feature[0]['address'],
        g_ic=selected(association['symbol_bindings'], 'g_ic')['address'],
        after_bss=return_sites(association, target), management_entry=int(management['start'], 0),
        after_assoc=return_sites(management, int(association['start'], 0)),
        hmac_counter=selected(management['symbol_bindings'], 'g_hmac_cnt')['address'],
        osi_pointer=selected(management['symbol_bindings'], 'g_osi_funcs_p')['address'],
        osi_table=table, osi_412_target=noop)
    return dict(schema='small-tv-wifi-bss-linkage-v1', passed=True, layout=layout,
        elf_sha256=sha(elf), app_sha256=sha(app), replacement_object_sha256=sha(own),
        sdk_archive_sha256=sha(net), sdk_references=references,
        entire_association_executed=False, external_rx_reachability_proved=False,
        physical_hardware_tested=False, whole_image_completeness_proved=False)


def main():
    """Produce a fresh guard report before a production build can be archived."""
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('elf', 'app', 'sdk-libraries', 'object', 'output'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    files = [args.elf, args.app, args.object, *sorted(args.sdk_libraries.glob('*.a'))]
    if args.output.exists() or args.output.resolve() in [p.resolve() for p in files]:
        raise ValueError('Preserve BSS inputs and existing reports')
    pins = {str(p.resolve()): sha(p.read_bytes()) for p in files}
    result = verify(args.elf.read_bytes(), args.app.read_bytes(), args.sdk_libraries, args.object.read_bytes())
    if any(sha(Path(p).read_bytes()) != digest for p, digest in pins.items()):
        raise ValueError('BSS inputs changed during qualification')
    result.update(inputs_sha256=pins, inputs_unchanged=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(dict(passed=True, sdk_references=len(result['sdk_references']))))


if __name__ == '__main__':
    main()
