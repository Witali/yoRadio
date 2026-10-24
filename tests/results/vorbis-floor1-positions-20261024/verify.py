"""Verify saved floor1 bytes and recompute finite PCM comparisons; run no tools."""
from pathlib import Path
import gzip,hashlib,json,re,struct

ROOT=Path(__file__).resolve().parent
manifest=json.loads((ROOT/'manifest.json').read_text())
cache={}
for alias,row in manifest['files'].items():
    assert row['object']=='objects/'+row['sha256']+'.gz'
    if row['object'] not in cache:
        cache[row['object']]=gzip.decompress((ROOT/row['object']).read_bytes())
    data=cache[row['object']]
    assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256'],alias
assert {p.relative_to(ROOT).as_posix() for p in (ROOT/'objects').iterdir()}==set(cache)

def raw(alias):return cache[manifest['files'][alias]['object']]
def report(alias):return json.loads(raw(alias))
def normalized(mapping):return {key.replace('\\','/'):value for key,value in mapping.items()}
def metrics(a,b):
    assert len(a)==len(b)==28160
    errors=[abs(x[0]-y[0]) for x,y in zip(struct.iter_unpack('<h',a),struct.iter_unpack('<h',b))]
    return max(errors),sum(x>2 for x in errors)

matrix=report('corpus/matrix.json')
assert [c['expected_valid'] for c in matrix['cases']]==[True]*8+[False]*6
for group,core in (('cyd',1),('c3',0),('count-control',1),('unique-control',1)):
    r=report(group+'/report.json');assert r['completed']
    assert all(c['state']=='complete' and c['exit_status']==0 for c in r['commands'])
    assert r['elf_machine']==(243 if group=='c3' else 94)
    for cmd in r['commands']:
        for kind in ('stdout','stderr'):
            data=raw(group+'/'+cmd['name']+'.'+kind+'.log')
            assert hashlib.sha256(data).hexdigest()==cmd[kind+'_sha256']
    log=raw(group+'/qemu.stdout.log').decode(errors='replace').replace('\r\n','\n')
    assert not re.search(r'Guru Meditation|abort\(\)|Backtrace:|assert failed|CORRUPT HEAP',log)
    assert log.count('FLOOR1_CONTROLLED_STOP')==1
    opens=re.findall(r'^FLOOR1_OPEN case=(\d+) result=(-?\d+) handle=([01])$',log,re.M)
    end=12 if group=='count-control' else 8 if group=='unique-control' else 14
    expected=[(str(i),'0','1') for i in range(8)]+[(str(i),'-1','0') for i in range(8,end)]
    if group.endswith('control'):expected.append((str(end),'0','1'))
    assert opens==expected
    failure=re.findall(r'^FLOOR1_FAILURE case=(\d+) reason=(\S+)$',log,re.M)
    if group.endswith('control'):
        assert r['control_effective'] and not r['passed'] and failure==[(str(end),'invalid_setup_rejected')]
    else:
        assert r['passed'] and not failure
        assert r['observed']['summary']==['8','6','112','225280',str(core)]
    rows=re.findall(r'^FLOOR1_PCM case=(\d+) packet=(\d+) consumed=(\d+) bytes=(\d+) hex=([0-9a-f]*)$',log,re.M)
    assert [(int(c),int(p)) for c,p,*_ in rows]==[(c,p) for c in range(8) for p in range(14)]
    pcm_pins=normalized(r['observed']['pcm'])
    assert set(pcm_pins)=={f'pcm/{c}.s16le' for c in range(8)}
    for c in range(8):
        pcm=b''
        for _,packet,consumed,count,hexdump in rows[c*14:(c+1)*14]:
            p=int(packet);data=bytes.fromhex(hexdump)
            assert len(data)==int(count)==matrix['cases'][c]['expected_packet_bytes'][p]
            assert int(consumed)==matrix['offsets'][p+1]-matrix['offsets'][p]
            pcm+=data
        assert pcm==raw(group+f'/pcm/{c}.s16le') and len(pcm)==28160 and any(pcm)
        assert hashlib.sha256(pcm).hexdigest()==pcm_pins[f'pcm/{c}.s16le']

original=report('references-original-nonpass/report.json')
assert original['result']=='NONPASS' and not original['passed'] and len(original['commands'])==28
for cmd in original['commands']:
    assert cmd['state']=='terminal' and cmd['reaped'] and not cmd.get('forced_stop')
    for kind in ('stdout','stderr'):
        assert hashlib.sha256(raw('references-original-nonpass/'+cmd[kind])).hexdigest()==cmd[kind+'_sha256']
replay=report('replay/report.json')
assert replay['completed'] and not replay['dual_reference_qualified']
maximum={}
for group in ('cyd','c3'):
    values=[]
    target=next(x for x in replay['targets'] if x['target']==('esp32' if group=='cyd' else 'esp32c3'))
    assert target['xiph_pcm_qualified'] is False
    for c in range(8):
        expected=raw(f'references-original-nonpass/case-{c:02d}-libvorbis.s16le')
        actual=raw(group+f'/pcm/{c}.s16le')
        error,over=metrics(actual,expected);values.append(error)
        fact=target['cases'][c]
        assert (error,over)==(fact['max_abs_error'],fact['over_bound'])
        assert (error>2)==(c<3)
        assert actual==raw(('c3' if group=='cyd' else 'cyd')+f'/pcm/{c}.s16le')
    maximum[group]=max(values)
print(json.dumps(dict(archive_verified=True,aliases=len(manifest['files']),unique_objects=len(cache),
    target_xiph_max_abs_error=maximum,original_dual_reference_nonpass_preserved=True,
    target_numeric_nonpass_preserved=True,new_decoder_or_target_execution=False,full_G6_qualified=False)))
