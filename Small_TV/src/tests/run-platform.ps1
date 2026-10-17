[CmdletBinding()]
param([string]$VsDevCmd="C:\Program Files\Microsoft Visual Studio\18\Community\Common7\Tools\VsDevCmd.bat",
      [string]$PythonPath)
$ErrorActionPreference="Stop"
$project=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$repo=[IO.Path]::GetFullPath((Join-Path $project "..\.."))
$output=Join-Path $repo ".build\small-tv-esp32c2\platform-tests"
$resources=Join-Path $repo ".build\small-tv-esp32c2\resources"
New-Item -ItemType Directory -Force -Path $output | Out-Null
if (!(Test-Path -LiteralPath $VsDevCmd)) {throw "Pass -VsDevCmd pointing to an installed MSVC development environment."}
if (!$PythonPath) {$PythonPath=Join-Path $repo ".idf\python-3.12.10\tools\python.exe"}
& $PythonPath (Join-Path $project "tools\prepare_resources.py") --output $resources
if ($LASTEXITCODE) {throw "Resource generation failed"}
$sources=@("tests/platform_test.c","app/network/wifi.c","app/services/weather.c","app/services/weather_parser.c","app/services/time_sync.c","app/services/timezones.c","app/text/text.c","app/display/backlight.c","app/display/st7789.c","app/display/factory_fonts.c","app/display/ui_renderer.c","app/display/clock_ui.c","app/display/factory_timer.c","app/display/factory_photo.c","app/display/factory_animation.c","third_party/cjson/cJSON.c")
$arguments=@("/nologo","/std:c11","/experimental:c11atomics","/W3","/D_CRT_SECURE_NO_WARNINGS","/Dsetenv=test_setenv","/Dtzset=test_tzset")
$arguments+='/FI"'+(Join-Path $project "tests/stubs/time_adapter.h")+'"'
foreach($include in @("tests/stubs","app/include","third_party/cjson")) {$arguments+='/I"'+(Join-Path $project $include)+'"'}
$arguments+='/I"'+$resources+'"'
foreach($source in $sources) {$arguments+='"'+(Join-Path $project $source)+'"'}
$arguments+='"'+(Join-Path $resources "factory_bitmaps.c")+'"'
$arguments+='/Fe"'+(Join-Path $output "platform_test.exe")+'"'
$batch=Join-Path $output "compile.cmd"
[IO.File]::WriteAllText($batch,"@echo off`r`ncall `"$VsDevCmd`" -arch=x64 -host_arch=x64 >nul`r`nif errorlevel 1 exit /b 1`r`ncd /d `"$output`"`r`ncl "+($arguments -join ' ')+"`r`nexit /b %errorlevel%`r`n")
& cmd.exe /d /c $batch
if ($LASTEXITCODE) {throw "Platform test compilation failed"}
$cases=@("wifi_setup","wifi_reconnect_scan","wifi_open_station","wifi_pending_dhcp","wifi_failure_recovered","wifi_failed_retries","restart_persistence_failure","wifi_allocation_failure","wifi_task_failure","weather_worker","time_worker","time_zone_boundaries","backlight_schedule","display_protocol_clipping","ui_transitions","text_field_windows","weather_field_cleanup","clock_coordinator","timer_driver_failures","clock_animation_selection","clock_text_scroll","clock_calendar_classic","clock_calendar_simple","clock_timezone_classic","clock_timezone_simple")
$cases+=@("clock_sync_classic","clock_sync_simple")
$cases+=@("regional_time_worker","regional_weather_worker")
$cases+=@("clock_first_digital_brightness")
$cases+=@("clock_photo_idle_brightness")
$cases+=@("clock_photo_reselect")
$cases+=@("clock_photo_active_reselect")
$cases+=@("clock_offline_dst_classic","clock_offline_dst_simple","clock_offline_dst_dial","clock_offline_photo")
$cases+=@("clock_weather_pending_classic","clock_weather_pending_simple","clock_weather_pending_dial","clock_weather_pending_photo")
$cases+=@("clock_startup_ready_classic","clock_startup_ready_simple","clock_startup_ready_photo","clock_startup_ready_dial","clock_startup_wait_sync","clock_startup_wait_address")
$results=@()
foreach($case in $cases) {
    $path=Join-Path $output "$case.json"
    if (Test-Path -LiteralPath $path) {Remove-Item -LiteralPath $path}
    & (Join-Path $output "platform_test.exe") $case $path
    if ($LASTEXITCODE) {throw "Platform scenario failed: $case"}
    $results+=Get-Content -Raw -LiteralPath $path | ConvertFrom-Json
}
$report=@{passed=$true;cases=$results;scope="Production worker/driver code with deterministic ESP-IDF adapters; no real RF, scheduling, electrical or TLS validation."}
$report | ConvertTo-Json -Depth 8 | Set-Content -Encoding utf8 -LiteralPath (Join-Path $output "report.json")
