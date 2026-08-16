[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$repository = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$optionsPath = Join-Path $repository "yoRadio\data\www\options.html.gz"
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

$options = Read-GzipText $optionsPath
$current = '<input type="number" id="abuff" data-command="abuff" value="9"'
if($options.Contains($current)) {
    Write-Host "Audio buffer default is already current in $optionsPath"
    return
}
$pattern = '(<input type="number" id="abuff" data-command="abuff" value=")\d+("[^>]*>)'
$updated = [regex]::Replace($options, $pattern, '${1}9$2', 1)
if($updated -eq $options) { throw "Could not update the audio buffer default" }

Write-GzipText $optionsPath $updated
Write-Host "Updated audio buffer default in $optionsPath"
