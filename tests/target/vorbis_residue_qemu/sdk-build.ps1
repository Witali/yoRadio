param([Parameter(Mandatory)][string]$Campaign,
      [Parameter(Mandatory)][string]$SdkDirectory,
      [Parameter(Mandatory)][string]$ToolsDirectory,
      [Parameter(Mandatory)][string]$PythonExecutable,
      [Parameter(Mandatory)][ValidateSet('esp32','esp32c3')][string]$Target,
      [Parameter(Mandatory)][string]$SourceSha256,
      [Parameter(Mandatory)][string]$HeaderSha256,
      [Parameter(Mandatory)][string]$QuantSourceSha256,
      [Parameter(Mandatory)][string]$QuantHeaderSha256,
      [Parameter(Mandatory)][string]$CodebookSourceSha256,
      [Parameter(Mandatory)][string]$CodebookHeaderSha256,
      [Parameter(Mandatory)][string]$SetupSourceSha256,
      [Parameter(Mandatory)][string]$SetupHeaderSha256,
      [Parameter(Mandatory)][string]$FloorPacketSourceSha256,
      [Parameter(Mandatory)][string]$FloorPacketHeaderSha256,
      [Parameter(Mandatory)][string]$ResidueSourceSha256,
      [Parameter(Mandatory)][string]$ResidueHeaderSha256,
      [Parameter(Mandatory)][string]$ComponentSha256,
      [Parameter(Mandatory)][string]$CasesSha256)
$ErrorActionPreference = 'Stop'
$Campaign = [IO.Path]::GetFullPath($Campaign)
if (!(Test-Path -LiteralPath (Join-Path $Campaign 'report.json') -PathType Leaf)) {
    throw 'Use the Python controller to create a fresh campaign'
}
$env:IDF_PATH = [IO.Path]::GetFullPath($SdkDirectory)
$env:IDF_TOOLS_PATH = [IO.Path]::GetFullPath($ToolsDirectory)
$env:RESIDUE_COMPONENT = (Join-Path $Campaign 'sources/components/native_vorbis_numeric').Replace('\','/')
$env:IDF_COMPONENT_MANAGER = '0'
$env:PYTHONNOUSERSITE = '1'
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'
$env:GIT_CONFIG_COUNT = '1'
$env:GIT_CONFIG_KEY_0 = 'core.longpaths'
$env:GIT_CONFIG_VALUE_0 = 'true'
$env:GIT_OPTIONAL_LOCKS = '0'
$python = [IO.Path]::GetFullPath($PythonExecutable)
$env:IDF_PYTHON_ENV_PATH = Split-Path (Split-Path $python)
$env:Path = (Split-Path $python) + ';' + $env:Path
. (Join-Path $env:IDF_PATH 'export.ps1')
if ($LASTEXITCODE -ne 0) { throw 'SDK activation failed' }
$idfArgs = @((Join-Path $env:IDF_PATH 'tools/idf.py'),'-C',(Join-Path $Campaign 'project'),
    '-B',(Join-Path $Campaign 'build'),'--no-ccache','-D',"IDF_TARGET=$Target",
    '-D',"SDKCONFIG=$Campaign/sdkconfig",'-D',"SDKCONFIG_DEFAULTS=$Campaign/project/sdkconfig.defaults",
    '-D',"FLOOR0_source_SHA256=$SourceSha256",'-D',"FLOOR0_header_SHA256=$HeaderSha256",
    '-D',"FLOOR0_quant_source_SHA256=$QuantSourceSha256",'-D',"FLOOR0_quant_header_SHA256=$QuantHeaderSha256",
    '-D',"FLOOR0_codebook_source_SHA256=$CodebookSourceSha256",'-D',"FLOOR0_codebook_header_SHA256=$CodebookHeaderSha256",
    '-D',"FLOOR0_setup_source_SHA256=$SetupSourceSha256",'-D',"FLOOR0_setup_header_SHA256=$SetupHeaderSha256",
    '-D',"FLOOR0_floor_packet_source_SHA256=$FloorPacketSourceSha256",'-D',"FLOOR0_floor_packet_header_SHA256=$FloorPacketHeaderSha256",
    '-D',"FLOOR0_residue_source_SHA256=$ResidueSourceSha256",'-D',"FLOOR0_residue_header_SHA256=$ResidueHeaderSha256",
    '-D',"FLOOR0_component_SHA256=$ComponentSha256",'-D',"FLOOR0_CASES_SHA256=$CasesSha256",
    '-D','CMAKE_JOB_POOLS=compile=2;link=1','-D','CMAKE_JOB_POOL_COMPILE=compile',
    '-D','CMAKE_JOB_POOL_LINK=link','build')
$toolPaths = @(Get-ChildItem Env: | Where-Object { $_.Name -imatch '^path$' -and $_.Value.Contains('tools\ninja') } | Select-Object -ExpandProperty Value)
if ($toolPaths.Count -ne 1) { throw 'Activated toolchain PATH missing' }
$start = [Diagnostics.ProcessStartInfo]::new()
$start.FileName = $python
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
    [ordered]@{ pid=$process.Id; exit_status=$process.ExitCode; argv=@($python)+$idfArgs } |
        ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $Campaign 'sdk-child.json') -Encoding utf8
    if ($process.ExitCode -ne 0) { throw "SDK build failed: $($process.ExitCode)" }
} finally {
    if ($process) { $process.Dispose() }
    if ($sdkStderr) { $sdkStderr.Dispose() }
    $sdkStdout.Dispose()
}
