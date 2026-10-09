param([Parameter(Mandatory=$true)][string]$Output)
$started = (Get-Date).ToUniversalTime().ToString('o')
$rows = Get-NetTCPConnection
$boardRows = @($rows | Where-Object { $_.RemoteAddress -eq '192.168.100.4' })
[ordered]@{
    started_utc = $started
    captured_utc = (Get-Date).ToUniversalTime().ToString('o')
    total = $rows.Count
    all_states = @($rows | Group-Object State | Select-Object Name,Count)
    board_states = @($boardRows | Group-Object State | Select-Object Name,Count)
    board_local_ports = @($boardRows | Select-Object LocalPort,RemotePort,State,OwningProcess)
    dynamic_ports = @(netsh int ipv4 show dynamicport tcp)
    excluded_ports = @(netsh int ipv4 show excludedportrange protocol=tcp)
} | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $Output
