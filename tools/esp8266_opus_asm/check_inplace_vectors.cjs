// Direct raw-vector/normalisation tests complement, not replace, full PCM tests.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {root,sourceHash}=require('./export.cjs');
const {buildHost,execute,hostPath,component}=require('../esp8266_opus_profile/build_host.cjs');
const {generate}=require('./algorithm_candidates.cjs');
async function check() {
 const base=await buildHost({bounded:true,fastInt64:0,firFlashWord:true,sanitize:true,asmBandsModel:'ebands-final'});
 const models=require('./ebands_final.cjs').cModels(),changes=generate('inplace-all',models),out=path.join(root,'.build/opus-algorithm-candidates/direct');fs.mkdirSync(out,{recursive:true});
 const pre=JSON.parse(fs.readFileSync(path.join(root,'firmware/development/esp8266-opus-pvq-prefix-word-candidate-v1/preflight.json'))),specs=[];
 for(let k=1;k<=175;k++)specs.push([2,k,4*k]);
 specs.push([2,32767,4*32767]);
 for(const row of pre.table.rows)for(let k=row.n;k<row.n+row.values.length-1;k++) {
  const v=row.values[k-row.n]+row.values[k+1-row.n];if(v<=0xffffffff)specs.push([row.n,k,v]);
 }
 for(let n=3;n<=176;n++)for(let k=1;k<=2;k++)specs.push([n,k,k===1?2*n:2*n*n]);
 const vectorMain=`
#include <stdio.h>
#include <stdlib.h>
static const unsigned research_specs[][3]={${specs.map(s=>'{'+s.join(',')+'U}').join(',')}};
int main(void) {
 unsigned seed=0x6b18cd32,cases=0;
 for(unsigned s=0;s<sizeof(research_specs)/sizeof(research_specs[0]);s++) {
  int n=research_specs[s][0],k=research_specs[s][1];unsigned v=research_specs[s][2];
  for(unsigned trial=0;trial<67;trial++) {
   int a[178];opus_int16 b[178];a[0]=a[n+1]=12345;b[0]=b[n+1]=23456;
   seed=1664525U*seed+1013904223U;
   unsigned index=trial==0?0:trial==1?v-1:trial==2?v/2:seed%v;
   opus_val32 ra=cwrsi(n,k,index,a+1),rb=research_cwrsi16(n,k,index,b+1);
   if(ra!=rb||a[0]!=12345||a[n+1]!=12345||b[0]!=23456||b[n+1]!=23456)return 2;
   int sum=0;for(int j=1;j<=n;j++){if(a[j]!=b[j])return 3;sum+=abs(a[j]);}
   if(sum!=k)return 4;cases++;
  }
 }
 printf("{\\"vectors\\":%u,\\"exact\\":true,\\"guards\\":true}\\n",cases);return 0;
}
`;
 const normalMain=`
#include <stdio.h>
int main(void) {
 const int gains[]={0,1,37,16384,32767};unsigned seed=42,cases=0;
 for(int n=2;n<=176;n++)for(int blocks=1;blocks<=16;blocks*=2)if(n%blocks==0)
 for(int trial=0;trial<16;trial++)for(unsigned gain=0;gain<sizeof(gains)/sizeof(gains[0]);gain++) {
  int iy[176];celt_norm a[178],b[178];opus_val32 energy=0;
  a[0]=a[n+1]=b[0]=b[n+1]=12345;
  for(int j=0;j<n;j++){seed=1664525U*seed+1013904223U;int value=(int)(seed%257)-128;if(trial==0)value=j==0?1:0;iy[j]=value;b[j+1]=value;energy+=value*value;}
  unsigned mask=extract_collapse_mask(iy,n,blocks),candidate_mask=research_mask16(b+1,n,blocks);
  normalise_residual(iy,a+1,n,energy,gains[gain]);research_normalise16(b+1,n,energy,gains[gain]);
  if(mask!=candidate_mask||a[0]!=12345||a[n+1]!=12345||b[0]!=12345||b[n+1]!=12345)return 2;
  for(int j=1;j<=n;j++)if(a[j]!=b[j])return 3;
  if(trial==0&&gains[gain]==0&&candidate_mask==0)return 4;
  cases++;
 }
 printf("{\\"normalisations\\":%u,\\"exact\\":true,\\"zero_gain_mask_preserved\\":true}\\n",cases);return 0;
}
`;
 const report={scope:'Host raw-vector and in-place normalisation tests under ASan/UBSan; not LX106 execution.',recipe_sha256:sourceHash(__filename),cases:[]};
 for(const [unit,main]of [['cwrs',vectorMain],['vq',normalMain]]) {
  const change=changes.find(c=>c.source.endsWith('/'+unit+'.c')),source=path.join(out,unit+'.c'),object=path.join(out,unit+'.o'),binary=path.join(out,unit);
  fs.writeFileSync(source,fs.readFileSync(change.file,'utf8')+main);
  execute('gcc',['-I'+hostPath(path.join(component,'upstream/celt')),...base.flags,'-c',hostPath(source),'-o',hostPath(object)]);
  const build=JSON.parse(fs.readFileSync(path.join(base.out,'build.json'))),objects=base.objects.filter((_,i)=>build.sources[i]!==change.base&&!build.sources[i].endsWith('probe.c'));
  execute('gcc',[...base.linkFlags,...objects.map(hostPath),hostPath(object),'-Wl,--gc-sections','-lm','-o',hostPath(binary)]);
  const result=JSON.parse(execute('env',['ASAN_OPTIONS=detect_leaks=0',hostPath(binary)]));assert.equal(result.exact,true);report.cases.push({unit,...result});console.log(unit,JSON.stringify(result));
 }
 fs.writeFileSync(path.join(out,'results.json'),JSON.stringify(report,null,2)+'\n');return report;
}
module.exports={check};if(require.main===module)check().catch(e=>{console.error(e);process.exitCode=1;});
