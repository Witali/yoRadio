param(
    [string]$SdkPath = '.worktree/esp8266-native-port/.build/esp8266-rtos-sdk',
    [string]$RuntimeRoot = '',
    [ValidatePattern('^[a-zA-Z0-9_-]+$')]
    [string]$Variant = 'esp8266-main',
    [ValidateSet('accepted-asm', 'c')]
    [string]$Profile = 'accepted-asm'
)
# Canonical radio build. No flashing, Wi-Fi changes or hardware reset.
$ErrorActionPreference = 'Stop'
$taskRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$taskStamp = [DateTime]::UtcNow.ToString('yyyyMMdd-HHmmss-fff')
$taskBase = "$Variant-base-$taskStamp"
$taskFinal = "$Variant-accepted-$taskStamp"
$taskArgs = @{
    SdkPath=$SdkPath; RuntimeRoot=$RuntimeRoot; Variant=$taskBase
    EnableOpus=$true; OpusInputBytes=1024; OpusScratchBytes=6144
    DmaBufferWords=512; StreamIdleTimeoutMs=3000
}
Push-Location $taskRoot
try {
    if ($Profile -eq 'accepted-asm') {
        # Authorizes verified ASM selection, not diagnostic workloads or logs.
        $taskArgs.Diagnostic=$true
        $taskArgs.OpusBackend='bands-tell-inline-asm'
        $taskArgs.OpusWordAsm=$true
        $taskArgs.OpusIcdfFlashWord=$true
        $taskArgs.OpusFirFlashWord=$true
        & node tools/esp8266_opus_asm/prepare_main_references.cjs
        if ($LASTEXITCODE -ne 0) { throw 'Accepted ASM reference verification failed' }
    }
    & tools/esp8266_audio_profile/build_i2s_pdm_production.ps1 @taskArgs
    if ($Profile -eq 'accepted-asm') {
        & node tools/esp8266_opus_asm/live_variant_v2.cjs $taskBase $taskFinal
        if ($LASTEXITCODE -ne 0) { throw 'Accepted ASM relocation/verification failed; nothing published' }
    } else { $taskFinal = $taskBase }
    & node tools/esp8266_opus_asm/publish_main.cjs $taskFinal $Variant $Profile
    if ($LASTEXITCODE -ne 0) { throw 'Main firmware validation failed; nothing published' }
    Write-Output "Main radio saved: firmware/development/$Variant/app.bin (not flashed)"
} finally { Pop-Location }
