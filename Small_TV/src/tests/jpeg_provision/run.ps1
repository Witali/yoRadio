[CmdletBinding()]
param([Parameter(Mandatory)][string]$OutputDirectory,
      [string]$PythonPath='C:/Work/yoRadio/.idf/tools-v6.1/python_env/idf6.1_py3.12_env/Scripts/python.exe',
      [string]$VsDevCmd='C:/Program Files/Microsoft Visual Studio/18/Community/Common7/Tools/VsDevCmd.bat')
$ErrorActionPreference='Stop'
$project=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$repo=[IO.Path]::GetFullPath((Join-Path $project '../..'))
$output=[IO.Path]::GetFullPath($OutputDirectory)
& $PythonPath -X utf8 -B (Join-Path $project 'tools/jpeg_guard_layout.py') --assets-dir (Join-Path $repo 'firmware/development/small-tv-esp32c2-reconstructed') --output $output
if($LASTEXITCODE){throw 'Provision fixture generation failed'}
$arguments=@('/nologo','/std:c11','/O2','/W4','/WX','/D_CRT_SECURE_NO_WARNINGS',
    ('/I"'+$output+'"'),('/I"'+(Join-Path $project 'storage')+'"'))
foreach($name in @('tests/jpeg_provision/native_test.c','storage/jpeg_provision.c','storage/jpeg_guard.c','storage/jpeg_transport.c')){
    $arguments+='"'+(Join-Path $project $name)+'"'
}
$arguments+=@('/Fe"'+(Join-Path $output 'jpeg_provision_test.exe')+'"','/link','bcrypt.lib')
$batch=Join-Path $output 'compile.cmd'
[IO.File]::WriteAllText($batch,"@echo off`r`ncall `"$VsDevCmd`" -arch=x64 -host_arch=x64 >nul`r`nif errorlevel 1 exit /b 1`r`ncd /d `"$output`"`r`nwhere cl > compiler-path.txt`r`ncl "+($arguments -join ' ')+"`r`nexit /b %errorlevel%`r`n")
& cmd.exe /d /c $batch
if($LASTEXITCODE){throw 'Provision host compilation failed'}
& (Join-Path $output 'jpeg_provision_test.exe') (Join-Path $output 'assets.bin') | Tee-Object -LiteralPath (Join-Path $output 'report.json')
if($LASTEXITCODE){throw 'Provision contract failed'}
