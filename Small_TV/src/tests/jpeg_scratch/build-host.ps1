[CmdletBinding()]
param([Parameter(Mandatory)][string]$OutputDirectory,[switch]$Nor,
      [string]$Fixtures='',
      [string]$Source='C:\Work\yoRadio\.build\libjpeg-turbo-3.2.0',
      [string]$PythonPath='C:\Work\yoRadio\.idf\tools-v6.1\python_env\idf6.1_py3.12_env\Scripts\python.exe',
      [string]$VsDevCmd='C:\Program Files\Microsoft Visual Studio\18\Community\Common7\Tools\VsDevCmd.bat')
$ErrorActionPreference='Stop'
$project=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'));$output=[IO.Path]::GetFullPath($OutputDirectory)
if(Test-Path -LiteralPath $output){throw 'Use a new host build output directory'}
if($Nor -and !$Fixtures){throw 'NOR backend requires prepared scratch fixtures'}
$driver=$output+'-driver';New-Item -ItemType Directory -Path $driver -ErrorAction Stop | Out-Null
$arguments=@('-X','utf8','-B',('"'+(Join-Path $project 'tests/jpeg_library_probe/build.py')+'"'),'--source',('"'+$Source+'"'),'--output',('"'+$output+'"'),
    '--cmake','"C:/Work/yoRadio/.idf/tools-v6.1/tools/cmake/4.0.3/bin/cmake.exe"','--ninja','"C:/Work/yoRadio/.idf/tools-v6.1/tools/ninja/1.12.1/ninja.exe"')
if($Nor){$arguments+=@('--adapted','--flash-tables','--compact-pools','--nor-fixtures',('"'+[IO.Path]::GetFullPath($Fixtures)+'"'))}
$batch=Join-Path $driver 'build.cmd'
[IO.File]::WriteAllText($batch,"@echo off`r`ncall `"$VsDevCmd`" -arch=x64 -host_arch=x64 >nul`r`nif errorlevel 1 exit /b 1`r`nset PYTHONDONTWRITEBYTECODE=1`r`n`"$PythonPath`" "+($arguments -join ' ')+"`r`nexit /b %errorlevel%`r`n")
& cmd.exe /d /c $batch;if($LASTEXITCODE -ne 0){throw 'Pinned host JPEG build failed'}
