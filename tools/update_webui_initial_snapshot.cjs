// Mechanical update of the authoritative gzip asset; safe to run repeatedly.
const fs=require('node:fs'),zlib=require('node:zlib'),path=require('node:path');
const file=path.join(__dirname,'../yoRadio/data/www/script.js.gz');
let source=zlib.gunzipSync(fs.readFileSync(file)).toString('utf8');
if(!source.includes('function websocketBootstrapEnabled(')) {
  const replace=(from,to)=>{if(source.split(from).length!==2)throw new Error('Ambiguous/missing anchor: '+from);source=source.replace(from,to);};
  replace('var websocket;',`var websocket;
var playerUiReady = false;
var initialPlayerMessages = [];
var initialPlayerOverflow = false;`);
  replace('function initWebSocket() {',`function websocketBootstrapEnabled(){
  return typeof webSocketInitialState !== 'undefined' && webSocketInitialState === true &&
    ['/','/index.html'].includes(window.location.pathname);
}
function initialPlayerStateReady(){
  playerUiReady = true;
  const pending = initialPlayerMessages;
  const resync = initialPlayerOverflow;
  initialPlayerMessages = [];
  initialPlayerOverflow = false;
  pending.forEach(data => onMessage({data}));
  if(!websocketBootstrapEnabled() || resync) websocket.send('getindex=1');
}
function initWebSocket() {`);
  replace('  websocket = new WebSocket(`ws://${hostname}/ws`);',`  initialPlayerMessages = [];
  initialPlayerOverflow = false;
  const initial = websocketBootstrapEnabled() ? '?initial=1' : '';
  websocket = new WebSocket(\`ws://\${hostname}/ws\${initial}\`);`);
  replace("if(['/','/index.html'].includes(pathname)) websocket.send('getindex=1');",
    "if(['/','/index.html'].includes(pathname) && !websocketBootstrapEnabled()) websocket.send('getindex=1');");
  replace('function onMessage(event) {\n  try{',`function onMessage(event) {
  // Native bootstrap can arrive before asynchronous fragment installation.
  // Bound the queue; overflow requests a fresh state after the DOM is ready.
  if(websocketBootstrapEnabled() && !playerUiReady){
    if(initialPlayerMessages.length < 16) initialPlayerMessages.push(event.data);
    else initialPlayerOverflow = true;
    return;
  }
  try{`);
  replace("        websocket.send('getindex=1');\n        //generatePlaylist", "        initialPlayerStateReady();\n        //generatePlaylist");
  fs.writeFileSync(file,zlib.gzipSync(Buffer.from(source),{level:9}));
}
