"""Independently replay typed AP peer observations and HTTP handle lifetime."""
import copy
import hashlib
import io
import struct

from elftools.elf.elffile import ELFFile
from network_event_abi import FIELDS


def verify_abi(report, obj, source):
    """Read the actual RV32 constant array rather than trusting JSON offsets."""
    assert report['passed'] and report['production_object_unchanged']
    assert hashlib.sha256(obj).hexdigest() == report['object_sha256']
    assert hashlib.sha256(source).hexdigest() == report['source_sha256']
    elf = ELFFile(io.BytesIO(obj))
    assert elf.elfclass == 32 and elf.little_endian
    assert elf['e_type'] == 'ET_REL' and elf['e_machine'] == 'EM_RISCV'
    symbols = [s for s in elf.get_section_by_name('.symtab').iter_symbols()
               if s.name == 'tv_wifi_event_wire']
    assert len(symbols) == 1
    symbol = symbols[0]; section = elf.get_section(symbol['st_shndx'])
    begin = symbol['st_value'] - section['sh_addr']
    data = section.data()[begin:begin+symbol['st_size']]
    assert len(data) == 4*len(FIELDS)
    assert dict(zip(FIELDS, struct.unpack('<'+'I'*len(FIELDS), data))) == report['wire']


def validate(report, wire, read_code, base_value):
    """Require SDK peers/HTTP/handles; FIXED_TEST: an AID belongs to an association."""
    assert report['passed'] and report['owners_stopped']
    assert not any(report[key] for key in ('network_lifecycle_complete',
        'all_functionality_verified', 'lcd_acceptance', 'rf_acceptance',
        'physical_hardware_tested'))
    assert report['wire'] == wire
    factory = report['firmware'] == 'original'
    assert factory or report['firmware'] == 'reconstructed'
    events = report['events']; active = set(); aids = {}; end = 0
    primary, secondary = '52:54:00:43:00:02', '52:54:00:43:00:03'
    departure = report.get('departure','secondary')
    assert departure in ('primary','secondary')
    survivor = secondary if departure == 'primary' else primary
    expected = [{primary}, {primary, secondary}, {survivor}, set(), {survivor}]
    assert len(report['phases']) == len(expected)
    for phase, wanted in zip(report['phases'], expected):
        begin, finish = phase['event_range']
        assert begin == end < finish <= len(events); end = finish
        for event in events[begin:finish]:
            name = event['function']; assert report['entries'][name] == event['pc']
            assert hashlib.sha256(read_code(event['pc'], 2)).hexdigest() == event['instruction_sha256']
            assert event['return_pc'] != event['pc'] and event['return_value'] >= 0
            if 'kind' not in event: continue
            assert name == 'wifi_event' and event['base'] == base_value
            kind = event['kind']; assert kind in ('connected', 'disconnected')
            assert event['event_id'] == wire[kind+'_id']
            raw = bytes.fromhex(event['event_data_hex'])
            assert len(raw) == (7 if factory else wire[kind+'_bytes'])
            offset = 0 if factory else wire[kind+'_mac']
            mac = ':'.join(f'{b:02x}' for b in raw[offset:offset+6])
            assert mac == event['mac'] and mac in (primary, secondary)
            aid_offset = 6 if factory else wire[kind+'_aid']
            aid = raw[aid_offset]
            assert 1 <= aid <= 3
            if not factory and kind == 'disconnected':
                reason = wire['disconnected_reason']
                assert int.from_bytes(raw[reason:reason+wire['reason_bytes']], 'little') == 3
            if kind == 'connected':
                # After the last peer leaves, the SDK can reuse AID 1 for a
                # different MAC. Require uniqueness only among active peers.
                assert mac not in active and aid not in aids.values()
                active.add(mac); aids[mac] = aid
            else:
                assert mac in active and aids.pop(mac) == aid
                active.remove(mac)
        assert set(phase['active_peers']) == active == wanted
        assert phase['mask'] == sum(1 << i for i, mac in enumerate((primary,secondary)) if mac in wanted)
        clients = phase['model_clients']
        assert len(clients) == 3
        for i, peer in enumerate(clients):
            assert peer['index'] == i and peer['mac'] == f'52:54:00:43:00:{2+i:02x}'
            assert peer['online'] == bool(phase['mask'] & (1 << i))
        if wanted:
            assert phase['http']['status'] == 200 and phase['http']['body'] == '0'
            relays = {r['mac']:r for r in phase['relay_ready_clients']}
            assert len(relays) == 3
            addresses = []
            for mac in wanted:
                relay = relays[mac]
                assert relay['online'] and relay['model_state'] == 5
                assert relay['offered_ipv4'] != '0.0.0.0'
                addresses.append(relay['offered_ipv4'])
            assert len(set(addresses)) == len(addresses)
        else: assert 'http' not in phase
    assert end == len(events)
    starts = [e for e in events if e['function'] == 'httpd_start']
    stops = [e for e in events if e['function'] == 'httpd_stop']
    handles = report['server_handles']
    if factory:
        assert len(starts) == 3 and len(stops) == 2 and len(handles) == 3
        assert handles[0] and handles[1:] == [0,0]
        assert [e['tracked_server_handle'] for e in starts] == handles
        assert report['phases'][0]['tracked_server_handle'] == handles[0]
        assert all(p['tracked_server_handle'] == 0 for p in report['phases'][1:])
        assert all(e['tracked_server_handle'] == 0 for e in stops)
        assert report['factory_loses_original_server_handle']
    else:
        assert len(starts) == len(handles) == 1 and handles[0] and not stops
        assert starts[0]['return_value'] == 0 and starts[0]['server_handle'] == handles[0]
    return dict(firmware=report['firmware'], departure=departure,
                sdk_peer_events=sum('kind' in e for e in events),
                http_checks=4, starts=len(starts), stops=len(stops), owners_stopped=True)


def rejection_checks(report, wire, read_code, base_value):
    """Prove that metadata-only peers, missing ACKs and lost evidence fail replay."""
    rejected = []
    for case in ('peer-bytes', 'event-kind', 'model-ready', 'http', 'handle', 'not-reaped'):
        wrong = copy.deepcopy(report)
        if case == 'peer-bytes':
            next(e for e in wrong['events'] if e.get('mac','').endswith(':03'))['event_data_hex'] = '00'*7
        elif case == 'event-kind':
            next(e for e in wrong['events'] if e.get('kind') == 'disconnected')['kind'] = 'connected'
        elif case == 'model-ready':
            wrong['phases'][1]['relay_ready_clients'][1]['model_state'] = 7
        elif case == 'http': wrong['phases'][2]['http']['status'] = 500
        elif case == 'handle': wrong['server_handles'][0] = 0
        else: wrong['owners_stopped'] = False
        try: validate(wrong, wire, read_code, base_value)
        except AssertionError: rejected.append(case)
        else: raise AssertionError('Unsafe network evidence accepted: '+case)
    return rejected
