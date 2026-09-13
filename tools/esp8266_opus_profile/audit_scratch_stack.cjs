// Read an existing target build and recompile isolated objects in a NEW output
// directory. No SDK/source edits, linking, serial operations or OTA.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const {spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'../..');
function audit(buildName,outputName) {
  if(!/^[\w-]+$/.test(buildName))throw Error('Expected a build variant name');
  const build=path.join(root,'.build',buildName);
  const commands=JSON.parse(fs.readFileSync(path.join(build,'compile_commands.json'),'utf8'));
  const out=path.resolve(root,outputName||'.build/opus-scratch-stack-'+buildName);
  if(!out.startsWith(root+path.sep)||fs.existsSync(out))throw Error('Use a new output directory inside the project');
  fs.mkdirSync(out,{recursive:true});const results=[];
  for(const mode of ['baseline','silk','silk-compact']) {
    const defines=['YORADIO_OPUS_CELT_SILK_SCRATCH='+(mode!=='baseline'?1:0),
      'YORADIO_OPUS_AUTOCORR_COMPACT='+(mode==='silk-compact'?1:0)];
    for(const name of ['celt_lpc.c','opus_decoder.c','opus_memory.c']) {
      const matches=commands.filter(c=>path.basename(c.file)===name);
      if(matches.length!==1)throw Error('Expected one compile command for '+name);
      const command=matches[0];if(/(?:^|\s)"/.test(command.command))throw Error('Quoted command requires argv parser');
      const args=command.command.trim().split(/\s+/).map(s=>s.replace(/\\"/g,'"'));
      const exe=args.shift(),object=path.join(out,mode+'-'+name+'.obj'),o=args.indexOf('-o');
      if(o<0)throw Error('Missing object output');args[o+1]=object;
      const d=args.indexOf('-MF');if(d>=0)args[d+1]=object+'.d';
      args.push('-fstack-usage',...defines.map(d=>'-D'+d));
      const run=spawnSync(exe,args,{cwd:command.directory,encoding:'utf8',timeout:60000});
      if(run.error||run.status!==0)throw Error(name+': '+(run.error||run.stderr));
      const frames=fs.readFileSync(object.replace(/\.obj$/,'.su'),'utf8').trim().split(/\r?\n/).map(line=>{
        const [symbol,bytes,kind]=line.split('\t');return{symbol,bytes:Number(bytes),kind};
      });
      const source=path.resolve(command.directory,command.file);
      results.push({mode,name,source:path.relative(root,source).replace(/\\/g,'/'),
        source_sha256_lf:crypto.createHash('sha256').update(fs.readFileSync(source,'utf8').replace(/\r\n/g,'\n')).digest('hex'),
        compiler:exe,arguments:args,frames});
      console.log(mode+' '+name+': '+JSON.stringify(frames.filter(f=>/autocorr|decode_frame|decode_bounded/.test(f.symbol))));
    }
  }
  const report={build:buildName,scope:'Individual LX106 GCC stack frames only. No linked image, summed call-depth, ISR margin or physical speed claim.',results};
  fs.writeFileSync(path.join(out,'results.json'),JSON.stringify(report,null,2)+'\n');return report;
}
module.exports={audit};
if(require.main===module)audit(process.argv[2],process.argv[3]);
