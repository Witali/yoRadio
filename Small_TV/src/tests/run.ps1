[CmdletBinding()]
param([string]$VsDevCmd="C:\Program Files\Microsoft Visual Studio\18\Community\Common7\Tools\VsDevCmd.bat")
$ErrorActionPreference="Stop"
$project=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$repo=[IO.Path]::GetFullPath((Join-Path $project "..\.."))
$output=Join-Path $repo ".build\small-tv-esp32c2\native-tests"
New-Item -ItemType Directory -Force -Path $output | Out-Null
if (!(Test-Path -LiteralPath $VsDevCmd)) {throw "Pass -VsDevCmd pointing to an installed MSVC development environment."}
$resources=Join-Path $repo ".build\small-tv-esp32c2\resources"
& (Join-Path $repo ".idf\python-3.12.10\tools\python.exe") (Join-Path $project "tools\prepare_resources.py") --output $resources
if ($LASTEXITCODE) {throw "Resource generation failed"}
$sources=@("tests/native_test.c","app/settings/settings.c","app/settings/factory_settings.c","app/services/weather_parser.c","app/media/assets.c","app/media/photo_upload.c","app/network/dns_packet.c","app/web/server.c","app/web/settings_api.c","app/web/photo_api.c","third_party/tjpgd/tjpgd.c","third_party/cjson/cJSON.c")
$arguments=@("/nologo","/std:c11","/W3","/D_CRT_SECURE_NO_WARNINGS","/DCJSON_NESTING_LIMIT=16")
foreach($include in @("tests/stubs","app/include","third_party/tjpgd","third_party/cjson")) {$arguments+='/I"'+(Join-Path $project $include)+'"'}
$arguments+='/I"'+$resources+'"'
foreach($source in $sources) {$arguments+='"'+(Join-Path $project $source)+'"'}
$arguments+='/Fe"'+(Join-Path $output "native_test.exe")+'"'
$batch=Join-Path $output "compile.cmd"
[IO.File]::WriteAllText($batch,"@echo off`r`ncall `"$VsDevCmd`" -arch=x64 -host_arch=x64 >nul`r`nif errorlevel 1 exit /b 1`r`ncd /d `"$output`"`r`ncl "+($arguments -join ' ')+"`r`nexit /b %errorlevel%`r`n")
& cmd.exe /d /c $batch
if ($LASTEXITCODE) {throw "Native test compilation failed"}
& (Join-Path $output "native_test.exe") (Join-Path $resources "assets.bin")
if ($LASTEXITCODE) {throw "Native tests failed"}
