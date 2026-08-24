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
if(-not $script.Contains("function hideUnsupportedSetting(id)")) {
    $script = Replace-Once $script @'
      if(typeof data.act !== 'undefined'){ data.act.forEach(showclass=> { classEach(showclass, function(el) { el.classList.remove("hidden"); }); }); return; }
'@ @'
      if(typeof data.hide !== 'undefined'){ data.hide.forEach(hideUnsupportedSetting); return; }
      if(typeof data.act !== 'undefined'){ data.act.forEach(showclass=> { classEach(showclass, function(el) { el.classList.remove("hidden"); }); }); return; }
'@ "active WebUI group handler"

    $script = Replace-Once $script @'
function setupElement(id,value){
'@ @'
function hideUnsupportedSetting(id){
  const element = getId(id);
  if(!element) return;
  const wrapper = element.closest('.inputwrap');
  (wrapper || element).classList.add('hidden');
}
function setupElement(id,value){
'@ "settings element handler"

    Write-GzipText $scriptPath $script
}

Write-Host "WebUI unsupported-capability handling is present"
