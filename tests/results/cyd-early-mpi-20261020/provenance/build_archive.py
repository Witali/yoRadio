"""Package immutable MPI evidence without invoking SDK/tools/tests or Git."""
from pathlib import Path
import gzip,hashlib,json,re,struct,sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
OUT=ROOT/'tests/results/cyd-early-mpi-20261020'
assert not (OUT/'manifest.json').exists(), 'Never replace a completed archive'
OUT.mkdir(parents=True,exist_ok=True)
sha=lambda raw:hashlib.sha256(raw).hexdigest()
entries={};payloads={};read_inputs={};bindings=[];primary={}
def dump(path,obj):
 path=OUT/path;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def is_binary(raw,path):
 return raw.startswith((b'\x7fELF',b'MZ',b'!<arch>\n')) or path.suffix.lower() in ('.elf','.bin','.obj','.o','.a','.exe','.dll','.pyc')
def read(path):
 path=Path(path).resolve();raw=path.read_bytes()
 if str(path) not in read_inputs:read_inputs[str(path)]={'bytes':len(raw),'sha256':sha(raw)}
 return raw
def add(path,role,preferred=None,metadata=False,original=None,expected=None):
 path=Path(path).resolve();raw=read(path);digest=sha(raw)
 if expected is not None:assert digest==expected,(path,expected,digest)
 original=str(original or path);key=(original,digest)
 if key in entries:
  if role not in entries[key]['roles']:entries[key]['roles'].append(role)
  return entries[key]
 binary=is_binary(raw,path)
 record={'id':len(entries),'original_path':original,'sha256':digest,'bytes':len(raw),'roles':[role],
         'read_from':str(path),'observed_bytes':True}
 if not binary and (not metadata or digest in payloads):
  if digest not in payloads:
   compressed=len(raw)>=131072
   stored=preferred or ('raw/'+digest[:2]+'/'+digest+('.gz' if compressed else ''))
   data=gzip.compress(raw,compresslevel=9,mtime=0) if compressed else raw
   target=OUT/stored;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
   payloads[digest]={'stored_path':stored,'encoding':'gzip' if compressed else 'raw','stored_bytes':len(data),'stored_sha256':sha(data)}
  record.update(payloads[digest]);record['disposition']='stored'
 else:
  record['disposition']='omitted';record['reason']=('Executable/archive/firmware/ROM/object bytes deliberately omitted' if binary else
    'Replaceable historical build detail or external compiled-header payload omitted; identity retained')
 entries[key]=record
 return record
def by_id(n):return next(v for v in entries.values() if v['id']==n)
def bind(container,tokens,target):
 bindings.append({'container_id':container['id'],'hash_tokens':tokens,'target_id':target['id']})
def top_report(folder,name,role):
 path=ROOT/'.build'/folder/('review.json' if '-review-' in folder else 'report.json')
 record=add(path,role,'reports/'+name+'.json');primary[name]=record['id']
 return record,json.loads(path.read_bytes())

campaigns={}
for folder,name,role in [
 ('cyd-early-mpi-host-02','host-02','authoritative canonical host'),
 ('cyd-early-mpi-qemu-01','qemu-01','authoritative isolated actual SDK/QEMU'),
 ('cyd-early-mpi-qualification-01','qualification-01','authoritative aggregate'),
 ('cyd-early-mpi-preflight-02','preflight-02','authoritative path/pin controls'),
 ('cyd-early-mpi-review-01','review-01','independent review with original host finding'),
 ('cyd-early-mpi-review-02','review-02','independent finding closure and final4 artifact binding'),
 ('cyd-early-mpi-host-01','history-host-01','historical ordering only; wrong board seam'),
 ('cyd-early-mpi-wrong-sdk-pin-02','wrong-sdk-pin-02','expected SDK pin rejection; no SDK mutation'),
 ('cyd-early-mpi-wrong-sdk-pin-01','history-wrong-sdk-pin-01','historical expected SDK pin rejection'),
 ('cyd-early-mpi-preflight-01','history-preflight-01','historical preflight before host header repair')]:
 record,value=top_report(folder,name,role);campaigns[folder]=(record,value)

def input_references(folder,container,value,role,history=False):
 base=ROOT/'.build'/folder
 source_rows=value.get('inputs',{})
 if isinstance(source_rows,dict):
  for original,row in source_rows.items():
   if not isinstance(row,dict) or 'sha256' not in row or 'snapshot' not in row:continue
   snapshot=base/row['snapshot'];target=add(snapshot,role+' frozen input',expected=row['sha256'])
   alias=add(snapshot,role+' original source version',original=original,expected=row['sha256'])
   bind(container,['inputs',original,'sha256'],alias)
 for index,command in enumerate(value.get('commands',[])):
  label=command.get('label')
  if not label or 'sha256' not in command:continue
  path=base/(label+'.log')
  if path.is_file():bind(container,['commands',index,'sha256'],add(path,role+' command log',expected=command['sha256']))
 for path,digest in value.get('generated_inputs',{}).items():
  bind(container,['generated_inputs',path],add(base/path,role+' generated seam/control',expected=digest))
 for path,digest in value.get('tools',{}).items():
  bind(container,['tools',path],add(path,role+' tool identity',metadata=True,expected=digest))

for folder,(container,value) in campaigns.items():
 role=container['roles'][0]
 if folder in ('cyd-early-mpi-host-01','cyd-early-mpi-host-02'):
  for path in sorted((ROOT/'.build'/folder).rglob('*')):
   if path.is_file():add(path,role+' complete host campaign')
 elif folder in ('cyd-early-mpi-preflight-01','cyd-early-mpi-preflight-02','cyd-early-mpi-wrong-sdk-pin-01','cyd-early-mpi-wrong-sdk-pin-02','cyd-early-mpi-qualification-01'):
  for path in sorted((ROOT/'.build'/folder).rglob('*')):
   if path.is_file():add(path,role+' metadata/source/log')
 elif folder in ('cyd-early-mpi-review-01','cyd-early-mpi-review-02'):
  for path in sorted((ROOT/'.build'/folder).rglob('*')):
   if path.is_file():add(path,role+' immutable review payload')
 elif folder=='cyd-early-mpi-qemu-01':
  for path in sorted((ROOT/'.build'/folder).glob('*')):
   if path.is_file():add(path,role+' top-level log/manifest')
  for path in sorted((ROOT/'.build'/folder/'sources').rglob('*')):
   if path.is_file():add(path,role+' frozen source/variant')
  for path in sorted((ROOT/'.build'/folder/'variants').rglob('*')):
   if path.is_file():add(path,role+' variant artifact/metadata')
 input_references(folder,container,value,role)

# Actual target bundle references: retain textual artifacts; omit executable,
# full flash and tool bytes. Retain external-header identities without copying
# the replaceable full SDK include tree; the explicitly frozen SDK17 stay raw.
qfolder=ROOT/'.build/cyd-early-mpi-qemu-01'
qrecord,q=campaigns['cyd-early-mpi-qemu-01']
source_manifest=json.loads((qfolder/'source-manifest.json').read_bytes())
sm=add(qfolder/'source-manifest.json','frozen pre-build source manifest')
for path,digest in source_manifest['frozen_sources'].items():bind(sm,['frozen_sources',path],add(qfolder/path,'frozen pre-build source',expected=digest))
assert sha(read(qfolder/'source-manifest.json'))==q['source_manifest_sha256']
bind(qrecord,['source_manifest_sha256'],sm)
for name,value in q['variants'].items():
 path=qfolder/'variants'/name/'execution-bundle.json';b=add(path,'actual target execution bundle');bundle=json.loads(path.read_bytes())
 assert b['sha256']==value['execution_bundle_sha256'];bind(qrecord,['variants',name,'execution_bundle_sha256'],b)
 for relative,digest in bundle['artifacts'].items():bind(b,['artifacts',relative],add(qfolder/relative,'actual target artifact',expected=digest))
 for original,digest in bundle['external_header_closure'].items():bind(b,['external_header_closure',original],add(original,'external header identity',metadata=True,expected=digest))

# Preserve each independent review's historical original->frozen relationships.
# An original path can legitimately have multiple hashes across host01/02.
for folder in ('cyd-early-mpi-review-01','cyd-early-mpi-review-02'):
 base=ROOT/'.build'/folder
 for filename,key in (('inputs.json','inputs'),('runtime-inputs.json','inputs')):
  path=base/filename
  if not path.is_file():continue
  container=add(path,'independent review mapping');value=json.loads(path.read_bytes())
  for index,row in enumerate(value[key]):
   original=row.get('source',row.get('path'));digest=row['sha256']
   if 'snapshot' in row:
    target=add(base/row['snapshot'],'independent frozen historical source/report',original=original,expected=digest)
   else:
    target=add(original,'independent identity-only reference',metadata=True,expected=digest)
   bind(container,[key,index,'sha256'],target)

# Only meaningful prototype reports/errors and small promotion receipts, not a
# duplicate SDK working build. Their nested references can be explicitly omitted.
draft=ROOT/'.build/cyd-early-mpi-draft-01'
for name in ('integration-inputs.json','integration.patch','prepare.py','finalize.py','qualify_promoted.py','check_promoted_guards_02.py'):
 if (draft/name).is_file():add(draft/name,'historical prototype preparation/metadata')
for folder in ('host-01','host-02','host-03','host-04','target-01','target-02','handoff-01'):
 base=draft/folder;path=base/'report.json'
 if not path.is_file():continue
 container=add(path,'historical prototype only','reports/history/draft-'+folder+'.json')
 value=json.loads(path.read_bytes())
 for log in base.glob('*.log'):
  important=folder.startswith('host') or folder=='target-01' or log.name.endswith(('-qemu.log','abort-site.log','whole-backtrace.log')) or folder=='handoff-01'
  add(log,'historical prototype log',metadata=not important)
 # Map every report-bound input, preserving its frozen historical version.
 for original,row in value.get('inputs',{}).items():
  if isinstance(row,dict) and row.get('snapshot') and (base/row['snapshot']).is_file():
   target=add(base/row['snapshot'],'historical prototype frozen input',original=original,expected=row['sha256'])
   bind(container,['inputs',original,'sha256'],target)
 for i,c in enumerate(value.get('commands',[])):
  if 'label' in c and 'sha256' in c and (base/(c['label']+'.log')).is_file():
   target=add(base/(c['label']+'.log'),'historical command identity',metadata=True,expected=c['sha256'])
   bind(container,['commands',i,'sha256'],target)
for folder in ('tracked-ready-01','tracked-ready-02','tracked-ready-03'):
 if (draft/folder/'manifest.json').is_file():add(draft/folder/'manifest.json','historical promoted-input receipt')

# Aggregate qualifiers contain direct report and ELF links; bind those exact
# recorded identities without changing the original JSON.
aggregate_record,aggregate=campaigns['cyd-early-mpi-qualification-01']
for section in ('host','target'):
 row=aggregate[section];target=add(row['report'],'aggregate authoritative report',expected=row['sha256']);bind(aggregate_record,[section,'sha256'],target)
for name,row in aggregate['target']['variants'].items():
 target=add(row['elf'],'aggregate ELF identity',metadata=True,expected=row['elf_sha256']);bind(aggregate_record,['target','variants',name,'elf_sha256'],target)

# Current source closure is separate from historical source snapshots. Do not
# relabel host01's old runner/platform as current production inputs.
current=[]
for folder in ('cyd-early-mpi-host-02','cyd-early-mpi-qemu-01'):
 for original,row in campaigns[folder][1]['inputs'].items():
  value=sha(read(original));assert value==row['sha256'],('current canonical input changed',original)
  current.append({'path':original,'sha256':value,'matches_final_campaign':folder})
add(Path(__file__),'archive construction source','provenance/build_archive.py')
stable={path:sha(Path(path).read_bytes())==value['sha256'] for path,value in read_inputs.items()}
assert all(stable.values())

dump('path-map.json',{'version':1,'entries':list(entries.values()),
 'identity_key':'original_path + sha256 (multiple historical versions are intentional)',
 'scope':'Every selected report/log/frozen source and each explicitly bound original input/artifact/header/tool path; unreferenced replaceable working-build/tool-temp files are outside selected archive scope.'})
dump('bindings.json',{'bindings':bindings,'meaning':'Each JSON hash value at hash_tokens equals its mapped target payload/omission SHA256.'})
dump('current-verification.json',{'stable_read_input_count':len(read_inputs),'all_read_inputs_unchanged_after':True,
 'current_canonical_inputs':current,'note':'Historical original source aliases are not required to equal current files; their frozen snapshots are the evidence.'})
dump('index.json',{'primary_report_ids':primary,'authoritative_host':'host-02','authoritative_target':'qemu-01',
 'host01_scope':'Historical ordering only. Its board/network-stack-profile claim is invalid and superseded by host02.',
 'prototype_scope':'Historical development reports/errors only; not canonical qualification.',
 'status':{'canonical_source_integrated':True,'default_enabled':False,'host_pass':True,'isolated_target_pass':True,
 'production_exports':'pending','actual_radio_pre_app_lock_state':'pending','physical_benefit':'unproven'},
 'omitted_payloads':'Executable/object/archive/ROM/fullflash bytes and replaceable external header/build details retain identities; original nested manifests are historical documents and may reference omitted payloads.',
 'counts':{'mapped_versions':len(entries),'stored_versions':sum(x['disposition']=='stored' for x in entries.values()),
 'omitted_versions':sum(x['disposition']=='omitted' for x in entries.values()),'unique_stored_payloads':len(payloads),'json_hash_bindings':len(bindings)}})
print(json.dumps({'phase':'payload complete; write README/HOST/verifier then manifest','archive':str(OUT),'mappings':len(entries),
 'payloads':len(payloads),'bindings':len(bindings),'unchanged_inputs':len(read_inputs)},indent=2))
