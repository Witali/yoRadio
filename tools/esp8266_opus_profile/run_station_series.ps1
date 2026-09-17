param(
    [Parameter(Mandatory=$true)][string]$Directory,
    [ValidateRange(10,100)][int]$Attempts=10,
    [int[]]$Stations=@(512,513)
)
# Ordinary playlist commands only. No benchmark endpoint, OTA, UART or reset.
$ErrorActionPreference='Stop'
$taskRoot=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$taskDirectory=[IO.Path]::GetFullPath((Join-Path $taskRoot $Directory))
if(-not $taskDirectory.StartsWith($taskRoot+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)){throw 'Reports must stay in repository'}
if(-not $Stations.Count -or ($Stations | Where-Object { $_ -lt 1 -or $_ -gt 65535 })){throw 'Invalid station numbers'}
if(Test-Path -LiteralPath (Join-Path $taskDirectory 'start1.json')){throw 'Existing attempts must not be overwritten'}
New-Item -ItemType Directory -Force -Path $taskDirectory | Out-Null
$taskSummary=@()
for($taskAttempt=1;$taskAttempt -le $Attempts;$taskAttempt++) {
    $taskStation=$Stations[($taskAttempt-1)%$Stations.Count]
    $taskStart=Join-Path $taskDirectory "start$taskAttempt.json"
    $taskWindow=Join-Path $taskDirectory "window$taskAttempt.json"
    Write-Output "START ordinary station $taskStation, attempt $taskAttempt/$Attempts"
    $ErrorActionPreference='Continue'
    & node (Join-Path $taskRoot 'tools/esp8266_audio_profile/check_prefill_board.cjs') command --command "play=$taskStation" --output $taskStart *> (Join-Path $taskDirectory "start$taskAttempt.log")
    $ErrorActionPreference='Stop'
    if(-not(Test-Path -LiteralPath $taskStart)){throw 'Missing command report; inspect before sending another Play'}
    Start-Sleep -Seconds 3
    $ErrorActionPreference='Continue'
    & node (Join-Path $PSScriptRoot 'run_stage_wall.cjs') --seconds 25 --output $taskWindow *> (Join-Path $taskDirectory "window$taskAttempt.log")
    $ErrorActionPreference='Stop'
    if(-not(Test-Path -LiteralPath $taskWindow)){throw 'Missing window; do not restart an uncertain attempt'}
    $taskCommand=Get-Content -LiteralPath $taskStart -Raw | ConvertFrom-Json
    $taskTrace=Get-Content -LiteralPath $taskWindow -Raw | ConvertFrom-Json
    $taskConfirmed=[bool]($taskCommand.command.messages | Where-Object { $_.current -eq $taskStation })
    $taskAudioPass=[bool]($taskTrace.result.continuity.pass -and -not $taskTrace.result.profile_error)
    $taskSummary+=[pscustomobject]@{
        attempt=$taskAttempt; station=$taskStation; current_confirmed=$taskConfirmed
        command_error=$taskCommand.error; audio_pass=$taskAudioPass
        pass=($taskConfirmed -and $taskAudioPass -and -not $taskCommand.error)
        result=$taskTrace.result
    }
    [IO.File]::WriteAllText((Join-Path $taskDirectory 'series.json'),($taskSummary | ConvertTo-Json -Depth 15),(New-Object Text.UTF8Encoding($false)))
    Write-Output ("MEASURED {0}/{1}: station={2}; confirmed={3}; continuous={4}; PCM ratio={5}; underruns={6}" -f $taskAttempt,$Attempts,$taskStation,$taskConfirmed,$taskAudioPass,$taskTrace.result.continuity.ratio,$taskTrace.result.continuity.underruns)
    if($taskAttempt -lt $Attempts){Start-Sleep -Seconds 3}
}
if($taskSummary | Where-Object { -not $_.pass }){exit 1}
