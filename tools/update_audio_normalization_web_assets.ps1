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
if(-not $options.Contains('id="normalize"')) {
    $anchor = @'
          <div class="hr">&nbsp;</div>
          <div class="flex-row" id="mdnsnamerow">
'@
    $replacement = @'
          <div class="flex-row">
            <div class="inputwrap">
              <span class="inputtitle">automatic sound normalization</span>
              <div class="checkbox cbwtitle" id="normalize" data-command="normalization"><div class="knob"></div></div>
            </div>
            <div class="inputwrap">
              <span class="inputtitle">maximum boost (dB)</span>
              <input type="number" id="normgain" data-command="normgain" value="20" min="0" max="20" step="1" />
            </div>
          </div>
          <div class="hr">&nbsp;</div>
          <div class="flex-row" id="mdnsnamerow">
'@
    $index = $options.IndexOf($anchor, [StringComparison]::Ordinal)
    if($index -lt 0) { throw "Could not find system settings insertion point" }
    $options = $options.Substring(0, $index) + $replacement +
        $options.Substring($index + $anchor.Length)
}

if(-not $options.Contains('id="normtarget"')) {
    $anchor = @'
          <div class="hr">&nbsp;</div>
'@
    $replacement = @'
          <div class="flex-row">
            <div class="inputwrap">
              <span class="inputtitle">target peak level (dBFS)</span>
              <input type="number" id="normtarget" data-command="normtarget" value="-3" min="-20" max="0" step="1" />
            </div>
            <div class="inputwrap">
              <span class="inputtitle">time constant (ms)</span>
              <input type="number" id="normtime" data-command="normtime" value="2000" min="100" max="10000" step="100" />
            </div>
          </div>
          <div class="hr">&nbsp;</div>
'@
    $index = $options.IndexOf($anchor, $options.IndexOf('id="normgain"'), [StringComparison]::Ordinal)
    if($index -lt 0) { throw "Could not find normalization settings insertion point" }
    $options = $options.Substring(0, $index) + $replacement +
        $options.Substring($index + $anchor.Length)
}

Write-GzipText $optionsPath $options
Write-Host "Updated audio normalization controls in $optionsPath"
