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
    if($Text.IndexOf($Old, $index + $Old.Length, [StringComparison]::Ordinal) -ge 0) {
        throw "Found more than one $Description"
    }
    return $Text.Substring(0, $index) + $New + $Text.Substring($index + $Old.Length)
}

$playerPath = Join-Path $www "player.html.gz"
$player = Read-GzipText $playerPath
if(-not $player.Contains('id="playlistfilter"')) {
    $player = Replace-Once $player @'
    <ul id="playlist"></ul>
'@ @'
    <label id="playlistsearch" for="playlistfilter">
      <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"></circle><path d="m16 16 5 5"></path></svg>
      <input id="playlistfilter" type="search" placeholder="Search stations" aria-label="Search stations by name" autocomplete="off" spellcheck="false">
    </label>
    <div id="playlistempty" class="hidden">No stations found</div>
    <ul id="playlist"></ul>
'@ "playlist element"
    Write-GzipText $playerPath $player
}

$scriptPath = Join-Path $www "script.js.gz"
$script = Read-GzipText $scriptPath
if(-not $script.Contains("function filterPlaylist(")) {
    $script = Replace-Once $script @'
function setCurrentItem(item){
  currentItem=item;
  const playlist = getId("playlist");
  let topPos = 0, lih = 0;
  playlist.querySelectorAll('li').forEach((item, index)=>{ item.attr('class','play'); if(index+1==currentItem){ item.classList.add("active"); topPos = item.offsetTop; lih = item.offsetHeight; } });
  playlist.scrollTo({ top: (topPos-playlist.offsetHeight/2+lih/2), left: 0, behavior: 'smooth' });
}
'@ @'
function setCurrentItem(item){
  currentItem=item;
  const playlist = getId("playlist");
  let activeItem = null;
  playlist.querySelectorAll('li[attr-id]').forEach(row => {
    row.classList.add('play');
    const active = Number(row.attr('attr-id')) === Number(currentItem);
    row.classList.toggle('active', active);
    if(active && !row.classList.contains('filtered')) activeItem = row;
  });
  if(activeItem) {
    playlist.scrollTo({
      top: activeItem.offsetTop-playlist.offsetHeight/2+activeItem.offsetHeight/2,
      left: 0,
      behavior: 'smooth'
    });
  }
}
function normalizeStationName(value){
  return String(value || '')
    .normalize('NFKD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLocaleLowerCase()
    .trim();
}
function filterPlaylist(value){
  const terms = normalizeStationName(value).split(/\s+/).filter(Boolean);
  let visible = 0;
  getId('playlist').querySelectorAll('li.play').forEach(item => {
    const name = normalizeStationName(item.dataset.name);
    const matches = terms.every(term => name.includes(term));
    item.classList.toggle('filtered', !matches);
    if(matches) visible++;
  });
  const empty = getId('playlistempty');
  if(empty) empty.classList.toggle('hidden', terms.length === 0 || visible > 0);
}
'@ "playlist selection function"

    $script = Replace-Once $script @'
  ul.innerHTML=html;
  setCurrentItem(currentItem);
  if(!modesd) initPLEditor();
'@ @'
  ul.innerHTML=html;
  setCurrentItem(currentItem);
  const filter = getId('playlistfilter');
  filterPlaylist(filter ? filter.value : '');
  if(!modesd) initPLEditor();
'@ "playlist rendering completion"

    $script = Replace-Once $script @'
  document.body.addEventListener('input', (event) => {
    let target = event.target;
    let command = target.dataset.command;
'@ @'
  document.body.addEventListener('input', (event) => {
    let target = event.target;
    if(target.id === 'playlistfilter') {
      filterPlaylist(target.value);
      return;
    }
    let command = target.dataset.command;
'@ "input event handler"

    Write-GzipText $scriptPath $script
}

$scriptChanged = $false
$oldCurrentSelection = @'
  playlist.querySelectorAll('li.play').forEach(row => {
    const active = Number(row.attr('attr-id')) === Number(currentItem);
'@
$newCurrentSelection = @'
  playlist.querySelectorAll('li[attr-id]').forEach(row => {
    row.classList.add('play');
    const active = Number(row.attr('attr-id')) === Number(currentItem);
'@
if($script.Contains($oldCurrentSelection)) {
    $script = Replace-Once $script $oldCurrentSelection $newCurrentSelection `
        "current station row selection"
    $scriptChanged = $true
}

$oldPlaylistRow = @'
      const active=(i+1==currentItem)?' class="active"':'';
      li=`<li${active} attr-id="${i+1}" class="play" data-name="${line[0].trim()}" data-url="${line[1].trim()}" data-ovol="${line[2].trim()}"><span class="text">${line[0].trim()}</span><span class="count">${i+1}</span></li>`;
'@
$newPlaylistRow = @'
      const active=(i+1==currentItem)?' active':'';
      li=`<li attr-id="${i+1}" class="play${active}" data-name="${line[0].trim()}" data-url="${line[1].trim()}" data-ovol="${line[2].trim()}"><span class="text">${line[0].trim()}</span><span class="count">${i+1}</span></li>`;
'@
if($script.Contains($oldPlaylistRow)) {
    $script = Replace-Once $script $oldPlaylistRow $newPlaylistRow `
        "playlist current station class"
    $scriptChanged = $true
}
if($scriptChanged) { Write-GzipText $scriptPath $script }

$stylePath = Join-Path $www "style.css.gz"
$style = Read-GzipText $stylePath
if(-not $style.Contains("#playlistsearch")) {
    $style = Replace-Once $style @'
#playlist {
'@ @'
#playlistsearch { position: relative; display: flex; align-items: center; width: 100%; margin: 0 0 8px 0; }
#playlistsearch svg { position: absolute; left: 11px; width: 19px; height: 19px; fill: none; stroke: var(--accent-dark); stroke-width: 2px; pointer-events: none; }
#playlistfilter { width: 100%; height: 38px; margin: 0; padding: 6px 34px 6px 38px; border: var(--input-border) 1px solid; border-radius: 19px;
  outline: none; background: var(--odd-bg-color); color: var(--accent-color); font: 18px Times, "Times New Roman", serif; user-select: text; }
#playlistfilter::placeholder { color: var(--main-hl-color); opacity: .75; }
#playlistfilter:focus { border-color: var(--accent-color); }
#playlistfilter::-webkit-search-cancel-button { -webkit-appearance: none; width: 22px; height: 22px; margin-right: -4px; cursor: pointer;
  background: linear-gradient(45deg, transparent 44%, var(--accent-color) 44%, var(--accent-color) 56%, transparent 56%),
              linear-gradient(-45deg, transparent 44%, var(--accent-color) 44%, var(--accent-color) 56%, transparent 56%); }
#playlistempty { width: 100%; padding: 10px 0; color: var(--main-hl-color); text-align: center; }
#playlist li.filtered { display: none; }
#playlist {
'@ "playlist styles"
    Write-GzipText $stylePath $style
}

$cancelButtonStyle = @'
#playlistfilter::-webkit-search-cancel-button { -webkit-appearance: none; width: 22px; height: 22px; margin-right: -4px; cursor: pointer;
  background: linear-gradient(45deg, transparent 44%, var(--accent-color) 44%, var(--accent-color) 56%, transparent 56%),
              linear-gradient(-45deg, transparent 44%, var(--accent-color) 44%, var(--accent-color) 56%, transparent 56%); }
'@
if(-not $style.Contains('#playlistfilter::-webkit-search-cancel-button')) {
    $style = Replace-Once $style @'
#playlistfilter:focus { border-color: var(--accent-color); }
'@ @"
#playlistfilter:focus { border-color: var(--accent-color); }
$cancelButtonStyle
"@ "playlist search clear button"
    Write-GzipText $stylePath $style
}

Write-Host "Added station-name search to WebUI assets"
