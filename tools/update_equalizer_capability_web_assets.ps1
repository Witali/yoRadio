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
    $index = $Text.IndexOf($Old, [StringComparison]::Ordinal)
    if($index -lt 0) { throw "Could not find $Description" }
    if($Text.IndexOf($Old, $index + $Old.Length, [StringComparison]::Ordinal) -ge 0) {
        throw "Found more than one $Description"
    }
    return $Text.Substring(0, $index) + $New + $Text.Substring($index + $Old.Length)
}

$script = Read-GzipText $scriptPath
if(-not $script.Contains("function applyPlayerCapabilities()")) {
    $script = Replace-Once $script @'
function onMessage(event) {
'@ @'
function applyPlayerCapabilities() {
  if(typeof equalizerEnabled !== 'undefined' && !equalizerEnabled) {
    ['bass', 'middle', 'trebble'].forEach(id => {
      const control = getId(id);
      if(control) control.closest('li').remove();
    });
  }
}
function onMessage(event) {
'@ "WebSocket message handler"

    $script = Replace-Once $script (
        "        getId('content').innerHTML = player; " + "`n"
    ) (
        "        getId('content').innerHTML = player;`n" +
        "        applyPlayerCapabilities();`n"
    ) "player HTML initialization"
}

Write-GzipText $scriptPath $script
Write-Host "Updated equalizer capability handling in $scriptPath"
