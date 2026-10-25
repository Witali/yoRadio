"""Decode only bounded numeric OSI/PM metadata, never stack or packet payloads."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from audit_factory_xrefs import sha


def decode(read, layout):
    """Use the qualified addresses; do not follow an unexpected guest pointer."""
    prior = layout['prior']
    word = lambda address: int.from_bytes(read(address, 4), 'little')
    pm, cfg = prior['g_pm'], prior['g_pm_cfg']
    pointer = word(prior['osi_pointer'])
    result = dict(osi_pointer=pointer, post_callback=word(layout['post_callback_slot']),
                  pm_bytes={str(offset): read(pm + offset, 1)[0] for offset in (1,14,15,16,488)},
                  pm_word36=word(pm + 36), config_enabled52=read(cfg + 52, 1)[0],
                  config_period72=int.from_bytes(read(cfg + 72, 2), 'little'),
                  config_fallback28=word(cfg + 28), config_adjustment56=word(cfg + 56),
                  timer_word4=word(pm + 492 + 4), timer_word16=word(pm + 492 + 16))
    result['osi_table_sha256'] = (sha(read(pointer, 480))
                                 if pointer == prior['osi_table']['address'] else None)
    return result
