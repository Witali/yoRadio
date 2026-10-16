#Requires -Version 7.5

function Read-SmallTvTestResult([string]$LiteralPath) {
    # Preserve ISO calendar references exactly; their country offset is test data.
    Get-Content -Raw -LiteralPath $LiteralPath | ConvertFrom-Json -DateKind String
}
