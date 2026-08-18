[CmdletBinding()]
param(
    [string]$DependencyRoot = "",
    [switch]$SkipToolchain
)

$ErrorActionPreference = "Stop"
$project = $PSScriptRoot
$worktreeRoot = [IO.Path]::GetFullPath((Join-Path $project "..\.."))
if ([string]::IsNullOrWhiteSpace($DependencyRoot)) {
    $DependencyRoot = Join-Path $worktreeRoot ".idf"
}
$DependencyRoot = [IO.Path]::GetFullPath($DependencyRoot)
$idfPath = Join-Path $DependencyRoot "v6.0.2"
$idfToolsPath = Join-Path $DependencyRoot "tools-v6.0.2"
$audioCodecPath = Join-Path $DependencyRoot "esp-adf-libs"
$pythonVersion = "3.12.10"
$pythonRoot = Join-Path $DependencyRoot "python-$pythonVersion"
$pythonPath = Join-Path $pythonRoot "tools"
$pythonExe = Join-Path $pythonPath "python.exe"
$downloads = Join-Path $DependencyRoot "downloads"
$pythonPackage = Join-Path $downloads "python.$pythonVersion.nupkg"
$pythonUrl = "https://www.nuget.org/api/v2/package/python/$pythonVersion"
$pythonSha256 = "0EB85C2DFCCCCF1B17352DE4C397F69194035B7D37149EACC16F1147D93DE3B8"

function Invoke-Git {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Arguments)
    $savedPath = $env:Path
    try {
        $gitExecPath = (& git --exec-path).Trim()
        $gitUsrBin = [IO.Path]::GetFullPath((Join-Path $gitExecPath "..\..\..\usr\bin"))
        $env:Path = "$gitExecPath;$gitUsrBin;$env:Path"
        & git -c core.longpaths=true @Arguments
        if ($LASTEXITCODE -ne 0) { throw "git failed: git $($Arguments -join ' ')" }
    } finally {
        $env:Path = $savedPath
    }
}

function Install-GitDependency {
    param(
        [Parameter(Mandatory)][string]$Url,
        [Parameter(Mandatory)][string]$Revision,
        [Parameter(Mandatory)][string]$Destination,
        [switch]$Submodules
    )
    if (Test-Path -LiteralPath (Join-Path $Destination ".git")) {
        $actual = (& git -C $Destination describe --tags --exact-match 2>$null)
        if (($LASTEXITCODE -ne 0) -or ($actual.Trim() -ne $Revision)) {
            throw "Dependency at $Destination is not pinned to $Revision"
        }
        if ($Submodules) {
            Invoke-Git -C $Destination submodule update --init --recursive --depth 1
        }
        Write-Host "Using existing dependency: $Destination"
        return
    }
    if (Test-Path -LiteralPath $Destination) {
        throw "Dependency path exists but is not a Git checkout: $Destination"
    }
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $Destination) | Out-Null
    Invoke-Git clone --branch $Revision --depth 1 $Url $Destination
    Invoke-Git -C $Destination config core.longpaths true
    if ($Submodules) {
        Invoke-Git -C $Destination submodule update --init --recursive --depth 1
    }
}

function Install-AudioCodec {
    param([Parameter(Mandatory)][string]$Destination)
    $revision = "67b8d0e98f58c774b8652480893037273190e8dc"
    if (Test-Path -LiteralPath (Join-Path $Destination ".git")) {
        $actual = (& git -C $Destination rev-parse HEAD).Trim()
        if ($actual -ne $revision) { throw "esp-adf-libs is not pinned to $revision" }
        Write-Host "Using existing dependency: $Destination"
        return
    }
    if (Test-Path -LiteralPath $Destination) {
        throw "Dependency path exists but is not a Git checkout: $Destination"
    }
    New-Item -ItemType Directory -Force -Path $Destination | Out-Null
    Invoke-Git -C $Destination init
    Invoke-Git -C $Destination remote add origin "https://github.com/espressif/esp-adf-libs.git"
    Invoke-Git -C $Destination sparse-checkout set esp_audio_codec
    Invoke-Git -C $Destination fetch --depth 1 origin $revision
    Invoke-Git -C $Destination checkout --detach FETCH_HEAD
}

New-Item -ItemType Directory -Force -Path $DependencyRoot, $downloads | Out-Null
if (-not (Test-Path -LiteralPath $pythonExe -PathType Leaf)) {
    if (-not (Test-Path -LiteralPath $pythonPackage -PathType Leaf)) {
        Invoke-WebRequest -Uri $pythonUrl -OutFile $pythonPackage
    }
    $actualHash = (Get-FileHash -LiteralPath $pythonPackage -Algorithm SHA256).Hash
    if ($actualHash -ne $pythonSha256) {
        throw "Python checksum mismatch: expected $pythonSha256, got $actualHash"
    }
    New-Item -ItemType Directory -Force -Path $pythonRoot | Out-Null
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    [IO.Compression.ZipFile]::ExtractToDirectory($pythonPackage, $pythonRoot, $true)
}

Install-GitDependency `
    -Url "https://github.com/espressif/esp-idf.git" `
    -Revision "v6.0.2" `
    -Destination $idfPath `
    -Submodules
Install-AudioCodec -Destination $audioCodecPath

if (-not $SkipToolchain) {
    $savedToolsPath = $env:IDF_TOOLS_PATH
    $savedPath = $env:Path
    try {
        $env:IDF_TOOLS_PATH = $idfToolsPath
        $env:Path = "$pythonPath;$pythonPath\Scripts;$env:Path"
        & (Join-Path $idfPath "install.ps1") esp32
        if ($LASTEXITCODE -ne 0) { throw "ESP-IDF toolchain installation failed" }
    } finally {
        $env:Path = $savedPath
        if ($null -eq $savedToolsPath) {
            Remove-Item Env:IDF_TOOLS_PATH -ErrorAction SilentlyContinue
        } else {
            $env:IDF_TOOLS_PATH = $savedToolsPath
        }
    }
}

Write-Host "Native dependencies are ready in $DependencyRoot"

