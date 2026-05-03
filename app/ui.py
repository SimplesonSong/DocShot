"""Modernized PySide6 UI for DocShot."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QObject, QThread, Qt, QUrl, Signal
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.converter import convert_word_to_images
from src.docshot import ConversionCancelledError

APP_STYLE = """
QWidget {
    background: #f6f8fc;
    color: #1f2937;
    font-family: "Segoe UI", "Microsoft YaHei UI", "Microsoft YaHei";
    font-size: 13px;
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
QLabel#SectionLabel {
    font-size: 14px;
    font-weight: 600;
    color: #111827;
}
QLabel#HintLabel {
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
"""


class ConversionWorker(QObject):
    """Run conversion in background thread."""

    progress = Signal(int, int)
    status = Signal(str)
    finished = Signal(list)
    failed = Signal(str)
    cancelled = Signal()

    def __init__(
        self,
        word_path: str,
        output_dir: str,
        image_format: str,
        quality_level: str,
    ) -> None:
        super().__init__()
        self.word_path = word_path
        self.output_dir = output_dir
        self.image_format = image_format
        self.quality_level = quality_level
        self._cancel_requested = False

    def request_cancel(self) -> None:
        self._cancel_requested = True

    def is_cancelled(self) -> bool:
        return self._cancel_requested

    def run(self) -> None:
        try:
            image_paths = convert_word_to_images(
                word_path=self.word_path,
                output_dir=self.output_dir,
                image_format=self.image_format,
                quality_level=self.quality_level,
                status_callback=self.status.emit,
                progress_callback=self.progress.emit,
                is_cancelled=self.is_cancelled,
            )
        except ConversionCancelledError:
            self.cancelled.emit()
            return
        except Exception as exc:
            self.failed.emit(str(exc))
            return

        self.finished.emit(image_paths)


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("DocShot 文档快照")
        self.resize(920, 680)
        self.setMinimumSize(860, 600)

        self.word_path: str = ""
        self.output_dir: str = ""

        self.worker_thread: QThread | None = None
        self.worker: ConversionWorker | None = None

        self.word_path_edit = QLineEdit()
        self.word_path_edit.setReadOnly(True)
        self.word_path_edit.setPlaceholderText("请选择 .doc 或 .docx 文件")

        self.output_dir_edit = QLineEdit()
        self.output_dir_edit.setReadOnly(True)
        self.output_dir_edit.setPlaceholderText("请选择导出目录")

        self.format_combo = QComboBox()
        self.format_combo.addItem("PNG", "png")
        self.format_combo.addItem("JPG", "jpg")

        self.quality_combo = QComboBox()
        self.quality_combo.addItem("普通", "normal")
        self.quality_combo.addItem("高清", "high")
        self.quality_combo.addItem("超清", "ultra")
        self.quality_combo.setCurrentIndex(1)

        self.start_btn = QPushButton("开始转换")
        self.start_btn.setObjectName("PrimaryButton")
        self.start_btn.clicked.connect(self.start_conversion)

        self.cancel_btn = QPushButton("取消转换")
        self.cancel_btn.clicked.connect(self.cancel_conversion)
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.setVisible(False)

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
        self.center_window()

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
        subtitle = QLabel("本地 Word 转高清图片工具")
        subtitle.setObjectName("SubtitleLabel")
        left.addWidget(title)
        left.addWidget(subtitle)

        tag = QLabel("Local · Private · Fast")
        tag.setObjectName("TagLabel")
        tag.setAlignment(Qt.AlignCenter)

        layout.addLayout(left, 1)
        layout.addWidget(tag, 0, Qt.AlignTop)
        return frame

    def create_main_card(self) -> QWidget:
        frame = QFrame()
        frame.setObjectName("Card")

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(12)

        layout.addWidget(self._section_label("选择 Word 文件"))
        word_row = QHBoxLayout()
        word_row.setSpacing(10)
        word_browse = QPushButton("浏览")
        word_browse.setFixedWidth(96)
        word_browse.clicked.connect(self.select_word_file)
        word_row.addWidget(self.word_path_edit, 1)
        word_row.addWidget(word_browse)
        layout.addLayout(word_row)

        layout.addSpacing(0)
        layout.addWidget(self._section_label("导出位置"))
        out_row = QHBoxLayout()
        out_row.setSpacing(10)
        out_browse = QPushButton("浏览")
        out_browse.setFixedWidth(96)
        out_browse.clicked.connect(self.select_output_dir)
        out_row.addWidget(self.output_dir_edit, 1)
        out_row.addWidget(out_browse)
        layout.addLayout(out_row)

        layout.addSpacing(0)
        layout.addWidget(self._section_label("导出参数"))
        param_row = QHBoxLayout()
        param_row.setSpacing(16)

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

        param_row.addLayout(format_col, 1)
        param_row.addLayout(quality_col, 1)
        param_row.addStretch()
        layout.addSpacing(0)
        layout.addLayout(param_row)
        layout.addSpacing(2)

        layout.addSpacing(2)
        layout.addWidget(self.start_btn)
        if self.cancel_btn.isVisible():
            layout.addWidget(self.cancel_btn)

        return frame

    def create_info_card(self) -> QWidget:
        frame = QFrame()
        frame.setObjectName("Card")

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(10)

        flow = QLabel("Word → PDF → Image")
        flow.setObjectName("SectionLabel")

        p1 = QLabel("• 本地处理，文件不上传")
        p2 = QLabel("• 高清导出，适合论文/合同/简历")
        p3 = QLabel("• 一页一图，方便分享和归档")
        for item in (p1, p2, p3):
            item.setObjectName("HintLabel")

        tip_title = QLabel("提示")
        tip_title.setObjectName("SectionLabel")
        tip = QLabel("首次使用请确保电脑已安装 Microsoft Word")
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

    def center_window(self) -> None:
        screen = self.screen() or self.windowHandle().screen() if self.windowHandle() else None
        if screen is None:
            return
        geo = screen.availableGeometry()
        x = geo.x() + (geo.width() - self.width()) // 2
        y = geo.y() + (geo.height() - self.height()) // 2
        self.move(x, y)

    @staticmethod
    def _section_label(text: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName("SectionLabel")
        return label

    def select_word_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "选择 Word 文件",
            "",
            "Word 文件 (*.doc *.docx)",
        )
        if path:
            self.word_path = path
            self.word_path_edit.setText(path)

    def select_output_dir(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if path:
            self.output_dir = path
            self.output_dir_edit.setText(path)

    def start_conversion(self) -> None:
        if not self.word_path:
            QMessageBox.warning(self, "提示", "请先选择 Word 文件。")
            return
        if not self.output_dir:
            QMessageBox.warning(self, "提示", "请先选择输出目录。")
            return
        if not Path(self.word_path).exists():
            QMessageBox.warning(self, "提示", "所选 Word 文件不存在，请重新选择。")
            return

        self.start_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("状态：准备中...")

        self.worker_thread = QThread(self)
        self.worker = ConversionWorker(
            word_path=self.word_path,
            output_dir=self.output_dir,
            image_format=self.format_combo.currentData(),
            quality_level=self.quality_combo.currentData(),
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

    def cancel_conversion(self) -> None:
        if self.worker is not None:
            self.worker.request_cancel()
            self.cancel_btn.setEnabled(False)
            self.status_label.setText("状态：正在取消...")

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

    def on_conversion_finished(self, image_paths: list[str]) -> None:
        self.status_label.setText("状态：转换完成")
        self.progress_bar.setValue(100)
        self.start_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        QMessageBox.information(
            self,
            "转换完成",
            f"转换完成，共导出 {len(image_paths)} 张图片。",
        )

    def on_conversion_failed(self, error_message: str) -> None:
        self.status_label.setText("状态：转换失败")
        self.progress_bar.setValue(0)
        self.start_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        QMessageBox.critical(self, "转换失败", error_message)

    def on_conversion_cancelled(self) -> None:
        self.status_label.setText("状态：已取消")
        self.start_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        QMessageBox.information(self, "已取消", "转换已取消。")

    def cleanup_thread(self) -> None:
        if self.worker is not None:
            self.worker.deleteLater()
            self.worker = None
        if self.worker_thread is not None:
            self.worker_thread.deleteLater()
            self.worker_thread = None
