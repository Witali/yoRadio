const fs=require('node:fs'),path=require('node:path');
const {execute}=require('./run_rcpdm_radio');
const root=path.resolve(__dirname,'../..');
function build(directory,stem='rcpdm8_quality') {
  if(!['rcpdm8_quality','rcpdm_precision','rcpdm_simple_quality','pdm_matrix_quality'].includes(stem)) throw Error('Unknown benchmark source');
  fs.mkdirSync(directory,{recursive:true});
  const source=fs.readFileSync(path.join(root,'esp8266/rtos-sdk-native/main/native_audio_output.c'),'utf8');
  const pack=source.slice(source.indexOf('i2s_pdm_pack32(int16_t sample)'));
  const start=pack.indexOf('    const uint32_t target = (uint32_t)((int32_t)sample - INT16_MIN);');
  const end=pack.indexOf('\n#endif',start);
  if(start<0 || end<start) throw Error('Cannot extract actual production PDM32');
  fs.writeFileSync(path.join(directory,'pdm32_original.inc'),'static uint32_t pdm32_original(uint32_t *accumulator,int16_t sample) {\n'+pack.slice(start,end).replaceAll('s_pdm_integrator','(*accumulator)')+'\n}\n');
  const exe=path.join(directory,stem.replaceAll('_','-')+(process.platform==='win32'?'.exe':''));
  const includes=[directory,path.join(root,'tests/native'),path.join(root,'esp8266/rtos-sdk-native/main')];
  const file=path.join(__dirname,stem+'.cpp');
  let result;
  if(process.platform==='win32') {
    const base='C:/Program Files/Microsoft Visual Studio'; let vc;
    for(const v of fs.readdirSync(base)) for(const e of fs.readdirSync(path.join(base,v))) {
      const p=path.join(base,v,e,'VC/Auxiliary/Build/vcvars64.bat');if(fs.existsSync(p)) vc=p;
    }
    if(!vc) throw Error('MSVC missing');
    const batch=path.join(directory,'build.cmd');
    fs.writeFileSync(batch,`@call "${vc}" >nul\r\n@if errorlevel 1 exit /b %errorlevel%\r\n@cl /nologo /std:c++17 /O2 /EHsc /W4 ${includes.map(p=>`/I"${p}"`).join(' ')} "${file}" /Fe:"${exe}"\r\n`);
    result=execute('cmd.exe',['/d','/c',batch],{cwd:directory});
  } else result=execute('c++',['-std=c++17','-O3',...includes.map(p=>`-I${p}`),file,'-o',exe],{cwd:directory});
  fs.writeFileSync(path.join(directory,'build.log'),result.stdout+result.stderr);return exe;
}
module.exports={build};
if(require.main===module) console.log(build(path.resolve(process.argv[2]||'radio_output/rcpdm8-quality/build'),process.argv[3]));
