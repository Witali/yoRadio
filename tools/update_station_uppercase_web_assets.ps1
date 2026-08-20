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

$optionsPath = Join-Path $www "options.html.gz"
$options = Read-GzipText $optionsPath
if(-not $options.Contains('id="upst"')) {
    $options = Replace-Once $options @'
          <div class="flex-row group group_tft group_oled group_nextion hidden">
            <div class="checkbox" id="nump" data-command="numplaylist"><div class="knob"></div>Numbered Playlist</div>
          </div>
'@ @'
          <div class="flex-row group group_tft group_oled group_nextion hidden">
            <div class="checkbox" id="nump" data-command="numplaylist"><div class="knob"></div>Numbered Playlist</div>
            <div class="checkbox" id="upst" data-command="stationuppercase"><div class="knob"></div>Uppercase station</div>
          </div>
'@ "display checkbox row"
    Write-GzipText $optionsPath $options
}

$scriptPath = Join-Path $www "script.js.gz"
$script = Read-GzipText $scriptPath
if(-not $script.Contains('id=="upst"')) {
    $script = Replace-Once $script @'
function setupElement(id,value){
  const element = getId(id);
'@ @'
function setupElement(id,value){
  if(id=="upst") document.documentElement.classList.toggle("station-uppercase", !!value);
  const element = getId(id);
'@ "WebUI element setup function"
    Write-GzipText $scriptPath $script
}

$stylePath = Join-Path $www "style.css.gz"
$style = Read-GzipText $stylePath
if(-not $style.Contains('.station-uppercase #nameset')) {
    $style = Replace-Once $style @'
#nameset { text-transform: uppercase; font-weight: bold;
'@ @'
#nameset { font-weight: bold;
'@ "station name style"
    $style = Replace-Once $style @'
#trackinfo { width: 100%; min-width: 0; max-width: 100%; overflow: hidden; }
'@ @'
.station-uppercase #nameset { text-transform: uppercase; }
#trackinfo { width: 100%; min-width: 0; max-width: 100%; overflow: hidden; }
'@ "station uppercase style insertion point"
    Write-GzipText $stylePath $style
}

Write-Host "Added the station uppercase display setting to WebUI"
