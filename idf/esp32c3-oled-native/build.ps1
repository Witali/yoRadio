[CmdletBinding(PositionalBinding = $false)]
param(
    [string]$BuildDirectory = "build",
    [string]$DependencyRoot = "",
    [string]$Sdkconfig = "sdkconfig",
    [string[]]$SdkconfigDefaults = @("sdkconfig.defaults"),
    [switch]$Setup,
    [switch]$DeepSleepClock,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$IdfArguments = @("build")
)

$ErrorActionPreference = "Stop"
$project = $PSScriptRoot
if ($DeepSleepClock) {
    if (-not $PSBoundParameters.ContainsKey("BuildDirectory")) {
        $BuildDirectory = "build-deep-sleep-clock"
    }
    if (-not $PSBoundParameters.ContainsKey("Sdkconfig")) {
        $Sdkconfig = "$BuildDirectory/sdkconfig"
    }
}
$worktreeRoot = [IO.Path]::GetFullPath((Join-Path $project "..\.."))
if ([string]::IsNullOrWhiteSpace($DependencyRoot)) {
    $DependencyRoot = Join-Path $worktreeRoot ".idf"
}
$DependencyRoot = [IO.Path]::GetFullPath($DependencyRoot)
$idf = Join-Path $DependencyRoot "v6.0.2"
$idfTools = Join-Path $DependencyRoot "tools-v6.0.2"
$bootstrapPython = Join-Path $DependencyRoot "python-3.12.10\tools"
$audioCodec = Join-Path $DependencyRoot "esp-adf-libs\esp_audio_codec"
$required = @(
    (Join-Path $idf "tools\idf.py"),
    (Join-Path $idf "export.ps1"),
    (Join-Path $bootstrapPython "python.exe"),
    (Join-Path $idfTools "idf-env.json"),
    (Join-Path $audioCodec "CMakeLists.txt"),
    (Join-Path $audioCodec "lib\esp32c3\libesp_audio_codec.a")
)
$missing = @($required | Where-Object {
    -not (Test-Path -LiteralPath $_ -PathType Leaf)
})
if ($Setup -or $missing.Count) {
    & (Join-Path $project "setup.ps1") -DependencyRoot $DependencyRoot
    if ($LASTEXITCODE -ne 0) { throw "setup.ps1 failed" }
    $missing = @($required | Where-Object {
        -not (Test-Path -LiteralPath $_ -PathType Leaf)
    })
}
if ($missing.Count) { throw "Missing dependencies: $($missing -join ', ')" }

$saved = @{
    Path = $env:Path
    IDF_PATH = $env:IDF_PATH
    IDF_TOOLS_PATH = $env:IDF_TOOLS_PATH
    IDF_COMPONENT_MANAGER = $env:IDF_COMPONENT_MANAGER
    PYTHONNOUSERSITE = $env:PYTHONNOUSERSITE
    PYTHONIOENCODING = $env:PYTHONIOENCODING
    PYTHONUTF8 = $env:PYTHONUTF8
    YORADIO_AUDIO_CODEC_COMPONENT = $env:YORADIO_AUDIO_CODEC_COMPONENT
}
try {
    $env:IDF_TOOLS_PATH = $idfTools
    $env:IDF_COMPONENT_MANAGER = "0"
    $env:PYTHONNOUSERSITE = "1"
    $env:PYTHONIOENCODING = "utf-8"
    $env:PYTHONUTF8 = "1"
    $env:YORADIO_AUDIO_CODEC_COMPONENT = $audioCodec
    $env:Path = "$bootstrapPython;$bootstrapPython\Scripts;$env:Path"
    . (Join-Path $idf "export.ps1")
    $idfPython = Get-Command python.exe -CommandType Application |
        Select-Object -First 1 -ExpandProperty Source
    $idfPathValue = @(Get-ChildItem Env: | Where-Object {
        ($_.Name -imatch '^path$') -and $_.Value.Contains('tools\ninja')
    } | Select-Object -First 1 -ExpandProperty Value)
    if ($idfPathValue.Count -ne 1) {
        throw "ESP-IDF toolchain PATH was not exported"
    }
    Push-Location $project
    try {
        # Explicitly apply both ON and OFF so reusing a build directory cannot
        # silently leave this opt-in mode enabled from an earlier build.
        $clockConfigPath = if ([IO.Path]::IsPathRooted($Sdkconfig)) {
            $Sdkconfig
        } else {
            Join-Path $project $Sdkconfig
        }
        $clockConfig = if (Test-Path -LiteralPath $clockConfigPath) {
            [IO.File]::ReadAllText($clockConfigPath)
        } else { "" }
        $clockConfig = [regex]::Replace($clockConfig,
            '(?m)^(?:CONFIG_YORADIO_DEEP_SLEEP_CLOCK=.*|# CONFIG_YORADIO_DEEP_SLEEP_CLOCK is not set)\r?\n?', '')
        $clockSetting = if ($DeepSleepClock) {
            "CONFIG_YORADIO_DEEP_SLEEP_CLOCK=y"
        } else { "# CONFIG_YORADIO_DEEP_SLEEP_CLOCK is not set" }
        New-Item -ItemType Directory -Force -Path (Split-Path $clockConfigPath) | Out-Null
        [IO.File]::WriteAllText($clockConfigPath,
            $clockConfig.TrimEnd() + [Environment]::NewLine + $clockSetting + [Environment]::NewLine,
            [Text.UTF8Encoding]::new($false))
        $arguments = @(
            (Join-Path $idf "tools\idf.py"),
            "-B", $BuildDirectory,
            "--no-ccache",
            "-D", "SDKCONFIG=$Sdkconfig",
            "-D", "SDKCONFIG_DEFAULTS=$($SdkconfigDefaults -join ';')"
        ) + $IdfArguments
        $process = Start-Process -Wait -PassThru -NoNewWindow `
            -FilePath $idfPython `
            -ArgumentList $arguments `
            -Environment @{ PATH = $idfPathValue[0] }
        if ($process.ExitCode -ne 0) {
            throw "idf.py failed with exit code $($process.ExitCode)"
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

