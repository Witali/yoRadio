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
        [AllowEmptyString()]
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
$optionsBlock = @'
          <div class="flex-row">
            <div class="inputwrap">
              <span class="inputtitle">MP3 decoder</span>
              <select id="mp3decoder" data-command="mp3decoder">
                <option value="0">Helix (legacy)</option>
                <option value="1">minimp3 (new)</option>
              </select>
            </div>
          </div>
'@
$optionsBlock = $optionsBlock -replace "`r`n", "`n"
if($options.Contains('id="mp3decoder"')) {
    $options = Replace-Once $options $optionsBlock "" "MP3 decoder setting"
    Write-GzipText $optionsPath $options
    Write-Host "Removed MP3 decoder setting from $optionsPath"
} else {
    Write-Host "MP3 decoder setting is already absent from $optionsPath"
}
