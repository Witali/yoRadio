"""Offline/read-only block evidence verification; stdlib, no process or clock."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path, PureWindowsPath
import re
import struct
import sys
sys.dont_write_bytecode=True
PROTOCOL='32fab1f7e362450c66185bfe51c0bdaadda5f022d796996225cb2feba3d98aa9'
CAPTURE='33a64601d773382e748d69391eb068d7bc2b682540e3b670ddc13c0a19e22f7e'

def need(ok,message):
    if not ok: raise RuntimeError(message)
def sha(data): return hashlib.sha256(data).hexdigest()
def norm(value): return str(value).replace('\\','/')


def verify(folder):
    folder=Path(folder).resolve(); m=json.loads((folder/'manifest.json').read_bytes())
    need(m['schema']=='cyd-public-block-matrix-archive-v1' and m['omitted_bytes_replayable'] is False,'Wrong manifest/scope')
    rows={}; raw={}; stored={'manifest.json','.gitattributes'}
    for original,row in m['files'].items():
        key=norm(original).casefold(); need(key not in rows,'Duplicate original identity'); rows[key]=row
        need(PureWindowsPath(original).is_absolute() and re.fullmatch('[0-9a-f]{64}',row['sha256']) and
             type(row['bytes']) is int and row['bytes']>=0,'Bad original identity')
        if row['stored'] is None:
            need(row.get('omission'),'Unexplained omission')
            if original.endswith('.elf'):
                h=bytes.fromhex(row['elf_header_hex'])
                need(len(h)==52 and h[:6]==b'\x7fELF\x01\x01' and struct.unpack_from('<H',h,18)[0]==row['elf_machine']==94,'Wrong captured ELF metadata')
            continue
        name=row['stored']; path=folder/name
        need(name==norm(name) and not PureWindowsPath(name).is_absolute() and ':' not in name and
             all(part not in ('','..','.') for part in name.split('/')) and name not in stored and
             not path.is_symlink() and path.resolve().is_relative_to(folder),'Unsafe/duplicate stored path')
        stored.add(name); blob=path.read_bytes()
        need(sha(blob)==row['stored_sha256'] and len(blob)==row['stored_bytes'],'Stored identity changed')
        need(row['encoding'] in ('gzip','raw'),'Unknown encoding')
        data=gzip.decompress(blob) if row['encoding']=='gzip' else blob
        need(sha(data)==row['sha256'] and len(data)==row['bytes'],'Decoded bytes changed')
        need(not original.endswith('.py') or row['encoding']=='raw','Python must stay raw'); raw[key]=data
    need(not any(p.is_symlink() for p in folder.rglob('*')) and
         {p.relative_to(folder).as_posix() for p in folder.rglob('*') if p.is_file()}==stored,'Exact archive file set changed')
    attrs=(folder/'.gitattributes').read_bytes()
    need(attrs==b'* -text\n** -text\n' and sha(attrs)==m['attributes_sha256'],'Byte-preservation rule changed')
    def ref(path,base=None):
        path=PureWindowsPath(path)
        if not path.is_absolute(): path=PureWindowsPath(base or m['repository_original'])/path
        value=norm(path).casefold(); need(value in rows,'Unarchived reference '+str(path)); return value
    def data(path,base=None): return raw[ref(path,base)]
    def obj(path,base=None): return json.loads(data(path,base))
    def pin(path,digest,size=None,base=None):
        r=rows[ref(path,base)]; need(r['sha256']==digest and (size is None or r['bytes']==size),'Referenced identity changed '+str(path))
    def root(role,name): return norm(m['repository_original'])+'/'+m['roots'][role]+'/'+norm(name)
    def get(role,name): return data(root(role,name))
    def js(role,name): return obj(root(role,name))
    def receipt(path,code):
        r=obj(path)
        need(r['status']=='TERMINAL' and type(r['returncode']) is int and r['returncode']==code and r.get('timed_out',False) is False,'Wrong actual terminal status')
        need(r['runner_sha256']==CAPTURE,'Capture utility mismatch'); pin('.build/cyd-vorbis-format-command-01.py',CAPTURE)
        pin(r['argv'][0],r['executable_sha256'])
        need(len(r['logs'])==2,'Missing process stream')
        for name,row in r['logs'].items(): pin(name,row['sha256'],row['bytes'],PureWindowsPath(path).parent)
        return r
    def wav(decoded,command):
        path=command['argv'][-1]; row=rows[ref(path)]
        need(row['stored'] is None and row['sha256']==decoded['wav_sha256'],'WAV identity changed')
        pcm=row['pcm']; need(pcm['sha256']==decoded['pcm_sha256'] and pcm['bytes']==decoded['pcm_bytes'] and
             pcm['channels']==2 and pcm['sample_width']==2,'Recorded omitted PCM identity changed')
    def packets(blob):
        result=[]; pending=bytearray(); pos=0
        while pos<len(blob):
            need(blob[pos:pos+5]==b'OggS\0' and pos+27<=len(blob),'Encoded source carrier header')
            count=blob[pos+26]; laces=blob[pos+27:pos+27+count]; cursor=pos+27+count
            need(len(laces)==count and cursor+sum(laces)<=len(blob),'Encoded source carrier length')
            for n in laces:
                pending.extend(blob[cursor:cursor+n]); cursor+=n
                if n<255: result.append(bytes(pending)); pending.clear()
            pos=cursor
        need(not pending and len(result)>3,'Incomplete encoded source packet')
        return result
    pairs={(1<<s,1<<l) for s in range(6,14) for l in range(s,14)}
    def coverage(cases):
        families={}
        for c in cases:
            i=c['input']; families.setdefault(i.get('family','minimal'),[]).append((i['short'],i['long']))
        need(all(len(v)==36 and set(v)==pairs for v in families.values()),'Incomplete/duplicate size matrix')
        return families
    dual,xiph,rate=(js(name,'report.json') for name in ('dual','xiph','rate'))
    need(dual['completed'] is True and dual['passed'] is False and len(dual['cases'])==108 and
         sum(c['passed'] is True for c in dual['cases'])==78 and len(dual['failures'])==30,'Original dual NONPASS108 was altered')
    need(len(coverage(dual['cases']))==3,'Three original families required')
    need(xiph['completed'] is True and xiph['reference_corpus_qualified'] is True and xiph['original_dual_reference_passed'] is False and
         len(xiph['cases'])==108 and not xiph['failures'] and xiph['full_G6_qualified'] is False,'Xiph proof incomplete/mislabeled')
    pin(root('dual','report.json'),xiph['original_report_sha256']); pin('.build/cyd-vorbis-floor-range-audit-01/AUDIT.md',xiph['normative_audit_sha256'])
    need(rate['completed'] is True and rate['passed'] is True and len(rate['cases'])==36 and not rate['failures'] and
         len(coverage(rate['cases']))==1,'Minimal192000 dual proof incomplete')
    for role,report,code in (('dual',dual,1),('rate',rate,0),('xiph',xiph,0)):
        rpath='.build/cyd-vorbis-block-'+{'dual':'host','rate':'rate-host','xiph':'xiph'}[role]+'-01-command.json'
        receipt(norm(m['repository_original'])+'/'+rpath,code)
        need(report['target_executed'] is False and report['production_changed'] is False,'Host report scope changed')
    pin('.build/cyd-vorbis-block-host-01-command.json',xiph['original_outer_receipt_sha256'])
    need(len(dual['commands'])==264 and len(rate['commands'])==108,'Historical command counts changed')
    for role,report in (('dual',dual),('rate',rate)):
        for path,digest in report['tools'].items(): pin(path,digest)
        pin('.build/cyd-vorbis-block-host-driver-01.py',report['driver_sha256'])
        pin(root('design','inspect_fixture.py'),report['inspector_sha256'])
        command_map={entry['name']:entry for entry in report['commands']}
        for c in report['cases']:
            pin(c['source_matrix'],c['source_matrix_sha256'])
            source=c['input'].get('path',norm(PureWindowsPath(c['source_matrix']).parent/c['input']['ogg']))
            pin(source,c['ogg_sha256'])
            for decoder in (('vorbis','libvorbis') if c['passed'] else ('vorbis',)):
                name='cases/'+c['id']+'/decode-'+decoder; entry=command_map[name]; path=root(role,entry['receipt'])
                pin(path,entry['sha256']); command=receipt(path,0 if c['passed'] else 3199971767)
                if c['passed']: wav(c['decoded'][decoder],command)
                else:
                    stderr=next(n for n in command['logs'] if n.endswith('.stderr.log'))
                    need(b'Floor value is too large for blocksize:' in data(stderr),'Original refusal is not the retained native floor restriction')
            if c['passed']:
                need(c['cross_reference_max_abs_error']<=2 and all(x['nonzero_bytes']>0 for x in c['decoded'].values()),'Dual-reference assertion changed')
        for entry in report['commands']:
            path=root(role,entry['receipt']); pin(path,entry['sha256'])
            r=obj(path); receipt(path,r['returncode'])
    by_id={c['id']:c for c in dual['cases']}; need({c['id'] for c in xiph['cases']}==set(by_id),'Xiph coverage differs')
    for c in xiph['cases']:
        old=by_id[c['id']]; need(c['input']==old['input'] and c['reference_qualified'] is True and
             c['native_comparison_qualified'] is old['passed'],'Xiph case lineage changed')
        if old['passed']: need(c['decoded']==old['decoded'],'Reused dual proof changed')
        else:
            path=root('xiph','cases/'+c['id']+'/decode-libvorbis.json'); pin(path,c['receipt_sha256']); r=receipt(path,0); wav(c,r)
            pin(root('dual','cases/'+c['id']+'/decode-vorbis.json'),c['native_refusal_receipt_sha256'])
            need(c['nonzero_bytes']>0,'Empty Xiph proof')
    banks=js('banks','banks.json'); freeze=js('banks','freeze.json')
    pin(root('banks','banks.json'),freeze['manifest_sha256']); pin(root('banks','banks_data.h'),freeze['banks_header_sha256'])
    pin('.build/cyd-vorbis-block-freeze-banks-01.py',freeze['freeze_script_sha256'])
    need((freeze['raw_banks'],freeze['cases'],freeze['paired_packets'])==(3,108,5472) and
         banks['xiph_cases_qualified']==108 and banks['native_cases_compared']==78 and banks['native_floor_refusals']==30 and
         banks['original_dual_reference_passed'] is False and banks['minimal_rate_rebind_qualified'] is True and banks['full_G6_qualified'] is False,'Bank freeze claims changed')
    for key,role in (('host_reference_report_sha256','xiph'),('original_dual_report_sha256','dual'),('minimal_rate_rebind_report_sha256','rate')):
        pin(root(role,'report.json'),banks[key])
    for path,digest in banks['matrix_pins'].items(): pin(path,digest)
    for role in ('design','protocol_prep'):
        for row in js(role,'input-pins.json')['inputs']: pin(row['path'],row['sha256'],row['bytes'])
        pinned=js(role,'pins.json')['files']
        for row in pinned: pin(root(role,row['relative']),row['sha256'],row['bytes'])
    for path,digest in js('sdk_prep','pins.json')['files'].items(): pin(root('sdk_prep',path),digest)
    test=js('protocol_prep','host-tests.command.json')
    need(test['completed'] is True and type(test['returncode']) is int and test['returncode']==0 and
         test['timed_out'] is False and test['interrupted'] is False and test['target_executed'] is False,'Synthetic protocol host result changed')
    for path,row in test['inputs'].items(): pin(path,row['sha256'],row['bytes'])
    for path,row in test['logs'].items(): pin(root('protocol_prep',path),row['sha256'],row['bytes'])
    canonical=js('canonical_protocol','host-tests.command.json')
    need(canonical['status']=='TERMINAL' and canonical['completed'] is True and type(canonical['returncode']) is int and
         canonical['returncode']==0 and canonical['timed_out'] is False and canonical['interrupted'] is False and
         canonical['target_executed'] is False and canonical['reviewed_files_still_byte_exact'] is True,'Canonical synthetic host check changed')
    for path,row in canonical['inputs'].items(): pin(path,row['sha256'],row['bytes'])
    for path,row in canonical['logs'].items(): pin(root('canonical_protocol',path),row['sha256'],row['bytes'])
    for name in ('block_protocol.py','test_block_protocol.py','host_model.json'):
        need(data('tests/vorbis_block_matrix/'+name)==get('protocol_prep',name),'Canonical/proposal protocol source differs')
    for name,row in canonical['preserved_existing_files'].items(): pin('tests/vorbis_block_matrix/'+name,row['sha256'],row['bytes'])
    header=get('banks','banks_data.h').decode()
    for bank in banks['banks']:
        arrays={}
        for part in ('info','setup','audio','modes','offsets'):
            match=re.search(r'\bbank_'+bank['name']+'_'+part+r'\[\]\s*=\s*\{([^}]+)\}',header)
            need(match,'Missing encoded bank array'); values=[int(x) for x in match.group(1).split(',') if x.strip()]
            if part in ('info','setup','audio'):
                blob=bytes(values); arrays[part]=blob
                need(sha(blob)==bank[part+'_sha256'] and len(blob)==bank[part+'_size'],'Raw bank bytes changed')
            else: need(values==bank['mode_flags' if part=='modes' else 'offsets'],'Bank packet layout changed')
        matrix=obj(bank['source_matrix']); cases=[c for c in matrix['cases'] if c.get('family',bank['name'])==bank['name']]
        need(len(cases)==36 and {(c['short'],c['long']) for c in cases}==pairs,'Frozen bank source coverage changed')
        for c in cases:
            source=PureWindowsPath(m['repository_original'])/bank['source_matrix']; source=source.parent/c['ogg']
            parsed=packets(data(source)); ident=bytearray(parsed[0][7:]); ident[21]=arrays['info'][21]
            need(bytes(ident)==arrays['info'] and parsed[2][7:]==arrays['setup'] and b''.join(parsed[3:])==arrays['audio'] and
                 c['mode_flags']==bank['mode_flags'],'Actual raw bank differs from encoded source corpus')
        if bank['name']=='minimal':
            rebound=js('rebound','generated01/matrix.json')
            for old,new in zip(matrix['cases'],rebound['cases']):
                before=packets(get('minimal','generated01/'+old['ogg'])); after=packets(get('rebound','generated01/'+new['ogg']))
                info=bytearray(before[0]); struct.pack_into('<I',info,12,192000)
                need(bytes(info)==after[0] and before[1:]==after[1:],'Minimal rate rebind changed more than header rate')
    # Canonical generators were executed separately; preserve their exact outputs
    # and the three metadata differences without re-running generation here.
    proposal=js('generator_prep','source-relation.json'); check=js('generator_check','report.json')
    need(check['completed'] is True and check['comparison_passed'] is True and not check['failures'] and
         check['codec_sdk_compiler_qemu_git_executed'] is False and check['codec_qualification_claimed'] is False and
         check['counts']['cases']==144 and check['counts']['byte_equal_files']==230 and check['counts']['metadata_only_files']==3 and
         check['counts']['byte_equal_ogg_files']==144 and check['counts']['raw_header_packets']==432 and check['counts']['raw_audio_packets']==5976,'Generator reproduction changed')
    pin(root('generator_prep','adaptation.diff'),proposal['adaptation_diff_sha256']); pin(root('generator_check','compare.py'),check['verifier_sha256'])
    for row in proposal['source_inputs']: pin(row['path'],row['sha256'],row['bytes'])
    for row in proposal['files']:
        pin(root('generator_prep',row['path']),row['sha256'],row['bytes'])
        pin('tests/vorbis_block_matrix/'+PureWindowsPath(row['path']).name,row['sha256'],row['bytes'])
    for row in check['files']:
        for prefix,key in (('historical','historical'),('canonical','canonical_output')): pin(row[key],row[prefix+'_sha256'],row[prefix+'_bytes'])
        if row['byte_equal']: need(row['historical_sha256']==row['canonical_sha256'],'Generator exact relation changed')
    for row in check['commands']:
        pin(row['path'],row['sha256']); c=obj(row['path'])
        need(type(c['returncode']) is int and c['returncode']==0 and c['codec_tools_executed'] is False and c['argv']==row['argv'],'Pure generator command changed')
        pin(c['argv'][2],c['generator_sha256'])
        for stream in ('stdout','stderr'): pin(c[stream]['path'],c[stream]['sha256'],c[stream]['bytes'])
    target=js('target','report.json'); terminal=obj(m['target_terminal'])
    need(terminal['status']=='TERMINAL' and type(terminal['exit_code']) is int and type(terminal['session_id']) is int and
         terminal['chunk_id'] and terminal['argv'] and terminal['cwd'],'Missing direct-tool terminal facts')
    pin(root('target','report.json'),terminal['report_sha256'])
    need(terminal['schema']=='direct-exec-tool-terminal-v1' and
         ref(terminal['argv'][4],terminal['cwd'])==ref(root('sdk_prep','run-cyd-vorbis-blocks-qemu.py')) and
         ref(terminal['argv'][terminal['argv'].index('--output')+1]+'/report.json',terminal['cwd'])==ref(root('target','report.json')),'Direct tool receipt launches different source/output')
    for path,row in target['inputs'].items(): pin(path,row['sha256']); pin(root('target',row['snapshot']),row['sha256'])
    for path,digest in target['tools'].items(): pin(path,digest)
    for mapping in ('variant_sources','build_outputs'):
        for path,digest in target[mapping].items(): pin(root('target',path),digest)
    for c in target['commands']:
        need(c['state'] in ('complete','failed','interrupted') and type(c['exit_status']) is int,'Live target command')
        for stream in ('stdout','stderr'): pin(root('target',c['name']+'.'+stream+'.log'),c[stream+'_sha256'])
    need(all(target[key] is False for key in ('full_G6_qualified','physical_device','production_radio_integration')),'Target scope inflated')
    need(target['encoded_data']==dict(manifest_sha256=freeze['manifest_sha256'],xiph_cases=108,native_compared=78,
         native_floor_refusals=30,minimal_rate_rebind_qualified=True),'Target uses different bank proof')
    accepted=target.get('passed') is True
    if accepted:
        need(terminal['exit_code']==0 and target['completed'] is True and target['block_matrix_qualified'] is True and
             target['result']=='RAW_BLOCK_MATRIX_ACCEPTED' and all(c['state']=='complete' and c['exit_status']==0 for c in target['commands']), 'Target acceptance lacks actual terminal success')
        cmds={c['name']:c for c in target['commands']}
        need(set(cmds)=={'sdk-head','sdk-clean','build','setup-macros','symbols','merge','qemu','sdk-head-after','sdk-clean-after'},'Nine actual owned commands required')
        sdk='7101770dc6db2667b3c477cc31365dd1acd6db4e'
        for name in ('sdk-head','sdk-head-after'): need(get('target',name+'.stdout.log').strip().decode()==sdk,'Wrong SDK6.0.2 identity')
        for name in ('sdk-clean','sdk-clean-after'): need(not get('target',name+'.stdout.log').strip(),'SDK tracked changes present')
        for name,row in target['sdk_build_logs'].items(): pin(root('target',name),row['sha256'],row['bytes'])
        ctx=target['setup_macro_context']; comp=js('target','build/compile_commands.json')
        need(ctx['row'] in comp and len(ctx['generated_inputs'])==2,'Actual setup row/context missing')
        own=[r for r in comp if '/variant/' in norm(r['file'])]
        need(len(own)==2 and {PureWindowsPath(r['file']).name for r in own}=={'setup.c','output.c'},'Actual raw source compile closure differs')
        original=ctx['original_argv']; need(original.count('-c')==original.count('-o')==1,'Unexpected outer compile argv')
        stripped=[]; skip=False
        for arg in original:
            if skip: skip=False; continue
            if arg=='-o': skip=True; continue
            if arg!='-c': stripped.append(arg)
        need(ctx['probe_argv']==stripped+['-E','-dM'] and cmds['setup-macros']['argv']==ctx['probe_argv'],'Macro context changed')
        for path,row in ctx['generated_inputs'].items():
            need(row['sha256_before']==row['sha256_after'],'Generated compiler context changed'); pin(path,row['sha256_before'])
        flags=next(p for p in ctx['generated_inputs'] if norm(p).endswith('/toolchain/cflags'))
        specs=next(p for p in ctx['generated_inputs'] if norm(p).endswith('/specs/picolibc.specs'))
        need([arg for arg in original if arg.startswith('@')]==['@'+norm(flags)] and data(flags).decode().splitlines()==
             ['-Wno-frame-address','-mlongcalls','-fno-builtin-memcpy','-fno-builtin-memset','-fno-builtin-bzero','"-specs='+norm(specs)+'"'] and data(specs),'Actual Xtensa response/specs changed')
        macros=get('target','setup-macros.stdout.log').decode().replace('\r\n','\n')
        for name in ('CONFIG_IDF_TARGET_ESP32','CONFIG_YORADIO_VORBIS_REPAIR'): need(re.search(r'^#define '+name+r' 1$',macros,re.M),'Wrong actual setup defines')
        need(not re.search(r'^#define LIMIT_TO_64kHz\b',macros,re.M),'Optional rate cap active')
        config=js('target','build/config/sdkconfig.json')
        need(config['IDF_TARGET']=='esp32' and config['YORADIO_VORBIS_REPAIR'] is True and config['FREERTOS_UNICORE'] is False,'Wrong target/repair/SMP config')
        for symbol in ('__wrap_esp_vorbis_dec_open','__wrap_esp_vorbis_dec_decode','esp_vorbis_dec_open','esp_vorbis_dec_decode'):
            need(re.search(r'\b'+symbol+r'$',get('target','symbols.stdout.log').decode(),re.M),'Actual public raw symbol missing')
        ninja=get('target','build/build.ninja')
        need(b'--wrap=esp_vorbis_dec_open' in ninja and b'--wrap=esp_vorbis_dec_decode' in ninja,'Actual raw link flags missing')
        recipe=js('target','build/flasher_args.json'); offsets={int(k,0):v for k,v in recipe['flash_files'].items()}
        need(set(offsets)=={0x1000,0x8000,0x10000} and recipe['extra_esptool_args']['chip']=='esp32' and
             recipe['flash_settings']==dict(flash_mode='dio',flash_size='4MB',flash_freq='40m'),'Wrong Xtensa image recipe')
        merge=[norm(v) for v in cmds['merge']['argv']]
        for offset,name in offsets.items():
            index=next(i for i,v in enumerate(merge) if v.startswith('0x') and int(v,0)==offset)
            need(ref(merge[index+1])==ref(root('target','build/'+name)),'Merge used different image')
        qargv=cmds['qemu']['argv']
        need(qargv[qargv.index('-smp')+1]=='2' and qargv[qargv.index('-M')+1]=='esp32,audiodev=quiet' and
             qargv[qargv.index('-nic')+1]=='none' and '-snapshot' in qargv and '-no-reboot' in qargv and
             qargv[-1]=='file='+str(PureWindowsPath(root('target','qemu-flash.bin')))+',if=mtd,format=raw','Wrong actual target machine/image')
        need(rows[ref(root('target','qemu-flash.bin'))]['bytes']==4194304,'Wrong merged image size')
        module=get('protocol_prep','block_protocol.py'); need(sha(module)==PROTOCOL,'Unreviewed target protocol module')
        ns={}; exec(compile(module,'frozen_block_protocol.py','exec'),ns)
        q=next(c for c in target['commands'] if c['name']=='qemu')
        observed=ns['validate_log']((get('target','qemu.stdout.log')+b'\n'+get('target','qemu.stderr.log')).decode(errors='replace'),
            banks['banks'],'cyd',manifest_sha256=freeze['manifest_sha256'],minimal_rate_rebind_qualified=True,
            returncode=q['exit_status'],timed_out=q['state']!='complete',interrupted=q['state']=='interrupted')
        need(observed==target['observed'],'Target protocol/counts changed')
    else:
        need(target['passed'] is False and target['block_matrix_qualified'] is False,'Unqualified target mislabeled')
        observed=None
    return dict(verified=True,original_dual_passed=False,original_dual_cases=108,native_compared=78,native_refusals=30,
        Xiph_cases=108,minimal192000_dual_cases=36,target_matrix_qualified=accepted,observed=observed,
        omitted_PCM_or_binaries_replayed=False,full_G6_qualified=False,radio_qualified=False,physical_qualified=False)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('archive',type=Path)
    print(json.dumps(verify(p.parse_args().archive),indent=2))
