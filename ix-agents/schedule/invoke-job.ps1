# ix-agents 专用定时 — 唯一 per-job 入口（禁止改用其它脚本）
param(
    [Parameter(Mandatory = $true)]
    [string] $JobId
)

$ErrorActionPreference = "Stop"
$WorkWithRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
Set-Location $WorkWithRoot

python -m pip install -q -r artifacts\ix-agent-run-cli\requirements.txt
python artifacts\ix-agent-run-cli\main.py schedule run --job-id $JobId
