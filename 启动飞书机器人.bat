@echo off
setlocal enabledelayedexpansion
chcp 936 >nul
title 飞书机器人 - 启动器
color 0A

echo ============================================
echo   飞书机器人 启动器  (OpenClaw Gateway)
echo ============================================
echo.

set "NODEEXE=C:\Program Files\nodejs\node.exe"
set "ENTRY=C:\Users\Administrator\AppData\Roaming\npm\node_modules\openclaw-cn\dist\entry.js"
set "CWD=C:\Users\Administrator\.openclaw"
set "LOG=C:\tmp\clawdbot\clawdbot-%date:~0,4%-%date:~5,2%-%date:~8,2%.log"

:: 1. 检查网关是否已运行（端口探测）
echo [1/3] 检查网关运行状态...
netstat -ano | findstr ":18789" | findstr "LISTENING" >nul 2>&1
if %errorlevel%==0 (
    echo     网关已在运行，无需重复启动。
    echo.
    echo     访问控制台: http://127.0.0.1:18789/
    goto :DONE
)

:: 2. 直接启动网关（gateway.cmd 方式：node 子进程常驻）
echo [2/3] 网关未运行，正在启动...
pushd "%CWD%"
start "飞书机器人网关" cmd /c ""%NODEEXE%" "%ENTRY%" gateway --port 18789 > "%LOG%" 2>&1"
popd

:: 3. 等待就绪并验证
echo [3/3] 等待网关就绪...
timeout /t 5 /nobreak >nul
netstat -ano | findstr ":18789" | findstr "LISTENING" >nul 2>&1
if %errorlevel%==0 (
    echo.
    echo [OK] 飞书机器人已启动！
    echo     控制台: http://127.0.0.1:18789/
) else (
    echo.
    echo [提示] 网关仍在初始化，可稍后访问 http://127.0.0.1:18789/
    echo     或手动运行: %NODEEXE% "%ENTRY%" gateway --port 18789
)

:DONE
echo.
echo --------------------------------------------
echo  关闭本窗口不会停止飞书机器人。
echo --------------------------------------------
echo.
pause