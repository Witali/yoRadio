const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {root,run,hash,sourceHash,component}=require('./export.cjs');
function compare(bin){
 const variants=['esp8266-opus-gcc-asm-v1','esp8266-opus-optimized-asm-v1'];
 const results=variants.map(variant=>{
  const dir=path.join(root,'.build',variant),art=path.join(root,'firmware/development',variant);
  const manifest=JSON.parse(fs.readFileSync(path.join(art,'manifest.json'),'utf8'));
  const elf=path.join(dir,'yoradio_esp8266_helix_native.elf');
  assert.equal(manifest.app_sha256.toLowerCase(),hash(fs.readFileSync(path.join(art,'app.bin'))));
  assert.equal(manifest.opus_asm_manifest_sha256.toLowerCase(),sourceHash(path.join(component,'asm/lx106/manifest.json')));
  const sections=Object.fromEntries([...run(path.join(bin,'xtensa-lx106-elf-size.exe'),['-A',elf]).matchAll(/^(\.(?:iram0|dram0|flash)\.\S+)\s+(\d+)\s+/gm)].map(m=>[m[1],Number(m[2])]));
  const nm=run(path.join(bin,'xtensa-lx106-elf-nm.exe'),['-S',elf]);
  const symbol=nm.match(/^([0-9a-f]+) ([0-9a-f]+) T ec_dec_update$/m);assert.ok(symbol);
  return {variant,app_bytes:fs.statSync(path.join(art,'app.bin')).size,app_sha256:manifest.app_sha256,sections,ec_dec_update_bytes:parseInt(symbol[2],16)};
 });
 for(const key of Object.keys(results[0].sections).filter(k=>!k.startsWith('.flash.')))assert.equal(results[0].sections[key],results[1].sections[key],'RAM/IRAM changed: '+key);
 const report={passed:true,scope:'Full linked images, static sections and symbol size; no device CPU/heap watermark measurement',results,app_delta_bytes:results[1].app_bytes-results[0].app_bytes,static_ram_delta_bytes:0,ec_dec_update_stack_bytes:{gcc:16,optimized:0},physical_speed_measured:false};
 fs.writeFileSync(path.join(root,'firmware/development/esp8266-opus-asm-library/build-comparison.json'),JSON.stringify(report,null,2)+'\n');console.log(report);return report;
}
module.exports={compare};if(require.main===module)compare(process.argv[2]);
