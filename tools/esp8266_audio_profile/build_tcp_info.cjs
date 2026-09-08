#!/usr/bin/env node
// Optional Windows test-host addon. Does not install/change Node or networking.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const {spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'../..');
async function build() {
  if(process.platform!=='win32'||process.arch!=='x64')throw Error('Windows x64 test host required');
  const version=process.version;
  if(!/^v\d+\.\d+\.\d+$/.test(version))throw Error('Unsupported Node version');
  const cache=path.join(root,'.build/node-tcp-info',version);fs.mkdirSync(cache,{recursive:true});
  const base='https://nodejs.org/download/release/'+version+'/';
  const checksums=await fetch(base+'SHASUMS256.txt');if(!checksums.ok)throw Error('Cannot load Node checksums');
  const expected=new Map((await checksums.text()).trim().split(/\r?\n/).map(s=>s.trim().split(/\s+/)).map(([hash,file])=>[file,hash]));
  for(const name of ['node-'+version+'-headers.tar.gz','win-x64/node.lib']) {
    const destination=path.join(cache,path.basename(name));
    if(!fs.existsSync(destination)) {
      const response=await fetch(base+name);if(!response.ok)throw Error('Download failed: '+name);
      fs.writeFileSync(destination,Buffer.from(await response.arrayBuffer()));
    }
    const actual=crypto.createHash('sha256').update(fs.readFileSync(destination)).digest('hex');
    if(actual!==expected.get(name))throw Error('Checksum mismatch: '+name);
  }
  const extracted=spawnSync('tar.exe',['-xf','node-'+version+'-headers.tar.gz'],{cwd:cache,encoding:'utf8'});
  if(extracted.status!==0)throw Error(extracted.stderr);
  let vcvars;
  const vs='C:/Program Files/Microsoft Visual Studio';
  for(const ver of fs.readdirSync(vs).sort().reverse())for(const edition of fs.readdirSync(path.join(vs,ver))) {
    const file=path.join(vs,ver,edition,'VC/Auxiliary/Build/vcvars64.bat');if(fs.existsSync(file))vcvars??=file;
  }
  if(!vcvars)throw Error('Visual C++ x64 tools not found');
  const output=path.join(cache,'tcp_info.node');
  const command=`@call "${vcvars}" >nul\r\n@if errorlevel 1 exit /b %errorlevel%\r\n`+
    `@cl /nologo /LD /O2 /EHsc /W4 /WX /D_WIN32_WINNT=0x0A00 /DNAPI_VERSION=8 /DNODE_GYP_MODULE_NAME=tcp_info `+
    `/I"${path.join(cache,'node-'+version,'include/node')}" "${path.join(__dirname,'tcp_info_addon.cc')}" `+
    `/link /OUT:"${output}" "${path.join(cache,'node.lib')}" ws2_32.lib\r\n`;
  const batch=path.join(cache,'build.cmd');fs.writeFileSync(batch,command);
  const result=spawnSync('cmd.exe',['/d','/c',batch],{cwd:cache,encoding:'utf8'});
  if(result.status!==0)throw Error(result.stdout+'\n'+result.stderr);
  console.log(output);
}
build().catch(error=>{console.error(error.message);process.exitCode=1});
