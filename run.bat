@echo off
setlocal enabledelayedexpansion

echo ==========================================
echo   星露谷物语 AI 自动化系统 - 一键启动器
echo ==========================================

:: 1. 检查 Python 环境
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到 Python，请确保已安装并添加到系统环境变量中。
    pause
    exit /b 1
)

:: 2. 安装/更新依赖
echo [1/3] 正在检查 Python 依赖...
pip install -r environment/requirements.txt --quiet
if %errorlevel% neq 0 (
    echo [警告] 依赖安装可能未完全成功，请检查网络连接。
)

:: 3. 首次启动检查 (init_wizard)
if not exist ".env" (
    echo [2/3] 检测到首次运行，正在启动初始化向导...
    echo ------------------------------------------
    python brain/init_wizard.py
    echo ------------------------------------------
    if not exist ".env" (
        echo [错误] 初始化未完成，无法启动系统。
        pause
        exit /b 1
    )
) else (
    echo [2/3] 环境配置已就绪。
)

:: 4. 启动 AI 决策引擎
echo [3/3] 正在启动 AI 战略大脑 (main.py)...
echo ------------------------------------------
echo 提示: 请确保您的星露谷物语已安装 SMAPI Mod 并处于运行状态。
echo ------------------------------------------
python main.py

pause
