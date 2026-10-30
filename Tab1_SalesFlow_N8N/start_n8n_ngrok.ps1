param(
  [int]$Port = 5678
)

$ErrorActionPreference = 'Stop'
$n8n = (Get-Command n8n.cmd -ErrorAction SilentlyContinue).Source
$ngrok = (Get-Command ngrok.exe -ErrorAction SilentlyContinue).Source
if (-not $n8n) { throw 'n8n.cmd was not found on PATH. Install n8n or add it to PATH.' }
if (-not $ngrok) { throw 'ngrok.exe was not found on PATH. Install ngrok and configure an authtoken.' }

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$logDir = Join-Path $root 'runtime-logs'
New-Item -ItemType Directory -Force -Path $logDir | Out-Null

Write-Host "Starting ngrok HTTPS tunnel to localhost:$Port..." -ForegroundColor Cyan
$ngrokLog = Join-Path $logDir 'ngrok.log'
$ngrokErr = Join-Path $logDir 'ngrok.err.log'
Start-Process -FilePath $ngrok -ArgumentList @('http', $Port, '--host-header=rewrite', '--log=stdout') `
  -WorkingDirectory $root -RedirectStandardOutput $ngrokLog -RedirectStandardError $ngrokErr -WindowStyle Hidden | Out-Null

$publicUrl = $null
for ($i = 0; $i -lt 30 -and -not $publicUrl; $i++) {
  Start-Sleep -Milliseconds 500
  try {
    $tunnels = Invoke-RestMethod -Uri 'http://127.0.0.1:4040/api/tunnels' -TimeoutSec 2
    $publicUrl = ($tunnels.tunnels | Where-Object { $_.proto -eq 'https' } | Select-Object -First 1).public_url
  } catch { }
}
if (-not $publicUrl) {
  throw "ngrok did not expose an HTTPS URL. Check $ngrokLog and confirm the ngrok account token is configured."
}

$env:N8N_HOST = '127.0.0.1'
$env:N8N_LISTEN_ADDRESS = '127.0.0.1'
$env:N8N_PORT = "$Port"
$env:N8N_PROTOCOL = 'http'
$env:WEBHOOK_URL = "$publicUrl/"
$env:N8N_EDITOR_BASE_URL = $publicUrl
$env:N8N_SECURE_COOKIE = 'false'

$n8nOut = Join-Path $logDir 'n8n.out.log'
$n8nErr = Join-Path $logDir 'n8n.err.log'
Start-Process -FilePath $env:ComSpec -ArgumentList @('/c', $n8n, 'start', '--host', '127.0.0.1', '--port', "$Port") `
  -WorkingDirectory $root -RedirectStandardOutput $n8nOut -RedirectStandardError $n8nErr -WindowStyle Hidden | Out-Null

Write-Host ''
Write-Host 'SalesFlow N8N HTTPS workspace is starting.' -ForegroundColor Green
Write-Host "Public HTTPS URL : $publicUrl" -ForegroundColor Green
Write-Host "Editor           : $publicUrl" -ForegroundColor Green
Write-Host "Webhook base     : $publicUrl/webhook/" -ForegroundColor Green
Write-Host "n8n logs         : $n8nOut" -ForegroundColor DarkGray
Write-Host "ngrok logs       : $ngrokLog" -ForegroundColor DarkGray
Write-Host ''
Write-Host 'Import the JSON files from workflows/, then activate the required workflows.' -ForegroundColor Yellow
