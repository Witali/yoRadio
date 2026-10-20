"""Offline Vorbis bridge integrity/selected-entry check; archive-only reads."""
from pathlib import Path
import gzip,hashlib,json,re
ROOT=Path(__file__).resolve().parent
sha=lambda data:hashlib.sha256(data).hexdigest()
def load(name):return json.loads((ROOT/name).read_bytes())
def check(value,why):
 if not value:raise ValueError(why)
manifest=load('manifest.json')['files'];listed={r['path']:r for r in manifest}
actual={p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file() and p!=ROOT/'manifest.json'}
check(len(listed)==len(manifest) and set(listed)==actual,'Full manifest set')
for name,row in listed.items():
 p=(ROOT/name).resolve();check(p.is_relative_to(ROOT),'Unsafe manifest path');data=p.read_bytes()
 check(len(data)==row['bytes'] and sha(data)==row['sha256'],'Manifest bytes '+name)
rows=load('path-map.json')['entries'];byid={r['id']:r for r in rows};decoded={}
check(len(rows)==len(byid),'Mapping IDs')
for r in rows:
 check(r['original_path'] and isinstance(r['bytes'],int) and re.fullmatch('[0-9a-f]{64}',r['sha256']),'Mapping identity')
 if r['disposition']=='omitted':check(r.get('reason') and 'stored_path' not in r,'Explicit omission');continue
 check(r['disposition']=='stored' and r['stored_path'] in listed,'Stored mapping')
 if r['sha256'] in decoded:continue
 data=(ROOT/r['stored_path']).read_bytes();check(len(data)==r['stored_bytes'] and sha(data)==r['stored_sha256'],'Encoded identity')
 check(r['encoding'] in ('raw','gzip'),'Encoding');data=gzip.decompress(data) if r['encoding']=='gzip' else data
 check(len(data)==r['bytes'] and sha(data)==r['sha256'],'Decoded identity')
 check(not data.startswith((b'\x7fELF',b'MZ',b'!<arch>\n')),'Binary must be omitted')
 check(not r['original_path'].replace('\\','/').endswith(('/input.ogg','/fixture.h')),'Fixture payload must be omitted')
 decoded[r['sha256']]=data
def document(r):return json.loads(decoded[r['sha256']])
for b in load('bindings.json')['bindings']:
 value=document(byid[b['container_id']])
 for token in b['hash_tokens']:value=value[token]
 check(value==byid[b['target_id']]['sha256'],'JSON hash binding')
index=load('index.json');reports={k:document(byid[v]) for k,v in index['primary_report_ids'].items()}
for key in ('raw','control','config'):check(reports[key]['passed'],'Final report '+key)
check(reports['raw']['actual_result']==['535','1602','2112000'],'Exact raw counts')
check(reports['control']['exact_failure']=='rejected_dsp_unchanged','Exact semantic control')
for key in ('raw','control'):
 check(len(reports[key]['actual_module_rows'])==3,'Three actual compile rows')
 check(not reports[key]['production_radio_integration'] and not reports[key]['physical_device'],'Isolated scope')
def final_log(key):
 report=byid[index['primary_report_ids'][key]]
 original=report['original_path'].replace('\\','/').rsplit('/',1)[0]+'/qemu.log'
 matches=[r for r in rows if r['original_path'].replace('\\','/')==original]
 check(len(matches)==1 and matches[0]['disposition']=='stored','Unique final runtime log')
 return decoded[matches[0]['sha256']].decode(errors='replace').replace('\r\n','\n')
log=final_log('raw')
check(log.count('CYD_VORBIS_RAW_COMPLETE packets=535 rejected=1602 pcm=2112000 original_exact=1 core=1')==1,'Exact raw completion marker')
check(not re.search(r'CYD_VORBIS_FAILURE|Guru Meditation|abort\(\)|CORRUPT HEAP|assert failed',log,re.I),'Raw error marker')
log=final_log('control')
check(re.findall(r'^CYD_VORBIS_FAILURE (.+)$',log,re.M)==['rejected_dsp_unchanged'] and log.count('CYD_VORBIS_CONTROLLED_STOP')==1,'Exact skip-preflight detection')
check('CYD_VORBIS_RAW_COMPLETE' not in log,'Control must not claim raw pass')
check(index['status']['radio_activation'] is False and len(index['status']['open'])==7,'Open gates')
check(index['all_packaged_read_inputs_unchanged_after'] and index['raw_report_bytes_unchanged'],'Archival checks')
print(json.dumps({'passed':True,'manifest_files':len(manifest),'mappings':len(rows),'decoded_payloads':len(decoded),'offline_only':True},indent=2))
