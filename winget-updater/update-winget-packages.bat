@echo off
REM --------------------------------------------------
REM Launcher for Update-Packages.ps1 (portable)
REM --------------------------------------------------

REM %~dp0 expands to the directory of this batch file
set "SCRIPT_DIR=%~dp0"

REM Path to the PowerShell script (assumes it's in the same folder as this .bat)
set "PS_SCRIPT=%SCRIPT_DIR%update-winget-packages.ps1"

REM Optional: Dry-Run mode
REM Set DRY_RUN=1 to enable dry-run; comment out or set 0 to disable
set "DRY_RUN=0"

REM Run the PowerShell script silently with bypassed execution policy
if "%DRY_RUN%"=="1" (
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%PS_SCRIPT%" -DryRun
) else (
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%PS_SCRIPT%"
)

REM Optional: pause to see any messages when testing
pause

exit /b
