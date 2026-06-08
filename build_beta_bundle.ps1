$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$bundleRoot = Join-Path $root "beta-bundle"
$bundleApp = Join-Path $bundleRoot "Prompt-Assistant-Beta"
$bundleSrc = Join-Path $bundleApp "src"
$zipPath = Join-Path $root "Prompt-Assistant-Beta.zip"

if (Test-Path $bundleRoot) {
    Remove-Item -Recurse -Force $bundleRoot
}

New-Item -ItemType Directory -Force -Path $bundleApp | Out-Null
New-Item -ItemType Directory -Force -Path $bundleSrc | Out-Null

robocopy (Join-Path $root "src") $bundleSrc /E /XD __pycache__ /XF *.pyc | Out-Null
Copy-Item -Force (Join-Path $root "start_prompt_assistant.bat") $bundleApp
Copy-Item -Force (Join-Path $root "README.md") $bundleApp
Get-ChildItem -Path $root -Filter "BETA-*.md" | ForEach-Object {
    Copy-Item -Force $_.FullName $bundleApp
}

if (Test-Path $zipPath) {
    Remove-Item -Force $zipPath
}

Compress-Archive -Path $bundleApp -DestinationPath $zipPath -Force
Write-Output "Created beta bundle: $zipPath"
