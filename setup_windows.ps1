# PowerShell script
Write-Host "🔍 Checking Python 3.11+..."
$pythonVersion = python --version
if (-not ($pythonVersion -like "*3.11*")) {
    Write-Host "Installing Python 3.11..."
    Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.11.5/python-3.11.5-amd64.exe" -OutFile "python_installer.exe"
    Start-Process -Wait -FilePath "./python_installer.exe" -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1"
    Remove-Item "python_installer.exe"
}

Write-Host "✅ Python version: $(python --version)"

Write-Host "🔍 Checking for Poetry..."
if (-not (Get-Command poetry -ErrorAction SilentlyContinue)) {
    Write-Host "📦 Installing Poetry..."
    (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
    $env:Path += ";$env:USERPROFILE\.poetry\bin"
}

Write-Host "📦 Installing dependencies..."
poetry install

Write-Host "✅ Windows setup complete. Run 'poetry shell' to activate environment."
