# DocShot 文档快照

DocShot 是一个本地运行的 Windows 桌面文档转换工具，聚焦常用格式互转，文件全程本地处理，不上传服务器。

## 功能一览

- `Word 转图片`
  - 支持 `.doc` / `.docx`
  - 可选图片格式：`PNG` / `JPG`
  - 可选清晰度：普通 / 高清 / 超清
- `Word 转 PDF`
  - 支持 `.doc` / `.docx`
  - 自动生成不重名输出文件
- `PDF 转 Word`
  - 快速模式：适合文字型 PDF（`pdf2docx`）
  - OCR 模式：适合扫描件 PDF（`PyMuPDF + PaddleOCR + python-docx`）

## 界面说明

- 主界面提供功能切换、输入文件选择、输出目录选择、进度与状态显示。
- 左侧操作区支持滚动，避免控件拥挤。
- 右上角提供“关于”按钮，支持显示收款码（`assets/reward_qr.png`）。

## 环境要求

- Windows 10/11（推荐）
- Python 3.10+
- Microsoft Word（仅 `Word 转图片` 和 `Word 转 PDF` 需要，依赖 `docx2pdf`）

## 安装依赖

```bash
pip install -r requirements.txt
```

## 启动方式

```bash
python main.py
```

## 目录约定

- 应用图标：`assets/icon.png`
- 关于页收款码：`assets/reward_qr.png`

## 输出命名规则

当目标文件已存在时，自动追加序号避免覆盖：

- `demo.pdf` -> `demo.docx` / `demo_1.docx` / `demo_2.docx`
- `demo.docx` -> `demo.pdf` / `demo_1.pdf` / `demo_2.pdf`

## OCR 模式说明

- OCR 模式适合扫描件 PDF，但速度慢于快速模式。
- 复杂排版（表格、双栏、图文混排）不保证完整还原。
- 首次运行 PaddleOCR 可能下载模型并耗时更久。

## 常见问题

### 1) OCR 报错或结果为空

建议按顺序检查：

1. 依赖是否完整安装（尤其 `paddleocr`、`paddlepaddle`）。
2. 输入是否为清晰可读的扫描图像（分辨率过低会影响识别）。
3. 优先尝试“快速模式”处理文字型 PDF。

### 2) Word 转换失败

- 请确认本机已安装可用的 Microsoft Word。
- 某些受保护文档或损坏文档可能转换失败。

## 打包

项目已包含 `DocShot.spec`，可使用 PyInstaller 打包：

```bash
pyinstaller DocShot.spec
```

## 免责声明

本工具仅用于学习与办公效率提升，请确保文档处理符合你所在组织的安全与合规要求。
