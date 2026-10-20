[CmdletBinding(PositionalBinding = $false)]
param([Parameter(Mandatory)][string]$Invocation)
$ErrorActionPreference = 'Stop'
$p = Get-Content -LiteralPath $Invocation -Raw | ConvertFrom-Json
if ($p.schema -ne 'ota-component-check-v1' -or $p.target -notin @('esp32', 'esp32c3')) { throw 'Invalid invocation' }
$env:IDF_TOOLS_PATH = $p.tools
$env:IDF_COMPONENT_MANAGER = '0'
$env:PYTHONNOUSERSITE = '1'
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONUTF8 = '1'
$env:YORADIO_AUDIO_CODEC_COMPONENT = 'C:/Work/yoRadio/.idf/esp-adf-libs/esp_audio_codec'
$env:YORADIO_LEGACY_IDF = 'C:/Work/yoRadio/.idf/v5.5.4'
$env:GIT_CONFIG_COUNT = '1'
$env:GIT_CONFIG_KEY_0 = 'core.longpaths'
$env:GIT_CONFIG_VALUE_0 = 'true'
$env:Path = 'C:/Work/yoRadio/.idf/python-3.12.10/tools;' + $env:Path
. (Join-Path $p.sdk 'export.ps1')
$python = (Get-Command python.exe -CommandType Application | Select-Object -First 1).Source
$toolPath = @(Get-ChildItem Env: | Where-Object { $_.Name -imatch '^path$' -and $_.Value.Contains('tools\ninja') } | Select-Object -ExpandProperty Value)
if ($toolPath.Count -ne 1) { throw 'Missing SDK toolchain PATH' }
Push-Location $p.project
try {
    $args = @((Join-Path $p.sdk 'tools/idf.py'), '-B', $p.build, '--no-ccache', '-D', ('SDKCONFIG=' + $p.config), '-D', ('SDKCONFIG_DEFAULTS=' + $p.defaults), '-D', ('CMAKE_PROJECT_INCLUDE=' + $p.probe), 'reconfigure')
    $process = Start-Process -FilePath $python -ArgumentList $args -NoNewWindow -Wait -PassThru -Environment @{ PATH = $toolPath[0] }
    if ($process.ExitCode -ne 0) { throw "SDK configure failed: $($process.ExitCode)" }
    $ninja = (Get-Command ninja.exe -CommandType Application | Select-Object -First 1).Source
    $process = Start-Process -FilePath $ninja -ArgumentList @('-C', $p.build, '-v', 'esp-idf/native_ota/libnative_ota.a') -NoNewWindow -Wait -PassThru -Environment @{ PATH = $toolPath[0] }
    if ($process.ExitCode -ne 0) { throw "OTA component build failed: $($process.ExitCode)" }
    $process = Start-Process -FilePath $ninja -ArgumentList @('-C', $p.build, '-t', 'deps') -NoNewWindow -Wait -PassThru -RedirectStandardOutput (Join-Path $p.run 'ninja-deps.txt') -Environment @{ PATH = $toolPath[0] }
    if ($process.ExitCode -ne 0) { throw "Dependency extraction failed: $($process.ExitCode)" }
} finally { Pop-Location }
