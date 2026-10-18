// Read-only source-assertion control; executes current tests on exact Git blobs.
const fs=require('node:fs');
const path=require('node:path');
const {execFileSync}=require('node:child_process');
const root=path.resolve(__dirname,'..');
const read=fs.readFileSync;
const cache=new Map();
fs.readFileSync=function(file,options){
  if(typeof file!=='string')return read.apply(this,arguments);
  const relative=path.relative(root,path.resolve(file)).replaceAll('\\','/');
  if(!relative.startsWith('../') && /^(idf|yoRadio|tools)\//.test(relative)){
    if(!cache.has(relative))cache.set(relative,execFileSync('git',['show','2db2fd91:'+relative],{cwd:root}));
    const data=cache.get(relative);
    const encoding=typeof options==='string'?options:options?.encoding;
    return encoding?data.toString(encoding):Buffer.from(data);
  }
  return read.apply(this,arguments);
};
