"""Rebind the audited Wi-Fi PM bodies to the saved NVS-fixed production pair."""
from copy import deepcopy

from audit_factory_xrefs import sha
from reverse.nothrow_linkage import LinkedRuntime
from reverse.rv32_link_match import model, match
from reverse.timer_event11_match import adapter_table, objects, unique
from reverse.timer_keep_alive import qualify as historical_qualify

NATIVE_SHA = 'da1ed0ce8c3af0f29d7851d8ac4e0c96dfe52ab9438df3274c8f6b09eaaf49c1'
APP_SHA = '8758bd09c80e707e400ec6059b39cdcfde05b71daa297cfc4fd36ac35dfbcf1a'


def qualify(factory, reference, native, app, old_pp, new_pp):
    """Keep historical identity guards and independently match every current body.

    The older ELF is a reference input, never a substitute for the current ELF.
    Object-local data anchors are checked across all nine native bodies; public
    calls and data additionally have to resolve to their unique linked symbols.
    """
    if sha(native) != NATIVE_SHA or sha(app) != APP_SHA:
        raise ValueError('Unexpected TIM production pair')
    previous = historical_qualify(factory, reference, old_pp, new_pp)
    linked = LinkedRuntime(native, app)
    def symbol(name):
        """Include the SDK's absolute ROM globals, rejecting duplicate definitions."""
        return unique(linked.symbols, name)
    layout = deepcopy(previous['layouts']['native'])
    base, parts = layout['prior'], objects(new_pp, 'native')
    gp = symbol('__global_pointer$')['st_value']
    rows, anchors = {}, {}
    all_rows = [*base['functions'], base['configuration_function'], *layout['functions']]
    for old in all_rows:
        name = old['name']
        source = parts['pp_timer.o' if name == 'pp_timer_keep_alive' else 'pm.o']
        function, code = linked.body(name)
        row = match(model(source, name), code, function['st_value'], gp)
        if row['linked_bytes'] != function['st_size']:
            raise ValueError('Incomplete current TIM chain body')
        row['linked_code_sha256'] = sha(code)
        for binding in row['symbol_bindings']:
            if binding['kind'] == 'call' or binding['binding'] != 'STB_LOCAL':
                if symbol(binding['name'])['st_value'] != binding['address']:
                    raise ValueError('Wrong current TIM chain symbol')
            if binding['binding'] == 'STB_LOCAL':
                key = (binding['name'], binding['section'])
                if key in anchors and anchors[key] != binding['address']:
                    raise ValueError('Inconsistent current PM object anchor')
                anchors[key] = binding['address']
                if binding['name'] == '.LANCHOR0' and binding['address'] != symbol('g_pm')['st_value']:
                    raise ValueError('Different current PM state')
        rows[name] = row
    base['functions'] = [rows[row['name']] for row in base['functions']]
    base['configuration_function'] = rows[base['configuration_function']['name']]
    layout['functions'] = [rows[row['name']] for row in layout['functions']]
    for name in ('g_pm', 'g_pm_cfg'):
        entry = symbol(name)
        if entry['st_size'] != base[name + '_bytes']:
            raise ValueError('Changed current PM data geometry')
        base[name] = entry['st_value']
    setter_data = [b['address'] for b in base['configuration_function']['symbol_bindings'] if b['kind'] == 'data']
    if setter_data != [base['g_pm_cfg']]:
        raise ValueError('Current setter uses another configuration object')
    base['gp'] = gp
    base['osi_pointer'] = symbol('g_osi_funcs_p')['st_value']
    base['osi_table'] = adapter_table(linked.read, 'native', linked.symbols)
    table = symbol('g_pp_timer_info')
    base['timer_table_address'] = table['st_value']
    wrapper = int(base['functions'][0]['start'], 0)
    if table['st_size'] != 120 or linked.read(table['st_value'] + 88, 8) != (11).to_bytes(4, 'little') + wrapper.to_bytes(4, 'little'):
        raise ValueError('Current event 11 selects another function')
    osi = linked.read(base['osi_table']['address'], 480)
    layout['osi_slots'] = {str(slot): int.from_bytes(osi[slot:slot+4], 'little') for slot in (264, 400, 408)}
    layout['station_global'] = symbol('g_ic')['st_value']
    result = {'factory': previous['layouts']['factory'], 'native': layout}
    for variant, selected in result.items():
        tim = next(row for row in selected['functions'] if row['name'] == 'pm_process_tim')
        counters = [b['address'] for b in tim['symbol_bindings'] if b['name'] == 'g_pm_cnt']
        if len(counters) != 1:
            raise ValueError('Missing TIM counter binding')
        selected['counter_address'] = counters[0]
        if variant == 'factory':
            # This slot is read directly by the fully matched TIM body.
            from audit_factory_xrefs import Image
            raw = Image(factory).read(selected['prior']['osi_table']['address'], 480)
            selected['osi_slots']['408'] = int.from_bytes(raw[408:412], 'little')
    return dict(schema='wifi-tim-linked-v1', layouts=result,
                factory_elf_sha256=sha(factory), reference_elf_sha256=sha(reference),
                native_elf_sha256=sha(native), native_app_sha256=sha(app),
                native_functions_matched=len(rows),
                full_runtime_lifecycle_proved=False, whole_image_completeness_proved=False,
                physical_hardware_tested=False)
