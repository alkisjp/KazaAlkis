param(
    [ValidateSet("Menu", "Run", "Setup", "Schedule", "DisableSchedule", "Status")]
    [string]$Action = "Menu",
    [string]$AIRoot = $(if ($env:AI_ROOT) { $env:AI_ROOT } else { "E:\AI" }),
    [string]$SendTime = "08:00"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$env:AI_ROOT = $AIRoot
$env:AI_MODELS = Join-Path $AIRoot "models"
$env:AI_CACHE = Join-Path $AIRoot "cache"
$env:AI_OUTPUTS = Join-Path $AIRoot "outputs"
$env:AI_VENVS = Join-Path $AIRoot "venvs"
$env:AI_LOGS = Join-Path $AIRoot "logs"
$env:AI_TMP = Join-Path $AIRoot "tmp"
$env:AI_VECTORSTORE = Join-Path $AIRoot "vectorstore"
$env:AI_TOOLS = Join-Path $AIRoot "tools"
$env:PYTHONUTF8 = "1"

function Initialize-AIWorkspace {
    if (-not (Test-Path $AIRoot)) {
        New-Item -ItemType Directory -Path $AIRoot -Force | Out-Null
    }
    foreach ($folder in "models", "models\ollama", "cache", "outputs", "logs", "tmp",
             "venvs", "vectorstore", "projects", "shared", "tools") {
        New-Item -ItemType Directory -Path (Join-Path $AIRoot $folder) -Force | Out-Null
    }
}

function Show-StorageStatus {
    $aiDrive = Get-PSDrive -Name ([IO.Path]::GetPathRoot($AIRoot).Substring(0, 1))
    $cDrive = Get-PSDrive -Name "C"
    Write-Host ("AI workspace: {0}" -f $AIRoot)
    Write-Host ("AI drive free: {0:N1} GB" -f ($aiDrive.Free / 1GB))
    Write-Host ("C: drive free: {0:N1} GB" -f ($cDrive.Free / 1GB))
    if ($ProjectRoot.StartsWith("C:", [StringComparison]::OrdinalIgnoreCase)) {
        Write-Warning "Project source is on C:. Runtime resources still route to AI_ROOT."
    }
    foreach ($path in $env:AI_MODELS, $env:AI_CACHE, $env:AI_OUTPUTS, $env:AI_VENVS,
             $env:AI_LOGS, $env:AI_TMP, $env:AI_VECTORSTORE, $env:AI_TOOLS) {
        if ($path.StartsWith("C:", [StringComparison]::OrdinalIgnoreCase)) {
            Write-Warning "Unexpected C: runtime path: $path"
        }
    }
    if (Test-Path (Join-Path $ProjectRoot "venv_kazaalkis")) {
        Write-Warning "Legacy repo-local venv detected. Use the E:\AI\venvs environment instead."
    }
}

function Get-AppPython {
    $venvPython = Join-Path $env:AI_VENVS "KazaALKIS\Scripts\python.exe"
    if (Test-Path $venvPython) { return $venvPython }
    return "python"
}

function Start-KazaALKIS {
    Write-Host "KazaALKIS: a daily Greek calendar with good manners and a decent memory."
    & (Get-AppPython) (Join-Path $ProjectRoot "KazaALKIS_launcher.py")
}

function Install-KazaALKIS {
    $venvPath = Join-Path $env:AI_VENVS "KazaALKIS"
    if (-not (Test-Path $venvPath)) { python -m venv $venvPath }
    $python = Join-Path $venvPath "Scripts\python.exe"
    $requirements = Join-Path $ProjectRoot "requirements.txt"
    if (Test-Path $requirements) { & $python -m pip install -r $requirements }
    & $python -c "from src.database import KazaALKISDatabase; db=KazaALKISDatabase(); db.connect(); db.initialize_schema(); db.close()"
}

function Enable-KazaALKISSchedule {
    $script = Join-Path $ProjectRoot "KazaALKIS.ps1"
    $action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$script`" -Action Run"
    $trigger = New-ScheduledTaskTrigger -Daily -At $SendTime
    Register-ScheduledTask -TaskName "KazaALKIS Daily Calendar" -Action $action -Trigger $trigger -Force | Out-Null
    Write-Host "Scheduled KazaALKIS daily at $SendTime."
}

function Disable-KazaALKISSchedule {
    Unregister-ScheduledTask -TaskName "KazaALKIS Daily Calendar" -Confirm:$false -ErrorAction SilentlyContinue
    Write-Host "KazaALKIS scheduled task disabled."
}

Initialize-AIWorkspace
Show-StorageStatus

if ($Action -eq "Run") { Start-KazaALKIS; exit }
if ($Action -eq "Setup") { Install-KazaALKIS; exit }
if ($Action -eq "Schedule") { Enable-KazaALKISSchedule; exit }
if ($Action -eq "DisableSchedule") { Disable-KazaALKISSchedule; exit }
if ($Action -eq "Status") { exit }

Write-Host ""
Write-Host "1. Run KazaALKIS"
Write-Host "2. Setup AI-rooted Python environment"
Write-Host "3. Schedule daily task"
Write-Host "4. Disable scheduled task"
Write-Host "5. Exit"
$choice = Read-Host "Select option"
if ($choice -eq "1") { Start-KazaALKIS }
elseif ($choice -eq "2") { Install-KazaALKIS }
elseif ($choice -eq "3") { Enable-KazaALKISSchedule }
elseif ($choice -eq "4") { Disable-KazaALKISSchedule }
