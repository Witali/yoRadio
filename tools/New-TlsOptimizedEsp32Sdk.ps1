[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$BuilderRoot,

    [Parameter(Mandatory)]
    [string]$SourceSdk,

    [Parameter(Mandatory)]
    [string]$Destination
)

$ErrorActionPreference = "Stop"

$builder = [IO.Path]::GetFullPath($BuilderRoot)
$source = [IO.Path]::GetFullPath($SourceSdk)
$destinationPath = [IO.Path]::GetFullPath($Destination)
$build = Join-Path $builder "build"

$requiredSourceFiles = @(
    (Join-Path $source "sdkconfig"),
    (Join-Path $source "flags\ld_libs"),
    (Join-Path $source "qio_qspi\include\sdkconfig.h"),
    (Join-Path $build "config\sdkconfig.h"),
    (Join-Path $builder "sdkconfig")
)
foreach ($requiredFile in $requiredSourceFiles) {
    if (-not (Test-Path -LiteralPath $requiredFile -PathType Leaf)) {
        throw "Required SDK input is missing: $requiredFile"
    }
}

$customConfig = Get-Content -Raw -LiteralPath (Join-Path $build "config\sdkconfig.h")
$requiredDefines = @(
    '#define CONFIG_MBEDTLS_ASYMMETRIC_CONTENT_LEN 1',
    '#define CONFIG_MBEDTLS_SSL_IN_CONTENT_LEN 16384',
    '#define CONFIG_MBEDTLS_SSL_OUT_CONTENT_LEN 4096'
)
foreach ($requiredDefine in $requiredDefines) {
    if (-not $customConfig.Contains($requiredDefine)) {
        throw "Custom sdkconfig.h does not contain: $requiredDefine"
    }
}

$libraryMappings = [ordered]@{
    "esp-idf\mbedtls\libmbedtls.a" = "lib\libmbedtls.a"
    "esp-idf\mbedtls\mbedtls\library\libmbedtls.a" = "lib\libmbedtls_2.a"
    "esp-idf\mbedtls\mbedtls\library\libmbedcrypto.a" = "lib\libmbedcrypto.a"
    "esp-idf\mbedtls\mbedtls\library\libmbedx509.a" = "lib\libmbedx509.a"
    "esp-idf\esp-tls\libesp-tls.a" = "lib\libesp-tls.a"
}
foreach ($relativeSource in $libraryMappings.Keys) {
    $library = Join-Path $build $relativeSource
    if (-not (Test-Path -LiteralPath $library -PathType Leaf)) {
        throw "Custom TLS library is missing: $library"
    }
}

if (Test-Path -LiteralPath $destinationPath) {
    throw "Destination already exists: $destinationPath"
}

Write-Host "Copying the stock ESP32 SDK to $destinationPath"
Copy-Item -LiteralPath $source -Destination $destinationPath -Recurse

foreach ($mapping in $libraryMappings.GetEnumerator()) {
    $from = Join-Path $build $mapping.Key
    $to = Join-Path $destinationPath $mapping.Value
    Copy-Item -LiteralPath $from -Destination $to -Force
    Write-Host "Overlaid $($mapping.Value)"
}

Copy-Item -LiteralPath (Join-Path $builder "sdkconfig") `
    -Destination (Join-Path $destinationPath "sdkconfig") -Force
Copy-Item -LiteralPath (Join-Path $build "config\sdkconfig.h") `
    -Destination (Join-Path $destinationPath "qio_qspi\include\sdkconfig.h") -Force

Write-Host "TLS-optimized SDK is ready: $destinationPath"
Write-Host "  RX record buffer: 16384 bytes"
Write-Host "  TX record buffer: 4096 bytes"
