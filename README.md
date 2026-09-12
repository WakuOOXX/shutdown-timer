# 定时助手 (Shutdown Timer)

一个 Windows 桌面小工具，支持**定时关机**和**定时休眠**，使用 Python + Tkinter 编写。

## 功能

- 定时关机 / 定时休眠
- 倒计时显示
- 任务执行前警告提示
- 可随时取消已设定的任务

## 运行

```bash
python main.py
```

要求：Python 3.x（使用标准库 Tkinter，无需额外依赖）

## 打包为 exe

```bash
pip install pyinstaller
build.bat
```

打包产物输出到 `dist/定时助手.exe`。

## 打包产物

桌面上使用的 `定时助手.exe` 即由本仓库源码通过 PyInstaller 打包生成（Python 3.14）。
