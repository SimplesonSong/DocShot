"""Modernized PySide6 UI for DocShot."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QObject, QThread, Qt, QUrl, Signal
from PySide6.QtGui import QDesktopServices, QPixmap
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app.converter import convert_word_to_images, convert_word_to_pdf, pdf_to_word_fast, pdf_to_word_ocr
from src.docshot import ConversionCancelledError

APP_STYLE = """
QWidget {
    background: #f6f8fc;
    color: #1f2937;
    font-family: "Segoe UI", "Microsoft YaHei UI", "Microsoft YaHei";
    font-size: 14px;
}
QLabel {
    background: transparent;
}
QLabel#TitleLabel {
    font-size: 28px;
    font-weight: 700;
    color: #111827;
}
QLabel#SubtitleLabel {
    font-size: 14px;
    color: #6b7280;
}
QLabel#TagLabel {
    background: #eef2ff;
    color: #4f46e5;
    border: 1px solid #dbe2ff;
    border-radius: 12px;
    padding: 6px 12px;
    font-weight: 600;
}
QFrame#Card {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
}
QFrame#AboutCard {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 14px;
}
QLabel#SectionLabel {
    font-size: 15px;
    font-weight: 600;
    color: #111827;
}
QLabel#AboutTitle {
    font-size: 22px;
    font-weight: 700;
    color: #111827;
}
QLabel#AboutBody {
    font-size: 13px;
    color: #4b5563;
}
QLabel#AboutMeta {
    font-size: 13px;
    color: #374151;
}
QLabel#QrHintLabel {
    font-size: 13px;
    color: #6b7280;
}
QLabel#QrImageLabel {
    background: #f8fafc;
    border: 1px solid #e5e7eb;
    border-radius: 10px;
    padding: 4px;
}
QLabel#HintLabel {
    background: transparent;
    font-size: 13px;
    font-weight: 400;
    color: #6b7280;
}
QLineEdit {
    min-height: 38px;
    max-height: 38px;
    border: 1px solid #d1d5db;
    border-radius: 10px;
    padding: 0 12px;
    background: #ffffff;
}
QLineEdit:read-only {
    background: #f8fafc;
    color: #374151;
}
QPushButton {
    min-height: 38px;
    max-height: 38px;
    border: 1px solid #d1d5db;
    border-radius: 10px;
    background: #ffffff;
    padding: 0 14px;
    font-weight: 600;
}
QPushButton:hover {
    background: #f3f4f6;
}
QPushButton:disabled {
    background: #f3f4f6;
    color: #9ca3af;
    border-color: #e5e7eb;
}
QPushButton#PrimaryButton {
    min-height: 46px;
    max-height: 46px;
    border: none;
    color: #ffffff;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #3b82f6, stop:1 #6366f1);
}
QPushButton#PrimaryButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #2563eb, stop:1 #4f46e5);
}
QComboBox {
    min-height: 38px;
    max-height: 38px;
    border: 1px solid #d1d5db;
    border-radius: 10px;
    padding: 0 12px;
    background: #ffffff;
}
QComboBox::drop-down {
    border: none;
    width: 26px;
}
QScrollArea {
    border: none;
    background: transparent;
}
QScrollBar:vertical {
    background: transparent;
    width: 9px;
    margin: 4px 2px 4px 2px;
    border: none;
}
QScrollBar::handle:vertical {
    background: #CBD5E1;
    min-height: 28px;
    border-radius: 4px;
}
QScrollBar::handle:vertical:hover {
    background: #94A3B8;
}
QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0px;
    width: 0px;
    border: none;
    background: transparent;
}
QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {
    background: transparent;
}
QProgressBar {
    min-height: 10px;
    max-height: 10px;
    border: 1px solid #e5e7eb;
    border-radius: 5px;
    background: #eef2f7;
    text-align: center;
    color: transparent;
}
QProgressBar::chunk {
    border-radius: 5px;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #60a5fa, stop:1 #6366f1);
}
QLabel#CopyrightLabel {
    font-size: 12px;
    color: #98A2B3;
}
QPushButton#AboutButton {
    min-height: 32px;
    max-height: 32px;
    min-width: 64px;
    border: 1px solid #dbe2ff;
    border-radius: 10px;
    background: #eef2ff;
    color: #4f46e5;
    font-size: 13px;
    font-weight: 600;
    padding: 0 12px;
}
QPushButton#AboutButton:hover {
    background: #e5eaff;
}
"""


class NoWheelComboBox(QComboBox):
    """A combobox that ignores mouse-wheel value changes."""

    def wheelEvent(self, event) -> None:  # type: ignore[override]
        event.ignore()


class AboutDialog(QDialog):
    """About dialog for DocShot."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("关于 DocShot")
        self.setFixedSize(460, 620)
        self.setModal(True)

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(0)

        card = QFrame()
        card.setObjectName("AboutCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(22, 20, 22, 18)
        card_layout.setSpacing(10)

        title = QLabel("DocShot 文档快照")
        title.setObjectName("AboutTitle")
        title.setAlignment(Qt.AlignCenter)

        version = QLabel("版本号：v2.0.0")
        version.setObjectName("AboutMeta")
        producer = QLabel("出品方：零一工作室")
        producer.setObjectName("AboutMeta")

        intro = QLabel(
            "DocShot 是一款本地文档转换工具，支持 Word 转图片、PDF 转 Word 等常用功能。"
            "文件在本地处理，不会上传到服务器。"
        )
        intro.setObjectName("AboutBody")
        intro.setWordWrap(True)

        author = QLabel(
            "零一工作室专注于实用工具、计算机科普和轻量级软件开发，希望用简单的软件解决真实的小问题。"
        )
        author.setObjectName("AboutBody")
        author.setWordWrap(True)
        contact = QLabel("如有反馈或制作软件的需求，请联系 2350368566@qq.com")
        contact.setObjectName("AboutBody")
        contact.setWordWrap(True)

        support_title = QLabel("支持作者")
        support_title.setObjectName("SectionLabel")
        support_desc = QLabel("如果这个工具帮到了你，可以扫码支持作者继续维护。")
        support_desc.setObjectName("QrHintLabel")
        support_desc.setWordWrap(True)

        qr_label = QLabel()
        qr_label.setObjectName("QrImageLabel")
        qr_label.setAlignment(Qt.AlignCenter)
        qr_label.setFixedSize(280, 280)

        loaded = False
        qr_candidates = [
            Path(__file__).resolve().parent.parent / "assets" / "Alipay_reward_qr_resize.png",
            Path.cwd() / "assets" / "Alipay_reward_qr_resize.png",
        ]
        for qr_path in qr_candidates:
            if not qr_path.exists():
                continue
            pixmap = QPixmap(str(qr_path))
            if pixmap.isNull():
                continue
            qr_label.setPixmap(
                pixmap.scaled(268, 268, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
            loaded = True
            break

        if not loaded:
            qr_label.setText("暂未添加收款码图片，请将图片放到 assets/reward_qr.png")
            qr_label.setWordWrap(True)

        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)

        card_layout.addWidget(title)
        card_layout.addSpacing(2)
        card_layout.addWidget(version)
        card_layout.addWidget(producer)
        card_layout.addSpacing(6)
        card_layout.addWidget(intro)
        card_layout.addWidget(author)
        card_layout.addWidget(contact)
        card_layout.addSpacing(8)
        card_layout.addWidget(support_title)
        card_layout.addWidget(support_desc)
        card_layout.addWidget(qr_label, 0, Qt.AlignCenter)
        card_layout.addStretch(1)
        card_layout.addWidget(close_btn)

        root.addWidget(card)


class ConversionWorker(QObject):
    """Run conversion in background thread."""

    progress = Signal(int, int)
    status = Signal(str)
    finished = Signal(object)
    failed = Signal(str)
    cancelled = Signal()

    def __init__(
        self,
        feature_mode: str,
        input_path: str,
        output_dir: str,
        image_format: str,
        quality_level: str,
        pdf_mode: str,
    ) -> None:
        super().__init__()
        self.feature_mode = feature_mode
        self.input_path = input_path
        self.output_dir = output_dir
        self.image_format = image_format
        self.quality_level = quality_level
        self.pdf_mode = pdf_mode
        self._cancel_requested = False

    def request_cancel(self) -> None:
        self._cancel_requested = True

    def is_cancelled(self) -> bool:
        return self._cancel_requested

    @staticmethod
    def _build_unique_path(input_path: str, output_dir: str, extension: str) -> Path:
        source = Path(input_path)
        out_dir = Path(output_dir)
        candidate = out_dir / f"{source.stem}{extension}"
        if not candidate.exists():
            return candidate

        index = 1
        while True:
            candidate = out_dir / f"{source.stem}_{index}{extension}"
            if not candidate.exists():
                return candidate
            index += 1

    def run(self) -> None:
        try:
            if self.feature_mode == "word_to_images":
                result = convert_word_to_images(
                    word_path=self.input_path,
                    output_dir=self.output_dir,
                    image_format=self.image_format,
                    quality_level=self.quality_level,
                    status_callback=self.status.emit,
                    progress_callback=self.progress.emit,
                    is_cancelled=self.is_cancelled,
                )
                self.finished.emit(result)
                return

            if self.feature_mode == "word_to_pdf":
                output_pdf = self._build_unique_path(self.input_path, self.output_dir, ".pdf")
                self.status.emit("正在转换 Word 到 PDF")
                self.progress.emit(30, 100)
                result_path = convert_word_to_pdf(self.input_path, str(output_pdf))
                self.progress.emit(100, 100)
                self.status.emit("转换完成")
                self.finished.emit(result_path)
                return

            output_docx = self._build_unique_path(self.input_path, self.output_dir, ".docx")

            if self.pdf_mode == "fast":
                self.status.emit("正在快速转换 PDF 到 Word")
                self.progress.emit(20, 100)
                result_path = pdf_to_word_fast(self.input_path, str(output_docx))
                self.progress.emit(100, 100)
                self.status.emit("转换完成")
                self.finished.emit(result_path)
                return

            result_path = pdf_to_word_ocr(
                pdf_path=self.input_path,
                output_docx_path=str(output_docx),
                status_callback=self.status.emit,
                progress_callback=self.progress.emit,
            )
            self.finished.emit(result_path)
        except ConversionCancelledError:
            self.cancelled.emit()
        except Exception as exc:
            self.failed.emit(str(exc))


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("DocShot 文档快照")
        self.resize(920, 680)
        self.setMinimumSize(860, 600)

        self.input_path: str = ""
        self.output_dir: str = ""

        self.worker_thread: QThread | None = None
        self.worker: ConversionWorker | None = None

        self.feature_combo = NoWheelComboBox()
        self.feature_combo.addItem("Word 转图片", "word_to_images")
        self.feature_combo.addItem("Word 转 PDF", "word_to_pdf")
        self.feature_combo.addItem("PDF 转 Word", "pdf_to_word")
        self.feature_combo.currentIndexChanged.connect(self.on_feature_mode_changed)

        self.input_label = self._section_label("选择 Word 文件")
        self.input_path_edit = QLineEdit()
        self.input_path_edit.setReadOnly(True)

        self.output_dir_edit = QLineEdit()
        self.output_dir_edit.setReadOnly(True)
        self.output_dir_edit.setPlaceholderText("请选择导出目录")

        self.file_browse_btn = QPushButton("浏览")
        self.file_browse_btn.setFixedWidth(96)
        self.file_browse_btn.clicked.connect(self.select_input_file)

        self.format_combo = NoWheelComboBox()
        self.format_combo.addItem("PNG", "png")
        self.format_combo.addItem("JPG", "jpg")

        self.quality_combo = NoWheelComboBox()
        self.quality_combo.addItem("普通", "normal")
        self.quality_combo.addItem("高清", "high")
        self.quality_combo.addItem("超清", "ultra")
        self.quality_combo.setCurrentIndex(1)

        self.pdf_mode_combo = NoWheelComboBox()
        self.pdf_mode_combo.addItem("快速模式：适合文字型 PDF", "fast")
        self.pdf_mode_combo.addItem("OCR 模式：适合扫描件 PDF", "ocr")

        self.ocr_hint_label = QLabel("OCR 模式适合扫描件，速度较慢，排版还原有限。")
        self.ocr_hint_label.setObjectName("HintLabel")
        self.ocr_hint_label.setWordWrap(True)

        self.word_params_frame = QFrame()
        self.word_params_frame.setFrameShape(QFrame.NoFrame)
        word_params_layout = QHBoxLayout(self.word_params_frame)
        word_params_layout.setContentsMargins(0, 0, 0, 0)
        word_params_layout.setSpacing(16)

        format_col = QVBoxLayout()
        format_col.setSpacing(8)
        format_label = QLabel("图片格式")
        format_label.setObjectName("HintLabel")
        format_col.addWidget(format_label)
        self.format_combo.setMinimumWidth(180)
        self.format_combo.setMaximumWidth(260)
        format_col.addWidget(self.format_combo, 0, Qt.AlignLeft)

        quality_col = QVBoxLayout()
        quality_col.setSpacing(8)
        quality_label = QLabel("清晰度")
        quality_label.setObjectName("HintLabel")
        quality_col.addWidget(quality_label)
        self.quality_combo.setMinimumWidth(180)
        self.quality_combo.setMaximumWidth(260)
        quality_col.addWidget(self.quality_combo, 0, Qt.AlignLeft)

        word_params_layout.addLayout(format_col, 1)
        word_params_layout.addLayout(quality_col, 1)
        word_params_layout.addStretch()

        self.pdf_mode_frame = QFrame()
        self.pdf_mode_frame.setFrameShape(QFrame.NoFrame)
        pdf_layout = QVBoxLayout(self.pdf_mode_frame)
        pdf_layout.setContentsMargins(0, 0, 0, 0)
        pdf_layout.setSpacing(8)
        pdf_label = QLabel("转换模式")
        pdf_label.setObjectName("HintLabel")
        self.pdf_mode_combo.setMinimumWidth(360)
        self.pdf_mode_combo.setMaximumWidth(520)
        pdf_layout.addWidget(pdf_label)
        pdf_layout.addWidget(self.pdf_mode_combo, 0, Qt.AlignLeft)
        pdf_layout.addWidget(self.ocr_hint_label)

        self.start_btn = QPushButton("开始转换")
        self.start_btn.setObjectName("PrimaryButton")
        self.start_btn.clicked.connect(self.start_conversion)

        self.about_btn = QPushButton("关于")
        self.about_btn.setObjectName("AboutButton")
        self.about_btn.clicked.connect(self.show_about_dialog)

        self.open_output_btn = QPushButton("打开输出目录")
        self.open_output_btn.clicked.connect(self.open_output_dir)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        self.status_label = QLabel("状态：就绪")
        self.copyright_label = QLabel("DocShot 文档快照 · 零一工作室出品")
        self.copyright_label.setObjectName("CopyrightLabel")
        self.copyright_label.setAlignment(Qt.AlignCenter)

        self.init_ui()
        self.apply_style()
        self.on_feature_mode_changed()

    def current_feature_mode(self) -> str:
        return str(self.feature_combo.currentData())

    def init_ui(self) -> None:
        root = QWidget(self)
        self.setCentralWidget(root)

        page = QVBoxLayout(root)
        page.setContentsMargins(24, 20, 24, 20)
        page.setSpacing(12)

        page.addWidget(self.create_header())

        main_row = QHBoxLayout()
        main_row.setSpacing(14)
        main_row.addWidget(self.create_main_card(), 3)
        main_row.addWidget(self.create_info_card(), 2)
        page.addLayout(main_row, 1)

        page.addWidget(self.create_footer())
        page.addSpacing(12)
        page.addWidget(self.copyright_label)

    def create_header(self) -> QWidget:
        frame = QFrame()
        frame.setObjectName("Card")

        layout = QHBoxLayout(frame)
        layout.setContentsMargins(20, 14, 20, 14)
        layout.setSpacing(12)

        left = QVBoxLayout()
        left.setSpacing(4)
        title = QLabel("DocShot")
        title.setObjectName("TitleLabel")
        subtitle = QLabel("本地文档转换工具")
        subtitle.setObjectName("SubtitleLabel")
        left.addWidget(title)
        left.addWidget(subtitle)

        tag = QLabel("Local · Private · Fast")
        tag.setObjectName("TagLabel")
        tag.setAlignment(Qt.AlignCenter)

        right = QVBoxLayout()
        right.setSpacing(8)
        right.setAlignment(Qt.AlignTop | Qt.AlignRight)
        right.addWidget(tag, 0, Qt.AlignRight)
        right.addWidget(self.about_btn, 0, Qt.AlignRight)

        layout.addLayout(left, 1)
        layout.addLayout(right, 0)
        return frame

    def create_main_card(self) -> QWidget:
        frame = QFrame()
        frame.setObjectName("Card")

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(20, 18, 20, 18)
        content_layout.setSpacing(14)

        content_layout.addWidget(self._section_label("功能选择"))
        feature_row = QHBoxLayout()
        feature_row.setSpacing(10)
        self.feature_combo.setMinimumWidth(240)
        feature_row.addWidget(self.feature_combo, 0, Qt.AlignLeft)
        feature_row.addStretch()
        content_layout.addLayout(feature_row)

        content_layout.addSpacing(2)
        content_layout.addWidget(self.input_label)
        file_row = QHBoxLayout()
        file_row.setSpacing(10)
        file_row.addWidget(self.input_path_edit, 1)
        file_row.addWidget(self.file_browse_btn)
        content_layout.addLayout(file_row)

        content_layout.addSpacing(2)
        content_layout.addWidget(self._section_label("导出位置"))
        out_row = QHBoxLayout()
        out_row.setSpacing(10)
        out_browse = QPushButton("浏览")
        out_browse.setFixedWidth(96)
        out_browse.clicked.connect(self.select_output_dir)
        out_row.addWidget(self.output_dir_edit, 1)
        out_row.addWidget(out_browse)
        content_layout.addLayout(out_row)

        content_layout.addSpacing(2)
        content_layout.addWidget(self._section_label("转换参数"))
        content_layout.addWidget(self.word_params_frame)
        content_layout.addWidget(self.pdf_mode_frame)

        content_layout.addSpacing(10)
        content_layout.addWidget(self.start_btn)

        content_layout.addStretch(1)
        scroll.setWidget(content)
        layout.addWidget(scroll)

        return frame

    def create_info_card(self) -> QWidget:
        frame = QFrame()
        frame.setObjectName("Card")

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(10)

        flow = QLabel("Word ⇄ PDF ⇄ Image")
        flow.setObjectName("SectionLabel")

        p1 = QLabel("• 本地处理，文件不上传")
        p2 = QLabel("• 支持 Word 转图片、Word 转 PDF、PDF 转 Word")
        p3 = QLabel("• OCR 模式适合扫描件 PDF")
        for item in (p1, p2, p3):
            item.setObjectName("HintLabel")
            item.setWordWrap(True)

        tip_title = QLabel("提示")
        tip_title.setObjectName("SectionLabel")
        tip = QLabel("OCR 模式速度较慢，且复杂版式可能无法完整还原")
        tip.setWordWrap(True)
        tip.setObjectName("HintLabel")

        layout.addWidget(flow)
        layout.addSpacing(4)
        layout.addWidget(p1)
        layout.addWidget(p2)
        layout.addWidget(p3)
        layout.addSpacing(10)
        layout.addWidget(tip_title)
        layout.addWidget(tip)
        layout.addStretch()
        return frame

    def create_footer(self) -> QWidget:
        frame = QFrame()
        frame.setObjectName("Card")

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(6)

        top_row = QHBoxLayout()
        top_row.setSpacing(12)
        top_row.addWidget(self.status_label, 1)
        top_row.addWidget(self.open_output_btn, 0)

        layout.addLayout(top_row)
        layout.addWidget(self.progress_bar)
        return frame

    def apply_style(self) -> None:
        self.setStyleSheet(APP_STYLE)

    @staticmethod
    def _section_label(text: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName("SectionLabel")
        return label

    def on_feature_mode_changed(self) -> None:
        self.input_path = ""
        self.input_path_edit.clear()

        mode = self.current_feature_mode()
        if mode == "word_to_images":
            self.input_label.setText("选择 Word 文件")
            self.input_path_edit.setPlaceholderText("请选择 .doc 或 .docx 文件")
            self.word_params_frame.setVisible(True)
            self.pdf_mode_frame.setVisible(False)
        elif mode == "word_to_pdf":
            self.input_label.setText("选择 Word 文件")
            self.input_path_edit.setPlaceholderText("请选择 .doc 或 .docx 文件")
            self.word_params_frame.setVisible(False)
            self.pdf_mode_frame.setVisible(False)
        else:
            self.input_label.setText("选择 PDF 文件")
            self.input_path_edit.setPlaceholderText("请选择 .pdf 文件")
            self.word_params_frame.setVisible(False)
            self.pdf_mode_frame.setVisible(True)

    def select_input_file(self) -> None:
        mode = self.current_feature_mode()
        if mode == "word_to_images" or mode == "word_to_pdf":
            path, _ = QFileDialog.getOpenFileName(
                self,
                "选择 Word 文件",
                "",
                "Word 文件 (*.doc *.docx)",
            )
        else:
            path, _ = QFileDialog.getOpenFileName(
                self,
                "选择 PDF 文件",
                "",
                "PDF 文件 (*.pdf)",
            )

        if path:
            self.input_path = path
            self.input_path_edit.setText(path)

    def select_output_dir(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if path:
            self.output_dir = path
            self.output_dir_edit.setText(path)

    def start_conversion(self) -> None:
        mode = self.current_feature_mode()

        if not self.input_path:
            if mode == "pdf_to_word":
                msg = "请先选择 PDF 文件。"
            else:
                msg = "请先选择 Word 文件。"
            QMessageBox.warning(self, "提示", msg)
            return

        if not self.output_dir:
            QMessageBox.warning(self, "提示", "请先选择输出目录。")
            return

        input_file = Path(self.input_path)
        if not input_file.exists():
            QMessageBox.warning(self, "提示", "所选文件不存在，请重新选择。")
            return

        suffix = input_file.suffix.lower()
        if mode == "pdf_to_word" and suffix != ".pdf":
            QMessageBox.warning(self, "提示", "PDF 转 Word 仅支持 .pdf 文件。")
            return

        if mode in {"word_to_images", "word_to_pdf"} and suffix not in {".doc", ".docx"}:
            QMessageBox.warning(self, "提示", "该功能仅支持 .doc/.docx 文件。")
            return

        self.start_btn.setEnabled(False)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.status_label.setText("状态：准备中...")

        self.worker_thread = QThread(self)
        self.worker = ConversionWorker(
            feature_mode=mode,
            input_path=self.input_path,
            output_dir=self.output_dir,
            image_format=str(self.format_combo.currentData()),
            quality_level=str(self.quality_combo.currentData()),
            pdf_mode=str(self.pdf_mode_combo.currentData()),
        )
        self.worker.moveToThread(self.worker_thread)

        self.worker_thread.started.connect(self.worker.run)
        self.worker.status.connect(self.on_status_update)
        self.worker.progress.connect(self.on_progress_update)
        self.worker.finished.connect(self.on_conversion_finished)
        self.worker.failed.connect(self.on_conversion_failed)
        self.worker.cancelled.connect(self.on_conversion_cancelled)

        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.failed.connect(self.worker_thread.quit)
        self.worker.cancelled.connect(self.worker_thread.quit)
        self.worker_thread.finished.connect(self.cleanup_thread)

        self.worker_thread.start()

    def open_output_dir(self) -> None:
        if not self.output_dir:
            QMessageBox.information(self, "提示", "请先选择输出目录。")
            return
        path = Path(self.output_dir)
        if not path.exists():
            QMessageBox.warning(self, "提示", "输出目录不存在。")
            return
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))

    def on_status_update(self, message: str) -> None:
        self.status_label.setText(f"状态：{message}")

    def on_progress_update(self, current: int, total: int) -> None:
        self.progress_bar.setRange(0, max(total, 1))
        self.progress_bar.setValue(current)

    def on_conversion_finished(self, result: object) -> None:
        self.status_label.setText("状态：转换完成")
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100)
        self.start_btn.setEnabled(True)

        mode = self.current_feature_mode()
        if mode == "word_to_images":
            image_paths = result if isinstance(result, list) else []
            QMessageBox.information(
                self,
                "转换完成",
                f"转换完成，共导出 {len(image_paths)} 张图片。",
            )
        elif mode == "word_to_pdf":
            output_path = str(result)
            QMessageBox.information(
                self,
                "转换完成",
                f"转换完成，PDF 文件已生成：\n{output_path}",
            )
        else:
            output_path = str(result)
            QMessageBox.information(
                self,
                "转换完成",
                f"转换完成，Word 文件已生成：\n{output_path}",
            )

    def on_conversion_failed(self, error_message: str) -> None:
        self.status_label.setText("状态：转换失败")
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.start_btn.setEnabled(True)
        QMessageBox.critical(self, "转换失败", error_message)

    def on_conversion_cancelled(self) -> None:
        self.status_label.setText("状态：已取消")
        self.start_btn.setEnabled(True)
        QMessageBox.information(self, "已取消", "转换已取消。")

    def show_about_dialog(self) -> None:
        dialog = AboutDialog(self)
        dialog.exec()

    def cleanup_thread(self) -> None:
        if self.worker is not None:
            self.worker.deleteLater()
            self.worker = None
        if self.worker_thread is not None:
            self.worker_thread.deleteLater()
            self.worker_thread = None
