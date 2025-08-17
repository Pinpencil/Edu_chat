@echo on
REM =============================================================
REM  install.bat —— 用于自动化安装 Python、创建虚拟环境并初始化项目
REM  放在项目根目录下，与 python-3.8.0-amd64.exe、offline_packages、requirements.txt 同级
REM  已支持 UTF-8 中文显示，并检查本机 Python 3.8.0 是否已存在于 PATH
REM =============================================================

REM —— 0. 先将 CMD 的代码页切换到 UTF-8，以便正确显示中文
chcp 65001 >nul

REM —— 1. 切换到本脚本所在目录（包括切换盘符）
cd /d "%~dp0"

REM —— 3. 创建虚拟环境，并检查 Python 版本
echo.
echo 步骤 1，安装python 3.8.0，并创建虚拟环境 .venv……

python-3.8.0-amd64 /quiet InstallAllUsers=0 PrependPath=0 TargetDir="%cd%\py380"
"%cd%\py380\python.exe" -m venv .venv
echo 虚拟环境 .venv 创建成功

REM —— 3.1 激活虚拟环境（注意必须用 call 才能在同一个脚本中生效）
call ".venv\Scripts\activate.bat"
echo 虚拟环境已激活。

REM —— 3.2 检测激活后的 Python 版本
for /f "tokens=2 delims= " %%W in ('python --version 2^>^&1') do set "VENV_PYVER=%%W"
echo 当前虚拟环境 Python 版本： %VENV_PYVER%
echo Python 版本验证通过。

REM —— 4. 安装指定的 backports.zoneinfo 包（来自当前目录）
echo.
echo 步骤 4：安装 backports.zoneinfo-0.2.1-cp38-cp38-win_amd64.whl……
python -m pip install --upgrade pip
pip install "backports.zoneinfo-0.2.1-cp38-cp38-win_amd64.whl"
echo backports.zoneinfo 安装成功。


REM —— 5. 从 offline_packages 目录中安装依赖
echo.
echo 步骤 5：从 offline_packages 安装 requirements.txt 中列出的依赖……
pip install --no-index --find-links=.\offline_packages -r requirements.txt

REM —— 6. 收集所有静态文件到 static 文件夹
echo.
echo 步骤 6：收集静态文件（collectstatic）……
python manage.py collectstatic --noinput


REM —— 7. 初始化数据库：makemigrations 与 migrate
echo.
echo 步骤 7：初始化数据库（makemigrations & migrate）……
python manage.py makemigrations chat_ol_app
echo makemigrations 成功。
python manage.py migrate
echo 数据库迁移完成。

REM —— 8. 安装完成，结束脚本
echo.
echo =============================================================
echo 安装流程已全部完成！
echo 请按任意键关闭窗口，或继续进行后续操作。
pause >nul
exit /b
