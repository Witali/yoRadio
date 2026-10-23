[CmdletBinding()]
param([Parameter(Mandatory)][string]$BuildDirectory,[Parameter(Mandatory)][string]$LibraryBuild,
      [Parameter(Mandatory)][string]$OracleDirectory,[string]$DependencyRoot='C:\Work\yoRadio\.idf')
$ErrorActionPreference='Stop'
$project=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'));$repo=[IO.Path]::GetFullPath((Join-Path $project '../..'))
$build=[IO.Path]::GetFullPath($BuildDirectory);$library=[IO.Path]::GetFullPath($LibraryBuild)
if(Test-Path -LiteralPath $build){throw 'Use a fresh target decoder build directory'}
$vendor=Get-Content -LiteralPath (Join-Path $library 'report.json') -Raw|ConvertFrom-Json
if($vendor.upstream_commit -ne 'c85e6b905bf237038faa936dab160ebfc5da0344' -or !$vendor.flash_tables -or !$vendor.compact_pools){throw 'Use qualified pinned RV32 library'}
if((Get-FileHash -LiteralPath (Join-Path $library 'library/libjpeg.a')).Hash.ToLower() -ne $vendor.library_sha256){throw 'RV32 archive differs'}
$idf=Join-Path $DependencyRoot 'v6.1-9a97f6c54ec6';$expected='9a97f6c54ec638111ce55cd36581b3c192f15207'
if((& git -C $idf rev-parse HEAD).Trim() -ne $expected){throw 'Pinned ESP-IDF differs'}
$bootstrap=Join-Path $DependencyRoot 'python-3.12.10/tools';$resources=Join-Path $build 'resources'
& (Join-Path $bootstrap 'python.exe') -B (Join-Path $PSScriptRoot 'prepare-idf.py') --assets-dir (Join-Path $repo 'firmware/development/small-tv-esp32c2-reconstructed') --oracle $OracleDirectory --output $resources
if($LASTEXITCODE -ne 0){throw 'Decoder probe preparation failed'}
$defaults=[IO.File]::ReadAllText((Join-Path $project 'sdkconfig.defaults')).Replace('CONFIG_PARTITION_TABLE_CUSTOM_FILENAME="partitions.csv"',('CONFIG_PARTITION_TABLE_CUSTOM_FILENAME="'+(Join-Path $project 'partitions.csv').Replace('\','/')+'"'))
[IO.File]::WriteAllText((Join-Path $build 'sdkconfig.defaults'),$defaults.Replace("`r`n","`n"),[Text.UTF8Encoding]::new($false))
# Pin source/header/private ABI dependencies before compilation.
$names=@('codec/jpeg_decoder.c','codec/jpeg_decoder.h','codec/jpeg_decoder_internal.h','codec/jpeg_memory.c','codec/jpeg_backing.c','codec/jpeg_backing.h','codec/jpeg_coefficients.c','codec/jpeg_coefficients.h','storage/jpeg_scratch.c','storage/jpeg_scratch.h','storage/jpeg_nor.c','storage/jpeg_nor.h','storage/jpeg_guard.c','storage/jpeg_guard.h','storage/jpeg_provision.c','storage/jpeg_provision.h','storage/jpeg_transport.c','storage/jpeg_transport.h','storage/jpeg_espidf.c','storage/jpeg_espidf.h','app/media/color_convert.c','app/include/color_convert.h','app/include/board.h','tests/jpeg_backing/idf_probe/CMakeLists.txt','tests/jpeg_backing/idf_probe/main/CMakeLists.txt','tests/jpeg_backing/idf_probe/main/probe.c','tests/jpeg_backing/prepare-idf.py','tests/jpeg_backing/build-idf.ps1','tools/jpeg_guard_layout.py','tools/jpeg_storage_layout.py','partitions.csv','sdkconfig.defaults')
$records=@(foreach($name in $names){[ordered]@{file=$name;sha256=(Get-FileHash -LiteralPath (Join-Path $project $name)).Hash.ToLower()}})
$pins=[ordered]@{};foreach($record in $records){$pins[(Join-Path $project $record.file)]=$record.sha256}
foreach($name in @('jpeg_layout.h','probe_fixture.h')){$path=Join-Path $resources $name;$hash=(Get-FileHash -LiteralPath $path).Hash.ToLower();$pins[$path]=$hash;$records+=[ordered]@{file="generated/$name";sha256=$hash}}
$vendorPaths=@('report.json','library/libjpeg.a'|ForEach-Object{Join-Path $library $_})
$vendorPaths+=@(Get-ChildItem -LiteralPath (Join-Path $library 'source/src') -Filter '*.h' -File|Select-Object -ExpandProperty FullName)
$vendorPaths+=@(Get-ChildItem -LiteralPath (Join-Path $library 'library') -Filter '*.h' -File|Select-Object -ExpandProperty FullName)
foreach($path in $vendorPaths){$pins[$path]=(Get-FileHash -LiteralPath $path).Hash.ToLower()}
[IO.File]::WriteAllText((Join-Path $build 'inputs.json'),(($pins|ConvertTo-Json).Replace("`r`n","`n")+"`n"),[Text.UTF8Encoding]::new($false))
$saved=@{};foreach($key in @('Path','IDF_PATH','IDF_TOOLS_PATH','IDF_COMPONENT_MANAGER','PYTHONNOUSERSITE','PYTHONIOENCODING','PYTHONUTF8','PYTHONDONTWRITEBYTECODE')){$saved[$key]=[Environment]::GetEnvironmentVariable($key)}
try {
    $env:IDF_TOOLS_PATH=Join-Path $DependencyRoot 'tools-v6.1';$env:IDF_COMPONENT_MANAGER='0';$env:PYTHONNOUSERSITE='1';$env:PYTHONIOENCODING='utf-8';$env:PYTHONUTF8='1';$env:PYTHONDONTWRITEBYTECODE='1'
    $env:Path="$bootstrap;$bootstrap\Scripts;$env:Path";. (Join-Path $idf 'export.ps1')
    $python=(Get-Command python.exe -CommandType Application|Select-Object -First 1).Source
    $toolPath=@(Get-ChildItem Env:|Where-Object{$_.Name -imatch '^path$' -and $_.Value.Contains('tools\ninja')}|Select-Object -First 1 -ExpandProperty Value)[0]
    Push-Location (Join-Path $PSScriptRoot 'idf_probe')
    try {
        $cmakeBuild=$build.Replace('\','/');$cmakeResources=$resources.Replace('\','/');$cmakeLibrary=$library.Replace('\','/')
        $arguments=@('-B',(Join-Path $idf 'tools/idf.py'),'-B',$build,'--no-ccache','-D',"SDKCONFIG=$cmakeBuild/sdkconfig",'-D',"SDKCONFIG_DEFAULTS=$cmakeBuild/sdkconfig.defaults",'-D',"JPEG_PROBE_GENERATED=$cmakeResources",'-D',"JPEG_PROBE_LIBRARY=$cmakeLibrary",'build')
        $process=Start-Process -Wait -PassThru -NoNewWindow -FilePath $python -ArgumentList $arguments -Environment @{PATH=$toolPath}
        if($process.ExitCode -ne 0){throw 'Decoder target build failed'}
    } finally {Pop-Location}
} finally {foreach($key in $saved.Keys){[Environment]::SetEnvironmentVariable($key,$saved[$key])}}
foreach($path in $pins.Keys){if((Get-FileHash -LiteralPath $path).Hash.ToLower() -ne $pins[$path]){throw "Target input changed: $path"}}
$destination=Join-Path $repo 'firmware/development/small-tv-jpeg-decoder-probe';New-Item -ItemType Directory -Force -Path $destination|Out-Null
foreach($pair in @(@('small_tv_jpeg_decoder_probe.bin','app.bin'),@('bootloader/bootloader.bin','bootloader.bin'),@('partition_table/partition-table.bin','partition-table.bin'),@('resources/assets.bin','assets.bin'),@('resources/assets-manifest.json','assets-manifest.json'),@('sdkconfig','sdkconfig'))){Copy-Item -LiteralPath (Join-Path $build $pair[0]) -Destination (Join-Path $destination $pair[1])}
$images=@(@{file='bootloader.bin';offset='0x0'},@{file='partition-table.bin';offset='0x8000'},@{file='app.bin';offset='0x10000'},@{file='assets.bin';offset='0x200000'})
foreach($image in $images){$path=Join-Path $destination $image.file;$image.sha256=(Get-FileHash -LiteralPath $path).Hash.ToLower();$image.bytes=(Get-Item -LiteralPath $path).Length}
$sourceJson=ConvertTo-Json -InputObject $records -Depth 6 -Compress
$aggregate=[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData([Text.Encoding]::UTF8.GetBytes($sourceJson))).ToLower()
$manifest=@{target='esp32c2';flash_bytes=4194304;source_sha256=$aggregate;inputs_unchanged_during_build=$true;idf_revision=$expected;status='standalone JPEG decoder/NOR probe; UI/Wi-Fi/hardware unverified';images=$images;source_files=$records;library_sha256=$vendor.library_sha256;elf_sha256=(Get-FileHash -LiteralPath (Join-Path $build 'small_tv_jpeg_decoder_probe.elf')).Hash.ToLower()}
[IO.File]::WriteAllText((Join-Path $destination 'manifest.json'),(($manifest|ConvertTo-Json -Depth 7).Replace("`r`n","`n")+"`n"),[Text.UTF8Encoding]::new($false))
Write-Host "Archived JPEG decoder probe to $destination"
