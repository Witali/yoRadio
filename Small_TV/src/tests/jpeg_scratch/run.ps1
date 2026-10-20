[CmdletBinding()]
param([Parameter(Mandatory)][string]$OutputDirectory,
      [string]$PythonPath='C:\Work\yoRadio\.idf\tools-v6.1\python_env\idf6.1_py3.12_env\Scripts\python.exe',
      [string]$VsDevCmd='C:\Program Files\Microsoft Visual Studio\18\Community\Common7\Tools\VsDevCmd.bat')
$ErrorActionPreference='Stop'
$project=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'));$repo=[IO.Path]::GetFullPath((Join-Path $project '../..'))
$output=[IO.Path]::GetFullPath($OutputDirectory)
& $PythonPath -X utf8 -B (Join-Path $PSScriptRoot 'prepare.py') --assets-dir (Join-Path $repo 'firmware/development/small-tv-esp32c2-reconstructed') --output $output
if($LASTEXITCODE -ne 0){throw 'Scratch preparation failed'}
# Capture compiler inputs before the build, then verify them after execution.
$inputs=@('native_test.c','nor_model.c','nor_model.h','prepare.py','run.ps1') | ForEach-Object {Join-Path $PSScriptRoot $_}
$inputs+=@('storage/jpeg_scratch.c','storage/jpeg_scratch.h','storage/jpeg_nor.c','storage/jpeg_nor.h') | ForEach-Object {Join-Path $project $_}
$inputs+=@(Join-Path $output 'scratch_fixture.h');$inputs+=@(Join-Path $output 'plan.json')
$pins=[ordered]@{}
foreach($path in $inputs){$pins[[IO.Path]::GetFullPath($path)]=(Get-FileHash -LiteralPath $path).Hash.ToLower()}
[IO.File]::WriteAllText((Join-Path $output 'inputs.json'),(($pins | ConvertTo-Json).Replace("`r`n","`n")+"`n"),[Text.UTF8Encoding]::new($false))
$args=@('/nologo','/std:c11','/O2','/W4','/WX','/D_CRT_SECURE_NO_WARNINGS',('/I"'+$output+'"'),('/I"'+(Join-Path $project 'storage')+'"'),
    ('"'+(Join-Path $PSScriptRoot 'native_test.c')+'"'),('"'+(Join-Path $PSScriptRoot 'nor_model.c')+'"'),
    ('"'+(Join-Path $project 'storage/jpeg_scratch.c')+'"'),('"'+(Join-Path $project 'storage/jpeg_nor.c')+'"'),('/Fe"'+(Join-Path $output 'jpeg_scratch_test.exe')+'"'))
$batch=Join-Path $output 'compile.cmd'
[IO.File]::WriteAllText($batch,"@echo off`r`ncall `"$VsDevCmd`" -arch=x64 -host_arch=x64 >nul`r`nif errorlevel 1 exit /b 1`r`ncd /d `"$output`"`r`nwhere cl > compiler-path.txt`r`ncl "+($args -join ' ')+"`r`nexit /b %errorlevel%`r`n")
& cmd.exe /d /c $batch;if($LASTEXITCODE -ne 0){throw 'Scratch compilation failed'}
& (Join-Path $output 'jpeg_scratch_test.exe') | Tee-Object -LiteralPath (Join-Path $output 'report.json')
if($LASTEXITCODE -ne 0){throw 'Scratch contract failed'}
foreach($path in $pins.Keys){if((Get-FileHash -LiteralPath $path).Hash.ToLower() -ne $pins[$path]){throw "Scratch input changed during compilation/test: $path"}}
$compiler=([IO.File]::ReadAllLines((Join-Path $output 'compiler-path.txt')))[0]
$products=[ordered]@{inputs_unchanged=$true;executable_sha256=(Get-FileHash -LiteralPath (Join-Path $output 'jpeg_scratch_test.exe')).Hash.ToLower();compiler=$compiler;compiler_sha256=(Get-FileHash -LiteralPath $compiler).Hash.ToLower()}
[IO.File]::WriteAllText((Join-Path $output 'products.json'),(($products | ConvertTo-Json).Replace("`r`n","`n")+"`n"),[Text.UTF8Encoding]::new($false))
