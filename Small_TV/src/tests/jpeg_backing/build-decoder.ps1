[CmdletBinding()]
param([Parameter(Mandatory)][string]$LibraryBuild,[Parameter(Mandatory)][string]$Fixtures,[Parameter(Mandatory)][string]$OutputDirectory,
      [string]$VsDevCmd='C:\Program Files\Microsoft Visual Studio\18\Community\Common7\Tools\VsDevCmd.bat')
$ErrorActionPreference='Stop';$project=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'));$library=[IO.Path]::GetFullPath($LibraryBuild);$fixtures=[IO.Path]::GetFullPath($Fixtures);$output=[IO.Path]::GetFullPath($OutputDirectory)
New-Item -ItemType Directory -Path $output -ErrorAction Stop | Out-Null
$record=Get-Content -LiteralPath (Join-Path $library 'build.json') -Raw|ConvertFrom-Json
if($record.upstream_commit -ne 'c85e6b905bf237038faa936dab160ebfc5da0344' -or !$record.flash_tables -or !$record.compact_pools){throw 'Use pinned qualified JPEG archive'}
$sources=@('codec/jpeg_decoder.c','codec/jpeg_memory.c','codec/jpeg_backing.c','codec/jpeg_coefficients.c','storage/jpeg_scratch.c','storage/jpeg_nor.c','app/media/color_convert.c','tests/jpeg_backing/decoder_driver.c','tests/jpeg_scratch/nor_model.c')
$headers=@('codec/jpeg_decoder.h','codec/jpeg_decoder_internal.h','codec/jpeg_backing.h','codec/jpeg_coefficients.h','storage/jpeg_scratch.h','storage/jpeg_nor.h','app/include/color_convert.h','tests/jpeg_decoder/driver.c','tests/jpeg_scratch/nor_model.h','tests/jpeg_backing/build-decoder.ps1')
$paths=@($sources+$headers|ForEach-Object{Join-Path $project $_})
$paths+=@(Get-ChildItem -LiteralPath (Join-Path $library 'source/src') -Filter '*.h' -File|Select-Object -ExpandProperty FullName)
$paths+=@(Get-ChildItem -LiteralPath (Join-Path $library 'library') -Filter '*.h' -File|Select-Object -ExpandProperty FullName)
$paths+=@(Join-Path $library 'library/jpeg-static.lib');$paths+=@(Join-Path $fixtures 'scratch_fixture.h')
$pins=[ordered]@{};foreach($path in $paths){$pins[$path]=(Get-FileHash -LiteralPath $path).Hash.ToLower()}
if($pins[(Join-Path $library 'library/jpeg-static.lib')] -ne $record.library_sha256){throw 'Archive differs'}
[IO.File]::WriteAllText((Join-Path $output 'inputs.json'),(($pins|ConvertTo-Json).Replace("`r`n","`n")+"`n"),[Text.UTF8Encoding]::new($false))
$args=@('/nologo','/std:c11','/O2','/W4','/WX','/MT','/DJPEG_STATIC','/D_CRT_SECURE_NO_WARNINGS')
$args+=@((Join-Path $project 'codec'),(Join-Path $project 'storage'),(Join-Path $project 'app/include'),(Join-Path $project 'tests/jpeg_scratch'),$fixtures,(Join-Path $library 'source/src'),(Join-Path $library 'library'))|ForEach-Object{'/I"'+$_+'"'}
$args+=@($sources|ForEach-Object{'"'+(Join-Path $project $_)+'"'})
$exe=Join-Path $output 'nor_decoder_test.exe';$args+=@('/Fe"'+$exe+'"','/link','"'+(Join-Path $library 'library/jpeg-static.lib')+'"');$batch=Join-Path $output 'compile.cmd'
[IO.File]::WriteAllText($batch,"@echo off`r`ncall `"$VsDevCmd`" -arch=x64 -host_arch=x64 >nul`r`nif errorlevel 1 exit /b 1`r`ncd /d `"$output`"`r`nwhere cl > compiler-path.txt`r`ncl "+($args -join ' ')+"`r`nexit /b %errorlevel%`r`n")
& cmd.exe /d /c $batch;if($LASTEXITCODE -ne 0){throw 'NOR decoder build failed'}
foreach($path in $pins.Keys){if((Get-FileHash -LiteralPath $path).Hash.ToLower() -ne $pins[$path]){throw "NOR decoder input changed: $path"}}
$result=[ordered]@{inputs_unchanged=$true;executable=$exe;executable_sha256=(Get-FileHash -LiteralPath $exe).Hash.ToLower();library_build=$library;fixtures=$fixtures}
[IO.File]::WriteAllText((Join-Path $output 'build.json'),(($result|ConvertTo-Json).Replace("`r`n","`n")+"`n"),[Text.UTF8Encoding]::new($false))
