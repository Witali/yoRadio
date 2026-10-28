[CmdletBinding()]
param([Parameter(Mandatory)][string]$OutputDirectory,
      [string]$VsDevCmd='C:\Program Files\Microsoft Visual Studio\18\Community\Common7\Tools\VsDevCmd.bat')
$ErrorActionPreference='Stop'
$taskOutput=[IO.Path]::GetFullPath($OutputDirectory)
if(Test-Path -LiteralPath $taskOutput){throw 'Use a new nothrow test directory'}
New-Item -ItemType Directory -Path $taskOutput -Force | Out-Null
$taskSource=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../app/platform/nothrow_new.cpp'))
$taskObject=Join-Path $taskOutput 'nothrow.obj'
$taskExecutable=Join-Path $taskOutput 'nothrow_test.exe'
$taskBatch=Join-Path $taskOutput 'compile.cmd'
$taskCommands=@(
    '@echo off',
    ('call "'+$VsDevCmd+'" -arch=x64 -host_arch=x64 >nul'),
    'if errorlevel 1 exit /b 1',
    ('cd /d "'+$taskOutput+'"'),
    ('cl /nologo /std:c++17 /EHsc /W4 /WX /c /FI"'+(Join-Path $PSScriptRoot 'hooks.hpp')+'" "'+$taskSource+'" /Fo"'+$taskObject+'"'),
    'if errorlevel 1 exit /b 1',
    ('cl /nologo /std:c++17 /EHsc /W4 /WX "'+(Join-Path $PSScriptRoot 'test.cpp')+'" "'+$taskObject+'" /Fe"'+$taskExecutable+'"'),
    'exit /b %errorlevel%'
)
[IO.File]::WriteAllText($taskBatch,($taskCommands -join "`r`n")+"`r`n")
& cmd.exe /d /c $taskBatch
if($LASTEXITCODE){throw 'Nothrow allocation host compilation failed'}
& $taskExecutable (Join-Path $taskOutput 'report.json')
if($LASTEXITCODE){throw 'Nothrow allocation host cases failed'}
