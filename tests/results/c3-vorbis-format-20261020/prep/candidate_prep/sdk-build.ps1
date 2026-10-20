[CmdletBinding(PositionalBinding = $false)]
param([Parameter(Mandatory)][string]$Campaign,
      [Parameter(Mandatory)][ValidateSet('0','1')][string]$ExpectedRejection,
      [Parameter(Mandatory)][string]$PinsSha256)
$ErrorActionPreference = 'Stop'
$prepRoot = $PSScriptRoot
$pinsPath = Join-Path $prepRoot 'pins.json'
if ((Get-FileHash -LiteralPath $pinsPath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $PinsSha256) {
    throw 'Explicit reviewed pins SHA mismatch'
}
$pins = Get-Content -LiteralPath $pinsPath -Raw | ConvertFrom-Json
if ($pins.schema -ne 'c3-public-vorbis-format-project-pins-v1') { throw 'Wrong source-only prep pins' }
if ($PSVersionTable.PSEdition -ne 'Core' -or
    [IO.Path]::GetFullPath((Get-Process -Id $PID).Path) -ne [IO.Path]::GetFullPath($pins.tools.powershell)) {
    throw 'Run this launcher with the pinned PowerShell Core executable'
}
function Assert-Identity($path, $identity) {
    $item = Get-Item -LiteralPath $path
    if ($item.Length -ne $identity.bytes -or
        (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant() -ne $identity.sha256) {
        throw "Pinned bytes changed: $path"
    }
}
foreach ($row in $pins.files) { Assert-Identity (Join-Path $prepRoot $row.relative) $row }
foreach ($row in $pins.external_inputs) { Assert-Identity $row.path $row }
$Campaign = [IO.Path]::GetFullPath($Campaign)
$draftRoot = [IO.Path]::GetFullPath((Join-Path $pins.repository '.build'))
if (!$Campaign.StartsWith($draftRoot + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase) -or
    $Campaign.StartsWith([IO.Path]::GetFullPath($prepRoot) + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase) -or
    (Test-Path -LiteralPath $Campaign)) {
    throw 'A fresh campaign outside this prep, inside the pinned repository .build, is required'
}
$env:IDF_PATH = $pins.sdk_directory
$env:IDF_TOOLS_PATH = $pins.tools_directory
$env:YORADIO_AUDIO_CODEC_COMPONENT = $pins.codec_directory
$env:IDF_COMPONENT_MANAGER = '0'
$env:IDF_TOOLCHAIN = 'gcc'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:PYTHONNOUSERSITE = '1'
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'
$env:GIT_CONFIG_COUNT = '1'
$env:GIT_CONFIG_KEY_0 = 'core.longpaths'
$env:GIT_CONFIG_VALUE_0 = 'true'
$env:GIT_OPTIONAL_LOCKS = '0'
# Future authorized execution only. These are read-only SDK provenance checks;
# source preparation never launches this script or Git/SDK/compiler commands.
$git = $pins.tools.git
$revision = (& $git -C $env:IDF_PATH rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $revision -ne $pins.sdk_revision) { throw 'Installed SDK source revision mismatch' }
$sdkStatus = (& $git -C $env:IDF_PATH status --porcelain --untracked-files=no)
if ($LASTEXITCODE -ne 0 -or $sdkStatus) { throw 'Installed SDK tracked source must be clean' }
New-Item -ItemType Directory -Path $Campaign | Out-Null
foreach ($row in $pins.files) {
    if ($row.relative.StartsWith('project/') -or $row.relative.StartsWith('variant/')) {
        $relative = if ($row.relative.StartsWith('project/')) { 'sources/' + $row.relative } else { $row.relative }
        $destination = [IO.Path]::GetFullPath((Join-Path $Campaign $relative))
        if (!$destination.StartsWith($Campaign + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) {
            throw 'Copied campaign source path escape'
        }
        New-Item -ItemType Directory -Force -Path (Split-Path $destination) | Out-Null
        Copy-Item -LiteralPath (Join-Path $prepRoot $row.relative) -Destination $destination
        Assert-Identity $destination $row
    }
}
Copy-Item -LiteralPath $pinsPath -Destination (Join-Path $Campaign 'pins.json')
$env:C3_VORBIS_CANDIDATE = (Join-Path $Campaign 'variant').Replace('\', '/')
$python = $pins.tools.python
$env:IDF_PYTHON_ENV_PATH = Split-Path (Split-Path $python)
$env:Path = (Split-Path $python) + ';' + $env:Path
. (Join-Path $env:IDF_PATH 'export.ps1')
if ($LASTEXITCODE -ne 0) { throw 'SDK activation failed' }
$toolPaths = @(Get-ChildItem Env: | Where-Object { $_.Name -imatch '^path$' -and $_.Value.Contains('tools\ninja') } | Select-Object -ExpandProperty Value)
if ($toolPaths.Count -ne 1) { throw 'Activated toolchain PATH missing' }
$compiler = (Get-Command riscv32-esp-elf-gcc.exe -CommandType Application -ErrorAction Stop | Select-Object -First 1).Source
if ([IO.Path]::GetFullPath($compiler) -ne [IO.Path]::GetFullPath($pins.tools.compiler)) { throw 'Activated compiler path differs from pinned RV32 tool' }
$selectedTools = [ordered]@{compiler=$compiler;python=$python}
foreach ($pair in @(@('cmake.exe','cmake'), @('ninja.exe','ninja'))) {
    $selected = (Get-Command $pair[0] -CommandType Application -ErrorAction Stop | Select-Object -First 1).Source
    if ([IO.Path]::GetFullPath($selected) -ne [IO.Path]::GetFullPath($pins.tools.($pair[1]))) { throw 'Activated CMake/Ninja differs from pinned tool' }
    $selectedTools[$pair[1]] = $selected
}
foreach ($row in $pins.external_inputs) { Assert-Identity $row.path $row }
$argsForIdf = @((Join-Path $env:IDF_PATH 'tools/idf.py'), '-C', (Join-Path $Campaign 'sources/project'),
 '-B', (Join-Path $Campaign 'build'), '--no-ccache', '-D', 'IDF_TARGET=esp32c3', '-D', 'IDF_TOOLCHAIN=gcc',
 '-D', "SDKCONFIG=$Campaign/sdkconfig", '-D', "SDKCONFIG_DEFAULTS=$Campaign/sources/project/sdkconfig.defaults",
 '-D', "FORMAT_EXPECT_LOW_RATE_REJECTION=$ExpectedRejection",
 '-D', 'CMAKE_JOB_POOLS=compile=2;link=1', '-D', 'CMAKE_JOB_POOL_COMPILE=compile', '-D', 'CMAKE_JOB_POOL_LINK=link', 'build')
$recordPath = Join-Path $Campaign 'sdk-build-result.json'
$record = [ordered]@{schema='c3-public-vorbis-format-sdk-build-v1';status='STARTING';
 sdk_revision=$revision; sdk_tracked_clean=$true; pins_sha256=$PinsSha256; expected_rejection=[int]$ExpectedRejection;
 compiler=$compiler; selected_tools=$selectedTools; executable=$python; argv=$argsForIdf; cwd=$Campaign;
 qualification_scope='SDK build only; no format/QEMU/runtime qualification'; child_pid=$null; returncode=$null}
$record | ConvertTo-Json -Depth 7 | Set-Content -LiteralPath $recordPath -Encoding utf8
[ordered]@{ PATH=$toolPaths[0]; IDF_PATH=$env:IDF_PATH; IDF_TOOLS_PATH=$env:IDF_TOOLS_PATH;
 IDF_PYTHON_ENV_PATH=$env:IDF_PYTHON_ENV_PATH } | ConvertTo-Json |
 Set-Content -LiteralPath (Join-Path $Campaign 'compiler-environment.json') -Encoding utf8
$start = [Diagnostics.ProcessStartInfo]::new()
$start.FileName = $python
$start.WorkingDirectory = $Campaign
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
    $record.status = 'RUNNING'
    $record.child_pid = $process.Id
    $record | ConvertTo-Json -Depth 7 | Set-Content -LiteralPath $recordPath -Encoding utf8
    $stdoutCopy = $process.StandardOutput.BaseStream.CopyToAsync($sdkStdout)
    $stderrCopy = $process.StandardError.BaseStream.CopyToAsync($sdkStderr)
    $process.WaitForExit()
    $copies = [Threading.Tasks.Task]::WhenAll([Threading.Tasks.Task[]]@($stdoutCopy, $stderrCopy))
    $copies.GetAwaiter().GetResult()
    $record.returncode = $process.ExitCode
    if ($process.ExitCode -ne 0) { throw "SDK build failed: $($process.ExitCode)" }
    foreach ($row in $pins.files) { Assert-Identity (Join-Path $prepRoot $row.relative) $row }
    foreach ($row in $pins.files) {
        if ($row.relative.StartsWith('project/') -or $row.relative.StartsWith('variant/')) {
            $relative = if ($row.relative.StartsWith('project/')) { 'sources/' + $row.relative } else { $row.relative }
            Assert-Identity (Join-Path $Campaign $relative) $row
        }
    }
    foreach ($row in $pins.external_inputs) { Assert-Identity $row.path $row }
    $record.status = 'TERMINAL_SUCCESS'
} catch {
    $record.status = 'TERMINAL_FAILURE'
    $record['error'] = $_.Exception.Message
    throw
} finally {
    if ($process) { $process.Dispose() }
    if ($sdkStderr) { $sdkStderr.Dispose() }
    $sdkStdout.Dispose()
    $record['stdout_sha256'] = (Get-FileHash -LiteralPath (Join-Path $Campaign 'sdk-build.stdout.log') -Algorithm SHA256).Hash.ToLowerInvariant()
    if (Test-Path -LiteralPath (Join-Path $Campaign 'sdk-build.stderr.log')) {
        $record['stderr_sha256'] = (Get-FileHash -LiteralPath (Join-Path $Campaign 'sdk-build.stderr.log') -Algorithm SHA256).Hash.ToLowerInvariant()
    }
    $record | ConvertTo-Json -Depth 7 | Set-Content -LiteralPath $recordPath -Encoding utf8
}
