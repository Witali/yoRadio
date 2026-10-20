[CmdletBinding()]
param([Parameter(Mandatory)][string]$OutputDirectory,
      [string]$PythonPath='C:\Work\yoRadio\.idf\tools-v6.1\python_env\idf6.1_py3.12_env\Scripts\python.exe',
      [string]$VsDevCmd='C:\Program Files\Microsoft Visual Studio\18\Community\Common7\Tools\VsDevCmd.bat')
$ErrorActionPreference='Stop';$project=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'));$repo=[IO.Path]::GetFullPath((Join-Path $project '../..'));$output=[IO.Path]::GetFullPath($OutputDirectory)
& $PythonPath -X utf8 -B (Join-Path $project 'tests/jpeg_scratch/prepare.py') --assets-dir (Join-Path $repo 'firmware/development/small-tv-esp32c2-reconstructed') --output $output
if($LASTEXITCODE -ne 0){throw 'Fixture preparation failed'}
$names=@('codec/jpeg_backing.c','codec/jpeg_backing.h','codec/jpeg_decoder.h','codec/jpeg_coefficients.c','codec/jpeg_coefficients.h','storage/jpeg_scratch.c','storage/jpeg_scratch.h','storage/jpeg_nor.c','storage/jpeg_nor.h','tests/jpeg_backing/native_test.c','tests/jpeg_backing/run.ps1','tests/jpeg_scratch/nor_model.c','tests/jpeg_scratch/nor_model.h')
$pins=[ordered]@{};foreach($name in $names){$path=Join-Path $project $name;$pins[$path]=(Get-FileHash -LiteralPath $path).Hash.ToLower()}
$pins[(Join-Path $output 'scratch_fixture.h')]=(Get-FileHash -LiteralPath (Join-Path $output 'scratch_fixture.h')).Hash.ToLower()
[IO.File]::WriteAllText((Join-Path $output 'inputs.json'),(($pins|ConvertTo-Json).Replace("`r`n","`n")+"`n"),[Text.UTF8Encoding]::new($false))
$args=@('/nologo','/std:c11','/O2','/W4','/WX')
$args+=@($output,(Join-Path $project 'codec'),(Join-Path $project 'storage'),(Join-Path $project 'tests/jpeg_scratch'))|ForEach-Object {'/I"'+$_+'"'}
$args+=@('codec/jpeg_backing.c','codec/jpeg_coefficients.c','storage/jpeg_scratch.c','storage/jpeg_nor.c','tests/jpeg_backing/native_test.c','tests/jpeg_scratch/nor_model.c')|ForEach-Object {'"'+(Join-Path $project $_)+'"'}
$args+=@('/Fe"'+(Join-Path $output 'backing_test.exe')+'"')
$batch=Join-Path $output 'compile.cmd'
[IO.File]::WriteAllText($batch,"@echo off`r`ncall `"$VsDevCmd`" -arch=x64 -host_arch=x64 >nul`r`nif errorlevel 1 exit /b 1`r`ncd /d `"$output`"`r`nwhere cl > compiler-path.txt`r`ncl "+($args -join ' ')+"`r`nexit /b %errorlevel%`r`n")
& cmd.exe /d /c $batch;if($LASTEXITCODE -ne 0){throw 'Backing compilation failed'}
& (Join-Path $output 'backing_test.exe')|Tee-Object -LiteralPath (Join-Path $output 'report.json');if($LASTEXITCODE -ne 0){throw 'Backing unit failed'}
foreach($path in $pins.Keys){if((Get-FileHash -LiteralPath $path).Hash.ToLower() -ne $pins[$path]){throw "Backing input changed: $path"}}
$result=[ordered]@{inputs_unchanged=$true;executable_sha256=(Get-FileHash -LiteralPath (Join-Path $output 'backing_test.exe')).Hash.ToLower()}
[IO.File]::WriteAllText((Join-Path $output 'build.json'),(($result|ConvertTo-Json).Replace("`r`n","`n")+"`n"),[Text.UTF8Encoding]::new($false))
