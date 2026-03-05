param(
    [string]$EditorExe = "C:\Program Files\Epic Games\UE_5.7\Engine\Binaries\Win64\UnrealEditor-Cmd.exe",
    [string]$UProject = "$PSScriptRoot\RootyTooty.uproject",
    [string]$TestName = "Project.Maps.PIE",
    [string]$LogPath
)

$ErrorActionPreference = "Stop"

if (-not $LogPath) {
    $safeTestName = ($TestName -replace "[^A-Za-z0-9_]", "_")
    $LogPath = "$PSScriptRoot\Saved\Logs\SmokeTest_${safeTestName}_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
}

$logDir = Split-Path -Parent $LogPath
if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
}

if (-not (Test-Path $EditorExe)) {
    throw "UnrealEditor-Cmd.exe not found at: $EditorExe"
}

if (-not (Test-Path $UProject)) {
    throw "Project file not found at: $UProject"
}

Write-Host "Running smoke test '$TestName'..."
Write-Host "Editor: $EditorExe"
Write-Host "Project: $UProject"
Write-Host "Log:    $LogPath"

$args = @(
    "`"$UProject`"",
    "-unattended",
    "-nop4",
    "-nosplash",
    "-NoSound",
    "-ExecCmds=`"Automation RunTests $TestName; Quit`"",
    "-TestExit=`"Automation Test Queue Empty`"",
    "-AbsLog=`"$LogPath`""
)

$process = Start-Process -FilePath $EditorExe -ArgumentList $args -Wait -PassThru -NoNewWindow
$exitCode = $process.ExitCode

$summary = @()
if (Test-Path $LogPath) {
    $summary = Select-String -Path $LogPath -Pattern "Test Completed\. Result=|TEST COMPLETE|No automation tests matched|Setting GIsCriticalError|Fatal error|Engine exit requested" -CaseSensitive:$false
}

Write-Host ""
Write-Host "=== Smoke Summary ==="
Write-Host "Process exit code: $exitCode"
if ($summary.Count -gt 0) {
    $summary | Select-Object -Last 12 | ForEach-Object { Write-Host $_.Line }
} else {
    Write-Host "No summary markers found in log."
}

$success = $false
if (Test-Path $LogPath) {
    $success = Select-String -Path $LogPath -Pattern "Test Completed\. Result=\{Success\}|TEST COMPLETE\. EXIT CODE: 0" -CaseSensitive:$false -Quiet
}

if ($success -and $exitCode -eq 0) {
    Write-Host ""
    Write-Host "Smoke test PASSED."
    exit 0
}

Write-Host ""
Write-Host "Smoke test FAILED."
if ($exitCode -ne 0) {
    exit $exitCode
}
exit 1
