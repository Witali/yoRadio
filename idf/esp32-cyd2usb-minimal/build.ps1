[CmdletBinding(PositionalBinding = $false)]
param(
    [string]$BuildDirectory = "build",
    [Alias("DacBackend")]
    [ValidateSet("continuous", "legacy", "pdm")]
    [string]$AudioBackend = "continuous",
    [switch]$Setup,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$IdfArguments = @("build")
)

$ErrorActionPreference = "Stop"
$project = $PSScriptRoot
$worktreeRoot = [IO.Path]::GetFullPath((Join-Path $project "..\.."))
$dependencyRoot = Join-Path $worktreeRoot ".idf"
$idf = Join-Path $dependencyRoot "v6.0.2"
$legacyIdf = Join-Path $dependencyRoot "v5.5.4"
$idfTools = Join-Path $dependencyRoot "tools-v6.0.2"
$bootstrapPython = Join-Path $dependencyRoot "python-3.12.10\tools"
$ninjaExe = Join-Path $idfTools "tools\ninja\1.12.1\ninja.exe"
$arduinoComponent = Join-Path $dependencyRoot "arduino"
$arduinoLibraries = Join-Path $dependencyRoot "libraries"

$required = @(
    (Join-Path $idf "tools\idf.py"),
    (Join-Path $idf "export.ps1"),
    (Join-Path $bootstrapPython "python.exe"),
    (Join-Path $idfTools "idf-env.json"),
    $ninjaExe,
    (Join-Path $arduinoComponent "CMakeLists.txt"),
    (Join-Path $arduinoLibraries "Adafruit_GFX_Library\Adafruit_GFX.cpp"),
    (Join-Path $arduinoLibraries "Adafruit_ST7735_and_ST7789_Library\Adafruit_ST7789.cpp"),
    (Join-Path $arduinoLibraries "XPT2046_Touchscreen\XPT2046_Touchscreen.cpp")
)
if ($AudioBackend -eq "legacy") {
    $required += (Join-Path $legacyIdf "components\driver\deprecated\i2s_legacy.c")
}
$missing = @($required | Where-Object { -not (Test-Path -LiteralPath $_ -PathType Leaf) })
if ($Setup -or ($missing.Count -gt 0)) {
    Write-Host "Installing pinned ESP-IDF dependencies..."
    & (Join-Path $project "setup.ps1")
    if ($LASTEXITCODE -ne 0) { throw "setup.ps1 failed with exit code $LASTEXITCODE" }
    $missing = @($required | Where-Object { -not (Test-Path -LiteralPath $_ -PathType Leaf) })
}
if ($missing.Count -gt 0) {
    throw "Required build dependencies are missing: $($missing -join ', ')"
}

$saved = @{
    Path = $env:Path
    IDF_PATH = $env:IDF_PATH
    IDF_TOOLS_PATH = $env:IDF_TOOLS_PATH
    IDF_COMPONENT_MANAGER = $env:IDF_COMPONENT_MANAGER
    PYTHONNOUSERSITE = $env:PYTHONNOUSERSITE
    PYTHONIOENCODING = $env:PYTHONIOENCODING
    PYTHONUTF8 = $env:PYTHONUTF8
    YORADIO_ARDUINO_COMPONENT = $env:YORADIO_ARDUINO_COMPONENT
    YORADIO_ARDUINO_LIBRARIES = $env:YORADIO_ARDUINO_LIBRARIES
    YORADIO_LEGACY_IDF = $env:YORADIO_LEGACY_IDF
}
try {
    $env:IDF_TOOLS_PATH = $idfTools
    $env:IDF_COMPONENT_MANAGER = "0"
    $env:PYTHONNOUSERSITE = "1"
    $env:PYTHONIOENCODING = "utf-8"
    $env:PYTHONUTF8 = "1"
    $env:YORADIO_ARDUINO_COMPONENT = $arduinoComponent
    $env:YORADIO_ARDUINO_LIBRARIES = $arduinoLibraries
    $env:YORADIO_LEGACY_IDF = $legacyIdf
    $env:Path = "$bootstrapPython;$bootstrapPython\Scripts;$env:Path"
    . (Join-Path $idf "export.ps1")
    $idfPython = (Get-Command python.exe -CommandType Application |
        Select-Object -First 1 -ExpandProperty Source)
    # PowerShell 7 can retain both PATH and Path after IDF activation.  CMake
    # then sees the stale variant and cannot locate Ninja or the Xtensa tools.
    # Give the child process one canonical PATH containing the IDF exports.
    $idfPathValue = @(Get-ChildItem Env: | Where-Object {
        ($_.Name -imatch '^path$') -and $_.Value.Contains('tools\ninja')
    } | Select-Object -First 1 -ExpandProperty Value)
    if ($idfPathValue.Count -ne 1) {
        throw "ESP-IDF activation did not export the toolchain PATH"
    }
    Push-Location $project
    try {
        $idfProcessArguments = @(
            (Join-Path $idf "tools\idf.py"),
            "-B", $BuildDirectory,
            "--no-ccache",
            "-D", "YORADIO_DAC_BACKEND=$AudioBackend"
        ) + $IdfArguments
        $idfProcess = Start-Process -Wait -PassThru -NoNewWindow `
            -FilePath $idfPython `
            -ArgumentList $idfProcessArguments `
            -Environment @{ PATH = $idfPathValue[0] }
        if ($idfProcess.ExitCode -ne 0) {
            throw "idf.py failed with exit code $($idfProcess.ExitCode)"
        }
    } finally {
        Pop-Location
    }
} finally {
    foreach ($key in $saved.Keys) {
        if ($null -eq $saved[$key]) {
            Remove-Item -Path "Env:$key" -ErrorAction SilentlyContinue
        } else {
            Set-Item -Path "Env:$key" -Value $saved[$key]
        }
    }
}
