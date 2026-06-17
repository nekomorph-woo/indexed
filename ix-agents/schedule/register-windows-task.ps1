# 将 registry 中已登记的 job 注册到 Windows 任务计划程序（ix-agents 专用，禁止其它注册方式）
param(
    [Parameter(Mandatory = $true)]
    [string] $JobId,
    [string] $At = "09:00",
    [ValidateSet("DAILY", "WEEKLY", "MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN")]
    [string] $Frequency = "WEEKLY",
    [string] $DayOfWeek = "MON"
)

$ErrorActionPreference = "Stop"
$ScheduleDir = $PSScriptRoot
$InvokeScript = Join-Path $ScheduleDir "invoke-job.ps1"
$TaskName = "indexed-ix-$JobId"

if (-not (Test-Path $InvokeScript)) {
    throw "缺少 invoke-job.ps1: $InvokeScript"
}

$pwsh = (Get-Command powershell.exe).Source
$action = New-ScheduledTaskAction -Execute $pwsh -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$InvokeScript`" -JobId `"$JobId`""

if ($Frequency -eq "DAILY") {
    $trigger = New-ScheduledTaskTrigger -Daily -At $At
} else {
    $dow = [System.DayOfWeek]::$DayOfWeek
    $trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek $dow -At $At
}

$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Force | Out-Null

Write-Host "已注册 Windows 任务: $TaskName"
Write-Host "  动作: invoke-job.ps1 -JobId $JobId"
Write-Host "禁止再为该 job 创建其它计划任务或脚本。"
