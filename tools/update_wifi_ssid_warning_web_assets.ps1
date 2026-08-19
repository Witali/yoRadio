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
        [Parameter(Mandatory)][string]$New
    )
    $index = $Text.IndexOf($Old, [StringComparison]::Ordinal)
    if($index -lt 0) { throw "Could not find Wi-Fi submission loop" }
    if($Text.IndexOf($Old, $index + $Old.Length, [StringComparison]::Ordinal) -ge 0) {
        throw "Found more than one Wi-Fi submission loop"
    }
    return $Text.Substring(0, $index) + $New + $Text.Substring($index + $Old.Length)
}

$script = Read-GzipText $scriptPath
if(-not $script.Contains("SSID_WARNING_TEXT")) {
    $script = Replace-Once $script @'
function submitWiFi(){
  var output="";
  var items=document.getElementsByClassName("credential");
  for (var i = 0; i <= items.length - 1; i++) {
    inputs=items[i].getElementsByTagName("input");
    if(inputs[0].value == "") continue;
    let ps=inputs[1].value==""?inputs[1].dataset.pass:inputs[1].value;
    output+=inputs[0].value+"\t"+ps+"\n";
  }
'@ @'
const SSID_WARNING_TEXT = 'Warning: one or more Wi-Fi names start or end with whitespace. Spaces are part of an SSID, so these are different network names. Save exactly as entered?';
function submitWiFi(){
  var output="";
  var items=document.getElementsByClassName("credential");
  var hasEdgeWhitespace=false;
  for (var i = 0; i <= items.length - 1; i++) {
    inputs=items[i].getElementsByTagName("input");
    if(inputs[0].value == "") continue;
    if(inputs[0].value !== inputs[0].value.trim()) hasEdgeWhitespace=true;
    let ps=inputs[1].value==""?inputs[1].dataset.pass:inputs[1].value;
    output+=inputs[0].value+"\t"+ps+"\n";
  }
  if(hasEdgeWhitespace && !window.confirm(SSID_WARNING_TEXT)) return;
'@
    Write-GzipText $scriptPath $script
}

Write-Host "Added leading/trailing whitespace warning to Wi-Fi settings"
