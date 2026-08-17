[CmdletBinding()]
param(
    [switch]$SkipToolchain
)

$ErrorActionPreference = "Stop"
$project = $PSScriptRoot
$worktreeRoot = [IO.Path]::GetFullPath((Join-Path $project "..\.."))
$dependencyRoot = Join-Path $worktreeRoot ".idf"
$idfPath = Join-Path $dependencyRoot "v6.0.2"
$legacyIdfPath = Join-Path $dependencyRoot "v5.5.4"
$idfToolsPath = Join-Path $dependencyRoot "tools-v6.0.2"
$arduinoPath = Join-Path $dependencyRoot "arduino"
$librariesPath = Join-Path $dependencyRoot "libraries"
$pythonVersion = "3.12.10"
$pythonPackageRoot = Join-Path $dependencyRoot "python-$pythonVersion"
$pythonPath = Join-Path $pythonPackageRoot "tools"
$pythonExe = Join-Path $pythonPath "python.exe"
$downloadPath = Join-Path $dependencyRoot "downloads"
$pythonPackage = Join-Path $downloadPath "python.$pythonVersion.nupkg"
$pythonPackageUrl = "https://www.nuget.org/api/v2/package/python/$pythonVersion"
$pythonPackageSha256 = "0EB85C2DFCCCCF1B17352DE4C397F69194035B7D37149EACC16F1147D93DE3B8"

function Invoke-Git {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Arguments)
    $savedGitPath = $env:Path
    try {
        # Git's shell helpers (notably git-submodule) need usr/bin and the
        # libexec directory even in restricted PowerShell environments.
        $gitExecPath = (& git --exec-path).Trim()
        $gitUsrBin = [IO.Path]::GetFullPath((Join-Path $gitExecPath "..\..\..\usr\bin"))
        $env:Path = "$gitExecPath;$gitUsrBin;$env:Path"
        & git -c core.longpaths=true @Arguments
        if ($LASTEXITCODE -ne 0) { throw "git failed: git $($Arguments -join ' ')" }
    } finally {
        $env:Path = $savedGitPath
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
        Write-Host "Using existing dependency: $Destination"
        Invoke-Git -C $Destination config core.longpaths true
        $actualRevision = (& git -C $Destination describe --tags --exact-match 2>$null)
        if (($LASTEXITCODE -ne 0) -or ($actualRevision.Trim() -ne $Revision)) {
            throw "Dependency at $Destination is not the pinned revision $Revision"
        }
        if ($Submodules) {
            Invoke-Git -C $Destination submodule update --init --recursive --depth 1
        }
        return
    }
    if (Test-Path -LiteralPath $Destination) {
        throw "Dependency path exists but is not a Git checkout: $Destination"
    }
    $parent = Split-Path -Parent $Destination
    New-Item -ItemType Directory -Force -Path $parent | Out-Null
    Invoke-Git clone --branch $Revision --depth 1 $Url $Destination
    Invoke-Git -C $Destination config core.longpaths true
    if ($Submodules) {
        Invoke-Git -C $Destination submodule update --init --recursive --depth 1
    }
}

New-Item -ItemType Directory -Force -Path $dependencyRoot, $librariesPath, $downloadPath |
    Out-Null

if (-not (Test-Path -LiteralPath $pythonExe -PathType Leaf)) {
    if (-not (Test-Path -LiteralPath $pythonPackage -PathType Leaf)) {
        Write-Host "Downloading portable Python $pythonVersion..."
        Invoke-WebRequest -Uri $pythonPackageUrl -OutFile $pythonPackage
    }
    $pythonHash = (Get-FileHash -LiteralPath $pythonPackage -Algorithm SHA256).Hash
    if ($pythonHash -ne $pythonPackageSha256) {
        throw "Python package checksum mismatch: expected $pythonPackageSha256, got $pythonHash"
    }
    Write-Host "Extracting local Python $pythonVersion..."
    New-Item -ItemType Directory -Force -Path $pythonPackageRoot | Out-Null
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    [IO.Compression.ZipFile]::ExtractToDirectory($pythonPackage, $pythonPackageRoot, $true)
}
& $pythonExe --version
if ($LASTEXITCODE -ne 0) { throw "Local Python installation is unusable: $pythonExe" }

# Official stable ESP-IDF.  Clone first and initialize submodules in a separate
# command so core.longpaths is active for the very deep Mbed TLS tree.
Install-GitDependency `
    -Url "https://github.com/espressif/esp-idf.git" `
    -Revision "v6.0.2" `
    -Destination $idfPath `
    -Submodules

# Keep the final pre-IDF-6 legacy I2S/DAC implementation available as source.
# It is compiled only by the optional legacy DAC build; its toolchain and
# submodules are deliberately not installed.
Install-GitDependency `
    -Url "https://github.com/espressif/esp-idf.git" `
    -Revision "v5.5.4" `
    -Destination $legacyIdfPath

# ESP-IDF 6 support is not in a stable Arduino release yet.  Pin the official
# 4.0 alpha instead of following master, so builds remain reproducible.
Install-GitDependency `
    -Url "https://github.com/espressif/arduino-esp32.git" `
    -Revision "4.0.0-alpha1" `
    -Destination $arduinoPath

Install-GitDependency `
    -Url "https://github.com/adafruit/Adafruit_BusIO.git" `
    -Revision "1.17.4" `
    -Destination (Join-Path $librariesPath "Adafruit_BusIO")
Install-GitDependency `
    -Url "https://github.com/adafruit/Adafruit-GFX-Library.git" `
    -Revision "1.12.6" `
    -Destination (Join-Path $librariesPath "Adafruit_GFX_Library")
Install-GitDependency `
    -Url "https://github.com/adafruit/Adafruit-ST7735-Library.git" `
    -Revision "1.11.0" `
    -Destination (Join-Path $librariesPath "Adafruit_ST7735_and_ST7789_Library")
Install-GitDependency `
    -Url "https://github.com/PaulStoffregen/XPT2046_Touchscreen.git" `
    -Revision "v1.4" `
    -Destination (Join-Path $librariesPath "XPT2046_Touchscreen")

# yoRadio extends the Adafruit built-in font with UI icons.  Keep the upstream
# checkout untouched in Git's index but install the required generated font in
# the ignored dependency tree used by this build.
Copy-Item -Force -LiteralPath (Join-Path $worktreeRoot "yoRadio\fonts\glcdfont.c") `
    -Destination (Join-Path $librariesPath "Adafruit_GFX_Library\glcdfont.c")

if (-not $SkipToolchain) {
    $savedIdfToolsPath = $env:IDF_TOOLS_PATH
    $savedPath = $env:Path
    try {
        $env:IDF_TOOLS_PATH = $idfToolsPath
        $env:Path = "$pythonPath;$pythonPath\Scripts;$env:Path"
        & (Join-Path $idfPath "install.ps1") esp32
        if ($LASTEXITCODE -ne 0) {
            throw "ESP-IDF toolchain installation failed with exit code $LASTEXITCODE"
        }
    } finally {
        $env:Path = $savedPath
        if ($null -eq $savedIdfToolsPath) {
            Remove-Item Env:IDF_TOOLS_PATH -ErrorAction SilentlyContinue
        } else {
            $env:IDF_TOOLS_PATH = $savedIdfToolsPath
        }
    }
}

Write-Host "ESP-IDF v6.0.2 and legacy DAC source dependencies are ready in $dependencyRoot"
