[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$repository = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$scriptPath = Join-Path $repository "yoRadio\data\www\script.js.gz"
$utf8 = [Text.UTF8Encoding]::new($false)

function Read-GzipText {
    param([Parameter(Mandatory)][string]$Path)
    $inputStream = [IO.File]::OpenRead($Path)
    try {
        $gzipStream = [IO.Compression.GzipStream]::new(
            $inputStream, [IO.Compression.CompressionMode]::Decompress)
        try {
            $reader = [IO.StreamReader]::new($gzipStream, $utf8, $true)
            try { return ($reader.ReadToEnd() -replace "`r`n", "`n") }
            finally { $reader.Dispose() }
        }
        finally { $gzipStream.Dispose() }
    }
    finally { $inputStream.Dispose() }
}

function Write-GzipText {
    param(
        [Parameter(Mandatory)][string]$Path,
        [Parameter(Mandatory)][string]$Text
    )
    $outputStream = [IO.File]::Create($Path)
    try {
        $gzipStream = [IO.Compression.GzipStream]::new(
            $outputStream, [IO.Compression.CompressionLevel]::SmallestSize)
        try {
            $bytes = $utf8.GetBytes($Text)
            $gzipStream.Write($bytes, 0, $bytes.Length)
        }
        finally { $gzipStream.Dispose() }
    }
    finally { $outputStream.Dispose() }
}

function Replace-Once {
    param(
        [Parameter(Mandatory)][string]$Text,
        [Parameter(Mandatory)][string]$Old,
        [Parameter(Mandatory)][string]$New,
        [Parameter(Mandatory)][string]$Description
    )
    $Old = $Old -replace "`r`n", "`n"
    $New = $New -replace "`r`n", "`n"
    $index = $Text.IndexOf($Old, [StringComparison]::Ordinal)
    if($index -lt 0) { throw "Could not find $Description" }
    if($Text.IndexOf($Old, $index + $Old.Length,
                     [StringComparison]::Ordinal) -ge 0) {
        throw "Found more than one $Description"
    }
    return $Text.Substring(0, $index) + $New +
        $Text.Substring($index + $Old.Length)
}

$script = Read-GzipText $scriptPath
if(-not $script.Contains("function resyncCurrentPage()")) {
    $script = Replace-Once $script @'
var loadedPlaylistMode = null;
var stationChangeScrollFrom = null;
'@ @'
var loadedPlaylistMode = null;
var playlistRequestSerial = 0;
var stationChangeScrollFrom = null;
'@ "playlist request state"

$script = Replace-Once $script @'
function onOpen(event) {
  console.log('Connection opened');
  pingUp();
  continueLoading(playMode); //playMode in variables.js
  loaded = true;
  wserrcnt=0;
}
'@ @'
function resyncCurrentPage(){
  if(typeof playMode === 'undefined') return;
  const pathname = window.location.pathname;
  if(playMode=="player"){
    if(['/','/index.html'].includes(pathname)) websocket.send('getindex=1');
    if(pathname=='/settings.html'){
      websocket.send('getsystem=1');
      websocket.send('getscreen=1');
      websocket.send('gettimezone=1');
      websocket.send('getweather=1');
      websocket.send('getcontrols=1');
      websocket.send('getactive=1');
    }
  }else{
    websocket.send('getactive=1');
  }
}
function onOpen(event) {
  console.log('Connection opened');
  pingUp();
  if(!loaded){
    continueLoading(playMode); //playMode in variables.js
    loaded = true;
  }else{
    resyncCurrentPage();
  }
  wserrcnt=0;
}
'@ "WebSocket open handler"

$script = $script -replace "then\(plcontent => \{ +`n", "then(plcontent => {`n"
$script = Replace-Once $script @'
function handlePlaylistData(fileData, previousScrollTop = null) {
  const ul = getId('playlist');
  if(previousScrollTop === null) previousScrollTop = ul.scrollTop;
  ul.innerHTML='';
  if (!fileData) return;
  const lines = fileData.split('\n');
  let li='', html='';
  for(var i = 0;i < lines.length;i++){
    let line = lines[i].split('\t');
    if(line.length==3){
      const active=(i+1==currentItem)?' active':'';
      li=`<li attr-id="${i+1}" class="play${active}" data-name="${line[0].trim()}" data-url="${line[1].trim()}" data-ovol="${line[2].trim()}"><span class="text">${line[0].trim()}</span><span class="count">${i+1}</span></li>`;
      html += li;
    }
  }
  ul.innerHTML=html;
  setCurrentItem(currentItem);
  const filter = getId('playlistfilter');
  filterPlaylist(filter ? filter.value : '');
  ul.scrollTop = previousScrollTop;
  if(!modesd) initPLEditor();
  bigplaylist = false;
}
function generatePlaylist(path){
  path = path.replace(/:\/\/.+?\//, `://${hostname}/`);
  const playlist = getId('playlist');
  const previousScrollTop = playlist.scrollTop;
  playlist.innerHTML='<div id="progress"><span id="loader"></span></div>';
  bigplaylist = true;
  fetch(path).then(response => response.text()).then(plcontent => {
          handlePlaylistData(plcontent, previousScrollTop);
        }).catch(() => {
          handlePlaylistData(null, previousScrollTop);
        });
}
'@ @'
function handlePlaylistData(fileData, previousScrollTop = null) {
  if(typeof fileData !== 'string') return false;
  const ul = getId('playlist');
  if(previousScrollTop === null) previousScrollTop = ul.scrollTop;
  const lines = fileData.split('\n');
  let li='', html='', validRows=0;
  for(var i = 0;i < lines.length;i++){
    let line = lines[i].split('\t');
    if(line.length==3){
      const active=(i+1==currentItem)?' active':'';
      li=`<li attr-id="${i+1}" class="play${active}" data-name="${line[0].trim()}" data-url="${line[1].trim()}" data-ovol="${line[2].trim()}"><span class="text">${line[0].trim()}</span><span class="count">${i+1}</span></li>`;
      html += li;
      validRows++;
    }
  }
  if(fileData.trim() && validRows==0) return false;
  ul.innerHTML=html;
  setCurrentItem(currentItem);
  const filter = getId('playlistfilter');
  filterPlaylist(filter ? filter.value : '');
  ul.scrollTop = previousScrollTop;
  if(!modesd) initPLEditor();
  return true;
}
function fetchPlaylist(path, attemptsLeft){
  return fetch(path, {cache: 'no-store'}).then(response => {
    if(response.ok === false) throw new Error(`HTTP ${response.status}`);
    return response.text();
  }).catch(error => {
    if(attemptsLeft <= 1) throw error;
    return new Promise(resolve => setTimeout(resolve, 250)).then(() => fetchPlaylist(path, attemptsLeft-1));
  });
}
function generatePlaylist(path){
  path = path.replace(/:\/\/.+?\//, `://${hostname}/`);
  const playlist = getId('playlist');
  const previousScrollTop = playlist.scrollTop;
  const requestSerial = ++playlistRequestSerial;
  bigplaylist = true;
  return fetchPlaylist(path, 3).then(plcontent => {
    if(requestSerial !== playlistRequestSerial) return false;
    return handlePlaylistData(plcontent, previousScrollTop);
  }).catch(error => {
    console.log('Playlist loading failed:', error.message);
    return false;
  }).then(success => {
    if(requestSerial === playlistRequestSerial) bigplaylist = false;
    return success;
  });
}
'@ "playlist loader"
}

if(-not $script.Contains("var initialPlaylistScrollPending = true;")) {
    $script = Replace-Once $script @'
var currentItemSynchronized = false;
var loadedPlaylistMode = null;
'@ @'
var currentItemSynchronized = false;
var initialPlaylistScrollPending = true;
var playlistLoaded = false;
var loadedPlaylistMode = null;
'@ "initial playlist scroll state"

    $script = Replace-Once $script @'
function shouldScrollCurrentItem(item){
  const changed = currentItemSynchronized && Number(item) !== Number(currentItem);
  const requested = takeStationChangeScroll(item);
  currentItemSynchronized = true;
  return requested || changed;
}
'@ @'
function shouldScrollCurrentItem(item){
  const initial = initialPlaylistScrollPending && playlistLoaded;
  const changed = currentItemSynchronized && Number(item) !== Number(currentItem);
  const requested = takeStationChangeScroll(item);
  if(initial) initialPlaylistScrollPending = false;
  currentItemSynchronized = true;
  return initial || requested || changed;
}
'@ "initial station scroll decision"

    $script = Replace-Once $script @'
  ul.innerHTML=html;
  setCurrentItem(currentItem);
  const filter = getId('playlistfilter');
'@ @'
  ul.innerHTML=html;
  playlistLoaded = true;
  const initialScroll = initialPlaylistScrollPending && Number(currentItem) > 0;
  setCurrentItem(currentItem, initialScroll);
  if(initialScroll) initialPlaylistScrollPending = false;
  const filter = getId('playlistfilter');
'@ "scroll after initial playlist rendering"
}

Write-GzipText $scriptPath $script
Write-Host "Updated WebUI playlist reconnect and loading resilience"
