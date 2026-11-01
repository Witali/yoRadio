"""Verify original host gain evidence and independent Decimal vectors as data."""
import argparse
from decimal import Decimal,localcontext,ROUND_HALF_UP
import hashlib
import json
import math
from pathlib import Path,PurePosixPath
import zipfile

FOLDER=Path(__file__).resolve().parent
ROOT=FOLDER.parents[2]


def need(condition,reason):
    if not condition:raise ValueError(reason)
def sha(body):return hashlib.sha256(body).hexdigest()


def verify(require_current=False):
    manifest=json.loads((FOLDER/'manifest.json').read_bytes())
    need(manifest['application_integer_pcm_gain'] and not manifest['production_integrated'] and not manifest['native_mcu'] and
         not manifest['numeric_conformance_claim'] and manifest['creator_comparison_numeric_bound'] is None,'precise qualification boundary')
    pin=manifest['archive'];path=FOLDER/pin['path']
    need(path.name=='captures.zip' and path.parent==FOLDER and path.stat().st_size==pin['bytes'] and sha(path.read_bytes())==pin['sha256'],'exact archive')
    with zipfile.ZipFile(path) as archive:
        names=archive.namelist();need(len(names)==len(set(names))==manifest['physical_blobs'],'unique physical inventory')
        blobs={name:archive.read(name) for name in names}
    for name,body in blobs.items():need(name=='blobs/'+sha(body) and not body.startswith(b'\x7fELF'),'all published bytes, no ELF')
    files={}
    for row in manifest['files']:
        name=row['path'];p=PurePosixPath(name);body=blobs[row['blob']]
        need(not p.is_absolute() and '..' not in p.parts and name not in files and len(body)==row['bytes'] and sha(body)==row['sha256'],'exact unique logical bytes')
        files[name]=body
    need(len(files)==manifest['logical_files'] and set(blobs)=={row['blob'] for row in manifest['files']},'complete archive census')
    omitted={row['path']:row for row in manifest['omitted_payloads']}
    need(len(omitted)==2 and all(name not in files and row['original_retained_locally'] and row['byte_payload_published'] is False for name,row in omitted.items()),'two unchanged local-only host executables')
    sources={}
    for label,campaign in manifest['campaigns'].items():
        prefix=label+'/';body=files[prefix+'report.json'];need(sha(body)==campaign['original_report_sha256'],'original report bytes')
        report=json.loads(body)
        need(report['passed'] and report['state']=='complete' and report['all_source_bindings_unchanged'] and
             not report['numeric_conformance_claim'] and not report['production_integrated'],'original passing scoped outcome')
        for row in report['sources']:
            frozen=files[prefix+row['snapshot']]
            need(sha(frozen)==row['sha256'] and len(frozen)==row['bytes'],'every original frozen source')
        sources[label]=report['sources']
        for name,row in report['generated'].items():
            frozen=files[prefix+name];need(sha(frozen)==row['sha256'] and len(frozen)==row['bytes'],'all independently generated input bytes')
        commands=report['commands'];need(len({row['name'] for row in commands})==len(commands) and
            {'build','test','libopus-post-sha256','libm-post-sha256'}<={row['name'] for row in commands},'complete actual command inventory')
        for command in commands:
            need(command['pid']>0 and command['state']=='complete' and command['exit_status']==0 and not command.get('timed_out'),'every actual child terminal zero')
            for stream in ('stdout','stderr'):
                row=command[stream];raw=files[prefix+row['path']]
                need(sha(raw)==row['sha256'] and len(raw)==row['bytes'],'every original native log')
        build=next(row for row in commands if row['name']=='build')
        need('-fsanitize=address,undefined,float-cast-overflow' in build['argv'] and '-Werror' in build['argv'] and
             not any(value.startswith('-DNDEBUG') for value in build['argv']),'sanitizers/cast checks/assertions remain enabled')
        binary=report['binary'];local=omitted[prefix+binary['path']]
        need(local['sha256']==binary['sha256'] and local['bytes']==binary['bytes'] and binary['local_only'],'exact executable omission identity without reading bytes')
        vectors=json.loads(files[prefix+'reference-vectors.json'])
        need(len(vectors)==1125 and report['reference']['precisions']==[80,120] and report['reference']['identical_vectors'],'selected independent reference census')
        lines=['#pragma once','typedef struct { int32_t gain; unsigned format,width; uint8_t input[4],expected[4]; } reference_vector;','static const reference_vector gain_vectors[] = {']
        with localcontext() as context:
            context.prec=100
            for row in vectors:
                name=row['format'];width=row['width'];low=-(1<<(width*8-1));high=-low-1
                need((name,row['format_id'],width) in [('U8',0,1),('S8',1,1),('S16LE',2,2),('S24LE',3,3),('S32LE',4,4)],'known explicit packed layout')
                factor=Decimal(10)**(Decimal(row['gain_q8'])/Decimal(5120))
                sample=max(low,min(high,int((Decimal(row['sample'])*factor).to_integral_value(rounding=ROUND_HALF_UP))))
                before=[row['sample']+128] if name=='U8' else list(row['sample'].to_bytes(width,'little',signed=True))
                after=[sample+128] if name=='U8' else list(sample.to_bytes(width,'little',signed=True))
                need(row['input']==before and row['expected']==after and row['expected_sample']==sample,'independent100-digit integer-PCM reference')
                lines.append('{%d,%u,%u,{%s},{%s}},'%(row['gain_q8'],row['format_id'],width,','.join(map(str,before)),','.join(map(str,after))))
        lines.append('};')
        need(files[prefix+'vectors.h'].decode().replace('\r\n','\n')=='\n'.join(lines)+'\n','actual compiled expected arrays match independent reference')
        rows=[json.loads(line) for line in files[prefix+'test.stdout.log'].decode().splitlines()]
        need(rows==report['test_records'] and len(rows)==11 and all(row['passed'] for row in rows) and
             not files[prefix+'test.stderr.log'],'complete native test transcript, no sanitizer diagnostics')
        complete=rows[-1];full=rows[0]
        need(complete['reference_vectors']==1125 and complete['vector_applications']==4500 and complete['identity_cases']==20 and
             complete['refusal_cases']==81 and complete['reuse_cases']==64 and complete['creator_observations']==9 and
             complete.get('overflow_guard_cases',0)==(5 if label=='host02' else 0),'all measured selected checks')
        need(full['factors']==65536 and full['silent_span_applications']==327680 and full['pow_calls']==65535 and
             full['finite_positive_monotone'],'entire signed Q7.8 gain range')
        need([row['gain_q8'] for row in rows[1:-1]]==[-32768,-1536,-256,-1,0,1,256,1536,32767],'all creator gain observations')
        for observation in rows[1:-1]:
            need(observation['creator']=='libopus 1.4' and observation['samples']==1920 and
                 observation['numerical_acceptance_bound'] is None and not observation['numeric_conformance_claim'] and
                 all(math.isfinite(observation[name]) and observation[name]>=0 for name in ('factor','max_absolute_difference','max_reference_magnitude','difference_energy')),'creator comparison is measured evidence without an invented numeric bound')
        for field,command_name in (('libopus_identity','libopus-post-sha256'),('libm_identity','libm-post-sha256')):
            need(files[prefix+command_name+'.stdout.log'].decode().strip()==report[field],'unchanged creator/libm executable identity')
    header='idf/components/native_stream/include/pcm_header_gain.h'
    old=next(row for row in sources['host01'] if row['path']==header)
    final=next(row for row in sources['host02'] if row['path']==header)
    need(old['sha256']==final['sha256'],'same primitive in both actual passing runs')
    if require_current:
        for row in sources['host02']:need(sha((ROOT/row['path']).read_bytes())==row['sha256'],'explicit current source binding')
    return dict(passed=True,logical_files=len(files),physical_blobs=len(blobs),legal_gains=65536,
                decimal_vectors=1125,exact_vector_applications=4500,creator_observations=9,
                creator_numeric_bound=None,production_integrated=False,current_sources_compared=require_current,
                archived_code_executed=False,omitted_executable_bytes_read=False)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--require-current',action='store_true')
    print(json.dumps(verify(parser.parse_args().require_current)))
