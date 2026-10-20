[CmdletBinding()]
param([string]$VsDevCmd="C:\Program Files\Microsoft Visual Studio\18\Community\Common7\Tools\VsDevCmd.bat",
      [string]$PythonPath)
$ErrorActionPreference="Stop"
$project=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$repo=[IO.Path]::GetFullPath((Join-Path $project "..\.."))
$output=Join-Path $repo ".build\small-tv-esp32c2\native-tests"
New-Item -ItemType Directory -Force -Path $output | Out-Null
if (!(Test-Path -LiteralPath $VsDevCmd)) {throw "Pass -VsDevCmd pointing to an installed MSVC development environment."}
$resources=Join-Path $repo ".build\small-tv-esp32c2\resources"
if (!$PythonPath) {$PythonPath=Join-Path $repo ".idf\python-3.12.10\tools\python.exe"}
& $PythonPath (Join-Path $project "tools\audit_correspondence.py")
if ($LASTEXITCODE) {throw "Factory/native correspondence is missing or stale; review the changed inputs"}
& $PythonPath (Join-Path $project "tests\correspondence_test.py")
if ($LASTEXITCODE) {throw "Correspondence omission controls failed"}
& $PythonPath (Join-Path $project "tools\prepare_resources.py") --output $resources
if ($LASTEXITCODE) {throw "Resource generation failed"}
$sources=@("tests/native_test.c","app/settings/settings.c","app/settings/factory_settings.c","app/services/weather_parser.c","app/text/text.c","app/media/assets.c","app/media/photo_upload.c","app/media/color_convert.c","codec/jpeg_privacy.c","app/network/dns_packet.c","app/web/server.c","app/web/request_body.c","app/web/settings_api.c","app/web/photo_api.c","third_party/tjpgd/tjpgd.c","third_party/cjson/cJSON.c")
$arguments=@("/nologo","/std:c11","/W3","/D_CRT_SECURE_NO_WARNINGS","/DCJSON_NESTING_LIMIT=16")
foreach($include in @("tests/stubs","app/include","codec","third_party/tjpgd","third_party/cjson")) {$arguments+='/I"'+(Join-Path $project $include)+'"'}
$arguments+='/I"'+$resources+'"'
foreach($source in $sources) {$arguments+='"'+(Join-Path $project $source)+'"'}
$arguments+='"'+(Join-Path $resources "web_pages.c")+'"'
$arguments+='/Fe"'+(Join-Path $output "native_test.exe")+'"'
$batch=Join-Path $output "compile.cmd"
[IO.File]::WriteAllText($batch,"@echo off`r`ncall `"$VsDevCmd`" -arch=x64 -host_arch=x64 >nul`r`nif errorlevel 1 exit /b 1`r`ncd /d `"$output`"`r`ncl "+($arguments -join ' ')+"`r`nexit /b %errorlevel%`r`n")
& cmd.exe /d /c $batch
if ($LASTEXITCODE) {throw "Native test compilation failed"}
& (Join-Path $output "native_test.exe") (Join-Path $resources "assets.bin") (Join-Path $output "report.json")
if ($LASTEXITCODE) {throw "Native tests failed"}
# The upload now calls the multi-scan privacy gate. Keep its independent grammar
# and callback controls in the ordinary native gate, without stale build reuse.
$privacyOutput=Join-Path $output ('jpeg-privacy-'+[Guid]::NewGuid().ToString('N'))
& (Join-Path $PSScriptRoot 'jpeg_privacy/run.ps1') -OutputDirectory $privacyOutput -VsDevCmd $VsDevCmd
Copy-Item -LiteralPath (Join-Path $privacyOutput 'report.json') -Destination (Join-Path $output 'privacy-report.json')
Write-Host 'PASS: independent JPEG privacy controls'
