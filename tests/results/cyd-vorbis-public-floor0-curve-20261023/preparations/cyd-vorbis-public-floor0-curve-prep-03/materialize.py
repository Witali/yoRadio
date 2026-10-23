"""Materialize exact original floor0 raw inputs for the public curve unit; root only."""
import argparse
from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import struct
import sys
from readback import readback

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
WITNESS_SHA = 'b3c377a86040410add2ed7bedfd26aac6dcef26b59fc1bc2dabbc45c1c2fd345'
PUBLIC_SHA = 'e1836251d072154691f87a74ea6cdae88d2cf2dd106fbc99908ec71f1f1a8e5a'
ORIGINAL_PUBLIC_SHA = 'd0372c1dbf4c95231927619a7a1a660bdf421d63b332966f5fe33b9572c002f2'


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def sha(data): return hashlib.sha256(data).hexdigest()


def fnv(data):
    value = 2166136261
    for octet in data:
        value = ((value ^ octet) * 16777619) & 0xffffffff
    return value


def build_model():
    path = HERE/'witness-source/curve_diagnostic.py'
    need(sha(path.read_bytes()) == WITNESS_SHA, 'Exact reviewed raw-field witness source')
    spec = importlib.util.spec_from_file_location('public_curve_raw_fields', path)
    witness = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(witness)
    # Normal pinned import. Only its finite raw/Fraction readers are called;
    # no diagnostic(), sanity_controls(), Bark/trigonometry or exp is run here.
    pins = json.loads((path.parent/'source-pins.json').read_bytes())
    for item in pins['inputs']:
        raw = (path.parent/item['snapshot']).read_bytes()
        need(len(raw) == item['bytes'] and sha(raw) == item['sha256'], 'Unchanged original raw witness input')
    corpus = path.parent/pins['fixture_root']
    matrix = json.loads((corpus/'matrix.json').read_bytes())
    construction = json.loads((corpus/'construction-fields.json').read_bytes())
    cases = [row for row in matrix['cases'] if row['id'] in witness.EXPECTED_IDS]
    need(tuple(row['id'] for row in cases) == witness.EXPECTED_IDS and len(matrix['cases']) == 9, 'Exact six original cases')
    model = dict(schema='public-tremor-floor0-curve-model-v1', counts=dict(cases=6,packets=84,calls=168,bins=0),
        public_floor0_sha256=PUBLIC_SHA, public_floor0_variant='PORTED_PUBLIC_TREMOR_FLOOR0',
        public_floor0_original_sha256=ORIGINAL_PUBLIC_SHA,
        public_floor0_portability_diff_sha256=sha((HERE/'public-floor0-portability.diff').read_bytes()),
        witness_sha256=WITNESS_SHA, cases=[], calls=[],
        semantics=dict(LSP='signed Q24 radians', amplitude='floor((raw*offset*16)/((1<<bits)-1)) Q4',
            residue='exact residue0 first16 in Q8; every later half-block bin zero',
            output='signed32 public MULT31_SHIFT15 output in Q24; never PCM',
            integer_context='Xtensa ILP32, little-endian, arithmetic signed right shift; explicitly ported public C threshold shifts and unused local only',
            comparison='Public integer Bark/cosine/lookup/rounding/clamp path; own binary64 math is diagnostic only'))
    for case_index,case in enumerate(cases):
        declaration = construction['variants'][case['variant']]
        config = witness.configuration(witness.read_layout((corpus/case['setup']).read_bytes(),declaration['setup']))
        identity = (corpus/case['identification']).read_bytes()
        need(identity[:7] == b'\x01vorbis' and len(identity) == 30 and identity[11] == 2 and
             int.from_bytes(identity[12:16],'little') == config['rate'] == 48000, 'Actual original header')
        short,long = 1 << (identity[28]&15), 1 << (identity[28]>>4)
        need((short,long) == (case['short'],case['long']), 'Actual original block sizes')
        metadata = json.loads((corpus/case['packet_metadata']).read_bytes())
        audio = (corpus/case['audio']).read_bytes()
        need(len(metadata) == len(declaration['audio']) == case['packet_count'] == 14 and
             len(case['offsets']) == 15 and case['offsets'][0] == 0 and case['offsets'][-1] == len(audio), 'Full84 packets including primers')
        model['cases'].append(dict(id=case['id'],order=config['order'],short=short,long=long,
            rate=config['rate'],bark=config['bark'],raw_sha256={kind:sha((corpus/case[kind]).read_bytes()) for kind in ('identification','setup','audio','packet_metadata')}))
        for packet_index,(packet,layout) in enumerate(zip(metadata,declaration['audio'])):
            start,end = case['offsets'][packet_index:packet_index+2]
            fields = witness.read_layout(audio[start:end],layout)
            mode = witness.field(fields,'audio.mode',1)
            need(start == packet['offset'] and end-start == packet['bytes'] and end>start and
                 witness.field(fields,'audio.type',1) == 0 and mode == packet['mode'] == case['mode_flags'][packet_index], 'Every original packet span/type/mode')
            if mode:
                need(witness.field(fields,'audio.previous_window',1) == case['mode_flags'][packet_index-1] and
                     witness.field(fields,'audio.next_window',1) == case['mode_flags'][packet_index+1], 'Actual long neighbors')
            n = (long if mode else short)//2
            for channel in (0,1):
                decoded = witness.floor_and_residue(fields,config,channel,packet)
                exact_lsp = [value * (1 << 24) for value in decoded['coefficients']]
                exact_residue = [value * 256 for value in decoded['residue']]
                need(all(value.denominator == 1 for value in exact_lsp + exact_residue), 'Exact dyadic public inputs')
                lsp, residue = list(map(int,exact_lsp)),list(map(int,exact_residue))
                need(len(lsp) == config['order'] and len(residue) == 16 and all(0 < value < 3*(1<<24) for value in lsp)
                     and all(a<b for a,b in zip(lsp,lsp[1:])) and all(0 < abs(value) <= 3*256 for value in residue), 'Valid bounded public input domain')
                words = [case_index,packet_index,channel,n,config['order'],config['bark'],decoded['public_Tremor_amplitude_Q4'],config['offset'],config['rate']//2]
                words += lsp + [0]*(6-len(lsp)) + residue
                need(len(words) == 31 and n in (32,128,1024), 'Every31-word descriptor/half-block')
                model['calls'].append(dict(call=len(model['calls']),words=words,input_fnv32=fnv(struct.pack('<31i',*words)),
                    lsp_radians_exact=list(map(str,decoded['coefficients'])),amplitude_exact=str(decoded['amplitude']),
                    amplitude_raw=decoded['raw_amplitude'],amplitude_bits=config['amplitude_bits'],
                    original_packet_sha256=sha(audio[start:end])))
                model['counts']['bins'] += n
    need(len(model['calls']) == 168 and len({(row['words'][0],row['words'][1]) for row in model['calls']}) == 84, 'Full6/84/168 model')
    return model


def header(model, model_sha):
    counts=model['counts']
    text = '#pragma once\n#include <stdint.h>\n'
    text += ''.join(f'#define {name} {value}\n' for name,value in (('CURVE_CASES',counts['cases']),('CURVE_PACKETS',counts['packets']),('CURVE_CALLS',counts['calls']),('CURVE_BINS',counts['bins'])))
    text += '#define CURVE_MODEL_SHA "'+model_sha+'"\n'
    text += 'static const int32_t curve_inputs[CURVE_CALLS][31] = {\n'
    text += '\n'.join('  {'+','.join(map(str,row['words']))+'},' for row in model['calls'])+'\n};\n'
    text += 'static const uint32_t curve_input_fnv[CURVE_CALLS] = {\n  '+','.join(str(row['input_fnv32'])+'u' for row in model['calls'])+'\n};\n'
    return text


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--readiness-sha256',required=True)
    args=parser.parse_args()
    repo=next(p for p in HERE.parents if (p/'idf/esp32-cyd2usb-native/main').is_dir())
    out=args.output.resolve()
    need(out.is_relative_to(repo/'.build') and not out.exists() and not out.is_relative_to(HERE) and not HERE.is_relative_to(out), 'Fresh independent runtime under task .build')
    need(sha((HERE/'readiness.json').read_bytes()) == args.readiness_sha256, 'Root-reviewed source readiness required')
    readiness=json.loads((HERE/'readiness.json').read_bytes())
    need(readiness['runtime_executed'] is False and readiness['schema']=='public-floor0-curve-source-only-readiness-v1', 'Source-only preparation')
    actual={p.relative_to(HERE).as_posix() for p in HERE.rglob('*') if p.is_file()}
    need(actual==set(readiness['files'])|{'readiness.json'}, 'Complete preparation inventory')
    for name,row in readiness['files'].items():
        raw=(HERE/name).read_bytes();need(len(raw)==row['bytes'] and sha(raw)==row['sha256'],'Frozen preparation identity')
    model=build_model()
    previous_raw=(HERE/'provenance/actual02/runtime/contract.json').read_bytes()
    need(sha(previous_raw)=='bf0af784b74881770781738cba30966e9f72893fd4d93f89e93df93d61eaeae3','Exact previous original-public contract')
    previous=json.loads(previous_raw)['model']
    need(all(model[key]==previous[key] for key in ('counts','cases','calls')),'All168 original raw descriptors/checksums/counts must remain unchanged by C portability')
    need(sha((HERE/'project/main/public/floor0.c').read_bytes())==PUBLIC_SHA and
         sha((HERE/'provenance/public-port/floor0.original.c').read_bytes())==ORIGINAL_PUBLIC_SHA,'Explicit compiled port/original public source identities')
    model_raw=json.dumps(model,sort_keys=True,separators=(',',':')).encode()
    text=header(model,sha(model_raw))
    recovered=readback(text,model)
    out.mkdir(parents=True,exist_ok=False)
    for source in sorted(HERE.rglob('*')):
        if source.is_file():
            target=out/'source-preparation'/source.relative_to(HERE);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
    shutil.copytree(HERE/'project',out/'project')
    for name in ('run-public-curve.py','owned_qmp.py','windows_compile_command.py','protocol.py'):
        shutil.copyfile(HERE/name,out/name)
    (out/'project/main/data.h').write_text(text,encoding='utf-8',newline='\n')
    contract=dict(schema='public-floor0-curve-contract-v1',model=model,model_sha256=sha(model_raw),header_sha256=sha(text.encode()),readback=recovered,
        previous_raw_descriptors_unchanged=True,previous_contract_sha256=sha(previous_raw),
        public_function_evaluated=False,target_codec_executed=False,reference_decoder_executed=False,PCM_computed=False,numeric_qualified=False,full_G6_qualified=False)
    (out/'contract.json').write_text(json.dumps(contract,indent=2)+'\n',encoding='utf-8',newline='\n')
    for name,row in readiness['files'].items():
        raw=(HERE/name).read_bytes()
        need(len(raw)==row['bytes'] and sha(raw)==row['sha256'] and (out/'source-preparation'/name).read_bytes()==raw,
             'Source changed while deriving/copying public curve runtime')
    for source in (HERE/'project').rglob('*'):
        if source.is_file():
            need((out/'project'/source.relative_to(HERE/'project')).read_bytes()==source.read_bytes(),'Runtime public/owned source copy differs')
    rows={p.relative_to(out).as_posix():dict(bytes=p.stat().st_size,sha256=sha(p.read_bytes())) for p in sorted(out.rglob('*')) if p.is_file()}
    runtime=dict(schema='public-floor0-curve-runtime-readiness-v1',runtime_executed=False,source_readiness_sha256=args.readiness_sha256,files=rows,
        contract_sha256=sha((out/'contract.json').read_bytes()),counts=model['counts'],public_function_evaluated=False,
        target_codec_executed=False,reference_decoder_executed=False,PCM_computed=False,numeric_qualified=False,full_G6_qualified=False)
    (out/'runtime-readiness.json').write_text(json.dumps(runtime,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(materialized=True,public_function_evaluated=False,counts=model['counts'],contract_sha256=runtime['contract_sha256'],runtime_readiness_sha256=sha((out/'runtime-readiness.json').read_bytes()))))


if __name__=='__main__':main()
