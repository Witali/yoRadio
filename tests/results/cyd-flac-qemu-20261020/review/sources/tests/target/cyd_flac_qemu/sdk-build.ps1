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
$env:CYD_FLAC_FROZEN_ROOT = Join-Path $output 'sources/repository'
$env:IDF_PATH = [IO.Path]::GetFullPath($IdfDirectory)
$env:IDF_TOOLS_PATH = [IO.Path]::GetFullPath($IdfToolsDirectory)
$env:IDF_COMPONENT_MANAGER = '0'
$env:PYTHONNOUSERSITE = '1'
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'
$python = [IO.Path]::GetFullPath($IdfPythonExecutable)
$env:IDF_PYTHON_ENV_PATH = [IO.Path]::GetDirectoryName([IO.Path]::GetDirectoryName($python))
$env:Path = [IO.Path]::GetDirectoryName($python) + ';' + $env:Path
$env:GIT_CONFIG_COUNT = '1'
$env:GIT_CONFIG_KEY_0 = 'core.longpaths'
$env:GIT_CONFIG_VALUE_0 = 'true'
$env:GIT_OPTIONAL_LOCKS = '0'
. (Join-Path $env:IDF_PATH 'export.ps1')
if ($LASTEXITCODE -ne 0) { throw 'Pinned SDK export failed' }
$idfArguments = @((Join-Path $env:IDF_PATH 'tools/idf.py'), '-C', $project, '-B', (Join-Path $output 'build'),
    '--no-ccache', '-D', 'IDF_TARGET=esp32', '-D', "SDKCONFIG=$output/sdkconfig",
    '-D', "SDKCONFIG_DEFAULTS=$project/sdkconfig.defaults", 'build')
$exportedPath = @(Get-ChildItem Env: | Where-Object {
    $_.Name -imatch '^path$' -and $_.Value.Contains('tools\ninja')
} | Select-Object -First 1 -ExpandProperty Value)
if ($exportedPath.Count -ne 1) { throw 'Pinned toolchain PATH missing' }
$start = [Diagnostics.ProcessStartInfo]::new()
$start.FileName = $python
$start.UseShellExecute = $false
$start.CreateNoWindow = $true
$start.Environment['PATH'] = $exportedPath[0]
foreach ($argument in $idfArguments) { [void]$start.ArgumentList.Add($argument) }
$process = [Diagnostics.Process]::Start($start)
$process.WaitForExit()
if ($process.ExitCode -ne 0) { throw "Pinned SDK custom FLAC build failed: $($process.ExitCode)" }
