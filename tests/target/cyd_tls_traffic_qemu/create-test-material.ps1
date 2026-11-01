param([Parameter(Mandatory)][string]$OutputDirectory)
$ErrorActionPreference = 'Stop'
# Ephemeral diagnostic credentials only. Never install a certificate/key in a
# Windows store. The CA signing key remains in memory; the server key stays in
# the explicitly ignored fresh campaign and must never enter publication.
$repository = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
$ignoredRoot = [IO.Path]::GetFullPath((Join-Path $repository '.build'))
$output = [IO.Path]::GetFullPath($OutputDirectory)
if (!$output.StartsWith($ignoredRoot + [IO.Path]::DirectorySeparatorChar,
        [StringComparison]::OrdinalIgnoreCase) -or (Test-Path -LiteralPath $output)) {
    throw 'Test material requires a fresh directory below this worktree .build'
}
[void][IO.Directory]::CreateDirectory($output)
$caKey = [Security.Cryptography.RSA]::Create(2048)
$serverKey = [Security.Cryptography.RSA]::Create(2048)
$ca = $null
$server = $null
try {
    $now = [DateTimeOffset]::UtcNow
    $from = $now.AddHours(-1)
    $until = $now.AddDays(7)
    $hash = [Security.Cryptography.HashAlgorithmName]::SHA256
    $padding = [Security.Cryptography.RSASignaturePadding]::Pkcs1
    $caRequest = [Security.Cryptography.X509Certificates.CertificateRequest]::new(
        'CN=YoRadio disposable emulator test CA', $caKey, $hash, $padding)
    $caRequest.CertificateExtensions.Add(
        [Security.Cryptography.X509Certificates.X509BasicConstraintsExtension]::new($true, $false, 0, $true))
    $caRequest.CertificateExtensions.Add(
        [Security.Cryptography.X509Certificates.X509KeyUsageExtension]::new(
            [Security.Cryptography.X509Certificates.X509KeyUsageFlags]::KeyCertSign -bor
            [Security.Cryptography.X509Certificates.X509KeyUsageFlags]::CrlSign, $true))
    $caRequest.CertificateExtensions.Add(
        [Security.Cryptography.X509Certificates.X509SubjectKeyIdentifierExtension]::new($caRequest.PublicKey, $false))
    $ca = $caRequest.CreateSelfSigned($from, $until)
    $request = [Security.Cryptography.X509Certificates.CertificateRequest]::new(
        'CN=cyd-tls.invalid', $serverKey, $hash, $padding)
    $request.CertificateExtensions.Add(
        [Security.Cryptography.X509Certificates.X509BasicConstraintsExtension]::new($false, $false, 0, $true))
    $request.CertificateExtensions.Add(
        [Security.Cryptography.X509Certificates.X509KeyUsageExtension]::new(
            [Security.Cryptography.X509Certificates.X509KeyUsageFlags]::DigitalSignature -bor
            [Security.Cryptography.X509Certificates.X509KeyUsageFlags]::KeyEncipherment, $true))
    $usage = [Security.Cryptography.OidCollection]::new()
    [void]$usage.Add([Security.Cryptography.Oid]::new('1.3.6.1.5.5.7.3.1'))
    $request.CertificateExtensions.Add(
        [Security.Cryptography.X509Certificates.X509EnhancedKeyUsageExtension]::new($usage, $true))
    $names = [Security.Cryptography.X509Certificates.SubjectAlternativeNameBuilder]::new()
    $names.AddDnsName('cyd-tls.invalid')
    $names.AddIpAddress([Net.IPAddress]::Parse('10.0.2.2'))
    $names.AddIpAddress([Net.IPAddress]::Parse('127.0.0.1'))
    $request.CertificateExtensions.Add($names.Build())
    $serial = [byte[]]::new(16)
    [Security.Cryptography.RandomNumberGenerator]::Fill($serial)
    $serial[0] = $serial[0] -band 0x7f
    $server = $request.Create($ca, $from, $until, $serial)
    [IO.File]::WriteAllText((Join-Path $output 'ca.pem'), $ca.ExportCertificatePem() + "`n")
    [IO.File]::WriteAllText((Join-Path $output 'server.pem'), $server.ExportCertificatePem() + "`n")
    [IO.File]::WriteAllText((Join-Path $output 'server-key.pem'), $serverKey.ExportPkcs8PrivateKeyPem() + "`n")
    $files = [ordered]@{}
    foreach ($name in @('ca.pem', 'server.pem', 'server-key.pem')) {
        $path = Join-Path $output $name
        $files[$name] = [ordered]@{
            bytes = (Get-Item -LiteralPath $path).Length
            sha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $path).Hash.ToLowerInvariant()
            local_only = $true
            private_key = ($name -ceq 'server-key.pem')
        }
    }
    [ordered]@{
        ephemeral_test_only = $true
        certificate_store_modified = $false
        ca_private_key_written = $false
        guest_epoch_seconds = $now.ToUnixTimeSeconds()
        not_before_utc = $from.ToString('o')
        not_after_utc = $until.ToString('o')
        files = $files
    } | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $output 'manifest.json') -Encoding utf8
    Write-Output '{"test_material_created":true,"private_key_local_only":true,"certificate_store_modified":false}'
} finally {
    if ($server) { $server.Dispose() }
    if ($ca) { $ca.Dispose() }
    $serverKey.Dispose()
    $caKey.Dispose()
}
