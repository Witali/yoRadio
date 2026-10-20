"""Prepare/publish a compact read-only Vorbis evidence copy after root readiness.

No SDK, compiler, Git, decoder or fixture generator is invoked. By default this
prints the plan only. --write also requires root_readiness_confirmed in the plan.
"""
from pathlib import Path
import argparse,gzip,hashlib,json,re,shutil

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--plan',type=Path,default=HERE/'plan.json')
parser.add_argument('--write',action='store_true')
args=parser.parse_args()
plan=json.loads(args.plan.read_bytes())
if not args.write:
 print(json.dumps({'writes':False,'root_ready':plan['root_readiness_confirmed'],'plan':plan},indent=2));raise SystemExit(0)
assert plan['root_readiness_confirmed'] is True,'Wait for root terminal-readiness authorization'
for name,digest in plan.get('authoritative_report_sha256',{}).items():
 assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,('authoritative report changed',name)
OUT=(ROOT/plan['archive']).resolve()
assert OUT==(ROOT/'tests/results/cyd-vorbis-bridge-20261020').resolve()
assert not OUT.exists(),'Never replace an archive'
sha=lambda raw:hashlib.sha256(raw).hexdigest()
reports={key:json.loads((ROOT/plan[key]/'report.json').read_bytes()) for key in ('raw','control','config')}
for key,r in reports.items():assert r['passed'] is True,(key,'not terminal PASS')
raw,control=reports['raw'],reports['control']
for r in (raw,control):
 assert r['all_sources_current'] and r['canonical_bridge_sources'] and not r['production_radio_integration'] and not r['physical_device']
 assert len(r['actual_module_rows'])==3
assert raw['actual_result']==['535','1602','2112000'] and raw['control'] is None
assert control['control']=='skip-preflight' and control['exact_failure']=='rejected_dsp_unchanged'
assert reports['config']['configure_only'] and not reports['config']['compiler_invoked']
assert not reports['config']['sdk_export_invoked'] and not reports['config']['runtime_invoked']
for item in plan['additional_final_reports']:
 value=json.loads((ROOT/item['path']).read_bytes());assert value[item.get('success_key','passed')] is True
OUT.mkdir(parents=True)
entries={};payloads={};observed={};bindings=[];primary={}
def dump(name,value):
 p=OUT/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def read(p):
 p=Path(p).resolve();data=p.read_bytes();observed.setdefault(str(p),sha(data));return data
def excluded(p,data):
 if p.suffix.lower() in ('.elf','.bin','.obj','.o','.a','.exe','.dll','.pyc') or data.startswith((b'\x7fELF',b'MZ',b'!<arch>\n')):
  return 'Executable/object/archive/tool/ROM/firmware bytes omitted'
 if p.suffix.lower() in ('.ogg','.pcm','.wav') or p.name=='fixture.h':
  return 'Existing fixture/generated fixture bytes not duplicated; original fixture and generator identities retained'
 return None
def add(p,role,preferred=None,metadata=False,original=None,expected=None):
 p=Path(p).resolve();data=read(p);digest=sha(data);assert expected is None or digest==expected,(p,expected,digest)
 key=(str(original or p),digest)
 if key in entries:
  if role not in entries[key]['roles']:entries[key]['roles'].append(role)
  return entries[key]
 row={'id':len(entries),'original_path':key[0],'sha256':digest,'bytes':len(data),'read_from':str(p),'roles':[role]}
 reason=excluded(p,data)
 if not reason and (not metadata or digest in payloads):
  if digest not in payloads:
   compressed=len(data)>=131072;encoded=gzip.compress(data,compresslevel=9,mtime=0) if compressed else data
   name=preferred or 'raw/'+digest[:2]+'/'+digest+('.gz' if compressed else '')
   target=OUT/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(encoded)
   payloads[digest]={'stored_path':name,'encoding':'gzip' if compressed else 'raw','stored_bytes':len(encoded),'stored_sha256':sha(encoded)}
  row.update(payloads[digest]);row['disposition']='stored'
 else:row.update(disposition='omitted',reason=reason or 'Replaceable historical build detail identity only')
 entries[key]=row;return row
def bind(container,tokens,target):bindings.append({'container_id':container['id'],'hash_tokens':tokens,'target_id':target['id']})
def input_refs(base,r,container,historical=False):
 for original,v in r.get('inputs',{}).items():
  if not isinstance(v,dict) or not v.get('snapshot'):continue
  source=base/v['snapshot'];add(source,'frozen source/header/fixture',expected=v['sha256'])
  if not historical:assert sha(read(original))==v['sha256'],('final source no longer current',original)
  target=add(source,'original historical version' if historical else 'original final source version',original=original,expected=v['sha256'])
  bind(container,['inputs',original,'sha256'],target)
 for original,digest in r.get('tools',{}).items():bind(container,['tools',original],add(original,'tool/ROM identity',metadata=True,expected=digest))
 for i,c in enumerate(r.get('commands',[])):
  name=c.get('name',c.get('label'));digest=c.get('sha256',c.get('log_sha256'))
  if name and digest and (base/(name+'.log')).is_file():bind(container,['commands',i,'sha256' if 'sha256' in c else 'log_sha256'],add(base/(name+'.log'),'captured command output',expected=digest))
 for name,c in r.get('cases',{}).items():
  if c.get('log_sha256') and (base/name/'configure.log').is_file():
   bind(container,['cases',name,'log_sha256'],add(base/name/'configure.log','configure-only case log',expected=c['log_sha256']))
 for name,digest in r.get('generated_inputs_before_cmake',{}).items():
  bind(container,['generated_inputs_before_cmake',name],add(base/name,'frozen pre-configure test input',expected=digest))
def campaign(key,base,historical=False):
 rp=base/'report.json';r=json.loads(rp.read_bytes());container=add(rp,'historical report' if historical else 'final report','reports/'+key+'.json');primary[key]=container['id']
 for p in base.glob('*'):
  if p.is_file():add(p,'historical top-level payload' if historical else 'final top-level payload')
 for subtree in ('sources','variant','inputs'):
  if (base/subtree).is_dir():
   for p in (base/subtree).rglob('*'):
    if p.is_file():add(p,'frozen canonical/variant/codec-header input')
 input_refs(base,r,container,historical)
 if r.get('configure_only'):
  for p in base.rglob('*'):
   if p.is_file():add(p,'configure-only project/log/cache input')
 for relative,digest in r.get('variant_sources',{}).items():bind(container,['variant_sources',relative],add(base/relative,'exact compiled bridge variant',expected=digest))
 bundle=r.get('execution_bundle')
 if isinstance(bundle,dict):
  for section in ('generated','variant_sources'):
   for relative,digest in bundle.get(section,{}).items():bind(container,['execution_bundle',section,relative],add(base/relative,'pre-execution source/fixture identity',expected=digest))
  build=base/'build'
  for relative in ('compile_commands.json','build.ninja','project_description.json','config/sdkconfig.json','config/sdkconfig.h','flasher_args.json','CMakeCache.txt'):
   if (build/relative).is_file():add(build/relative,'actual build metadata (no rebuild)')
  if (build/'project_description.json').is_file():
   desc=json.loads((build/'project_description.json').read_bytes())
   for kind,field in [('app_elf','elf_sha256'),('app_bin','app_sha256')]:
    if field in r:bind(container,[field],add(build/desc[kind],'actual artifact identity',metadata=True,expected=r[field]))
  if (base/'qemu-flash.bin').is_file() and bundle.get('flash_sha256'):
   bind(container,['execution_bundle','flash_sha256'],add(base/'qemu-flash.bin','full flash identity',metadata=True,expected=bundle['flash_sha256']))
 for name,digest in r.get('archives',{}).items():
  target=Path(plan['codec_component'])/'lib/esp32'/name
  bind(container,['archives',name],add(target,'pinned codec archive identity',metadata=True,expected=digest))
 if 'actual_module_rows' in r:
  dump('metadata/'+key+'-three-compile-rows.json',r['actual_module_rows'])
 return container,r

for key in ('raw','control','config'):campaign(key,ROOT/plan[key])
for i,item in enumerate(plan['additional_final_reports']):
 p=ROOT/item['path'];row=add(p,'additional final aggregate/review report','reports/final-extra-'+str(i)+'.json');primary['final-extra-'+str(i)]=row['id']
for i,folder in enumerate(plan['history']):campaign('history-'+str(i),ROOT/folder,True)

# Preserve the separate explicitly partial ABI analysis and configure-only
# guard draft. Binaries in those trees remain identity-only; never analyze or
# execute SDK/codec algorithms during packaging.
for key in ('abi','guard'):
 base=ROOT/plan[key]
 for p in base.rglob('*'):
  if p.is_file():add(p,'partial ABI/guard draft evidence')
 rp=base/'report.json';r=json.loads(rp.read_bytes());container=add(rp,'partial ABI/guard report','reports/'+key+'.json');primary[key]=container['id']
 if key=='guard':input_refs(base,r,container,True)
 ip=base/'inputs.json'
 if ip.is_file():
  table=json.loads(ip.read_bytes());doc=add(ip,'partial ABI source mapping')
  for index,v in enumerate(table['inputs']):
   if v.get('snapshot'):target=add(base/v['snapshot'],'partial ABI original source version',original=v['source'],expected=v['sha256'])
   else:target=add(v['source'],'partial ABI binary identity',metadata=True,expected=v['sha256'])
   bind(doc,['inputs',index,'sha256'],target)
add(ROOT/plan['fixture_original'],'reusable existing fixture identity',metadata=True)
add(Path(__file__),'packager source','provenance/package.py')
add(args.plan,'final approved packaging plan','provenance/plan.json')
assert all(sha(Path(p).read_bytes())==digest for p,digest in observed.items())
dump('path-map.json',{'entries':list(entries.values()),'identity_key':'original_path + sha256; prior versions are intentional'})
dump('bindings.json',{'bindings':bindings})
dump('index.json',{'primary_report_ids':primary,'final_reports':['raw','control','config'],
 'status':plan['scope'],'source_format_history':'raw01/control01 pre-normalization history; final02 uses normalized source bytes, no claim that historical bytes are current.',
 'fixture_policy':'input Ogg and generated fixture header omitted to avoid duplicating existing fixture payload',
 'raw_report_bytes_unchanged':True,'all_packaged_read_inputs_unchanged_after':True,'read_input_count':len(observed)})
for source,name in [('README.template.md','README.md'),('HOST.template.md','HOST.md'),('verify.template.py','verify.py')]:
 shutil.copyfile(HERE/source,OUT/name)
files=[]
for p in sorted(OUT.rglob('*')):
 if p.is_file() and p!=OUT/'manifest.json':
  data=p.read_bytes();files.append({'path':p.relative_to(OUT).as_posix(),'bytes':len(data),'sha256':sha(data)})
dump('manifest.json',{'files':files})
print(json.dumps({'archive':str(OUT),'files':len(files)+1,'mappings':len(entries),'payloads':len(payloads),
 'bindings':len(bindings),'manifest_sha256':sha((OUT/'manifest.json').read_bytes())},indent=2))
