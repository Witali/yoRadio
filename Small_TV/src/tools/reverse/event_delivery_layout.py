"""Qualify factory event-delivery metadata and the successful startup teardown slice."""
import io

from elftools.elf.elffile import ELFFile

from audit_factory_xrefs import Image, sha
from reverse.rv32_link_match import branch_target, link_register
from reverse.timer_event11_match import NATIVE_SHA, unique


def qualify(factory, native):
    """Bind every read/breakpoint to original bytes, not a newer SDK layout assumption."""
    image = Image(factory)
    if sha(native) != NATIVE_SHA: raise ValueError('Unexpected native event-lifetime ELF')
    elf = ELFFile(io.BytesIO(native)); symbols = list(elf.get_section_by_name('.symtab').iter_symbols())
    regions = {
        'handler_execute': (0x420aeb72, 50),
        'event_post_wrapper': (0x420b19b4, 28),
        'default_event_post': (0x420aeb06, 42),
        'default_event_unregister': (0x420aeae0, 38),
        'startup_tail_with_errors': (0x4200cd90, 144),
        'current_task_leaf': (0x4038a1b8, 10),
    }
    code = {name: dict(start=start, bytes_hex=image.read(start, size, True).hex())
            for name, (start, size) in regions.items()}
    assert image.read(0x4038a1b8, 10, True).hex() == 'b747cc3f03a507948280'
    assert image.read(0x420aeb8a, 20, True).hex() == '9841032807009047cc4348430298b24041018280'
    for address, target in ((0x4200cdae, 0x420aeae0), (0x4200cdc0, 0x420aeae0),
                            (0x420aeb20, 0x420af6f2), (0x420b19be, 0x420aeb06),
                            (0x420b19ca, 0x420aeb06)):
        raw = image.read(address, 4, True)
        assert link_register(raw) == 1 and branch_target(raw, address) == target
    assert int.from_bytes(image.read(0x3fcb459c+180, 4), 'little') == 0x420b19b4
    # These are the actual lw count/capacity/item-width accesses in queue send.
    assert image.read(0x40387afe, 4, True).hex() == '03298403'
    assert image.read(0x40387ab4, 2, True).hex() == '5c5c'
    assert image.read(0x40387a90, 2, True).hex() == '3c41'
    # The dedicated-task send path loads task8/queue4 from the same loop object.
    assert image.read(0x420af72e, 2, True).hex() == '0444'
    assert image.read(0x420af744, 2, True).hex() == '4840'
    native_names = ('wifi_event', 'connected', 'station_retries', 'station_failed', 'scanning',
                    'station_configured', 'last_station_address', 'WIFI_EVENT', 'IP_EVENT', 'esp_wifi_connect')
    return dict(schema='factory-event-delivery-layout-v1', code=code,
        factory=dict(default_loop=0x3fcc3c04, current_task=0x3fcc3940, loop_prefix=24,
                     queue_offset=4, task_offset=8, running_offset=12, mutex_offset=16,
                     queue_prefix=68, count_offset=56, length_offset=60, item_offset=64,
                     post_bytes=16, callback=0x4200c602,
                     wifi_base=int.from_bytes(image.read(0x3c0f1eb8,4),'little'),
                     ip_base=int.from_bytes(image.read(0x3c0f1848,4),'little')),
        native={name:dict(address=unique(symbols,name)['st_value'],size=unique(symbols,name)['st_size']) for name in native_names},
        factory_elf_sha256=sha(factory), native_elf_sha256=sha(native),
        full_startup_function_proved=False, whole_image_completeness_proved=False, physical_hardware_tested=False)
