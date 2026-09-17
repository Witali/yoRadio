param(
    [string]$SdkPath='C:/Work/yoRadio/.worktree/esp8266-native-port/.build/esp8266-rtos-sdk',
    [string]$RuntimeRoot='C:/Work/yoRadio/.build'
)
# Build only; never flash implicitly. Keep C/default production unchanged.
$ErrorActionPreference='Stop'
$taskRoot=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
Push-Location $taskRoot
try {
    & tools/esp8266_audio_profile/build_i2s_pdm_production.ps1 -SdkPath $SdkPath -RuntimeRoot $RuntimeRoot -Variant esp8266-opus-live-asm-base-20260917 -Diagnostic -EnableOpus -OpusBackend bands-tell-inline-asm -OpusWordAsm -OpusIcdfFlashWord -OpusFirFlashWord -NoSpiffsCache -Pdm32Iram -Pdm32Batch -OpusStreamTest -StreamIdleTimeoutMs 3000
    if($LASTEXITCODE -ne 0){throw 'Ordinary radio build failed'}
    # Recover the two reference ELFs from committed proof artifacts if the
    # disposable build directory was cleaned. Never replace a different ELF.
    & node -e 'const fs=require("fs"),path=require("path"),zlib=require("zlib"),f=require("./tools/esp8266_opus_asm/live_accepted.cjs"),b=require("./tools/esp8266_opus_asm/frozen_reloads.cjs");const c=f.chain();for(const [v,data]of[[c[0].proof.parent,zlib.gunzipSync(fs.readFileSync("firmware/development/"+c[0].variant+"/parent.elf.gz"))],[c.at(-1).variant,b.patchElf(zlib.gunzipSync(fs.readFileSync("firmware/development/"+c.at(-1).variant+"/parent.elf.gz")),c.at(-1).proof.patches)]]){const p=path.join(".build",v,b.elfName);if(fs.existsSync(p)){require("assert").deepStrictEqual(fs.readFileSync(p),data);}else{fs.mkdirSync(path.dirname(p),{recursive:true});fs.writeFileSync(p,data);}}'
    if($LASTEXITCODE -ne 0){throw 'Reference ELF recovery failed'}
    & node tools/esp8266_opus_asm/live_accepted.cjs
    if($LASTEXITCODE -ne 0){throw 'Accepted ASM relocation failed'}
} finally { Pop-Location }
