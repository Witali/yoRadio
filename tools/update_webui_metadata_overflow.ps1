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

$playerPath = Join-Path $www "player.html.gz"
$player = Read-GzipText $playerPath
if(-not $player.Contains('id="trackinfo"')) {
    $player = Replace-Once $player @'
  <div>
    <div id="nameset" class="text"></div>
    <div id="meta" class="text"></div>
  </div>
'@ @'
  <div id="trackinfo">
    <div id="nameset" class="text"></div>
    <div id="meta" class="text"></div>
  </div>
'@ "station and song information block"
    Write-GzipText $playerPath $player
}

$stylePath = Join-Path $www "style.css.gz"
$style = Read-GzipText $stylePath
if(-not $style.Contains('#trackinfo {')) {
    $style = Replace-Once $style @'
#meta { text-transform: uppercase; font-size: 16px; min-height: 19px; margin-bottom: 14px; text-align: center; color: var(--main-hl-color); user-select: text;}
'@ @'
#trackinfo { width: 100%; min-width: 0; max-width: 100%; overflow: hidden; }
#meta { width: 100%; min-width: 0; max-width: 100%; overflow: hidden; white-space: nowrap; text-overflow: clip; text-transform: uppercase; font-size: 16px; min-height: 19px; margin-bottom: 14px; text-align: center; color: var(--main-hl-color); user-select: text;}
'@ "song metadata style"
    Write-GzipText $stylePath $style
}

Write-Host "Constrained long song metadata in WebUI"
