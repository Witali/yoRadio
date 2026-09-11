// Recompile selected target objects with GCC stack-usage reports. No SDK edits,
// linking, firmware updates or claims that single frames prove call-chain depth.
const fs=require('node:fs'),path=require('node:path'),{spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'../..');
function audit(buildName,outputName) {
  if(!/^[\w-]+$/.test(buildName))throw Error('Expected build variant name');
  const build=path.join(root,'.build',buildName),out=path.join(root,'.build','pcm-stack-'+buildName);
  const commands=JSON.parse(fs.readFileSync(path.join(build,'compile_commands.json')));
  const wanted=['audio_pcm_queue.c','native_audio_output.c','native_audio_normalizer.cpp','AudioNormalizer.cpp','esp8266_nodac_i2s.c'];
  fs.mkdirSync(out,{recursive:true});const result={build:buildName,files:[],note:'Individual GCC frames, not a summed call-chain or ISR stack proof. Physical high-water marks remain required.'};
  for(const name of wanted) {
    const matches=commands.filter(x=>path.basename(x.file)===name);
    if(matches.length!==1)throw Error('Expected one compile command for '+name);
    const command=matches[0];
    // Current ESP8266 Windows toolchain/project paths contain no whitespace.
    // Reject shell-quoted paths rather than silently compiling different flags.
    if(/(?:^|\s)"/.test(command.command))throw Error('Quoted path needs an argv parser');
    const args=command.command.trim().split(/\s+/).map(s=>s.replace(/\\"/g,'"'));
    const executable=args.shift(),index=args.indexOf('-o');
    if(index<0)throw Error('No object output');
    const object=path.join(out,name+'.obj');args[index+1]=object;args.push('-fstack-usage');
    const run=spawnSync(executable,args,{cwd:command.directory,encoding:'utf8',timeout:60000});
    if(run.error || run.status!==0)throw Error(name+': '+(run.error||run.stderr));
    const report=object.replace(/\.obj$/,'.su');
    const frames=fs.readFileSync(report,'utf8').trim().split(/\r?\n/).map(line=>{
      const [symbol,bytes,kind]=line.split('\t');return {symbol,bytes:Number(bytes),kind};
    });
    result.files.push({name,frames});console.log(name+': maximum individual frame '+Math.max(...frames.map(f=>f.bytes))+'B');
  }
  const output=path.resolve(root,outputName||path.relative(root,path.join(out,'summary.json')));
  if(!output.startsWith(root+path.sep))throw Error('Output outside project');
  fs.mkdirSync(path.dirname(output),{recursive:true});fs.writeFileSync(output,JSON.stringify(result,null,2)+'\n');
  return result;
}
module.exports={audit};
if(require.main===module)audit(process.argv[2],process.argv[3]);
