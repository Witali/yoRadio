"""Qualify complete null-completion, quick-wake and PM state-setter bodies."""
from copy import deepcopy

from audit_factory_xrefs import Image, sha
from reverse.nothrow_linkage import LinkedRuntime
from reverse.rv32_link_match import model, match
from reverse.timer_event11_match import objects, unique
from reverse.timer_tim import qualify as tim_qualify

HELPERS = {'pm_tx_null_data_done_quick_wake_process': 0x4207595a,
           'pm_set_state': 0x42074aec}


def qualify(factory, reference, native, app, old_pp, new_pp, replacements=None):
    """Extend existing strict image pins; verify whole helper bodies and shared anchors."""
    prior=tim_qualify(factory,reference,native,app,old_pp,new_pp)
    layouts=deepcopy(prior['layouts'])
    image,linked=Image(factory),LinkedRuntime(native,app)
    for variant,library in (('factory',old_pp),('native',new_pp)):
        layout=layouts[variant];base=layout['prior'];source=objects(library,variant)['pm.o']
        shared,locals_={},{}
        existing=[*base['functions'][1:],base['configuration_function'],*layout['functions']]
        for row in existing:
            for binding in row['symbol_bindings']:
                if binding['binding']=='STB_LOCAL':
                    key=(binding['name'],binding['section'])
                    if key in locals_ and locals_[key]!=binding['address']:raise ValueError('Conflicting PM local anchor')
                    locals_[key]=binding['address']
                else:
                    if binding['name'] in shared and shared[binding['name']]!=binding['address']:
                        raise ValueError('Conflicting PM shared anchor')
                    shared[binding['name']]=binding['address']
        helpers=[]
        for name,old_address in HELPERS.items():
            spec=model(source,name)
            if variant=='factory':start=old_address;code=image.read(start,len(spec['code'])+64,True)
            else:
                symbol,code=linked.body(name);start=symbol['st_value']
            if replacements and (variant,name) in replacements:code=replacements[variant,name]
            row=match(spec,code,start,base['gp'])
            if variant=='native' and row['linked_bytes']!=symbol['st_size']:raise ValueError('Incomplete null helper')
            callers={b['address'] for known in existing for b in known['symbol_bindings'] if b['name']==name}
            if callers!={start}:raise ValueError('Parent calls a different null helper')
            for binding in row['symbol_bindings']:
                key=(binding['name'],binding['section'])
                if binding['binding']=='STB_LOCAL':
                    if key in locals_ and locals_[key]!=binding['address']:raise ValueError('Different null helper data')
                    locals_[key]=binding['address']
                else:
                    if binding['name'] in shared and shared[binding['name']]!=binding['address']:
                        raise ValueError('Different null helper shared callee')
                    shared[binding['name']]=binding['address']
                if variant=='native' and (binding['kind']=='call' or binding['binding']!='STB_LOCAL'):
                    if unique(linked.symbols,binding['name'])['st_value']!=binding['address']:
                        raise ValueError('Wrong current null helper symbol')
            row['linked_code_sha256']=sha(code[:row['linked_bytes']]);helpers.append(row)
        layout['functions'].extend(helpers)
        osi=base['osi_table']['address']
        raw=image.read(osi+412,4) if variant=='factory' else linked.read(osi+412,4)
        layout['osi_slots']['412']=int.from_bytes(raw,'little')
        parent=next(row for row in layout['functions'] if row['name']=='pm_tx_null_data_done_process')
        if [b['address'] for b in parent['symbol_bindings'] if b['name']=='g_pm_cnt'] != [layout['counter_address']]:
            raise ValueError('Null completion uses a different counter object')
        layout['extra_helpers']=helpers
    return dict(schema='wifi-null-completion-linked-v1',layouts=layouts,
        factory_elf_sha256=sha(factory),reference_elf_sha256=sha(reference),native_elf_sha256=sha(native),
        native_app_sha256=sha(app),full_runtime_lifecycle_proved=False,
        whole_image_completeness_proved=False,physical_hardware_tested=False)
