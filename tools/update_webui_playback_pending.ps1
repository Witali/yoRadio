[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$repository = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$www = Join-Path $repository "yoRadio\data\www"
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
    $index = $Text.IndexOf($Old, [StringComparison]::Ordinal)
    if($index -lt 0) { throw "Could not find $Description" }
    if($Text.IndexOf($Old, $index + $Old.Length,
                     [StringComparison]::Ordinal) -ge 0) {
        throw "Found more than one $Description"
    }
    return $Text.Substring(0, $index) + $New +
        $Text.Substring($index + $Old.Length)
}

$scriptPath = Join-Path $www "script.js.gz"
$script = Read-GzipText $scriptPath
if(-not $script.Contains("function setPlaybackPending(pending)")) {
    $script = Replace-Once $script @'
var currentItem = 0;
var playlistmod = new Date().getTime();
'@ @'
var currentItem = 0;
var stationChangeScrollFrom = null;
var playbackPendingTimer = null;
var playlistmod = new Date().getTime();
'@ "WebUI player state variables"

    $script = Replace-Once $script @'
function onClose(event) {
  wserrcnt++;
'@ @'
function onClose(event) {
  setPlaybackPending(false);
  wserrcnt++;
'@ "WebSocket close handler"

    $script = Replace-Once $script @'
      if(typeof data.current !== 'undefined') { setCurrentItem(data.current); return; }
'@ @'
      if(typeof data.current !== 'undefined') { setCurrentItem(data.current, takeStationChangeScroll(data.current)); return; }
'@ "current station status handler"

    $script = Replace-Once $script @'
function setupElement(id,value){
  if(id=="upst") document.documentElement.classList.toggle("station-uppercase", !!value);
'@ @'
function setPlaybackPending(pending){
  const button = getId('playbutton');
  if(!button) return;
  clearTimeout(playbackPendingTimer);
  playbackPendingTimer = null;
  button.classList.toggle('connecting', pending);
  button.attr('aria-disabled', pending ? 'true' : 'false');
  if(pending) playbackPendingTimer = setTimeout(() => setPlaybackPending(false), 15000);
}
function requestStationChangeScroll(){
  stationChangeScrollFrom = Number(currentItem);
}
function takeStationChangeScroll(item){
  if(stationChangeScrollFrom === null || Number(item) === stationChangeScrollFrom) return false;
  stationChangeScrollFrom = null;
  return true;
}
function setupElement(id,value){
  if(id=="upst") document.documentElement.classList.toggle("station-uppercase", !!value);
  if(id=="playerwrap" && value=="playing") setPlaybackPending(false);
'@ "playback pending helpers"

    $script = Replace-Once $script @'
      if(id=='meta' || id=='nameset') setCurrentItem(currentItem);
'@ @'
      if(id=='meta' || id=='nameset') setCurrentItem(currentItem, false);
'@ "metadata station refresh"

    $script = Replace-Once $script @'
function setCurrentItem(item){
'@ @'
function setCurrentItem(item, shouldScroll=false){
'@ "current station selection function"

    $script = Replace-Once $script @'
  if(activeItem) {
'@ @'
  if(activeItem && shouldScroll) {
'@ "playlist scroll condition"

    $script = Replace-Once $script @'
  setCurrentItem(item)
  websocket.send(`play=${item}`);
'@ @'
  stationChangeScrollFrom = null;
  setCurrentItem(item, false);
  websocket.send(`play=${item}`);
'@ "playlist station click"

    $script = Replace-Once $script @'
    if(target.classList.contains("snfknob")) target = target.parentElement;
'@ @'
    if(target.classList.contains("snfknob")) target = target.parentElement;
    if(target.id === 'nameset') { setCurrentItem(currentItem, true); return; }
'@ "station heading click"

    $script = Replace-Once $script @'
        if(target.classList.contains("cmdbutton")) { websocket.send(`${command}=1`); }
'@ @'
        if(target.classList.contains("cmdbutton")) {
          if(target.id === 'playbutton') {
            if(target.classList.contains('connecting')) return;
            stationChangeScrollFrom = null;
            setCurrentItem(currentItem, true);
            const player = getId('playerwrap');
            if(player && player.classList.contains('stopped')) setPlaybackPending(true);
          }
          if(target.id === 'prevbutton' || target.id === 'nextbutton') requestStationChangeScroll();
          websocket.send(`${command}=1`);
        }
'@ "player command buttons"

    $script = Replace-Once $script @'
          setCurrentItem(item)
          websocket.send(`${command}=${item}`);
'@ @'
          stationChangeScrollFrom = null;
          setCurrentItem(item, false);
          websocket.send(`${command}=${item}`);
'@ "command-based station click"

    Write-GzipText $scriptPath $script
}

if(-not $script.Contains("function shouldScrollCurrentItem(item)")) {
    $script = Replace-Once $script @'
var currentItem = 0;
var stationChangeScrollFrom = null;
'@ @'
var currentItem = 0;
var currentItemSynchronized = false;
var stationChangeScrollFrom = null;
'@ "current station synchronization state"

    $script = Replace-Once $script @'
      if(typeof data.current !== 'undefined') { setCurrentItem(data.current, takeStationChangeScroll(data.current)); return; }
'@ @'
      if(typeof data.current !== 'undefined') { setCurrentItem(data.current, shouldScrollCurrentItem(data.current)); return; }
'@ "physical station change handler"

    $script = Replace-Once $script @'
function takeStationChangeScroll(item){
  if(stationChangeScrollFrom === null || Number(item) === stationChangeScrollFrom) return false;
  stationChangeScrollFrom = null;
  return true;
}
'@ @'
function takeStationChangeScroll(item){
  if(stationChangeScrollFrom === null || Number(item) === stationChangeScrollFrom) return false;
  stationChangeScrollFrom = null;
  return true;
}
function shouldScrollCurrentItem(item){
  const changed = currentItemSynchronized && Number(item) !== Number(currentItem);
  const requested = takeStationChangeScroll(item);
  currentItemSynchronized = true;
  return requested || changed;
}
'@ "physical station change scroll decision"

    Write-GzipText $scriptPath $script
}

if(-not $script.Contains("const startingPlayback =")) {
    $script = Replace-Once $script @'
          if(target.id === 'playbutton') {
            if(target.classList.contains('connecting')) return;
            stationChangeScrollFrom = null;
            setCurrentItem(currentItem, true);
            const player = getId('playerwrap');
            if(player && player.classList.contains('stopped')) setPlaybackPending(true);
          }
'@ @'
          if(target.id === 'playbutton') {
            if(target.classList.contains('connecting')) return;
            const player = getId('playerwrap');
            const startingPlayback = player && player.classList.contains('stopped');
            if(startingPlayback) {
              stationChangeScrollFrom = null;
              setCurrentItem(currentItem, true);
              setPlaybackPending(true);
            }
          }
'@ "Play-only playlist scroll"

    Write-GzipText $scriptPath $script
}

if(-not $script.Contains("const previousScrollTop = ul.scrollTop;")) {
    $script = Replace-Once $script @'
function handlePlaylistData(fileData) {
  const ul = getId('playlist');
  ul.innerHTML='';
'@ @'
function handlePlaylistData(fileData) {
  const ul = getId('playlist');
  const previousScrollTop = ul.scrollTop;
  ul.innerHTML='';
'@ "playlist scroll position capture"

    $script = Replace-Once $script @'
  const filter = getId('playlistfilter');
  filterPlaylist(filter ? filter.value : '');
  if(!modesd) initPLEditor();
'@ @'
  const filter = getId('playlistfilter');
  filterPlaylist(filter ? filter.value : '');
  ul.scrollTop = previousScrollTop;
  if(!modesd) initPLEditor();
'@ "playlist scroll position restore"

    Write-GzipText $scriptPath $script
}

$stylePath = Join-Path $www "style.css.gz"
$style = Read-GzipText $stylePath
if(-not $style.Contains("#playbutton.connecting")) {
    $style = Replace-Once $style @'
.gb.nb { border-color: transparent; }
'@ @'
.gb.nb { border-color: transparent; }
#playbutton.connecting { opacity: .45; cursor: wait; pointer-events: none; }
#playbutton.connecting:active { top: 0; }
#nameset { cursor: pointer; }
'@ "pending Play button style"
    Write-GzipText $stylePath $style
}

Write-Host "Updated WebUI playback pending state and playlist scrolling"
