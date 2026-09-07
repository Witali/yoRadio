// Add a shared, optional preloaded-fragment path. All other boards keep fetch.
const fs=require('node:fs'), zlib=require('node:zlib'), path=require('node:path');
const file=path.join(__dirname,'../yoRadio/data/www/script.js.gz');
let source=zlib.gunzipSync(fs.readFileSync(file)).toString('utf8');
if(!source.includes('function fetchUiResource(')) {
  const anchor="const yoTitle =";
  if(!source.includes(anchor)) throw new Error('Missing shared script anchor');
  source=source.replace(anchor,`function fetchUiResource(path) {
  const assets = window.yoUiAssets;
  if(assets && Object.prototype.hasOwnProperty.call(assets, path))
    return Promise.resolve(new Response(assets[path], {status: 200}));
  return fetch(uiResource(path), {cache: 'no-store'});
}
${anchor}`);
  let count=0;
  source=source.replace(/fetch\(uiResource\('([^']+)'\), \{cache: 'no-store'\}\)/g,
    (_,asset)=>{++count;return `fetchUiResource('${asset}')`;});
  if(count!==10) throw new Error('Unexpected fragment fetch count: '+count);
  fs.writeFileSync(file,zlib.gzipSync(Buffer.from(source),{level:9}));
}
