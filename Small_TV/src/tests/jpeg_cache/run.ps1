[CmdletBinding()]
param([Parameter(Mandatory)][string]$OutputDirectory,[Parameter(Mandatory)][string]$LibraryBuild,[switch]$Quick,
      [string]$PythonPath='C:\Work\yoRadio\.idf\tools-v6.1\python_env\idf6.1_py3.12_env\Scripts\python.exe',
      [string]$VsDevCmd='C:\Program Files\Microsoft Visual Studio\18\Community\Common7\Tools\VsDevCmd.bat')
$ErrorActionPreference='Stop';$project=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'));$repo=[IO.Path]::GetFullPath((Join-Path $project '../..'));$output=[IO.Path]::GetFullPath($OutputDirectory)
& $PythonPath -X utf8 -B (Join-Path $project 'tools/jpeg_cache_layout.py') --assets-dir (Join-Path $repo 'firmware/development/small-tv-esp32c2-reconstructed') --library-build $LibraryBuild --output $output
if($LASTEXITCODE -ne 0){throw 'Cache layout preparation failed'}
$names=@('storage/jpeg_cache.c','storage/jpeg_cache.h','storage/jpeg_guard.h','storage/jpeg_nor.c','storage/jpeg_nor.h','storage/jpeg_journal.c','storage/jpeg_journal.h','tests/jpeg_cache/native_test.c','tests/jpeg_cache/run.ps1')
$pins=[ordered]@{};foreach($name in $names){$path=Join-Path $project $name;$pins[$path]=(Get-FileHash -LiteralPath $path).Hash.ToLower()}
$plan=Get-Content -LiteralPath (Join-Path $output 'plan.json') -Raw|ConvertFrom-Json
foreach($property in $plan.cache_inputs_sha256.PSObject.Properties){$pins[$property.Name]=$property.Value}
foreach($name in @('jpeg_layout.h','jpeg_cache_layout.h')){$path=Join-Path $output $name;$pins[$path]=(Get-FileHash -LiteralPath $path).Hash.ToLower()}
[IO.File]::WriteAllText((Join-Path $output 'inputs.json'),(($pins|ConvertTo-Json).Replace("`r`n","`n")+"`n"),[Text.UTF8Encoding]::new($false))
$args=@('/nologo','/std:c11','/O2','/W4','/WX','/MT','/D_CRT_SECURE_NO_WARNINGS')
$args+=@($output,(Join-Path $project 'storage'))|ForEach-Object{'/I"'+$_+'"'}
$args+=@('storage/jpeg_cache.c','storage/jpeg_nor.c','storage/jpeg_journal.c','tests/jpeg_cache/native_test.c')|ForEach-Object{'"'+(Join-Path $project $_)+'"'}
$exe=Join-Path $output 'jpeg_cache_test.exe';$args+=@('/Fe"'+$exe+'"','/link','bcrypt.lib');$batch=Join-Path $output 'compile.cmd'
[IO.File]::WriteAllText($batch,"@echo off`r`ncall `"$VsDevCmd`" -arch=x64 -host_arch=x64 >nul`r`nif errorlevel 1 exit /b 1`r`ncd /d `"$output`"`r`nwhere cl > compiler-path.txt`r`ncl "+($args -join ' ')+"`r`nexit /b %errorlevel%`r`n")
& cmd.exe /d /c $batch;if($LASTEXITCODE -ne 0){throw 'Cache host build failed'}
$arguments=@();if($Quick){$arguments+='--quick'}
& $exe @arguments|Tee-Object -LiteralPath (Join-Path $output 'report.json');if($LASTEXITCODE -ne 0){throw 'Cache contract failed'}
foreach($path in $pins.Keys){if((Get-FileHash -LiteralPath $path).Hash.ToLower() -ne $pins[$path]){throw "Cache input changed: $path"}}
$compiler=([IO.File]::ReadAllLines((Join-Path $output 'compiler-path.txt')))[0]
$record=[ordered]@{inputs_unchanged=$true;executable=$exe;executable_sha256=(Get-FileHash -LiteralPath $exe).Hash.ToLower();compiler=$compiler;compiler_sha256=(Get-FileHash -LiteralPath $compiler).Hash.ToLower();quick=[bool]$Quick}
[IO.File]::WriteAllText((Join-Path $output 'build.json'),(($record|ConvertTo-Json).Replace("`r`n","`n")+"`n"),[Text.UTF8Encoding]::new($false))
