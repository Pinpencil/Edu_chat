@echo off
REM 0. 切换 CMD 代码页为 UTF-8，确保中文显示正常
chcp 65001 >nul

REM 1. 切换到脚本所在目录（包括盘符）
cd /d "%~dp0"

REM 2. 激活虚拟环境
call .\.venv\Scripts\activate

echo.
echo 启动 Daphne 服务器（0.0.0.0:8001），按 Ctrl+C 停止……
daphne -b 0.0.0.0 -p 8001 chat_ol_study.asgi:application
echo.
echo 服务器已启动！按 Ctrl+C 停止。
