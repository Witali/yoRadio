[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$OutputDirectory,
    [Parameter(Mandatory)][string]$IdfDirectory,
    [Parameter(Mandatory)][string]$IdfToolsDirectory,
    [Parameter(Mandatory)][string]$IdfPythonExecutable
)
$ErrorActionPreference = 'Stop'
$output = [IO.Path]::GetFullPath($OutputDirectory)
$project = Join-Path $output 'sources/harness/project'
if (!(Test-Path -LiteralPath (Join-Path $output 'source-manifest.json')) -or
    !(Test-Path -LiteralPath (Join-Path $project 'main/main.cpp')) -or
    !(Test-Path -LiteralPath (Join-Path $project 'main/fixture.ogg')) -or
    (Test-Path -LiteralPath (Join-Path $output 'build')) -or
    (Test-Path -LiteralPath (Join-Path $output 'sdkconfig'))) {
    throw 'Use run-cyd-espressif-vorbis-task-qemu.py to prepare a fresh campaign'
}
$env:CYD_VORBIS_TASK_FROZEN_ROOT = (Join-Path $output 'sources/repository').Replace('\', '/')
$env:CYD_VORBIS_TASK_VENDOR = (Join-Path $output 'sources/vendor/esp_audio_codec').Replace('\', '/')
$env:IDF_PATH = [IO.Path]::GetFullPath($IdfDirectory)
$env:IDF_TOOLS_PATH = [IO.Path]::GetFullPath($IdfToolsDirectory)
$env:IDF_COMPONENT_MANAGER = '0'
$env:PYTHONNOUSERSITE = '1'
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'
$env:GIT_CONFIG_COUNT = '1'
$env:GIT_CONFIG_KEY_0 = 'core.longpaths'
$env:GIT_CONFIG_VALUE_0 = 'true'
$env:GIT_OPTIONAL_LOCKS = '0'
$python = [IO.Path]::GetFullPath($IdfPythonExecutable)
$env:IDF_PYTHON_ENV_PATH = Split-Path (Split-Path $python)
$env:Path = (Split-Path $python) + ';' + $env:Path
. (Join-Path $env:IDF_PATH 'export.ps1')
if ($LASTEXITCODE -ne 0) { throw 'SDK activation failed' }
$idfArgs = @((Join-Path $env:IDF_PATH 'tools/idf.py'), '-C', $project,
    '-B', (Join-Path $output 'build'), '--no-ccache', '-D', 'IDF_TARGET=esp32',
    '-D', "SDKCONFIG=$output/sdkconfig", '-D', "SDKCONFIG_DEFAULTS=$project/sdkconfig.defaults",
    '-D', 'CMAKE_JOB_POOLS=compile=2;link=1', '-D', 'CMAKE_JOB_POOL_COMPILE=compile',
    '-D', 'CMAKE_JOB_POOL_LINK=link', 'build')
$toolPaths = @(Get-ChildItem Env: | Where-Object {
    $_.Name -imatch '^path$' -and $_.Value.Contains('tools\ninja')
} | Select-Object -ExpandProperty Value)
if ($toolPaths.Count -ne 1) { throw 'Activated SDK toolchain PATH missing' }
$start = [Diagnostics.ProcessStartInfo]::new()
$start.FileName = $python
$start.UseShellExecute = $false
$start.CreateNoWindow = $true
$start.RedirectStandardOutput = $true
$start.RedirectStandardError = $true
$start.Environment['PATH'] = $toolPaths[0]
foreach ($arg in $idfArgs) { [void]$start.ArgumentList.Add($arg) }
$stdoutFile = [IO.File]::Open((Join-Path $output 'sdk-build.stdout.log'), [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::Read)
$stderrFile = $null
$process = $null
try {
    $stderrFile = [IO.File]::Open((Join-Path $output 'sdk-build.stderr.log'), [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::Read)
    $process = [Diagnostics.Process]::Start($start)
    $stdoutCopy = $process.StandardOutput.BaseStream.CopyToAsync($stdoutFile)
    $stderrCopy = $process.StandardError.BaseStream.CopyToAsync($stderrFile)
    $process.WaitForExit()
    $copies = [Threading.Tasks.Task]::WhenAll([Threading.Tasks.Task[]]@($stdoutCopy, $stderrCopy))
    $copies.GetAwaiter().GetResult()
    [ordered]@{ pid=$process.Id; exit_status=$process.ExitCode; argv=@($python)+$idfArgs } |
        ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $output 'sdk-child.json') -Encoding utf8
    if ($process.ExitCode -ne 0) { throw "Whole CYD task SDK build failed: $($process.ExitCode)" }
} finally {
    if ($process) { $process.Dispose() }
    if ($stderrFile) { $stderrFile.Dispose() }
    $stdoutFile.Dispose()
}
