[CmdletBinding()]
param([Parameter(Mandatory)][string]$CampaignDirectory,
      [Parameter(Mandatory)][string]$RepositoryDirectory,
      [Parameter(Mandatory)][string]$SourceDirectory,
      [Parameter(Mandatory)][string]$SdkDirectory,[Parameter(Mandatory)][string]$ToolsDirectory,
      [switch]$SkipAcquireControl,[switch]$OomGate)
$ErrorActionPreference = 'Stop'
$campaign = [IO.Path]::GetFullPath($CampaignDirectory)
$candidate = [IO.Path]::GetFullPath($SourceDirectory)
$repository = [IO.Path]::GetFullPath($RepositoryDirectory)
$draft = Join-Path $repository '.build'
if (!$campaign.StartsWith($draft + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase) -or
    !$candidate.StartsWith((Join-Path $campaign 'sources/variants') + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase) -or
    !(Test-Path -LiteralPath (Join-Path $campaign 'source-manifest.json'))) {
    throw 'Only a freshly frozen output inside repository .build is allowed'
}
$env:IDF_PATH = [IO.Path]::GetFullPath($SdkDirectory)
$env:IDF_TOOLS_PATH = [IO.Path]::GetFullPath($ToolsDirectory)
$env:IDF_COMPONENT_MANAGER = '0'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:PYTHONNOUSERSITE = '1'
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'
$env:GIT_OPTIONAL_LOCKS = '0'
$env:GIT_CONFIG_COUNT = '1'
$env:GIT_CONFIG_KEY_0 = 'core.longpaths'
$env:GIT_CONFIG_VALUE_0 = 'true'
$env:CCACHE_DISABLE = '1'
$env:CMAKE_BUILD_PARALLEL_LEVEL = '2'
$temporary = Join-Path $campaign 'tool-temp'
[void][IO.Directory]::CreateDirectory($temporary)
$env:TEMP = $temporary
$env:TMP = $temporary
$env:EARLY_MPI_SOURCE_ROOT = $candidate.Replace('\', '/')
$env:EARLY_MPI_KCONFIG = (Join-Path $campaign 'sources/repo/idf/esp32-cyd2usb-native/main/Kconfig.projbuild').Replace('\', '/')
$python = Join-Path $env:IDF_TOOLS_PATH 'python_env/idf6.0_py3.12_env/Scripts/python.exe'
$env:IDF_PYTHON_ENV_PATH = [IO.Path]::GetDirectoryName([IO.Path]::GetDirectoryName($python))
$env:Path = [IO.Path]::GetDirectoryName($python) + ';' + $env:Path
. (Join-Path $env:IDF_PATH 'export.ps1')
if ($LASTEXITCODE -ne 0) { throw 'Read-only SDK export failed' }
$exportedPath = @(Get-ChildItem Env: | Where-Object { $_.Name -imatch '^path$' -and $_.Value.Contains('tools\ninja') } | Select-Object -First 1 -ExpandProperty Value)
if ($exportedPath.Count -ne 1) { throw 'Pinned toolchain PATH missing' }
$project = Join-Path $campaign 'sources/repo/tests/target/cyd_early_mpi_qemu'
$build = Join-Path $campaign 'working-build'
function Run-Hidden([string]$FileName, [string[]]$Arguments) {
    $start = [Diagnostics.ProcessStartInfo]::new()
    $start.FileName = $FileName
    $start.UseShellExecute = $false
    $start.CreateNoWindow = $true
    $start.RedirectStandardOutput = $true
    $start.RedirectStandardError = $true
    $start.Environment['PATH'] = $exportedPath[0]
    foreach ($argument in $Arguments) { [void]$start.ArgumentList.Add($argument) }
    $process = [Diagnostics.Process]::Start($start)
    $stdout = $process.StandardOutput.ReadToEndAsync()
    $stderr = $process.StandardError.ReadToEndAsync()
    $process.WaitForExit()
    Write-Output $stdout.GetAwaiter().GetResult()
    Write-Output $stderr.GetAwaiter().GetResult()
    if ($process.ExitCode -ne 0) { throw "Isolated SDK tool failed: $($process.ExitCode)" }
}
$skip = if ($SkipAcquireControl) { 'ON' } else { 'OFF' }
$oom = if ($OomGate) { 'ON' } else { 'OFF' }
Run-Hidden $python @((Join-Path $env:IDF_PATH 'tools/idf.py'), '-C', $project, '-B', $build, '--no-ccache',
    '-D', 'IDF_TARGET=esp32', '-D', 'PROJECT_VER=early-mpi-fixture', '-D', "SDKCONFIG=$campaign/working-sdkconfig",
    '-D', "SDKCONFIG_DEFAULTS=$project/sdkconfig.defaults", '-D', "TEST_SKIP_ACQUIRE_CONTROL=$skip", '-D', "TEST_VOID_OOM=$oom", 'reconfigure')
$cache = Get-Content -LiteralPath (Join-Path $build 'CMakeCache.txt') -Raw
$ninja = [regex]::Match($cache, '(?m)^CMAKE_MAKE_PROGRAM:FILEPATH=(.+)$').Groups[1].Value.Trim()
if (!(Test-Path -LiteralPath $ninja -PathType Leaf)) { throw 'Actual configured Ninja missing' }
Run-Hidden $ninja @('-C', $build, '-j', '2')
