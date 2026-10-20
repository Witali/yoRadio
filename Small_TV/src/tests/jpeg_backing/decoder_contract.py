"""Real decoder/NOR pixels, physical failures and bounded-stop recovery."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess


def sha(path):
    """Identify the exact independent oracle, fixture, program and source inputs."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    """Retain physical partial writes across two jobs of the same decoder."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build',type=Path,required=True)
    parser.add_argument('--oracle',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();out=args.output.resolve();out.mkdir(parents=True,exist_ok=False)
    build=json.loads((args.build/'build.json').read_text());oracle=json.loads((args.oracle/'report.json').read_text())
    assert oracle['passed'] and sha(Path(build['executable']))==build['executable_sha256']
    pins=json.loads((args.build/'inputs.json').read_text());pins[str(Path(__file__).resolve())]=sha(Path(__file__))
    pins[str((args.oracle/'report.json').resolve())]=sha(args.oracle/'report.json')
    assert all(sha(Path(p))==h for p,h in pins.items())
    fixtures=args.oracle/'fixtures';first=out/'first.rgb';second=out/'second.rgb'
    report=dict(passed=False,build=build,inputs_sha256=pins,positive=[],limits=[],negative=[],faults=[],stops=[],transitions=[])
    gold={row['name']:row['rgb565_sha256'] for row in oracle['positive']}

    def decode(name,capacity=460800,pool=65536,fault=None,recovery=None):
        """Each program owns a strict4MiB model; its second job keeps actual bytes."""
        image=fixtures/name;pins[str(image.resolve())]=sha(image)
        command=[build['executable'],str(image),str(first),str(second),'240',str(pool),str(capacity)]
        if fault:command.extend(map(str,fault))
        if recovery is not None:
            assert fault;command.append(str(fixtures/recovery))
        result=subprocess.run(command,capture_output=True,timeout=30)
        assert result.returncode==0,(command,result.returncode,result.stdout,result.stderr)
        row=json.loads(result.stdout);assert row['heap_final']==0,row
        for phase in ('first','recovery'):
            d=row[phase];assert d['opened']==d['closed'] and d['pool_peak']<=pool,row
        row.update(first_sha256=sha(first),second_sha256=sha(second))
        if row['recovery']['status']=='ok':
            assert row['second_sha256']==gold[recovery or name],row
        return row

    try:
        for item in oracle['positive']:
            name=item['name'];assert sha(fixtures/name)==item['fixture_sha256']
            row=decode(name)
            if name.startswith('sampling-44-'):
                for phase in ('first','recovery'):
                    d=row[phase]
                    if name.endswith('-12.jpg'):
                        assert d['status']=='library-pool-limit' and d['required']==70760 and d['available']==65536,row
                    else:
                        assert d['status']=='backing-capacity' and d['required']==524288 and d['available']==460800,row
                    assert d['available_known'] and not d['opened'],row
                    assert not row['physical_'+phase]['calls'],row
                report['limits'].append(dict(name=name,kind='native-resources',result=row))
                # Increasing only the host pool exposes the independent padded
                # backing limit. It does not claim this JPEG fits the device.
                row=decode(name,pool=262144)
                for phase in ('first','recovery'):
                    d=row[phase];assert d['status']=='backing-capacity' and d['required']==524288 and d['available']==460800 and not d['opened'],row
                    assert not row['physical_'+phase]['calls'],row
                report['limits'].append(dict(name=name,kind='padded-backing',result=row))
            else:
                assert row['first']['status']==row['recovery']['status']=='ok' and row['first_sha256']==gold[name],row
                assert row['recovery']['reused_object'],row
                if row['first']['opened']:assert row['recovery_last_id']>row['first_last_id'],row
                report['positive'].append(dict(name=name,result=row))
        full='full-cmyk12.jpg';small='cmyk-progressive-12.jpg'
        for capacity in (0,1,460799):
            row=decode(full,capacity=capacity)
            for phase in ('first','recovery'):
                d=row[phase];assert d['status']=='backing-capacity' and d['required']==460800 and d['available']==capacity and d['available_known'],row
                assert not d['opened'] and not row['physical_'+phase]['calls'],row
            report['limits'].append(dict(name=full,capacity=capacity,result=row))
        for item in oracle['negative']:
            row=decode(item['name'],fault=('physical',999999),recovery=full)
            assert row['first']['status']==item['result']['first']['status'],row
            assert row['recovery']['status']=='ok' and row['recovery']['reused_object'],row
            report['negative'].append(dict(name=item['name'],result=row))
        for transition in oracle['transitions']:
            before,after=transition['before'],transition['after']
            row=decode(before,fault=('physical',999999),recovery=after)
            assert row['first']['status']==row['recovery']['status']=='ok' and row['first_sha256']==gold[before],row
            assert row['recovery']['reused_object'],row
            report['transitions'].append(dict(before=before,after=after,result=row))
        control=decode(small);calls=control['physical_first']['calls']
        for ordinal in range(1,calls+1):
            row=decode(small,fault=('physical',ordinal))
            assert row['physical_first']['fault_hits']==1 and row['first']['status']=='backing-io' and row['first']['callback_error'],row
            assert row['recovery']['status']=='ok' and row['recovery']['reused_object'],row
            report['faults'].append(dict(name=small,ordinal=ordinal,result=row))
            if ordinal%100==0:print('physical errors and same-object recoveries:',ordinal,'/',calls,flush=True)
        full_control=decode(full);n=full_control['physical_first']['calls']
        for ordinal in sorted({1,2,17,35,n//2,n-1,n}):
            row=decode(full,fault=('physical',ordinal))
            assert row['physical_first']['fault_hits']==1 and row['first']['status']=='backing-io' and row['recovery']['status']=='ok',row
            report['faults'].append(dict(name=full,ordinal=ordinal,result=row))
        for kind,status in (('time','time-limit'),('budget','io-budget'),('cancel','cancelled')):
            for name,maximum in ((small,calls),(full,n)):
                for ordinal in sorted({1,2,3,17,35,maximum//2,maximum-1,maximum}):
                    row=decode(name,fault=(kind,ordinal))
                    assert row['first']['status']==status and row['physical_first']['calls']==ordinal,row
                    assert row['recovery']['status']=='ok' and row['recovery']['reused_object'],row
                    report['stops'].append(dict(name=name,kind=kind,ordinal=ordinal,result=row))
        report['traffic']=dict(name=full,result=full_control)
        report['passed']=True
    finally:
        report['inputs_unchanged']=all(sha(Path(p))==h for p,h in pins.items());report['passed'] &= report['inputs_unchanged']
        report['scope']='Real portable decoder + packed adapter + NOR/scratch, exact RGB565 independent oracle, strict page/1-to-0/erase model and two-job reuse. No target/HTTP/native UI, device endurance or whole RAM proof.'
        (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('PASS NOR decoder:',len(report['positive']),'images,',len(report['faults']),'physical failures,',len(report['stops']),'bounded stops',flush=True)


if __name__=='__main__':main()
