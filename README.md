# DocShot 文档快照

## 项目简介
DocShot 文档快照是一个基于 Python 的 Windows 本地桌面工具，目标是将 Word 文档转换为高清图片导出。

## 当前阶段
当前处于第二步：已实现 Word 转 PDF（仅限本地命令行调用），尚未实现 PDF 转图片、GUI 与 exe 打包。

## 后续计划
1. 增加 PDF 转高清图片导出流程。
2. 增加基础桌面界面（文件选择、导出路径、状态提示）。
3. 优化图片清晰度与导出参数。
4. 增加日志与异常处理。
5. 使用 PyInstaller 打包为 Windows 可执行文件（`.exe`）。

## 本地运行方法
1. 安装 Python 3.10+。
2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
3. 查看帮助：
   ```bash
   python main.py --help
   ```
4. 执行 Word 转 PDF：
   ```bash
   python main.py "C:\\path\\input.docx" "C:\\path\\output.pdf"
   ```
5. 无参数运行（仅显示项目名）：
   ```bash
   python main.py
   ```
