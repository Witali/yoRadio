param([Parameter(Mandatory)][string]$Campaign,
      [Parameter(Mandatory)][string]$SdkDirectory,
      [Parameter(Mandatory)][string]$ToolsDirectory,
      [Parameter(Mandatory)][string]$PythonExecutable)
$ErrorActionPreference = 'Stop'
$campaignPath = [IO.Path]::GetFullPath($Campaign)
$contractPath = Join-Path $campaignPath 'source-manifest.json'
if (!(Test-Path -LiteralPath $contractPath -PathType Leaf) -or
    (Test-Path -LiteralPath (Join-Path $campaignPath 'build'))) {
    throw 'Use the controller to prepare a fresh isolated campaign'
}
$contract = Get-Content -LiteralPath $contractPath -Raw | ConvertFrom-Json
foreach ($entry in $contract.sources.PSObject.Properties) {
    $path = [IO.Path]::GetFullPath((Join-Path $campaignPath $entry.Value.snapshot))
    if (!$path.StartsWith($campaignPath + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase) -or
        (Get-FileHash -Algorithm SHA256 -LiteralPath $path).Hash.ToLowerInvariant() -cne $entry.Value.sha256) {
        throw 'Frozen source mismatch'
    }
}
foreach ($entry in $contract.generated_project_inputs.PSObject.Properties) {
    $path = [IO.Path]::GetFullPath((Join-Path $campaignPath $entry.Name))
    if (!$path.StartsWith($campaignPath + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase) -or
        (Get-FileHash -Algorithm SHA256 -LiteralPath $path).Hash.ToLowerInvariant() -cne $entry.Value.sha256) {
        throw 'Generated project or diagnostic CA input mismatch'
    }
}
$env:IDF_PATH = [IO.Path]::GetFullPath($SdkDirectory)
$env:IDF_TOOLS_PATH = [IO.Path]::GetFullPath($ToolsDirectory)
$env:TLS_TRAFFIC_REPOSITORY = (Join-Path $campaignPath 'sources/repository').Replace('\','/')
$env:TLS_TRAFFIC_PRODUCTION_KCONFIG = (Join-Path $env:TLS_TRAFFIC_REPOSITORY 'idf/esp32-cyd2usb-native/main/Kconfig.projbuild').Replace('\','/')
$env:IDF_COMPONENT_MANAGER = '0'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:PYTHONNOUSERSITE = '1'
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'
$env:GIT_CONFIG_COUNT = '1'
$env:GIT_CONFIG_KEY_0 = 'core.longpaths'
$env:GIT_CONFIG_VALUE_0 = 'true'
$env:GIT_OPTIONAL_LOCKS = '0'
$env:CCACHE_DISABLE = '1'
$python = [IO.Path]::GetFullPath($PythonExecutable)
$env:IDF_PYTHON_ENV_PATH = Split-Path (Split-Path $python)
$env:Path = (Split-Path $python) + ';' + $env:Path
$temporary = Join-Path $campaignPath 'tool-temp'
[void][IO.Directory]::CreateDirectory($temporary)
$env:TEMP = $temporary
$env:TMP = $temporary
$head = & git -c core.longpaths=true -C $env:IDF_PATH rev-parse HEAD
if ($head.Trim() -cne '7101770dc6db2667b3c477cc31365dd1acd6db4e') { throw 'Wrong SDK revision' }
$dirty = & git -c core.longpaths=true -C $env:IDF_PATH status --porcelain --untracked-files=no
if ($dirty) { throw 'Installed SDK tracked sources must remain clean' }
. (Join-Path $env:IDF_PATH 'export.ps1')
if ($LASTEXITCODE -ne 0) { throw 'SDK activation failed' }
$idfArgs = @((Join-Path $env:IDF_PATH 'tools/idf.py'),'-C',(Join-Path $campaignPath 'project'),
    '-B',(Join-Path $campaignPath 'build'),'--no-ccache','-D','IDF_TARGET=esp32',
    '-D',"SDKCONFIG=$campaignPath/sdkconfig",'-D',"SDKCONFIG_DEFAULTS=$campaignPath/project/sdkconfig.defaults",
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
$stdoutFile = [IO.File]::Open((Join-Path $campaignPath 'sdk-build.stdout.log'),[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::Read)
$stderrFile = $null
$process = $null
try {
    $stderrFile = [IO.File]::Open((Join-Path $campaignPath 'sdk-build.stderr.log'),[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::Read)
    $process = [Diagnostics.Process]::Start($start)
    $stdoutCopy = $process.StandardOutput.BaseStream.CopyToAsync($stdoutFile)
    $stderrCopy = $process.StandardError.BaseStream.CopyToAsync($stderrFile)
    $process.WaitForExit()
    [Threading.Tasks.Task]::WhenAll([Threading.Tasks.Task[]]@($stdoutCopy,$stderrCopy)).GetAwaiter().GetResult()
    [ordered]@{pid=$process.Id;exit_status=$process.ExitCode;argv=@($python)+$idfArgs} |
        ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $campaignPath 'sdk-child.json') -Encoding utf8
    if ($process.ExitCode -ne 0) { throw "SDK build failed: $($process.ExitCode)" }
} finally {
    if ($process) { $process.Dispose() }
    if ($stderrFile) { $stderrFile.Dispose() }
    $stdoutFile.Dispose()
}
