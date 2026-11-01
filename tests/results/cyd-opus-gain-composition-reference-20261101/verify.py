"""Verify independent gain data; execute no decoder, MCU, archived program or gain helper."""
from decimal import Decimal,localcontext,ROUND_HALF_UP
import hashlib
import importlib.util
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
    report=json.loads((FOLDER/'report.json').read_bytes())
    code=ROOT/'tests/prepare-cyd-opus-gain-playback.py'
    need(sha(code.read_bytes())==manifest['controller_sha256'] and
         (FOLDER/'controller.py').read_bytes()==code.read_bytes(),'pinned reviewed canonical data preparer')
    need(report['passed'] and report['all_source_bindings_current'] and not report['decoder_executed'] and
         not report['native_target_executed'] and not report['production_gain_qualified'] and
         not report['mono_mixing_policy_qualified'] and not report['normalizer_policy_qualified'] and
         not report['numeric_codec_conformance_claim'],'reference preparation has no production or codec acceptance claim')
    need(report['decimal_precision_digits']==[100,160] and report['distinct_signed16_tables']==28 and
         report['signed16_table_entries']==1835008 and len(report['variants'])==14 and len(report['references'])==56 and
         len(report['vectors'])==420,'actual complete gain/volume data census')
    spec=importlib.util.spec_from_file_location('reviewed_gain_fixture_data',code)
    preparer=importlib.util.module_from_spec(spec);spec.loader.exec_module(preparer)
    for name,pin in preparer.FIXTURES.items():
        body=(ROOT/pin['path']).read_bytes()
        need(len(body)==pin['bytes'] and sha(body)==pin['sha256'],'complete current canonical source fixture')
        pages,packets=preparer.parse(body)
        need(int.from_bytes(packets[0][10:12],'little')==312 and pages[-1]['granule']==528312,'unchanged actual playback bounds')
        for row in [row for row in report['variants'] if row['fixture']==name]:
            changed=preparer.mutate(body,pages,row['gain_q8'],row['serial'])
            need(sha(changed)==row['sha256'] and len(changed)==row['bytes'],'reconstruct complete legal gain/serial view without executing a decoder')
            for i,page in enumerate(pages):
                patch=row['patches'][i];stop=page['end'] if i==0 else page['offset']+27
                need(patch['offset']==page['offset'] and patch['bytes']==stop-page['offset'] and
                     bytes.fromhex(patch['header_hex'])==changed[page['offset']:stop],'all exact small header overlays')
    with localcontext() as context:
        context.prec=120
        for row in report['vectors']:
            denominator=254*16
            player=(row['volume']*16*32768+denominator//2)//denominator
            need(player==row['player_q15'],'existing player gain independently evaluated')
            factor=(Decimal(10)**(Decimal(row['gain_q8'])/Decimal(5120)))*Decimal(player)/Decimal(32768)
            expected=int((Decimal(row['input'])*factor).to_integral_value(rounding=ROUND_HALF_UP))
            need(row['expected']==max(-32768,min(32767,expected)),'every selected vector independently recomputed at120 Decimal digits')
    silence=sha(bytes(2112000))
    for row in report['references']:
        need(row['bytes']==2112000 and row['samples']==1056000 and row['player_q15']==preparer.q15(row['volume']),
             'all full reference rows cover every retained stereo sample')
        if row['volume']==0 or row['gain_q8']==-32768:
            need(row['sha256']==silence and row['nonzero_samples']==0,'exact full mute/extreme-negative silence')
        if row['gain_q8']==0 and row['volume']==254:
            need(row['sha256']==preparer.FIXTURES[row['fixture']]['logical_sha'],'zero gain preserves the earlier exact logical output')
        if row['gain_q8']==12288 and row['volume']==1:
            need(row['saturation_samples']==0 and row['differs_from_header_clip_then_player_samples']>900000,
                 'early-clipping counterexample affects actual full unsaturated output')
    omitted=manifest['omitted_local_payloads']
    need(len(omitted)==18 and all(row['original_retained_locally'] and row['byte_payload_published'] is False for row in omitted),
         'complete stock PCM/encoded variants remain local with identities')
    print(json.dumps(dict(passed=True,crc_valid_full_views=14,full_stereo_references=56,
        selected_vectors_recomputed=420,archived_code_executed=False,decoder_executed=False,
        production_gain_qualified=False,omitted_full_pcm_recomputed=False)))


if __name__=='__main__':verify()
