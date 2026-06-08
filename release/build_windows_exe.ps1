$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$specPath = Join-Path $PSScriptRoot "PromptAssistantBeta.spec"
$distRoot = Join-Path $root "dist"
$releaseRoot = Join-Path $root "release-build"
$bundleName = "Prompt-Assistant-Beta-Windows"
$bundleRoot = Join-Path $releaseRoot $bundleName
$venvPython = Join-Path $root ".venv\Scripts\python.exe"

if (-not (Test-Path $venvPython)) {
    Write-Error "Project virtual environment Python was not found."
}

$pyinstallerCheck = & $venvPython -c "import importlib.util; raise SystemExit(0 if importlib.util.find_spec('PyInstaller') else 1)"
if ($LASTEXITCODE -ne 0) {
    Write-Error "PyInstaller is not installed yet. Install the release extras first, then rerun this script."
}

if (Test-Path $releaseRoot) {
    try {
        Remove-Item -Recurse -Force $releaseRoot
    }
    catch {
        $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
        $bundleName = "$bundleName-$timestamp"
        $bundleRoot = Join-Path $releaseRoot $bundleName
    }
}

if (Test-Path $distRoot) {
    Remove-Item -Recurse -Force $distRoot
}

Push-Location $root
try {
    & $venvPython -m PyInstaller --noconfirm $specPath
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller build failed."
    }

    New-Item -ItemType Directory -Force -Path $bundleRoot | Out-Null
    Copy-Item -Recurse -Force (Join-Path $distRoot "PromptAssistantBeta") $bundleRoot
    Copy-Item -Force (Join-Path $root "README.md") $bundleRoot
    Get-ChildItem -Path $root -Filter "BETA-*.md" | ForEach-Object {
        Copy-Item -Force $_.FullName $bundleRoot
    }
    $bundleAppHome = Join-Path $bundleRoot "PromptAssistantBeta\.prompt_assistant"
    New-Item -ItemType Directory -Force -Path $bundleAppHome | Out-Null
    $sourceCache = Join-Path $root ".prompt_assistant\prompt_library_cache.json"
    if (Test-Path $sourceCache) {
        Copy-Item -Force $sourceCache $bundleAppHome
    }

    Write-Output "Windows release bundle created at: $bundleRoot"
}
finally {
    Pop-Location
}
