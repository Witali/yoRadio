[CmdletBinding()]
param([Parameter(Mandatory)][string]$OutputDirectory,
      [string]$VsDevCmd='C:\Program Files\Microsoft Visual Studio\18\Community\Common7\Tools\VsDevCmd.bat')
$ErrorActionPreference='Stop'
$project=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'));$output=[IO.Path]::GetFullPath($OutputDirectory)
New-Item -ItemType Directory -Path $output -ErrorAction Stop | Out-Null
$pins=[ordered]@{}
foreach($path in @((Join-Path $project 'codec/jpeg_coefficients.c'),(Join-Path $project 'codec/jpeg_coefficients.h'),(Join-Path $PSScriptRoot 'native_test.c'),$PSCommandPath)){
    $pins[[IO.Path]::GetFullPath($path)]=(Get-FileHash -LiteralPath $path).Hash.ToLower()
}
[IO.File]::WriteAllText((Join-Path $output 'inputs.json'),(($pins | ConvertTo-Json).Replace("`r`n","`n")+"`n"),[Text.UTF8Encoding]::new($false))
$args=@('/nologo','/std:c11','/O2','/W4','/WX',('/I"'+(Join-Path $project 'codec')+'"'),
    ('"'+(Join-Path $PSScriptRoot 'native_test.c')+'"'),('"'+(Join-Path $project 'codec/jpeg_coefficients.c')+'"'),('/Fe"'+(Join-Path $output 'jpeg_coefficients_test.exe')+'"'))
$batch=Join-Path $output 'compile.cmd'
[IO.File]::WriteAllText($batch,"@echo off`r`ncall `"$VsDevCmd`" -arch=x64 -host_arch=x64 >nul`r`nif errorlevel 1 exit /b 1`r`ncd /d `"$output`"`r`nwhere cl > compiler-path.txt`r`ncl "+($args -join ' ')+"`r`nexit /b %errorlevel%`r`n")
& cmd.exe /d /c $batch;if($LASTEXITCODE -ne 0){throw 'Coefficient compilation failed'}
& (Join-Path $output 'jpeg_coefficients_test.exe') | Tee-Object -LiteralPath (Join-Path $output 'report.json')
if($LASTEXITCODE -ne 0){throw 'Coefficient contract failed'}
foreach($path in $pins.Keys){if((Get-FileHash -LiteralPath $path).Hash.ToLower() -ne $pins[$path]){throw "Coefficient input changed during compilation/test: $path"}}
$compiler=([IO.File]::ReadAllLines((Join-Path $output 'compiler-path.txt')))[0]
$products=[ordered]@{inputs_unchanged=$true;executable_sha256=(Get-FileHash -LiteralPath (Join-Path $output 'jpeg_coefficients_test.exe')).Hash.ToLower();compiler=$compiler;compiler_sha256=(Get-FileHash -LiteralPath $compiler).Hash.ToLower()}
[IO.File]::WriteAllText((Join-Path $output 'products.json'),(($products | ConvertTo-Json).Replace("`r`n","`n")+"`n"),[Text.UTF8Encoding]::new($false))
