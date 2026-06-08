@echo off
setlocal

powershell -ExecutionPolicy Bypass -File "%~dp0build_beta_bundle.ps1"

endlocal
