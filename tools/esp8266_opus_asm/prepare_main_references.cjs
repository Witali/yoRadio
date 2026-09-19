// Restore disposable analysis ELFs from authenticated tracked evidence.
// Proven recipes stay unchanged; never regenerate old benchmarks.
const fs=require('node:fs'),path=require('node:path'),zlib=require('node:zlib');
const assert=require('node:assert/strict');
const {root,hash}=require('./export.cjs'),f=require('./frozen_reloads.cjs');
function restore(variant,elf,expected){
 assert.equal(hash(elf),expected,'Reference ELF hash');
 const file=path.join(root,'.build',variant,f.elfName);
 if(fs.existsSync(file))assert.equal(hash(fs.readFileSync(file)),expected,'Existing reference cache differs; inspect '+file);
 else {fs.mkdirSync(path.dirname(file),{recursive:true});fs.writeFileSync(file,elf);}
}
function main(){
 const accepted=require('./ebands_final.cjs');
 const proof=accepted.verifyPair().proof;
 const directory=path.join(root,'firmware/development',accepted.variant('candidate'));
 const elf=f.patchElf(zlib.gunzipSync(fs.readFileSync(path.join(directory,'parent.elf.gz'))),proof.patches);
 restore(accepted.variant('candidate'),elf,proof.candidate_elf_sha256);
 const raw='esp8266-opus-folding-control-v1';
 const data=zlib.gunzipSync(fs.readFileSync(path.join(root,'firmware/development',raw,'linked.elf.gz')));
 const first=require('./live_variant_v2.cjs').chain()[0].proof;
 restore(raw,data,first.parent_elf_sha256);
 console.log('Accepted ASM reference ELFs verified/restored; no board access.');
}
module.exports={restore};if(require.main===module)main();
