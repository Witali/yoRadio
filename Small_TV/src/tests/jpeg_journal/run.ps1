[CmdletBinding()]
param([Parameter(Mandatory)][string]$OutputDirectory,[switch]$Quick,
      [string]$PythonPath='C:\Work\yoRadio\.idf\tools-v6.1\python_env\idf6.1_py3.12_env\Scripts\python.exe',
      [string]$VsDevCmd='C:\Program Files\Microsoft Visual Studio\18\Community\Common7\Tools\VsDevCmd.bat')
$ErrorActionPreference='Stop'
$project=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$repo=[IO.Path]::GetFullPath((Join-Path $project '../..'))
$output=[IO.Path]::GetFullPath($OutputDirectory)
& $PythonPath -X utf8 -B (Join-Path $PSScriptRoot 'prepare.py') --assets-dir (Join-Path $repo 'firmware/development/small-tv-esp32c2-reconstructed') --output $output
if ($LASTEXITCODE -ne 0) { throw 'Journal fixture preparation failed' }
$arguments=@('/nologo','/std:c11','/O2','/W4','/WX','/D_CRT_SECURE_NO_WARNINGS',
    ('/I"'+$output+'"'),('"'+(Join-Path $PSScriptRoot 'native_test.c')+'"'),
    ('"'+(Join-Path $project 'storage/jpeg_journal.c')+'"'),
    ('"'+(Join-Path $project 'storage/jpeg_nor.c')+'"'),
    ('/Fe"'+(Join-Path $output 'jpeg_journal_test.exe')+'"'),'/link','bcrypt.lib')
$batch=Join-Path $output 'compile.cmd'
[IO.File]::WriteAllText($batch,"@echo off`r`ncall `"$VsDevCmd`" -arch=x64 -host_arch=x64 >nul`r`nif errorlevel 1 exit /b 1`r`ncd /d `"$output`"`r`nwhere cl > compiler-path.txt`r`ncl "+($arguments -join ' ')+"`r`nexit /b %errorlevel%`r`n")
& cmd.exe /d /c $batch
if ($LASTEXITCODE -ne 0) { throw 'Journal host compilation failed' }
$testArguments=@($output)
if ($Quick) { $testArguments+='--quick' }
& (Join-Path $output 'jpeg_journal_test.exe') @testArguments | Tee-Object -LiteralPath (Join-Path $output 'report.json')
if ($LASTEXITCODE -ne 0) { throw 'Journal contract failed' }
