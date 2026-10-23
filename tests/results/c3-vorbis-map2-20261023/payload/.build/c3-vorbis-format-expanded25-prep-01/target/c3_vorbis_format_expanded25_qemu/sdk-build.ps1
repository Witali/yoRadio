param([Parameter(Mandatory)][string]$Campaign,
      [Parameter(Mandatory)][string]$Repository,
      [Parameter(Mandatory)][string]$SdkDirectory,
      [Parameter(Mandatory)][string]$ToolsDirectory,
      [Parameter(Mandatory)][string]$CodecDirectory)
$ErrorActionPreference = 'Stop'
$Campaign = [IO.Path]::GetFullPath($Campaign)
$draftRoot = Join-Path ([IO.Path]::GetFullPath($Repository)) '.build'
if (!$Campaign.StartsWith($draftRoot + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase) -or
    !(Test-Path -LiteralPath (Join-Path $Campaign 'report.json') -PathType Leaf) -or
    !(Test-Path -LiteralPath (Join-Path $Campaign 'variant/vorbis_repair_abi.h') -PathType Leaf)) {
    throw 'Only a runner-prepared fresh campaign inside repository .build is supported'
}
$env:IDF_PATH = [IO.Path]::GetFullPath($SdkDirectory)
$env:IDF_TOOLS_PATH = [IO.Path]::GetFullPath($ToolsDirectory)
$env:YORADIO_AUDIO_CODEC_COMPONENT = [IO.Path]::GetFullPath($CodecDirectory)
$env:C3_VORBIS_CANDIDATE = (Join-Path $Campaign 'variant').Replace('\', '/')
$env:IDF_COMPONENT_MANAGER = '0'
$env:IDF_TOOLCHAIN = 'gcc'
$env:PYTHONNOUSERSITE = '1'
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'
$env:GIT_CONFIG_COUNT = '1'
$env:GIT_CONFIG_KEY_0 = 'core.longpaths'
$env:GIT_CONFIG_VALUE_0 = 'true'
$env:GIT_OPTIONAL_LOCKS = '0'
$python = Join-Path $env:IDF_TOOLS_PATH 'python_env/idf6.1_py3.12_env/Scripts/python.exe'
$env:IDF_PYTHON_ENV_PATH = Split-Path (Split-Path $python)
$env:Path = (Split-Path $python) + ';' + $env:Path
. (Join-Path $env:IDF_PATH 'export.ps1')
if ($LASTEXITCODE -ne 0) { throw 'SDK activation failed' }
$report = Get-Content -LiteralPath (Join-Path $Campaign 'report.json') -Raw | ConvertFrom-Json
$setupSha = $report.selected_setup_sha256
if ($setupSha -notmatch '^[0-9a-f]{64}$' -or
    (Get-FileHash -LiteralPath (Join-Path $Campaign 'variant/vorbis_repair/setup.c') -Algorithm SHA256).Hash.ToLowerInvariant() -ne $setupSha) {
    throw 'Controller-selected frozen setup differs'
}
$argsForIdf = @((Join-Path $env:IDF_PATH 'tools/idf.py'), '-C', (Join-Path $Campaign 'sources/project'),
 '-B', (Join-Path $Campaign 'build'), '--no-ccache', '-D', 'IDF_TARGET=esp32c3', '-D', 'IDF_TOOLCHAIN=gcc',
 '-D', "SDKCONFIG=$Campaign/sdkconfig", '-D', "SDKCONFIG_DEFAULTS=$Campaign/sources/project/sdkconfig.defaults",
 '-D', "CORPUS_SETUP_SHA256=$setupSha",
 '-D', 'CMAKE_JOB_POOLS=compile=2;link=1', '-D', 'CMAKE_JOB_POOL_COMPILE=compile', '-D', 'CMAKE_JOB_POOL_LINK=link', 'build')
$toolPaths = @(Get-ChildItem Env: | Where-Object { $_.Name -imatch '^path$' -and $_.Value.Contains('tools\ninja') } | Select-Object -ExpandProperty Value)
if ($toolPaths.Count -ne 1) { throw 'Activated toolchain PATH missing' }
$compiler = (Get-Command riscv32-esp-elf-gcc.exe -CommandType Application -ErrorAction Stop | Select-Object -First 1).Source
$nm = Join-Path (Split-Path $compiler) 'riscv32-esp-elf-nm.exe'
$expectedCompiler = Join-Path $env:IDF_TOOLS_PATH 'tools/riscv32-esp-elf/esp-15.2.0_20251204/riscv32-esp-elf/bin/riscv32-esp-elf-gcc.exe'
if ([IO.Path]::GetFullPath($compiler) -ne [IO.Path]::GetFullPath($expectedCompiler)) { throw 'Wrong activated RV32 compiler path' }
$cmake = (Get-Command cmake.exe -CommandType Application -ErrorAction Stop | Select-Object -First 1).Source
$ninja = (Get-Command ninja.exe -CommandType Application -ErrorAction Stop | Select-Object -First 1).Source
if ([IO.Path]::GetFullPath($cmake) -ne [IO.Path]::GetFullPath((Join-Path $env:IDF_TOOLS_PATH 'tools/cmake/4.0.3/bin/cmake.exe')) -or
    [IO.Path]::GetFullPath($ninja) -ne [IO.Path]::GetFullPath((Join-Path $env:IDF_TOOLS_PATH 'tools/ninja/1.12.1/ninja.exe'))) {
    throw 'Wrong activated CMake/Ninja path'
}

[ordered]@{ compiler=$compiler; compiler_sha256=(Get-FileHash -LiteralPath $compiler -Algorithm SHA256).Hash.ToLowerInvariant();
 nm=$nm; nm_sha256=(Get-FileHash -LiteralPath $nm -Algorithm SHA256).Hash.ToLowerInvariant();
 cmake=$cmake; cmake_sha256=(Get-FileHash -LiteralPath $cmake -Algorithm SHA256).Hash.ToLowerInvariant();
 ninja=$ninja; ninja_sha256=(Get-FileHash -LiteralPath $ninja -Algorithm SHA256).Hash.ToLowerInvariant() } | ConvertTo-Json |
 Set-Content -LiteralPath (Join-Path $Campaign 'compiler-identity-before-build.json') -Encoding utf8
[ordered]@{ PATH=$toolPaths[0]; IDF_PATH=$env:IDF_PATH; IDF_TOOLS_PATH=$env:IDF_TOOLS_PATH;
 IDF_PYTHON_ENV_PATH=$env:IDF_PYTHON_ENV_PATH } | ConvertTo-Json |
 Set-Content -LiteralPath (Join-Path $Campaign 'compiler-environment.json') -Encoding utf8
$start = [Diagnostics.ProcessStartInfo]::new()
$start.FileName = $python
$start.UseShellExecute = $false
$start.CreateNoWindow = $true
$start.RedirectStandardOutput = $true
$start.RedirectStandardError = $true
$start.Environment['PATH'] = $toolPaths[0]
foreach ($arg in $argsForIdf) { [void]$start.ArgumentList.Add($arg) }
$sdkStdout = [IO.File]::Open((Join-Path $Campaign 'sdk-build.stdout.log'), [IO.FileMode]::CreateNew,
 [IO.FileAccess]::Write, [IO.FileShare]::Read)
$sdkStderr = $null
$process = $null
try {
    $sdkStderr = [IO.File]::Open((Join-Path $Campaign 'sdk-build.stderr.log'), [IO.FileMode]::CreateNew,
     [IO.FileAccess]::Write, [IO.FileShare]::Read)
    $process = [Diagnostics.Process]::Start($start)
    $stdoutCopy = $process.StandardOutput.BaseStream.CopyToAsync($sdkStdout)
    $stderrCopy = $process.StandardError.BaseStream.CopyToAsync($sdkStderr)
    $process.WaitForExit()
    $copies = [Threading.Tasks.Task]::WhenAll([Threading.Tasks.Task[]]@($stdoutCopy, $stderrCopy))
    $copies.GetAwaiter().GetResult()
    if ($process.ExitCode -ne 0) { throw "SDK build failed: $($process.ExitCode)" }
} finally {
    if ($process) { $process.Dispose() }
    if ($sdkStderr) { $sdkStderr.Dispose() }
    $sdkStdout.Dispose()
}
