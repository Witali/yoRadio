"""Qualify explicit speaker layouts through real CYD readers and three producers."""
import argparse
from decimal import Decimal, localcontext, ROUND_HALF_UP
from functools import lru_cache
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


@lru_cache(None)
def matrices(channels,precision):
    return mix.reference(channels,precision)


@lru_cache(None)
def header_factor(gain,precision):
    with localcontext() as context:
        context.prec=precision
        return Decimal(10)**(Decimal(gain)/5120)


def expected_mono(samples,gain,volume,balance,precision):
    channels=len(samples)
    if channels<=2:
        return headers.expected_mono(gain,samples[0],samples[1] if channels==2 else 0,
                                     channels,volume,balance,precision)
    with localcontext() as context:
        context.prec=precision
        left,right=matrices(channels,precision)
        gl=(volume*(16+balance if balance<0 else 16)*32768+2032)//4064
        gr=(volume*(16-balance if balance>0 else 16)*32768+2032)//4064
        # Exact row sums avoid turning a mathematical half-integer into
        # opposing tiny Decimal errors at different reference precisions.
        if all(n==samples[0] for n in samples):
            value=Decimal(samples[0]*(gl+gr)*(1 if channels<=4 else 2))
        else:
            value=sum(Decimal(n)*(l*gl+r*gr) for n,l,r in zip(samples,left,right))
        value=value*header_factor(gain,precision)/65536
        rounded=int(value.to_integral_value(rounding=ROUND_HALF_UP))
        return min(32767,max(-32768,rounded))


def vectors():
    rows=[]
    for channels in range(1,9):
        patterns=[[25000 if c==speaker else 0 for c in range(channels)] for speaker in range(channels)]
        patterns.extend([[32767]*channels,[-32768]*channels,
                         [30000 if c%2==0 else -30000 for c in range(channels)],
                         [1]*channels,[-1]*channels])
        if channels>1:
            cancellation=[0]*channels;cancellation[0]=30000
            cancellation[1 if channels in (2,4) else 2]=-30000
            patterns.append(cancellation)
        for bits,gain,volume,balance,pattern in itertools.product(
                (8,16,24,32),(-32768,-1536,0,1536,12288,32767),(0,1,127,254),(-16,0,16),patterns):
            samples=[(n//256)*256 if bits==8 else n for n in pattern]
            a=expected_mono(tuple(samples),gain,volume,balance,100)
            b=expected_mono(tuple(samples),gain,volume,balance,160)
            if a!=b:raise ValueError('reference precision disagreement')
            rows.append(dict(channels=channels,bits=bits,gain=gain,volume=volume,balance=balance,samples=samples,expected=a))
    return rows


def main():
    global mix,headers
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True,type=Path)
    out=parser.parse_args().output.resolve()
    if not out.is_relative_to(ROOT/'.build') or out.exists():raise ValueError('fresh ignored capture')
    out.mkdir(parents=True)
    production=Path('idf/esp32-cyd2usb-native/main/native_audio_output.c')
    include=Path('idf/components/native_stream/include')
    adapter=Path('idf/components/native_audio_normalizer')
    algorithm=Path('yoRadio/src/audioI2S')
    harness=Path('tests/native/cyd_surround_output_test.c')
    bridge=Path('tests/native/cyd_surround_output_reference.cpp')
    platform=Path('tests/native/cyd_normalizer_test.c')
    paths=[Path(__file__).resolve().relative_to(ROOT),production,production.with_suffix('.h'),harness,bridge,platform,
           *[include/name for name in ('pcm_header_gain.h','pcm_channel_layout.h','pcm_speaker_mix.h')],
           *[adapter/name for name in ('native_audio_normalizer.cpp','native_audio_normalizer.h')],
           *[algorithm/name for name in ('AudioNormalizer.cpp','AudioNormalizer.h')],
           Path('tests/native/cyd_output_metrics_noop.h'),Path('tests/run-cyd-output-gain.py'),
           Path('tests/run-cyd-header-gain.py'),Path('tests/run-pcm-speaker-mix-host.py'),
           Path('tools/codec_benchmark/run_output_dma_host.py')]
    report=dict(passed=False,state='preparing',sources={},variants={},physical_hardware=False,
                production_layout_queue_selected=False,full_codec_conformance_claim=False)
    def save():(out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    for path in paths:
        body=(ROOT/path).read_bytes();target=out/'sources'/path
        target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(body)
        report['sources'][path.as_posix()]=hashlib.sha256(body).hexdigest()
    save()
    try:
        helper=load('surround_extract',ROOT/'tests/run-cyd-output-gain.py')
        mix=load('surround_matrix_oracle',ROOT/'tests/run-pcm-speaker-mix-host.py')
        headers=load('surround_header_oracle',ROOT/'tests/run-cyd-header-gain.py')
        common_tools=load('surround_host_tools',ROOT/'tools/codec_benchmark/run_output_dma_host.py')
        host,run=common_tools.host,common_tools.run
        rows=vectors();report['decimal_vectors']=len(rows)
        matrix=''
        for side,name in ((0,'reference_left'),(1,'reference_right')):
            matrix+='static const long double '+name+'[8][8] = {\n'
            for channels in range(1,9):matrix+=' {'+','.join(format(n,'.60g')+'L' for n in matrices(channels,160)[side])+'},\n'
            matrix+='};\n'
        declarations='typedef struct {unsigned channels,bits;int gain;unsigned volume;int balance;int16_t samples[8];int expected;} surround_vector;\n'
        declarations+='static const surround_vector surround_vectors[] = {\n'
        for row in rows:
            declarations+=' {'+','.join(str(row[k]) for k in ('channels','bits','gain','volume','balance'))+', {'+','.join(map(str,row['samples']))+'}, '+str(row['expected'])+'},\n'
        (out/'surround_vectors.h').write_text(matrix+declarations+'};\n')
        (out/'surround_vectors.json').write_text(json.dumps(rows,separators=(',',':'))+'\n')
        frozen=out/'sources';source=(frozen/production).read_text()
        common=source[source.index('static int16_t scale_sample_q15('):source.index('#if CONFIG_YORADIO_NATIVE_AUDIO_OUTPUT_PDM')]
        constants='\n'.join(re.findall(r'^#define [^\n]+',source,re.M))+'\n'
        branches={name:source.split(start,1)[1].split(end,1)[0] for name,start,end in (
            ('pdm','#if CONFIG_YORADIO_NATIVE_AUDIO_OUTPUT_PDM','#elif CONFIG_YORADIO_NATIVE_AUDIO_OUTPUT_DAC'),
            ('dac','#elif CONFIG_YORADIO_NATIVE_AUDIO_OUTPUT_DAC','#elif CONFIG_YORADIO_NATIVE_AUDIO_OUTPUT_LEGACY_DAC'))}
        branches['legacy']=source.split('#elif CONFIG_YORADIO_NATIVE_AUDIO_OUTPUT_LEGACY_DAC',1)[1]
        platform_text=(frozen/platform).read_text().split('/* PRODUCTION */',1)[0]
        flags=['-O2','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined,float-cast-overflow','-fno-omit-frame-pointer','-fno-pie','-pthread']
        objects=[]
        for path in (adapter/'native_audio_normalizer.cpp',algorithm/'AudioNormalizer.cpp',bridge):
            obj=out/(path.stem+'.o');objects.append(host(obj))
            (out/(path.stem+'-build.log')).write_bytes(run(['g++','-std=c++17',*flags,
                '-I'+host(frozen/adapter),'-I'+host(frozen/algorithm),'-c',host(frozen/path),'-o',host(obj)]))
        report['state']='executing';save()
        for backend,branch in branches.items():
            p=platform_text
            generated='#include "pcm_header_gain.h"\n#include "pcm_channel_layout.h"\n#include "pcm_speaker_mix.h"\n'+constants+common
            if backend=='pdm':
                for name in ('pdm_write_resampled','pdm_flush','reset_resampler'):
                    p=p.replace(helper.function(p,name).rstrip(),'',1)
                generated+=''.join(helper.function(branch,name) for name in ('reset_resampler','pdm_write_block','pdm_flush','pdm_queue_sample','pdm_write_resampled'))
            if backend=='dac':generated+=helper.function(branch,'dac_write_block')
            if backend=='legacy':generated+=''.join(helper.function(branch,name) for name in ('legacy_pack_dac_code','legacy_fractional_dac_step','legacy_write_frames','legacy_write_silence'))
            generated+=''.join(helper.function(branch,name) for name in ('native_audio_output_configure','native_audio_output_write_pcm','native_audio_output_discard_pcm','native_audio_output_flush_pcm','native_audio_output_pause'))
            (out/(backend+'.inc')).write_text(generated)
            unit,obj,binary=out/(backend+'.c'),out/(backend+'.o'),out/backend
            unit.write_text((frozen/harness).read_text().replace('/* PLATFORM */',p).replace('/* PRODUCTION */',generated))
            (out/(backend+'-build.log')).write_bytes(run(['gcc','-std=c11',*flags,'-Wno-unused-function','-Wno-unused-variable',
                '-DTEST_'+backend.upper()+'=1','-I'+host(frozen/'tests/native'),'-I'+host(frozen/adapter),'-I'+host(frozen/include),'-I'+host(out),'-c',host(unit),'-o',host(obj)]))
            (out/(backend+'-link.log')).write_bytes(run(['g++',*flags,'-no-pie',host(obj),*objects,
                *['-Wl,--wrap='+name for name in ('native_audio_normalizer_configure','native_audio_normalizer_reset','native_audio_normalizer_process_block','native_audio_normalizer_process_multichannel_block')],'-lm','-o',host(binary)]))
            trace=out/(backend+'-reference.csv')
            log=run(['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1','UBSAN_OPTIONS=halt_on_error=1',host(binary),host(trace)])
            (out/(backend+'.log')).write_bytes(log)
            checks=0
            for line in trace.read_text().splitlines():
                values=list(map(int,line.split(',')));channels,gain,volume,balance=values[:4]
                if len(values)!=channels+5:raise ValueError('complete traced logical channels')
                samples=tuple(values[4:-1]);actual=values[-1]
                if any(expected_mono(samples,gain,volume,balance,p)!=actual for p in (100,160)):
                    raise ValueError('independent complete-channel Decimal trace differs')
                checks+=1
            report['variants'][backend]=dict(passed=True,result=log.decode().strip(),decimal_trace_checks=checks);save()
            print(backend+': '+log.decode().strip(),flush=True)
        if not all(sha(ROOT/path)==report['sources'][path.as_posix()] for path in paths):raise ValueError('sources changed during qualification')
        report.update(passed=True,state='complete',all_source_bindings_current=True,compiler=run(['gcc','--version']).decode().splitlines()[0])
    except BaseException as error:
        report.update(passed=False,state='nonpass',error=type(error).__name__)
        if isinstance(error,subprocess.CalledProcessError):(out/'failure.log').write_bytes(error.output)
        raise
    finally:save()


if __name__=='__main__':main()
