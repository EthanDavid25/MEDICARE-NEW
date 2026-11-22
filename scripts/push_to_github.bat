@echo off
echo ============================================================
echo MEDICARE - Publish to MEDICARE-NEW (GitHub)
echo Target: https://github.com/EthanDavid25/MEDICARE-NEW.git
echo ============================================================
echo.
cd /d "%~dp0\.."
echo Current branch and commit:
git branch --show-current
git log -1 --oneline
echo.
echo Pushing branch 'main' to origin...
git push -u origin main
echo.
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Successfully published to MEDICARE-NEW!
) else (
    echo [ERROR] Push failed. If prompted for GitHub login, please sign in.
    echo Alternatively, if using a Personal Access Token:
    echo git push https://YOUR_TOKEN@github.com/EthanDavid25/MEDICARE-NEW.git main
)
pause
