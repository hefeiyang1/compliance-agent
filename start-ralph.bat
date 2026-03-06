@echo off
echo ========================================
echo Starting Ralph for Compliance Agent...
echo ========================================
echo.

cd /d "D:\Study\Ralph for Claude Code\compliance-agent"

echo Current directory:
cd
echo.

echo Starting Ralph with monitoring...
echo ========================================
echo.

C:\Users\HEFEIYANG\.local\bin\ralph --monitor

echo.
echo ========================================
echo Ralph stopped. Press any key to exit...
pause
