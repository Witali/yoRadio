const test=require('node:test'),assert=require('node:assert/strict'),path=require('node:path');
const {execFileSync}=require('node:child_process'),root=path.resolve(__dirname,'..');
const git=args=>execFileSync('git',['-c','core.autocrlf=true',...args],{cwd:root,encoding:'utf8'});
test('all later PVQ JSON evidence is explicitly checked out with LF on Windows',()=>{
 for(const family of['row-word','endpoint-word','index-word','index-half'])for(const suffix of['manifest.json','runs/run1.json','controls/after/run10.json']){
  const file='firmware/development/esp8266-opus-pvq-'+family+'-candidate-v1/'+suffix;
  const attrs=git(['check-attr','text','eol','--',file]);assert.ok(attrs.includes(': text: set'));assert.ok(attrs.includes(': eol: lf'));
 }
});
test('PVQ logs retain raw line endings and JSON normalization is byte-reproducible',()=>{
 const prefix='firmware/development/esp8266-opus-pvq-index-half-candidate-v1/';
 for(const suffix of['host.log','controls/after/run10.log'])assert.ok(git(['check-attr','text','--',prefix+suffix]).includes(': text: unset'));
 const hash=input=>execFileSync('git',['-c','core.autocrlf=true','hash-object','--path='+prefix+'runs/run1.json','--stdin'],{cwd:root,input,encoding:'utf8'}).trim();
 assert.equal(hash('{"value":1}\n'),hash('{"value":1}\r\n'));
});
test('new memory and qn JSON evidence keeps LF and native logs retain their bytes',()=>{
 for(const dir of['esp8266-opus-live-memory-diag-v1/evidence/runs','esp8266-opus-pvq-qn-table-candidate-v1/qualified/before']){
  const prefix='firmware/development/'+dir;
  const json=execFileSync('git',['check-attr','text','eol','--',prefix+'/run1.json'],{cwd:root,encoding:'utf8'});
  assert.match(json,/: text: set/);assert.match(json,/: eol: lf/);
  assert.match(execFileSync('git',['check-attr','text','--',prefix+'/run1.log'],{cwd:root,encoding:'utf8'}),/: text: unset/);
 }
});
test('qn parent ELF archive is LFS-managed binary',()=>{
 const file='firmware/development/esp8266-opus-pvq-qn-table-candidate-v1/parent.elf.gz';
 const out=execFileSync('git',['check-attr','filter','text','--',file],{cwd:root,encoding:'utf8'});
 assert.match(out,/: filter: lfs/);assert.match(out,/: text: unset/);
});
