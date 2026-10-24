param([Parameter(Mandatory)][string]$Campaign,
      [Parameter(Mandatory)][string]$SdkDirectory,
      [Parameter(Mandatory)][string]$ToolsDirectory,
      [Parameter(Mandatory)][string]$CodecDirectory,
      [Parameter(Mandatory)][string]$PythonExecutable,
      [Parameter(Mandatory)][ValidateSet('esp32','esp32c3')][string]$Target,
      [ValidateSet('on','off')][string]$Renderer = 'off',
      [ValidateSet('direct','registered')][string]$Dispatch = 'direct',
      [ValidateSet('none','register-open','register-decode')][string]$BindingControl = 'none',
      [ValidateSet('on','off')][string]$ResetCycles = 'off',
      [ValidateSet('on','off')][string]$OpenOom = 'off')
$ErrorActionPreference = 'Stop'
$Campaign = [IO.Path]::GetFullPath($Campaign)
if (!(Test-Path -LiteralPath (Join-Path $Campaign 'report.json') -PathType Leaf)) {
    throw 'Use the Python runner to prepare a fresh campaign'
}
$env:IDF_PATH = [IO.Path]::GetFullPath($SdkDirectory)
$env:IDF_TOOLS_PATH = [IO.Path]::GetFullPath($ToolsDirectory)
$env:YORADIO_AUDIO_CODEC_COMPONENT = [IO.Path]::GetFullPath($CodecDirectory)
$env:VORBIS_FLOOR1_MAIN = (Join-Path $Campaign 'variant').Replace('\','/')
$env:IDF_COMPONENT_MANAGER = '0'
$env:PYTHONNOUSERSITE = '1'
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'
$env:GIT_CONFIG_COUNT = '1'
$env:GIT_CONFIG_KEY_0 = 'core.longpaths'
$env:GIT_CONFIG_VALUE_0 = 'true'
$env:GIT_OPTIONAL_LOCKS = '0'
$env:IDF_PYTHON_ENV_PATH = Split-Path (Split-Path $PythonExecutable)
$env:Path = (Split-Path $PythonExecutable) + ';' + $env:Path
. (Join-Path $env:IDF_PATH 'export.ps1')
if ($LASTEXITCODE -ne 0) { throw 'SDK activation failed' }
$idfArgs = @((Join-Path $env:IDF_PATH 'tools/idf.py'),'-C',(Join-Path $Campaign 'project'),
    '-B',(Join-Path $Campaign 'build'),'--no-ccache','-D',"IDF_TARGET=$Target",
    '-D',"SDKCONFIG=$Campaign/sdkconfig",'-D',"SDKCONFIG_DEFAULTS=$Campaign/project/sdkconfig.defaults",
    '-D',"FLOOR1_RENDER_MODE=$Renderer",
    '-D',"FLOOR1_DISPATCH_MODE=$Dispatch",'-D',"FLOOR1_BINDING_CONTROL=$BindingControl",
    '-D',"FLOOR1_RESET_MODE=$ResetCycles",
    '-D',"FLOOR1_OPEN_OOM_MODE=$OpenOom",
    '-D','CMAKE_JOB_POOLS=compile=2;link=1','-D','CMAKE_JOB_POOL_COMPILE=compile','-D','CMAKE_JOB_POOL_LINK=link')
foreach ($part in @('setup','output','abi','floor')) {
    $relative = if ($part -eq 'abi') { 'vorbis_repair_abi.h' } elseif ($part -eq 'floor') { 'vorbis_repair/floor1_render.h' } else { "vorbis_repair/$part.c" }
    $digest = (Get-FileHash -LiteralPath (Join-Path $Campaign "variant/$relative") -Algorithm SHA256).Hash.ToLowerInvariant()
    $idfArgs += @('-D',"FLOOR1_${part}_SHA256=$digest")
}
$idfArgs += 'build'
$toolPaths = @(Get-ChildItem Env: | Where-Object { $_.Name -imatch '^path$' -and $_.Value.Contains('tools\ninja') } | Select-Object -ExpandProperty Value)
if ($toolPaths.Count -ne 1) { throw 'Activated toolchain PATH missing' }
$start = [Diagnostics.ProcessStartInfo]::new()
$start.FileName = $PythonExecutable
$start.UseShellExecute = $false
$start.CreateNoWindow = $true
$start.RedirectStandardOutput = $true
$start.RedirectStandardError = $true
$start.Environment['PATH'] = $toolPaths[0]
foreach ($arg in $idfArgs) { [void]$start.ArgumentList.Add($arg) }
$sdkStdout = [IO.File]::Open((Join-Path $Campaign 'sdk-build.stdout.log'),[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::Read)
$sdkStderr = $null
$process = $null
try {
    $sdkStderr = [IO.File]::Open((Join-Path $Campaign 'sdk-build.stderr.log'),[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::Read)
    $process = [Diagnostics.Process]::Start($start)
    $stdoutCopy = $process.StandardOutput.BaseStream.CopyToAsync($sdkStdout)
    $stderrCopy = $process.StandardError.BaseStream.CopyToAsync($sdkStderr)
    $process.WaitForExit()
    $copies = [Threading.Tasks.Task]::WhenAll([Threading.Tasks.Task[]]@($stdoutCopy,$stderrCopy))
    $copies.GetAwaiter().GetResult()
    if ($process.ExitCode -ne 0) { throw "SDK build failed: $($process.ExitCode)" }
} finally {
    if ($process) { $process.Dispose() }
    if ($sdkStderr) { $sdkStderr.Dispose() }
    $sdkStdout.Dispose()
}
