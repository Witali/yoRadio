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
if(-not $script.Contains("const uiRevision =")) {
    $script = Replace-Once $script @'
const params = new URLSearchParams(query);
'@ @'
const params = new URLSearchParams(query);
const uiRevision = params.get('ui') || yoVersion;
function uiResource(path) {
  const separator = path.includes('?') ? '&' : '?';
  return `${path}${separator}ui=${encodeURIComponent(uiRevision)}`;
}
'@ "UI revision initialization"

    $replacements = @(
        @('fetch(`player.html?${yoVersion}`)', "fetch(uiResource('player.html'), {cache: 'no-store'})"),
        @('fetch(`options.html?${yoVersion}`)', "fetch(uiResource('options.html'), {cache: 'no-store'})"),
        @('fetch(`updform.html?${yoVersion}`)', "fetch(uiResource('updform.html'), {cache: 'no-store'})"),
        @('fetch(`irrecord.html?${yoVersion}`)', "fetch(uiResource('irrecord.html'), {cache: 'no-store'})"),
        @("fetch('logo.svg')", "fetch(uiResource('logo.svg'), {cache: 'no-store'})")
    )
    foreach($replacement in $replacements) {
        $script = $script.Replace($replacement[0], $replacement[1])
    }
    $script = $script.Replace('loadCSS(`ir.css?${yoVersion}`)', "loadCSS(uiResource('ir.css'))")
    $script = $script.Replace('loadJS(`ir.js?${yoVersion}`', "loadJS(uiResource('ir.js')")
}

$script = $script.Replace(
    "const uiRevision = params.get('ui') || yoVersion;",
    "const uiRevision = typeof webUiRevision === 'undefined' ? (params.get('ui') || yoVersion) : webUiRevision;"
)

$navigationReplacements = @(
    @('window.location.href=`http://${hostname}/`', "window.location.href=uiResource('/')"),
    @('location.href=`http://${hostname}/`', "location.href=uiResource('/')"),
    @('window.location.href=`http://${hostname}/settings.html`', "window.location.href=uiResource('/settings.html')"),
    @('window.location.href=`http://${hostname}/update.html`', "window.location.href=uiResource('/update.html')"),
    @('window.location.href=`http://${hostname}/ir.html`', "window.location.href=uiResource('/ir.html')")
)
foreach($replacement in $navigationReplacements) {
    $script = $script.Replace($replacement[0], $replacement[1])
}

Write-GzipText $scriptPath $script
Write-Host "Updated WebUI cache busting in $scriptPath"
