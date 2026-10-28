"""Independently replay the timer correction and validate archived runtime evidence."""
import argparse
from copy import deepcopy
import gzip
import io
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from audit_factory_xrefs import sha
from reverse.nothrow_linkage import LinkedRuntime
from keep_alive_range_test import run
from keep_alive_range_runtime_evidence import timer,network,display,owners
from verify_wifi_producer_evidence import verify as before_verify


def bounded_gzip(path, maximum=2097152):
    """Read a bounded report/frame without allowing unbounded decompression."""
    compressed=path.read_bytes();assert len(compressed)<=262144
    with gzip.GzipFile(fileobj=io.BytesIO(compressed)) as stream:raw=stream.read(maximum+1)
    assert len(raw)<=maximum
    return compressed,raw


def payload(base, ref):
    """Validate path, size and both hashes before interpreting a report."""
    path=(base/ref['file']).resolve();assert path.is_relative_to(base.resolve())
    compressed,raw=bounded_gzip(path)
    assert sha(compressed)==ref['gzip_sha256'] and sha(raw)==ref['sha256'] and len(raw)==ref['bytes']
    return json.loads(raw)


def pins(values):
    """Require the exact original local inputs, preserving old build identities."""
    for name,digest in values.items():assert sha(Path(name).read_bytes())==digest,('Changed input',name)


def owner_bytes(path):
    """Read either the original local JSON or its byte-preserving archive copy."""
    return bounded_gzip(path)[1] if path.suffix=='.gz' else path.read_bytes()


def same(recorded,measured):
    """Reject any altered argument, effect, coverage, binding or claimed scope."""
    if recorded!=measured:raise ValueError('Timer range evidence differs from instruction replay')


def baseline(root):
    """Replay the preserved factory/native failing-before producer proof unchanged."""
    path=root/'Small_TV/qemu/parity/factory-wifi-producer-validation-20261028.json'
    proof=json.loads(path.read_bytes());recorded=payload(path.parent,proof['report'])
    inputs=recorded['inputs_sha256'];pins(inputs)
    def selected(digest):
        matches=[Path(name) for name,value in inputs.items() if value==digest]
        assert len(matches)==1;return matches[0]
    result=before_verify(path,root,
        selected('8c9fd166a6536bc1bc236fc98018eb0daba9aad01ce8356511ad68eba03de882'),
        selected('9e4ec88d6e85ae58fa3e164362f1b10491f9edef0feaa4af8c52c9fa88446e24'),
        selected('da1ed0ce8c3af0f29d7851d8ac4e0c96dfe52ab9438df3274c8f6b09eaaf49c1'),
        selected('8758bd09c80e707e400ec6059b39cdcfde05b71daa297cfc4fd36ac35dfbcf1a'),
        selected('b460bb305a8d3c5e93489a03710108a06435d58bf12410e080c0c6805a74bade'),
        selected('c7797847c9229cc14b27194b5b7ccd63c20e2c909815d72e189973dd9f2a1aa2'),
        selected('8f989ecd7104520083727442247aed08ad93ef2bc304ae727022f8573f4bc558'),
        selected('c2df6fcca4c1c19c9c6b8171f16461e52a636da90dd7f7be3b67bed4fbe71cca'),
        selected('c8a9c8884c8397c273672fe03d5caed85ae3c62c34c299373bd21e1de31b990a'))
    assert result['timer_safety_gate_passed'] is False and result['conditional_timer_defect_baseline']
    return result


def frames(root, report, project):
    """Rehash original saved rasters and the independent factory setup reference."""
    result={'reference':bounded_gzip(project/'tests/fixtures/display/factory-setup.ppm.gz')[1]}
    for row in report['cycles']:
        ref=row['frame'];path=(root/ref['file']).resolve();assert path.is_relative_to(root.resolve())
        compressed,raw=bounded_gzip(path);assert sha(compressed)==ref['sha256']
        result[row['variant']]=raw
    return result


def mutations(data,linked,libraries,owned,rasters):
    """Reject semantic corruption even after archive hashes have already been checked."""
    rejected=[]
    actions={}
    for fault in ('delay-truncated','alarm-truncated','raw-alarm-truncated','cancel-not-zero',
                  'wrong-field-address','wrong-dwarf','bss-feature-enabled','wrong-arm-return',
                  'wrong-cancel-return','extra-fixture-write','unclean-owner-exit'):
        changed=deepcopy(data['long-timer'])
        if fault=='delay-truncated':changed['api_delay_us']&=0xffffffff
        elif fault=='alarm-truncated':changed['observations'][0]['alarm']&=0xffffffff
        elif fault=='raw-alarm-truncated':
            row=changed['observations'][0];row['alarm']&=0xffffffff
            row['raw_reads'][2]['hex']=row['alarm'].to_bytes(8,'little').hex()
        elif fault=='cancel-not-zero':
            row=changed['observations'][3];row['alarm']=1;row['raw_reads'][2]['hex']='0100000000000000'
        elif fault=='wrong-field-address':changed['observations'][1]['raw_reads'][2]['address']+=4
        elif fault=='wrong-dwarf':changed['native_dwarf']['esp_timer']['fields']['alarm']['size']=4
        elif fault=='bss-feature-enabled':changed['observed_feature_enabled']=True
        elif fault=='wrong-arm-return':changed['observations'][0]['pc']+=2
        elif fault=='wrong-cancel-return':changed['observations'][3]['pc']+=2
        elif fault=='extra-fixture-write':changed['fixture_writes'].append(deepcopy(changed['fixture_writes'][0]))
        else:changed['exit_code']=1
        actions[fault]=lambda changed=changed:timer(changed,linked,data['cpu']['qualification'],libraries)
    for fault in ('stale-ntp','forged-ntp-difference','wrong-station-address','network-with-lcd'):
        changed=deepcopy(data['network'])
        if fault=='stale-ntp':changed['phases'][2]['network']['ntp']['response_count']=0
        elif fault=='forged-ntp-difference':changed['phases'][0]['network']['ntp']['difference_seconds']=0
        elif fault=='wrong-station-address':changed['phases'][0]['network']['state']['station_address']='127.0.0.1'
        else:changed['display_tested']=True
        actions[fault]=lambda changed=changed:network(changed)
    for fault in ('wrong-lcd','display-network-coupling','changed-pixel'):
        changed=deepcopy(data['display']);pixels=deepcopy(rasters)
        if fault=='wrong-lcd':changed['cycles'][1]['display']['differing_rgb_bytes']=1
        elif fault=='display-network-coupling':changed['network']['executed']=True
        else:pixels['reconstructed']=pixels['reconstructed'][:-1]+bytes([pixels['reconstructed'][-1]^1])
        actions[fault]=lambda changed=changed,pixels=pixels:display(changed,pixels)
    changed=deepcopy(owned);changed['owners'][0]['matching_owner_present']=True
    actions['live-owner']=lambda:owners(changed,data['network'],data['display'],data['long-timer'])
    for fault,action in actions.items():
        try:action()
        except (AssertionError,ValueError):rejected.append(fault)
        else:raise AssertionError('Altered runtime evidence accepted: '+fault)
    for fault in ('wrong-execution-count','wrong-ms-unit','incomplete-coverage','false-lifecycle'):
        changed=deepcopy(data['cpu']);changed.pop('inputs_sha256');changed.pop('inputs_unchanged')
        expected=deepcopy(changed)
        if fault=='wrong-execution-count':changed['instructions']['executions']-=1
        elif fault=='wrong-ms-unit':changed['instructions']['samples']['period-4197']['result']['effects'][-1][1]//=1000
        elif fault=='incomplete-coverage':changed['instructions']['coverage'][0]['visited']-=1
        else:changed['full_runtime_lifecycle_proved']=True
        try:same(changed,expected)
        except ValueError:rejected.append(fault)
        else:raise AssertionError('Altered CPU evidence accepted: '+fault)
    return rejected


def verify(args):
    """Read immutable reports, replay both generations and recompute runtime conclusions."""
    proof=json.loads(args.proof.read_bytes());assert proof['schema']=='small-tv-keep-alive-range-validation-v1'
    assert proof['passed'] and not proof['bss_feature_enabled'] and not proof['decoder_flash_budget_changed']
    for name in ('full_runtime_lifecycle_proved','whole_image_completeness_proved','physical_hardware_tested',
                 'full_suite_passed','soak_24h_passed','independent_evidence_consumer_complete'):
        assert proof[name] is False
    for name,digest in proof['source_pins'].items():
        path=(args.root/name).resolve();assert path.is_relative_to(args.root.resolve()) and sha(path.read_bytes())==digest
    data={name:payload(args.proof.parent,row) for name,row in proof['reports'].items()}
    for report in data.values():
        assert report['passed']
        if 'inputs_sha256' in report:assert report['inputs_unchanged'];pins(report['inputs_sha256'])
    archived=args.root/'firmware/development/small-tv-esp32c2-reconstructed'
    elf=args.build/'small_tv_reconstructed.elf';app=archived/'app.bin'
    assert sha(elf.read_bytes())==proof['elf_sha256'] and sha(app.read_bytes())==proof['app_sha256']
    source=json.loads((archived/'source-manifest.json').read_bytes());assert source['aggregate_sha256']==proof['source_sha256']
    assert sha(json.dumps(source['files'],separators=(',',':'),sort_keys=True).encode())==source['aggregate_sha256']
    for row in source['files']:
        path=args.build/'resources'/row['file'][10:] if row['file'].startswith('generated/') else args.root/'Small_TV/src'/row['file']
        assert sha(path.read_bytes())==row['sha256'],('Production input changed',row['file'])
    before=baseline(args.baseline_root)
    libraries=args.sdk/'components/esp_wifi/lib/esp32c2'
    measured=run(elf.read_bytes(),app.read_bytes(),libraries,
        (args.build/'esp-idf/app/CMakeFiles/__idf_app.dir/network/wifi_keep_alive.c.obj').read_bytes(),
        (args.build/'esp-idf/esp_timer/CMakeFiles/__idf_esp_timer.dir/src/ets_timer_legacy.c.obj').read_bytes(),
        (args.sdk/'components/esp_timer/src/ets_timer_legacy.c').read_bytes(),
        (args.baseline_root/'.build/nvs-storage-fixed-20261026/small_tv_reconstructed.elf').read_bytes(),
        (args.baseline_root/'firmware/development/small-tv-esp32c2-reconstructed/app.bin').read_bytes())
    recorded=deepcopy(data['cpu']);recorded.pop('inputs_sha256');recorded.pop('inputs_unchanged')
    same(recorded,json.loads(json.dumps(measured)))
    linked=LinkedRuntime(elf.read_bytes(),app.read_bytes())
    live=timer(data['long-timer'],linked,measured['qualification'],libraries)
    net=network(data['network']);rasters=frames(args.display_root,data['display'],args.root/'Small_TV/src')
    panel=display(data['display'],rasters)
    assert data['display']['app_sha256']==proof['app_sha256'] and data['display']['native_elf_sha256']==proof['elf_sha256']
    for report in (data['network'],data['long-timer']):
        assert report['inputs_sha256'][str(elf.resolve())]==proof['elf_sha256']
    owned=json.loads(owner_bytes(args.owners));owners(owned,data['network'],data['display'],data['long-timer'])
    assert data['native']['checks']==6298 and data['privacy']['assertions']==3727 and data['nothrow']['cases']==26
    artifact=data['artifact'];assert artifact['cases']==8 and artifact['errors']==artifact['failures']==0
    assert artifact['app_sha256']==proof['app_sha256'] and artifact['source_sha256']==proof['source_sha256']
    rejected=mutations(data,linked,libraries,owned,rasters)
    return dict(passed=True,before=before,executions=measured['instructions']['executions'],
        static_controls=measured['rejected_controls'],evidence_controls=rejected,
        timer=live,network=net,display=panel,owners_absent=5,
        independent_evidence_consumer_complete=True,full_runtime_lifecycle_proved=False,
        whole_image_completeness_proved=False,physical_hardware_tested=False,
        full_suite_passed=False,soak_24h_passed=False)


def main():
    """Run offline CPU replay only and preserve any previous verification result."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[3])
    for name in ('proof','build','sdk','baseline-root','display-root','owners','output'):
        parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args();assert not args.output.exists()
    result=verify(args);args.output.parent.mkdir(parents=True,exist_ok=True)
    result['verifier_sha256']=sha(Path(__file__).read_bytes())
    result['runtime_validator_sha256']=sha(Path(__file__).with_name('keep_alive_range_runtime_evidence.py').read_bytes())
    result['proof_sha256']=sha(args.proof.read_bytes());result['owners_sha256']=sha(owner_bytes(args.owners))
    args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result))


if __name__=='__main__':main()
