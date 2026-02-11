# SieshKa-Bot/scripts/run_local_api.ps1
# Компактный локальный тест API: health, settings, menu, guest orders
# Легко адаптируется под порт и окружение. Работает без внешней CI.

param(
  [int]$Port = 8000,
  [switch]$SkipDeps
)

# Auto-detect CI environments to skip heavy deps when needed
if (-not $PSBoundParameters.ContainsKey('SkipDeps')) {
  if (($env:CI -eq "true") -or ($env:GITHUB_ACTIONS) -or ($env:CI -eq "1")) {
    $SkipDeps = $true
  }
}

$ErrorActionPreference = "Stop"

# Определяем корень репозитория и директорию проекта
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path $ScriptDir -Parent
$ShopDir = Join-Path $RepoRoot "shop"

# 0) Prepare results logging (JSON/CSV for CI analytics)
$ResultsDir = Join-Path $RepoRoot "scripts/results"
if (-Not (Test-Path $ResultsDir)) {
  New-Item -ItemType Directory -Path $ResultsDir | Out-Null
}
$Results = @()

# 1) Create virtual environment, if needed
$venvPath = Join-Path $RepoRoot "venv"
if (-Not (Test-Path $venvPath)) {
  Write-Host "Creating virtual environment at $venvPath"
  python -m venv $venvPath
}
$PythonExe = Join-Path $venvPath "Scripts\python.exe"

# 2) Установить зависимости (быстрый режим; можно пропускать незаверенные зависимости)
Write-Host "Installing dependencies..."
if ($SkipDeps) {
  Write-Host "SKIP_DEPS is enabled: skipping dependency installation."
} else {
  try {
    & $PythonExe -m pip install --upgrade pip
    # Support both possible locations of requirements.txt (nested or root)
    $ReqPathNested = Join-Path $RepoRoot "SieshKa-Bot/requirements.txt"
    $ReqPathRoot = Join-Path $RepoRoot "requirements.txt"
    if (Test-Path $ReqPathNested) {
      & $PythonExe -m pip install -r $ReqPathNested
    } elseif (Test-Path $ReqPathRoot) {
      & $PythonExe -m pip install -r $ReqPathRoot
    } else {
      Write-Host "Requirements file not found in known locations. Skipping dependency installation."
    }
  } catch {
    Write-Host "Warning: dependency installation failed: $($_.Exception.Message)"
    # Proceed anyway; if dependencies are already installed, uvicorn start may still work
  }
}

# 3) Запуск uvicorn (фоновый процесс)
$LogFile = Join-Path $RepoRoot "uvicorn.log"
$ErrFile = Join-Path $RepoRoot "uvicorn.err"
$Proc = Start-Process -FilePath $PythonExe -ArgumentList "-m","uvicorn","app.main:app","--reload","--host","0.0.0.0","--port",$Port -NoNewWindow -RedirectStandardOutput $LogFile -RedirectStandardError $ErrFile -PassThru
Write-Host "Starting uvicorn (PID=$($Proc.Id))..."

# 4) Ожидание готовности сервера
$HealthUrl = "http://localhost:$Port/api/v1/health"
$Start = Get-Date
$Ready = $false
while (-Not $Ready -and ((Get-Date) - $Start).TotalSeconds -lt 60) {
  Start-Sleep -Seconds 1
  try {
    $Resp = Invoke-WebRequest -Uri $HealthUrl -UseBasicParsing -TimeoutSec 3
    if ($Resp.StatusCode -ge 200 -and $Resp.StatusCode -lt 400) { $Ready = $true }
  } catch {
    # пропускать ошибки до готовности
  }
}
if (-Not $Ready) {
  Stop-Process -Id $Proc.Id -Force
  Write-Host "Server did not become ready in time"
  exit 1
}
Write-Host "Server is ready."

# 5) Тестирование основных эндпоинтов
$Endpoints = @(
  "/api/v1/health",
  "/api/v1/settings",
  "/api/v1/settings/payment-methods",
  "/api/v1/menu/categories",
  "/api/v1/menu/products"
)
foreach ($Ep in $Endpoints) {
  $epStart = Get-Date
  $code = 0
  $ok = $false
  $err = $null
  try {
    $R = Invoke-WebRequest -Uri "http://localhost:$Port$Ep" -Method Get -TimeoutSec 10
    if ($R -and $R.StatusCode) {
      $code = $R.StatusCode
      $ok = ($code -ge 200 -and $code -lt 300)
    }
  } catch {
    $err = $_.Exception.Message
    $code = 0
    $ok = $false
  }
  $epDuration = [int]([math]::Round((New-TimeSpan -Start $epStart -End (Get-Date)).TotalMilliseconds))
  $entry = [pscustomobject]@{
    endpoint = $Ep
    status_code = $code
    ok = $ok
    duration_ms = $epDuration
    timestamp = (Get-Date).ToString("o")
    error = $err
  }
  $Results += $entry
  Write-Host "$Ep -> $(if ($ok) {'OK'} else {'FAIL'}) (HTTP $code)"
}

# 7) CI Analytics: write results to JSON/CSV
$JsonPath = Join-Path $ResultsDir "results.json"
$Results | ConvertTo-Json -Depth 5 | Out-File -Encoding UTF8 $JsonPath
$CsvPath = Join-Path $ResultsDir "results.csv"
$Results | Export-Csv -NoTypeInformation -Encoding UTF8 $CsvPath
Write-Host "Results written to $JsonPath and $CsvPath"

# 6) Гостевой заказ (guest order)
$Payload = @{
  name = "Test User"
  phone = "+10000000000"
  address = "Test Address"
  items = @(
    @{ product_id = "burger"; quantity = 1; modifiers = @() ; special_instructions = "" }
  )
  notes = ""
} | ConvertTo-Json -Depth 3

try {
  $Guest = Invoke-RestMethod -Uri "http://localhost:$Port/api/v1/orders/guest" -Method POST -ContentType "application/json" -Body $Payload
  Write-Host "Guest order created, ID: $($Guest.order_id)"
} catch {
  Write-Host "Guest order failed: $($_.Exception.Message)"
}

# 7) Завершение
if ($Proc -and $Proc.Id) {
  try {
    Stop-Process -Id $Proc.Id -Force
  } catch {
    # Ignore if process already stopped
  }
}
Write-Host "Server stopped."
