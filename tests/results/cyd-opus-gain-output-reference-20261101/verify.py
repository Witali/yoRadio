"""Verify independent mono reference data; execute no decoder or gain helper."""
from decimal import Decimal,localcontext,ROUND_HALF_UP
import hashlib
import json
from pathlib import Path

FOLDER=Path(__file__).resolve().parent
ROOT=FOLDER.parents[2]


def need(value,reason):
    if not value:raise ValueError(reason)


def sha(body):return hashlib.sha256(body).hexdigest()


def verify():
    manifest=json.loads((FOLDER/'manifest.json').read_bytes())
    for row in manifest['files']:
        body=(FOLDER/row['path']).read_bytes()
        need(sha(body)==row['sha256'] and len(body)==row['bytes'],'every published original byte')
    code=(ROOT/'tests/prepare-cyd-opus-gain-output-reference.py').read_bytes()
    need(code==(FOLDER/'controller.py').read_bytes() and sha(code)==manifest['controller_sha256'],'exact canonical independent mono preparer')
    report=json.loads((FOLDER/'report.json').read_bytes())
    need(report['passed'] and report['all_source_bindings_current'] and not report['decoder_executed'] and
         not report['native_target_executed'] and not report['production_gain_qualified'] and
         not report['normalization_enabled'],'independent data preparation scope')
    need(report['full_references']==len(report['references'])==56 and report['selected_vectors']==len(report['vectors'])==7200 and
         report['checked_stereo_sum_entries']==3145704 and report['decimal_precision_digits']==[100,160],'complete original reference census')

    def q15(value):
        return (value+16384)//32768 if value>=0 else -((-value+16384)//32768)

    factors={}
    with localcontext() as context:
        context.prec=120
        for row in report['vectors']:
            gain,volume,balance,channels=(row[key] for key in ('gain_q8','volume','balance','channels'))
            left=(volume*(16+balance if channels>1 and balance<0 else 16)*32768+2032)//4064
            right=(volume*(16-balance if balance>0 else 16)*32768+2032)//4064
            if gain:
                if gain not in factors:factors[gain]=Decimal(10)**(Decimal(gain)/Decimal(5120))
                wide=Decimal(row['left']*left+(row['right']*right if channels>1 else 0))*factors[gain]/Decimal(32768*(2 if channels>1 else 1))
                expected=max(-32768,min(32767,int(wide.to_integral_value(rounding=ROUND_HALF_UP))))
            else:
                expected=q15(row['left']*left)
                if channels>1:
                    total=expected+q15(row['right']*right)
                    expected=total//2 if total>=0 else -((-total)//2)
            need(expected==row['expected'],'every mono/balance/layout vector recomputed at120 Decimal digits')
    silence=sha(bytes(1056000))
    for row in report['references']:
        need(row['bytes']==1056000 and row['frames']==528000 and row['balance']==0 and not row['normalization'],
             'all original final mono rows cover the complete retained span')
        if row['volume']==0 or row['gain_q8']==-32768:
            need(row['sha256']==silence and row['nonzero_samples']==0,'exact full silence references')
        if row['gain_q8']==12288 and row['volume']==1:
            need(row['saturation_samples']==0 and row['peak']>1000,'full anti-early-clipping output is unsaturated and audible')
    omitted=manifest['omitted_local_payloads']
    need(len(omitted)==2 and all(row['original_retained_locally'] and row['byte_payload_published'] is False and row['bytes']>0 for row in omitted),
         'two original complete stock PCM payloads stay local with exact identities')
    print(json.dumps(dict(passed=True,full_mono_references=56,selected_vectors_recomputed=7200,
        decoder_executed=False,production_gain_qualified=False,omitted_full_pcm_recomputed=False)))


if __name__=='__main__':verify()
