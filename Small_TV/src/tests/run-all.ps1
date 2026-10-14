[CmdletBinding()]
param(
    [switch]$SkipMachine,
    [switch]$SkipQemu,
    [switch]$InstallOracleDependencies,
    [string]$QemuRoot="C:\Work\QEMU-ESP32",
    [string]$PythonPath,
    [string]$VsDevCmd="C:\Program Files\Microsoft Visual Studio\18\Community\Common7\Tools\VsDevCmd.bat",
    [string]$OutputDirectory
)
$ErrorActionPreference="Stop"
$repo=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\..\.."))
if (!$PythonPath) {$PythonPath=Join-Path $repo ".idf\tools-v6.1\python_env\idf6.1_py3.12_env\Scripts\python.exe"}
if (!$OutputDirectory) {$OutputDirectory=Join-Path $repo (".build\small-tv-functional\"+[DateTime]::UtcNow.ToString("yyyyMMdd-HHmmss-fff"))}
$OutputDirectory=[IO.Path]::GetFullPath($OutputDirectory)
New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null
$started=[DateTime]::UtcNow.ToString("o")
$groups=[Collections.Generic.List[object]]::new()
function Invoke-TestGroup([string]$Name,[scriptblock]$Action,[string]$ResultPath) {
    Write-Host "Running $Name..."
    $watch=[Diagnostics.Stopwatch]::StartNew()
    try {
        if(Test-Path -LiteralPath $ResultPath){Remove-Item -LiteralPath $ResultPath}
        & $Action *>&1 | Tee-Object -FilePath (Join-Path $OutputDirectory "$Name.log") | Out-Host
        $data=Get-Content -Raw -LiteralPath $ResultPath | ConvertFrom-Json
        if (!$data.passed) {throw "Result did not pass: $ResultPath"}
        $groups.Add(@{name=$Name;status="passed";seconds=$watch.Elapsed.TotalSeconds;result=$data})
    } catch {
        $groups.Add(@{name=$Name;status="failed";seconds=$watch.Elapsed.TotalSeconds;error=$_.Exception.Message})
        Write-Warning "$Name failed: $($_.Exception.Message)"
    }
}
$nativeReport=Join-Path $repo ".build\small-tv-esp32c2\native-tests\report.json"
Invoke-TestGroup "native" {& (Join-Path $PSScriptRoot "run.ps1") -VsDevCmd $VsDevCmd} $nativeReport
$platformReport=Join-Path $repo ".build\small-tv-esp32c2\platform-tests\report.json"
Invoke-TestGroup "platform" {& (Join-Path $PSScriptRoot "run-platform.ps1") -VsDevCmd $VsDevCmd} $platformReport
$frontendReport=Join-Path $OutputDirectory "frontend.json"
Invoke-TestGroup "frontend" {
    & $PythonPath (Join-Path $PSScriptRoot "frontend_test.py") --output $frontendReport
    if($LASTEXITCODE){throw "Frontend JavaScript tests failed"}
} $frontendReport
$integrityReport=Join-Path $OutputDirectory "integrity.json"
Invoke-TestGroup "integrity" {
    & $PythonPath (Join-Path $PSScriptRoot "artifact_test.py") --output $integrityReport
    if($LASTEXITCODE){throw "Artifact integrity tests failed"}
} $integrityReport
$timezoneSourcesReport=Join-Path $OutputDirectory "timezone-sources.json"
Invoke-TestGroup "timezone_sources" {
    & $PythonPath (Join-Path $PSScriptRoot "timezone_update_test.py") --output $timezoneSourcesReport
    if($LASTEXITCODE){throw "Offline timezone archive/update tests failed"}
} $timezoneSourcesReport
if ($SkipMachine) {$groups.Add(@{name="machine";status="not_run";reason="Explicit -SkipMachine"})}
else {
    $machineFolder=Join-Path $OutputDirectory "machine"
    $controlReport=Join-Path $OutputDirectory "control.json"
    if(Test-Path -LiteralPath $controlReport){Remove-Item -LiteralPath $controlReport}
    Invoke-TestGroup "machine" {
        & (Join-Path $PSScriptRoot "run-machine-oracle.ps1") -PythonPath $PythonPath -OutputDirectory $machineFolder -Control -ControlOutputPath $controlReport -InstallDependencies:$InstallOracleDependencies
    } (Join-Path $machineFolder "report.json")
    # The renderer and control checks are separate gates; never accept an old control result.
    if(Test-Path -LiteralPath $controlReport){
        $control=Get-Content -Raw -LiteralPath $controlReport | ConvertFrom-Json
        $groups.Add(@{name="machine_control";status=$(if($control.passed){"passed"}else{"failed"});result=$control})
    }else{$groups.Add(@{name="machine_control";status="failed";error="No fresh control report"})}
}
if ($SkipMachine) {$groups.Add(@{name="machine_classic";status="not_run";reason="Explicit -SkipMachine"})}
else {
    $classicReport=Join-Path $OutputDirectory "classic.json"
    Invoke-TestGroup "machine_classic" {
        & $PythonPath (Join-Path $PSScriptRoot "classic_oracle.py") --output $classicReport
        if($LASTEXITCODE){throw "Classic renderer/animation machine comparison failed"}
    } $classicReport
}
if ($SkipMachine) {$groups.Add(@{name="machine_weather";status="not_run";reason="Explicit -SkipMachine"})}
else {
    $weatherReport=Join-Path $OutputDirectory "weather-render.json"
    Invoke-TestGroup "machine_weather" {
        & $PythonPath (Join-Path $PSScriptRoot "weather_render_oracle.py") --output $weatherReport
        if($LASTEXITCODE){throw "Weather decoder/field/scroll machine comparison failed"}
    } $weatherReport
}
if ($SkipMachine) {$groups.Add(@{name="machine_calendar";status="not_run";reason="Explicit -SkipMachine"})}
else {
    $calendarReport=Join-Path $OutputDirectory "calendar.json"
    Invoke-TestGroup "machine_calendar" {
        & $PythonPath (Join-Path $PSScriptRoot "calendar_oracle.py") --output $calendarReport
        if($LASTEXITCODE){throw "Calendar/date machine comparison failed"}
    } $calendarReport
}
if ($SkipMachine) {$groups.Add(@{name="machine_jpeg";status="not_run";reason="Explicit -SkipMachine"})}
else {
    $jpegReport=Join-Path $OutputDirectory "jpeg.json"
    Invoke-TestGroup "machine_jpeg" {
        & $PythonPath (Join-Path $PSScriptRoot "jpeg_oracle.py") --output $jpegReport
        if($LASTEXITCODE){throw "JPEG decoder/error machine comparison failed"}
    } $jpegReport
}
if ($SkipMachine) {$groups.Add(@{name="machine_timezones";status="not_run";reason="Explicit -SkipMachine"})}
else {
    $timezoneReport=Join-Path $OutputDirectory "timezones.json"
    Invoke-TestGroup "machine_timezones" {
        & $PythonPath (Join-Path $PSScriptRoot "timezone_oracle.py") --output $timezoneReport
        if($LASTEXITCODE){throw "Country timezone/libc machine comparison failed"}
    } $timezoneReport
}
if ($SkipQemu) {$groups.Add(@{name="qemu";status="not_run";reason="Explicit -SkipQemu"})}
else {
    $qemuFolder=Join-Path $OutputDirectory "qemu"
    Invoke-TestGroup "qemu" {
        & $PythonPath (Join-Path $PSScriptRoot "qemu_suite.py") --qemu-root $QemuRoot --output $qemuFolder
        if($LASTEXITCODE){throw "Full-firmware QEMU tests failed"}
    } (Join-Path $qemuFolder "report.json")
}
$groups.Add(@{name="hardware_browser_soak";status="not_run";reason="Physical board/RF/live weather service, long-run memory and full browser acceptance remain manual; focused browser regression is recorded separately"})
$archive=Join-Path $repo "firmware\development\small-tv-esp32c2-reconstructed"
$manifest=Get-Content -Raw -LiteralPath (Join-Path $archive "manifest.json") | ConvertFrom-Json
$testInputs=@(Get-ChildItem -LiteralPath $PSScriptRoot -Recurse -File | Where-Object {$_.Extension -in @('.c','.h','.inc','.ps1','.py','.txt')} | Sort-Object FullName | ForEach-Object {
    @{file=$_.FullName.Substring($repo.Length+1).Replace('\','/');sha256=(Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()}
})
$passed=@($groups | Where-Object {$_.status -eq "failed"}).Count -eq 0
$report=@{schema_version=1;started_utc=$started;finished_utc=[DateTime]::UtcNow.ToString("o");passed=$passed;all_functionality_verified=$false;
    automatic_profile=$(if($SkipMachine -or $SkipQemu){"reduced"}else{"host_machine_qemu"});source_sha256=$manifest.source_sha256;
    app_sha256=(Get-FileHash -LiteralPath (Join-Path $archive "app.bin") -Algorithm SHA256).Hash.ToLowerInvariant();test_inputs=$testInputs;groups=$groups;
    notes=@("Passing automated checks does not establish complete factory equivalence or physical operation.","No board flashing or OTA; original dump and archived images remain read-only.","Host assertions include parameter sweeps; their count is not a code-coverage percentage.")}
$reportPath=Join-Path $OutputDirectory "report.json"
$report | ConvertTo-Json -Depth 24 | Set-Content -Encoding utf8 -LiteralPath $reportPath
Write-Host "Functional report: $reportPath"
if (!$passed) {throw "One or more functional groups failed. See report.json and per-group logs."}
