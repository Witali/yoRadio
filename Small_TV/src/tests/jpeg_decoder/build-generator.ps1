[CmdletBinding()]
param([Parameter(Mandatory)][string]$LibraryBuild,[Parameter(Mandatory)][string]$OutputDirectory,
      [string]$VsDevCmd='C:\Program Files\Microsoft Visual Studio\18\Community\Common7\Tools\VsDevCmd.bat')
$ErrorActionPreference='Stop';$library=[IO.Path]::GetFullPath($LibraryBuild);$output=[IO.Path]::GetFullPath($OutputDirectory)
New-Item -ItemType Directory -Path $output -ErrorAction Stop | Out-Null
$source=Join-Path $PSScriptRoot 'generate.c';$archive=Join-Path $library 'library/jpeg-static.lib'
$record=Get-Content (Join-Path $library 'build.json') -Raw | ConvertFrom-Json
if((Get-FileHash -LiteralPath $archive).Hash.ToLower() -ne $record.library_sha256){throw 'Generator library hash differs'}
$pins=[ordered]@{}
foreach($path in @($source,$archive,$PSCommandPath)){$pins[[IO.Path]::GetFullPath($path)]=(Get-FileHash -LiteralPath $path).Hash.ToLower()}
[IO.File]::WriteAllText((Join-Path $output 'inputs.json'),(($pins|ConvertTo-Json).Replace("`r`n","`n")+"`n"),[Text.UTF8Encoding]::new($false))
$batch=Join-Path $output 'compile.cmd';$exe=Join-Path $output 'generate.exe'
[IO.File]::WriteAllText($batch,"@echo off`r`ncall `"$VsDevCmd`" -arch=x64 -host_arch=x64 >nul`r`nif errorlevel 1 exit /b 1`r`ncd /d `"$output`"`r`ncl /nologo /std:c11 /O2 /W4 /WX /MT /DJPEG_STATIC /D_CRT_SECURE_NO_WARNINGS /I`"$library/source/src`" /I`"$library/library`" `"$source`" /Fe`"$exe`" /link `"$archive`"`r`nexit /b %errorlevel%`r`n")
& cmd.exe /d /c $batch;if($LASTEXITCODE -ne 0){throw 'Sampling generator build failed'}
foreach($path in $pins.Keys){if((Get-FileHash -LiteralPath $path).Hash.ToLower() -ne $pins[$path]){throw 'Generator source changed'}}
$result=[ordered]@{inputs_unchanged=$true;executable=$exe;executable_sha256=(Get-FileHash -LiteralPath $exe).Hash.ToLower();library_build=$library}
[IO.File]::WriteAllText((Join-Path $output 'build.json'),(($result|ConvertTo-Json).Replace("`r`n","`n")+"`n"),[Text.UTF8Encoding]::new($false))
