"""Exact recorded public-curve versus own binary64 diagnostic; never a codec or policy gate."""
import argparse
from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path, PurePosixPath
import re
import struct
import sys

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
CONTROLLER_SHA='a31f9dbf5e19d292d3cd5cf04def819d8470ea4b1747d6678e8c8e707157bb56'
REPORT_SHA='d00a30f91d37f998af97f63cd9433e140e8d72f6c9a126de58ee260c929354cd'
TERMINAL_SHA='c3865f287ee84567b7840b45d5d8db4c239d317a537c76f2f6a231019bea163e'
PUBLIC_SHA='e1836251d072154691f87a74ea6cdae88d2cf2dd106fbc99908ec71f1f1a8e5a'
PROTOCOL_SHA='9b1abe4fa383976291157d6d1991feafda69fa63cfaf312c5c4f588f46279dc8'
MATH_SHA='b3c377a86040410add2ed7bedfd26aac6dcef26b59fc1bc2dabbc45c1c2fd345'
RUNTIME_READINESS_SHA='97de1886431efe1302f1125f223752800eaa83b599168dda41d31a0442cd0e65'
CONTRACT_SHA='1f8817117df942c4d6564614e71a90147a9faa6e782ff945830dc11d5b9f6e3d'


def need(ok,reason):
    if not ok:raise ValueError(reason)


def sha(data):return hashlib.sha256(data).hexdigest()


def safe(value):
    value=str(value).replace('\\','/')
    path=PurePosixPath(value)
    need(value and not path.is_absolute() and '..' not in path.parts and ':' not in value,'Scoped recorded snapshot path')
    return path.as_posix()


def load_pinned(name,path,expected,read):
    read(path,expected)
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # Normal SHA-pinned definitions; no guarded entrypoint is called.
    return module


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('capture','outer-receipt','output'):
        parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--readiness-sha256',required=True)
    args=parser.parse_args()
    repo=next(p for p in HERE.parents if (p/'idf/esp32-cyd2usb-native/main').is_dir())
    capture=args.capture.resolve();out=args.output.resolve();receipt_path=args.outer_receipt.resolve()
    need(capture==repo/'.build/cyd-vorbis-public-floor0-curve-capture-03' and
         receipt_path==repo/'.build/cyd-vorbis-public-floor0-curve-capture-03-terminal.json', 'Exact selected capture03 and direct terminal paths')
    protected=(HERE,capture,repo/'.build/cyd-vorbis-public-floor0-curve-prep-03',
               repo/'.build/cyd-vorbis-public-floor0-curve-runtime-03')
    need(out.is_relative_to(repo/'.build') and not out.exists() and
         not any(out.is_relative_to(path) or path.is_relative_to(out) for path in protected),'Fresh independent diagnostic file')
    need(re.fullmatch('[0-9a-f]{64}',args.readiness_sha256),'Explicit reviewed analytic preparation readiness SHA')
    identities={}
    def read(path,expected=None,size=None):
        path=Path(path).resolve();data=path.read_bytes();row=dict(bytes=len(data),sha256=sha(data))
        need(expected is None or row['sha256']==expected,'Exact bound input SHA: '+str(path))
        need(size is None or len(data)==size,'Exact bound input size: '+str(path))
        need(path not in identities or identities[path]==row,'Input role identity changed')
        identities[path]=row
        return data
    readiness=json.loads(read(HERE/'readiness.json',args.readiness_sha256))
    need(readiness['schema']=='public-floor0-analytic-source-readiness-v1' and readiness['source_only'] is True,'Reviewed source-only analytic preparation')
    need({p.relative_to(HERE).as_posix() for p in HERE.rglob('*') if p.is_file()}==set(readiness['files'])|{'readiness.json'},'Exact analytic preparation inventory')
    for name,row in readiness['files'].items():read(HERE/safe(name),row['sha256'],row['bytes'])
    origins=json.loads(read(HERE/'source-origins.json'))
    for group in ('runtime','unchanged_helpers'):
        for row in origins[group].values():read(repo/safe(row['path']),row['sha256'],row['bytes'])
    protocol=load_pinned('exact_public_curve_protocol',HERE/'protocol.py',PROTOCOL_SHA,read)
    math=load_pinned('public_curve_own_analytic_math',HERE/'curve_diagnostic.py',MATH_SHA,read)
    need(sys.float_info.radix==2 and sys.float_info.mant_dig==53 and sys.float_info.max_exp==1024,'Binary64 float context')
    report_raw=read(capture/'report.json',REPORT_SHA);report=json.loads(report_raw)
    outer_raw=read(receipt_path,TERMINAL_SHA);outer=json.loads(outer_raw)
    need(outer==dict(schema='direct-exec-tool-terminal-v1',session_id=43646,terminal_chunk_id='f26f66',exit_code=0,
         report_sha256=sha(report_raw),entrypoint_sha256=CONTROLLER_SHA),'Actual exact direct terminal0/report/controller/session/chunk binding')
    need(report['schema']=='public-floor0-curve-runtime-v1' and report['result']=='PUBLIC_TREMOR_FLOOR0_CURVES_CAPTURED'
         and report['passed'] is True and report['completed'] is True and report['source_compile_link_qualified'] is True
         and report['public_function_evaluated'] is True and report['declared_inputs_tools_configs_unchanged'] is True
         and report['readiness_sha256']==RUNTIME_READINESS_SHA and
         all(report[key] is False for key in ('target_codec_executed','reference_decoder_executed','vendor_backend_qualified',
             'PCM_computed','PCM_qualified','full_G6_qualified','physical_qualified','production_radio_integration')),'Exact complete bounded public-function capture')
    frozen={}
    for origin,row in report['inputs'].items():
        snapshot=safe(row['snapshot']);path=(capture/snapshot).resolve()
        need(path.is_relative_to(capture/'sources'),'All frozen inputs remain inside selected capture sources')
        read(path,row['sha256'],row['bytes']);need(snapshot not in frozen,'Unique recorded snapshot role');frozen[snapshot]=row
    need(frozen['sources/run-public-curve.py']['sha256']==CONTROLLER_SHA and
         frozen['sources/runtime-readiness.json']['sha256']==RUNTIME_READINESS_SHA,
         'Captured exact executed controller and reviewed runtime readiness')
    commands=report['commands'];need(len(commands)==22 and len({c['name'] for c in commands})==22,'All22 unique actual owned commands')
    for command in commands:
        need(command['state']=='complete' and command['exit_status']==0 and type(command['pid']) is int and command['pid']>0
             and all(command[key] is False for key in ('timed_out','interrupted','force_stopped')),'Every actual owned command normal terminal0')
        if command['name']!='qemu':
            for stream in ('stdout','stderr'):read(capture/(command['name']+'.'+stream+'.log'),command[stream+'_sha256'])
    qemu=next(row for row in commands if row['name']=='qemu')
    need(Path(qemu['cwd']).resolve()==capture and all(qemu[key] is True for key in ('complete_observed','lifecycle_qualified',
         'qmp_capabilities_acknowledged','qmp_quit_acknowledged','owned_shutdown_observed')),'Actual selected capture QMP lifecycle')
    for name in ('qemu.serial.log','qemu.stderr.log','qemu.qmp.stdout.log','qemu.qmp.requests.jsonl'):
        read(capture/name,qemu[name]['sha256'],qemu[name]['bytes'])
    need(frozen['sources/owned_qmp.py']['sha256']=='9e48796aba1dd8bef63b5e3f4beff4a2f042c3e180dabff40c9904fcdabe9416',
         'Exact captured helper enforces EOF/join; no unrecorded direct booleans are fabricated')
    messages=[json.loads(line) for line in read(capture/'qemu.qmp.stdout.log').splitlines() if line]
    requests=[json.loads(line) for line in read(capture/'qemu.qmp.requests.jsonl').splitlines() if line]
    need(messages==[row['message'] for row in qemu['qmp_messages']] and len(messages)==4 and 'QMP' in messages[0]
         and requests==qemu['qmp_requests'] and [row['message'] for row in requests]==[
             dict(execute='qmp_capabilities',id='owned-capabilities'),dict(execute='quit',id='owned-quit')], 'Complete recorded actual QMP request/message closure')
    need([row for row in messages if 'return' in row]==[{'return':{},'id':'owned-capabilities'},{'return':{},'id':'owned-quit'}]
         and [row['data'] for row in messages if row.get('event')=='SHUTDOWN']==[dict(guest=False,reason='host-qmp-quit')]
         and all('error' not in row and row.get('event') not in ('RESET','GUEST_PANICKED') for row in messages),'Actual acknowledged owned host quit, no error/reset substitute')
    need(qemu['actual_started_time_ns']<requests[0]['actual_sent_time_ns']<requests[1]['actual_sent_time_ns']<qemu['actual_terminal_time_ns'],'Actual QMP lifecycle order')
    contract=protocol.load_contract(capture/'sources/contract.json',CONTRACT_SHA)
    need(frozen['sources/contract.json']['sha256']==CONTRACT_SHA and frozen['sources/project/main/data.h']['sha256']==contract['header_sha256'], 'Actual full source contract and compiled input header')
    port=json.loads(read(HERE/'public-portability.json'))
    need(port['ported_floor0_sha256']==PUBLIC_SHA==contract['model']['public_floor0_sha256']==report['public_floor0_sha256']
         and contract['model']['public_floor0_variant']==report['public_source_variant']=='PORTED_PUBLIC_TREMOR_FLOOR0'
         and frozen['sources/project/main/public/floor0.c']['sha256']==PUBLIC_SHA, 'Exact PORTED public function identity; no original-public execution claim')
    contexts=report['compile_contexts'];need(len(contexts)==3 and {row['label'] for row in contexts}=={'curve_unit','floor0','floor_lookup'},'Exactly3 actual own/public TUs')
    sources={'curve_unit':'sources/project/main/curve_unit.c','floor0':'sources/project/main/public/floor0.c','floor_lookup':'sources/project/main/public/floor_lookup.c'}
    for context in contexts:
        source=(capture/sources[context['label']]).resolve()
        need(Path(context['actual_row']['file']).resolve()==source and any(Path(row['path']).resolve()==source and
             row['sha256']==frozen[sources[context['label']]]['sha256'] for row in context['actual_dependencies']),'Actual TU and GCC dependency bind real compiled source')
    serial=read(capture/'qemu.serial.log');stderr=read(capture/'qemu.stderr.log')
    need(sha(serial[:qemu['serial_bytes_at_complete']])==qemu['serial_sha256_at_complete'],'Actual COMPLETE prefix binding')
    observed=protocol.validate_log((serial+b'\n'+stderr).decode(errors='replace'),contract,returncode=qemu['exit_status'],timed_out=qemu['timed_out'],interrupted=qemu['interrupted'])
    curves=observed.pop('curves');need(observed==report['observed'],'Strict full168/full-bin evidence before math')
    need(len(curves)==len(report['observed_curves'])==168 and observed['bins']==58368,'Every original complete call before comparison')
    expected_paths=set()
    for row,persisted in zip(curves,report['observed_curves']):
        expected='observed-curves/'+f"{row['call']:03d}.i32le"
        need(persisted==dict({key:value for key,value in row.items() if key!='values'},path=expected),'Every complete curve metadata record and unique fixed path')
        need(read(capture/expected,row['sha256'],row['bytes'])==row['values'],'Every persisted complete curve byte')
        expected_paths.add((capture/expected).resolve())
    need({p.resolve() for p in (capture/'observed-curves').iterdir()}==expected_paths,'Exact complete168 persisted file inventory')
    rows=[];positive=0
    for raw,curve in zip(contract['model']['calls'],curves):
        w=raw['words']
        exact_lsp=[Fraction(value) for value in raw['lsp_radians_exact']]
        need(len(exact_lsp)==w[4] and exact_lsp==[Fraction(value,1<<24) for value in w[9:9+w[4]]]
             and w[9+w[4]:15]==[0]*(6-w[4]), 'Exact analytic radians are the actual Q24 descriptor inputs')
        bits=raw['amplitude_bits'];amp=raw['amplitude_raw'];exact_amplitude=Fraction(raw['amplitude_exact'])
        need(type(bits) is int and bits in (6,8) and type(amp) is int and 0<amp<(1<<bits)
             and exact_amplitude==Fraction(amp*w[7],(1<<bits)-1)
             and w[6]==(exact_amplitude*16).__floor__(), 'Exact raw amplitude and Q4 descriptor conversion')
        lsp=list(map(float,exact_lsp))
        values=struct.unpack('<'+'i'*w[3],curve['values'])
        bins=[]
        for index in range(16):
            frequency=math.frequency_point(index,w[3],w[8]*2,w[5])
            exact=math.requested_curve(lsp,Fraction(raw['amplitude_exact']),w[7],frequency['mapped_angle_radians'])
            ampq4=math.requested_curve(lsp,Fraction(w[6],16),w[7],frequency['mapped_angle_radians'])
            positive+=int(exact['requested_db']>0)
            bins.append(dict(bin=index,public_output_Q24=values[index],residue_Q8=w[15+index],
                public_gain_estimate=values[index]/(w[15+index]*65536),own_math_map=frequency,
                own_exact_amplitude_curve=exact,own_Q4_amplitude_curve=ampq4))
        rows.append(dict(call=raw['call'],case=w[0],packet=w[1],channel=w[2],full_public_bins=w[3],
            full_public_curve_sha256=curve['sha256'],active_bins=bins))
    result=dict(result='PUBLIC_CURVE_OWN_BINARY64_DIAGNOSTIC_COMPLETED',capture_report_sha256=sha(report_raw),outer_receipt_sha256=sha(outer_raw),
        direct_terminal_session=outer['session_id'],direct_terminal_chunk=outer['terminal_chunk_id'],
        executed_controller_sha256=CONTROLLER_SHA,source_readiness_sha256=args.readiness_sha256,
        counts=dict(cases=6,packets=84,calls=168,full_public_bins=observed['bins'],active_bin_comparisons=len(rows)*16),
        own_ideal_positive_db_observations=positive,cases=rows,
        interpretation='Own mathematical Bark map and binary64 equations; public integer Bark/rounding/lookup/clamp differ. No equality or tolerance policy, PCM or backend attribution.',
        public_function_evaluated=True,public_source_variant='PORTED_PUBLIC_TREMOR_FLOOR0',
        public_floor0_sha256=port['ported_floor0_sha256'],own_binary64_diagnostic_computed=True,target_codec_executed=False,reference_decoder_executed=False,
        PCM_computed=False,vendor_behavior_attributed=False,numeric_qualified=False,full_G6_qualified=False,physical_qualified=False)
    for path,row in identities.items():
        data=path.read_bytes();need(len(data)==row['bytes'] and sha(data)==row['sha256'],'Bound input changed during diagnostic')
    result['validated_inputs']={str(path):row for path,row in identities.items()}
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('x',encoding='utf-8',newline='\n') as stream:stream.write(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({key:result[key] for key in ('result','counts','own_ideal_positive_db_observations','numeric_qualified','full_G6_qualified')}))


if __name__=='__main__':main()
