[CmdletBinding()]
param([Parameter(Mandatory)][string]$LibraryBuild,[Parameter(Mandatory)][string]$OutputDirectory,
      [string]$VsDevCmd='C:\Program Files\Microsoft Visual Studio\18\Community\Common7\Tools\VsDevCmd.bat')
$ErrorActionPreference='Stop'
$project=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'));$output=[IO.Path]::GetFullPath($OutputDirectory);$library=[IO.Path]::GetFullPath($LibraryBuild)
New-Item -ItemType Directory -Path $output -ErrorAction Stop | Out-Null
$record=Get-Content -LiteralPath (Join-Path $library 'build.json') -Raw | ConvertFrom-Json
if(!$record.flash_tables -or !$record.compact_pools -or $record.variant -ne 'adapted' -or $record.upstream_commit -ne 'c85e6b905bf237038faa936dab160ebfc5da0344'){throw 'Use the pinned qualified bounded/flash-table/compact library'}
$paths=@('codec/jpeg_decoder.c','codec/jpeg_memory.c','codec/jpeg_decoder.h','codec/jpeg_decoder_internal.h','app/media/color_convert.c','app/include/color_convert.h','tests/jpeg_decoder/driver.c','tests/jpeg_decoder/build.ps1') | ForEach-Object {Join-Path $project $_}
$paths+=@(Join-Path $library 'library/jpeg-static.lib')
# Pin private ABI/configuration headers used by this new compilation too.
$paths+=@(Get-ChildItem -LiteralPath (Join-Path $library 'source/src') -Filter '*.h' -File | Select-Object -ExpandProperty FullName)
$paths+=@(Get-ChildItem -LiteralPath (Join-Path $library 'library') -Filter '*.h' -File | Select-Object -ExpandProperty FullName)
$pins=[ordered]@{}
foreach($path in $paths){$pins[[IO.Path]::GetFullPath($path)]=(Get-FileHash -LiteralPath $path).Hash.ToLower()}
if($pins[(Join-Path $library 'library/jpeg-static.lib')] -ne $record.library_sha256){throw 'Library archive hash differs'}
[IO.File]::WriteAllText((Join-Path $output 'inputs.json'),(($pins | ConvertTo-Json).Replace("`r`n","`n")+"`n"),[Text.UTF8Encoding]::new($false))
$include=@((Join-Path $project 'codec'),(Join-Path $project 'app/include'),(Join-Path $library 'source/src'),(Join-Path $library 'library'))
$args=@('/nologo','/std:c11','/O2','/W4','/WX','/MT','/DJPEG_STATIC','/D_CRT_SECURE_NO_WARNINGS')
$args+=@($include | ForEach-Object {'/I"'+$_+'"'})
$args+=@('codec/jpeg_decoder.c','codec/jpeg_memory.c','app/media/color_convert.c','tests/jpeg_decoder/driver.c') | ForEach-Object {'"'+(Join-Path $project $_)+'"'}
$args+=@('/Fe"'+(Join-Path $output 'jpeg_decoder_test.exe')+'"','/link','"'+(Join-Path $library 'library/jpeg-static.lib')+'"')
$batch=Join-Path $output 'compile.cmd'
[IO.File]::WriteAllText($batch,"@echo off`r`ncall `"$VsDevCmd`" -arch=x64 -host_arch=x64 >nul`r`nif errorlevel 1 exit /b 1`r`ncd /d `"$output`"`r`nwhere cl > compiler-path.txt`r`ncl "+($args -join ' ')+"`r`nexit /b %errorlevel%`r`n")
& cmd.exe /d /c $batch;if($LASTEXITCODE -ne 0){throw 'Native decoder compilation failed'}
foreach($path in $pins.Keys){if((Get-FileHash -LiteralPath $path).Hash.ToLower() -ne $pins[$path]){throw "Decoder input changed during compilation: $path"}}
$compiler=([IO.File]::ReadAllLines((Join-Path $output 'compiler-path.txt')))[0]
$products=[ordered]@{inputs_unchanged=$true;executable=(Join-Path $output 'jpeg_decoder_test.exe');executable_sha256=(Get-FileHash -LiteralPath (Join-Path $output 'jpeg_decoder_test.exe')).Hash.ToLower();compiler=$compiler;compiler_sha256=(Get-FileHash -LiteralPath $compiler).Hash.ToLower();library_build=$library}
[IO.File]::WriteAllText((Join-Path $output 'build.json'),(($products | ConvertTo-Json).Replace("`r`n","`n")+"`n"),[Text.UTF8Encoding]::new($false))
