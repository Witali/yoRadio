"""Compare captured public curve bins with own binary64 math diagnostically only."""
import argparse
from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import sys
from protocol import load_contract,validate_log

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent


def need(ok,reason):
    if not ok:raise ValueError(reason)


def sha(data):return hashlib.sha256(data).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--capture',type=Path,required=True)
    parser.add_argument('--outer-receipt',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    repo=next(p for p in HERE.parents if (p/'idf/esp32-cyd2usb-native/main').is_dir())
    capture=args.capture.resolve();out=args.output.resolve()
    need(capture.is_relative_to(repo/'.build') and out.is_relative_to(repo/'.build') and not out.exists() and
         not out.is_relative_to(HERE) and not out.is_relative_to(capture),'Fresh independent diagnostic file')
    report_raw=(capture/'report.json').read_bytes();report=json.loads(report_raw)
    outer_raw=args.outer_receipt.resolve().read_bytes();outer=json.loads(outer_raw)
    need(outer['status']=='TERMINAL' and type(outer['returncode']) is int and outer['returncode']==0 and
         type(outer['owned_pid']) is int and outer['owned_pid']>0 and not outer.get('timed_out',False) and not outer.get('interrupted',False), 'Actual direct outer terminal0 required')
    need(any(Path(value).name=='run-public-curve.py' for value in outer['argv']) and Path(outer['cwd']).resolve()==repo,
         'Actual direct curve controller argv/cwd')
    for path,row in outer['logs'].items():
        data=Path(path).read_bytes();need(len(data)==row['bytes'] and sha(data)==row['sha256'],'Actual outer log bytes')
    need(report['schema']=='public-floor0-curve-runtime-v1' and report['result']=='PUBLIC_TREMOR_FLOOR0_CURVES_CAPTURED' and
         report['completed'] is True and report['public_function_evaluated'] is True and
         all(report[key] is False for key in ('target_codec_executed','reference_decoder_executed','PCM_qualified','full_G6_qualified','physical_qualified')), 'Bounded actual public-function capture only')
    for command in report['commands']:
        need(command['state']=='complete' and command['exit_status']==0 and type(command['pid']) is int and command['pid']>0 and
             all(command[key] is False for key in ('timed_out','interrupted','force_stopped')), 'Every actual owned command normal terminal0')
    qemu=next(row for row in report['commands'] if row['name']=='qemu')
    need(qemu['lifecycle_qualified'] is True and qemu['qmp_quit_acknowledged'] is True and qemu['owned_shutdown_observed'] is True,'Actual QMP lifecycle required')
    contract_fact=next(row for row in report['inputs'].values() if row['snapshot']=='sources/contract.json')
    contract=load_contract(capture/'sources/contract.json',contract_fact['sha256'])
    serial=(capture/'qemu.serial.log').read_bytes();stderr=(capture/'qemu.stderr.log').read_bytes()
    need(sha(serial)==qemu['qemu.serial.log']['sha256'] and sha(stderr)==qemu['qemu.stderr.log']['sha256'],'Actual complete curve streams')
    observed=validate_log((serial+b'\n'+stderr).decode(errors='replace'),contract,returncode=qemu['exit_status'],timed_out=qemu['timed_out'],interrupted=qemu['interrupted'])
    curves=observed.pop('curves');need(observed==report['observed'],'Strict full168/full-bin evidence before math')
    need(len(curves)==len(report['observed_curves'])==168,'Every persisted original call before analytic comparison')
    for row,persisted in zip(curves,report['observed_curves']):
        path=(capture/persisted['path']).resolve();need(path.is_relative_to(capture) and path.read_bytes()==row['values'] and persisted['sha256']==sha(row['values']),'Every persisted curve byte')
    module_path=HERE/'witness-source/curve_diagnostic.py'
    need(sha(module_path.read_bytes())=='b3c377a86040410add2ed7bedfd26aac6dcef26b59fc1bc2dabbc45c1c2fd345','Exact own analytic formula source')
    spec=importlib.util.spec_from_file_location('public_curve_own_analytic_math',module_path)
    math=importlib.util.module_from_spec(spec);spec.loader.exec_module(math)
    rows=[];positive=0
    for raw,curve in zip(contract['model']['calls'],curves):
        w=raw['words'];lsp=list(map(lambda value:float(Fraction(value)),raw['lsp_radians_exact']))
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
        counts=dict(cases=6,packets=84,calls=168,full_public_bins=observed['bins'],active_bin_comparisons=len(rows)*16),
        own_ideal_positive_db_observations=positive,cases=rows,
        interpretation='Own mathematical Bark map and binary64 equations; public integer Bark/rounding/lookup/clamp differ. No equality or tolerance policy, PCM or backend attribution.',
        public_function_evaluated=True,own_binary64_diagnostic_computed=True,target_codec_executed=False,reference_decoder_executed=False,
        PCM_computed=False,vendor_behavior_attributed=False,numeric_qualified=False,full_G6_qualified=False,physical_qualified=False)
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('x',encoding='utf-8',newline='\n') as stream:stream.write(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({key:result[key] for key in ('result','counts','own_ideal_positive_db_observations','numeric_qualified','full_G6_qualified')}))


if __name__=='__main__':main()
