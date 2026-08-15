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
    $first = $Text.IndexOf($Old, [StringComparison]::Ordinal)
    if($first -lt 0) { throw "Could not find $Description" }
    if($Text.IndexOf($Old, $first + $Old.Length, [StringComparison]::Ordinal) -ge 0) {
        throw "Found more than one $Description"
    }
    return $Text.Substring(0, $first) + $New + $Text.Substring($first + $Old.Length)
}

$optionsPath = Join-Path $www "options.html.gz"
$options = Read-GzipText $optionsPath
$optionsAnchor = @'
          </div>
          <div class="hr">&nbsp;</div>
          <div class="flex-row" id="mdnsnamerow">
'@
$optionsReplacement = @'
          </div>
          <div class="flex-row">
            <div class="inputwrap">
              <span class="inputtitle">MP3 decoder</span>
              <select id="mp3decoder" data-command="mp3decoder">
                <option value="0">Helix (legacy)</option>
                <option value="1">minimp3 (new)</option>
              </select>
            </div>
          </div>
          <div class="hr">&nbsp;</div>
          <div class="flex-row" id="mdnsnamerow">
'@
$options = if($options.Contains('id="mp3decoder"')) {
    $options
} else {
    Replace-Once $options $optionsAnchor $optionsReplacement "system settings insertion point"
}
Write-GzipText $optionsPath $options

$scriptPath = Join-Path $www "script.js.gz"
$script = Read-GzipText $scriptPath
$script = if($script.Contains("element.tagName==='SELECT'")) {
    $script
} else {
    Replace-Once $script `
        "if(element.type==='text' || element.type==='number' || element.type==='password'){" `
        "if(element.type==='text' || element.type==='number' || element.type==='password' || element.tagName==='SELECT'){" `
        "settings value assignment"
}
Write-GzipText $scriptPath $script

$stylePath = Join-Path $www "style.css.gz"
$style = Read-GzipText $stylePath
if(!$style.Contains('input[type=number], select {')) {
    $style = Replace-Once $style `
        "input[type=text], input[type=password], input[type=number] {" `
        "input[type=text], input[type=password], input[type=number], select {" `
        "settings input style"
}
if(!$style.Contains('input[type=number]:focus, select:focus')) {
    $style = Replace-Once $style `
        "input[type=text]:focus, input[type=password]:focus, input[type=number]:focus { outline: none; }" `
        "input[type=text]:focus, input[type=password]:focus, input[type=number]:focus, select:focus { outline: none; }" `
        "settings focus style"
}
Write-GzipText $stylePath $style

Write-Host "Updated MP3 decoder settings assets in $www"
