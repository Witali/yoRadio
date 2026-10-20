[CmdletBinding()]
param([Parameter(Mandatory)][string]$OutputDirectory,
      [string]$VsDevCmd='C:/Program Files/Microsoft Visual Studio/18/Community/Common7/Tools/VsDevCmd.bat')
$ErrorActionPreference='Stop'
$project=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$output=[IO.Path]::GetFullPath($OutputDirectory)
if(Test-Path -LiteralPath $output){throw 'Use a fresh privacy test directory'}
New-Item -ItemType Directory -Path $output -Force | Out-Null
$batch=Join-Path $output 'compile.cmd'
$command='cl /nologo /std:c11 /O2 /W4 /WX /MT /D_CRT_SECURE_NO_WARNINGS /I"'+$project+'/codec" "'+$PSScriptRoot+'/native_test.c" "'+$project+'/codec/jpeg_privacy.c" /Fe"'+$output+'/jpeg_privacy_test.exe"'
[IO.File]::WriteAllText($batch,"@echo off`r`ncall `"$VsDevCmd`" -arch=x64 -host_arch=x64 >nul`r`nif errorlevel 1 exit /b 1`r`ncd /d `"$output`"`r`n$command`r`nexit /b %errorlevel%`r`n")
& cmd.exe /d /c $batch
if($LASTEXITCODE -ne 0){throw 'Privacy compilation failed'}
& (Join-Path $output 'jpeg_privacy_test.exe') | Set-Content -LiteralPath (Join-Path $output 'report.json') -Encoding utf8
if($LASTEXITCODE -ne 0){throw 'Privacy controls failed'}
