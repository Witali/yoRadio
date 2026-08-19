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

$old = @'
function hideSpinner(){
  getId("progress").classList.add("hidden");
  getId("content").classList.remove("hidden");
}
'@
$new = @'
function hideSpinner(){
  const startupProgress = document.querySelector('body > #progress');
  if(startupProgress) startupProgress.classList.add("hidden");
  getId("content").classList.remove("hidden");
}
'@

$script = Read-GzipText $scriptPath
if($script.Contains($old)) {
    $script = $script.Replace($old, $new)
} elseif(-not $script.Contains($new)) {
    throw "Could not find the WebUI startup spinner implementation"
}

Write-GzipText $scriptPath $script
Write-Host "Updated WebUI startup spinner in $scriptPath"
