const test=require('node:test'),assert=require('node:assert/strict'),{execFileSync}=require('node:child_process');
const {root}=require('../tools/esp8266_opus_asm/export.cjs');
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
