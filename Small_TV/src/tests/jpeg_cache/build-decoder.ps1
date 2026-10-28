[CmdletBinding()]
param([Parameter(Mandatory)][string]$OutputDirectory,[Parameter(Mandatory)][string]$LibraryBuild,
      [string]$PythonPath='C:\Work\yoRadio\.idf\tools-v6.1\python_env\idf6.1_py3.12_env\Scripts\python.exe',
      [string]$VsDevCmd='C:\Program Files\Microsoft Visual Studio\18\Community\Common7\Tools\VsDevCmd.bat')
$ErrorActionPreference='Stop';$project=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'));$repo=[IO.Path]::GetFullPath((Join-Path $project '../..'))
$output=[IO.Path]::GetFullPath($OutputDirectory);$library=[IO.Path]::GetFullPath($LibraryBuild);$resources=Join-Path $output 'resources'
if(Test-Path -LiteralPath $output){throw 'Use a fresh decoder/cache build directory'}
& $PythonPath -X utf8 -B (Join-Path $project 'tools/jpeg_cache_layout.py') --assets-dir (Join-Path $repo 'firmware/development/small-tv-esp32c2-reconstructed') --library-build $library --output $resources
if($LASTEXITCODE -ne 0){throw 'Cache layout preparation failed'}
$sources=@('codec/jpeg_decoder.c','codec/jpeg_memory.c','codec/jpeg_backing.c','codec/jpeg_coefficients.c','storage/jpeg_cache.c','storage/jpeg_nor.c','storage/jpeg_journal.c','storage/jpeg_scratch.c','app/media/color_convert.c','tests/jpeg_cache/decoder_driver.c')
$headers=@('codec/jpeg_decoder.h','codec/jpeg_decoder_internal.h','codec/jpeg_backing.h','codec/jpeg_coefficients.h','storage/jpeg_cache.h','storage/jpeg_nor.h','storage/jpeg_journal.h','storage/jpeg_scratch.h','storage/jpeg_guard.h','app/include/color_convert.h','tests/jpeg_cache/native_test.c','tests/jpeg_cache/build-decoder.ps1')
$pins=[ordered]@{};foreach($name in @($sources+$headers)){$path=Join-Path $project $name;$pins[$path]=(Get-FileHash -LiteralPath $path).Hash.ToLower()}
$plan=Get-Content -LiteralPath (Join-Path $resources 'plan.json') -Raw|ConvertFrom-Json
foreach($p in $plan.cache_inputs_sha256.PSObject.Properties){$pins[$p.Name]=$p.Value}
foreach($name in @('jpeg_layout.h','jpeg_cache_layout.h')){$path=Join-Path $resources $name;$pins[$path]=(Get-FileHash -LiteralPath $path).Hash.ToLower()}
$private=@(Get-ChildItem -LiteralPath (Join-Path $library 'source/src') -Filter '*.h' -File|Select-Object -ExpandProperty FullName)
$private+=@(Get-ChildItem -LiteralPath (Join-Path $library 'library') -Filter '*.h' -File|Select-Object -ExpandProperty FullName)
foreach($path in $private){$pins[$path]=(Get-FileHash -LiteralPath $path).Hash.ToLower()}
[IO.File]::WriteAllText((Join-Path $output 'inputs.json'),(($pins|ConvertTo-Json).Replace("`r`n","`n")+"`n"),[Text.UTF8Encoding]::new($false))
$args=@('/nologo','/std:c11','/O2','/W4','/WX','/MT','/DJPEG_STATIC','/D_CRT_SECURE_NO_WARNINGS')
$args+=@($resources,(Join-Path $project 'storage'),(Join-Path $project 'codec'),(Join-Path $project 'app/include'),(Join-Path $library 'source/src'),(Join-Path $library 'library'))|ForEach-Object{'/I"'+$_+'"'}
$args+=@($sources|ForEach-Object{'"'+(Join-Path $project $_)+'"'})
$exe=Join-Path $output 'jpeg_cache_decoder_test.exe';$args+=@('/Fe"'+$exe+'"','/link','bcrypt.lib','"'+(Join-Path $library 'library/jpeg-static.lib')+'"');$batch=Join-Path $output 'compile.cmd'
[IO.File]::WriteAllText($batch,"@echo off`r`ncall `"$VsDevCmd`" -arch=x64 -host_arch=x64 >nul`r`nif errorlevel 1 exit /b 1`r`ncd /d `"$output`"`r`nwhere cl > compiler-path.txt`r`ncl "+($args -join ' ')+"`r`nexit /b %errorlevel%`r`n")
& cmd.exe /d /c $batch;if($LASTEXITCODE -ne 0){throw 'Cache decoder host build failed'}
foreach($path in $pins.Keys){if((Get-FileHash -LiteralPath $path).Hash.ToLower() -ne $pins[$path]){throw "Cache decoder input changed: $path"}}
$compiler=([IO.File]::ReadAllLines((Join-Path $output 'compiler-path.txt')))[0]
$record=[ordered]@{inputs_unchanged=$true;executable=$exe;executable_sha256=(Get-FileHash -LiteralPath $exe).Hash.ToLower();compiler=$compiler;compiler_sha256=(Get-FileHash -LiteralPath $compiler).Hash.ToLower();resources=$resources;codec_id=$plan.cache_codec_id}
[IO.File]::WriteAllText((Join-Path $output 'build.json'),(($record|ConvertTo-Json).Replace("`r`n","`n")+"`n"),[Text.UTF8Encoding]::new($false))
