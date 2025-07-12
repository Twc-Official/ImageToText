import sys
import os
import pytesseract
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QTextEdit, QVBoxLayout,
    QFileDialog, QTabWidget, QLabel, QHBoxLayout, QMessageBox,
    QComboBox, QLineEdit, QFormLayout, QGroupBox, QStyleFactory
)
from PyQt6.QtGui import (
    QPixmap, QPainter, QColor, QPen, QGuiApplication, QIcon, QAction
)
from PyQt6.QtCore import Qt, QRect, QPoint, QTimer
from PIL import Image
import tempfile
import subprocess
import shutil
import platform


# --- Check if Tesseract is installed ---
def detect_tesseract():
    """
    Returns either:
        (True, tesseract_path) if found
        (False, None) if not found
    """
    # Check common Windows locations first
    if platform.system() == "Windows":
        default_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"
        ]
        for p in default_paths:
            if os.path.exists(p):
                return True, p

    # Check if callable in PATH
    try:
        output = subprocess.check_output(["tesseract", "--version"], stderr=subprocess.STDOUT)
        return True, "tesseract"
    except Exception:
        return False, None

# --- Toast Notification Widget ---
class Toast(QWidget):
    def __init__(self, message, duration=2000):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("""
            QLabel {
                background-color: #333333;
                color: white;
                padding: 10px;
                border-radius: 8px;
                font-size: 13px;
            }
        """)
        layout = QVBoxLayout()
        label = QLabel(message)
        layout.addWidget(label)
        self.setLayout(layout)
        self.adjustSize()
        QTimer.singleShot(duration, self.close)

# --- Main UI ---
class TextCaptureApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Text Capture Tool v2")
        self.setWindowIcon(QIcon.fromTheme("edit-copy"))
        self.setMinimumSize(700, 500)

        # Tesseract check
        self.tesseract_found, self.tesseract_path = detect_tesseract()
        if self.tesseract_found:
            pytesseract.pytesseract.tesseract_cmd = self.tesseract_path
        else:
            QMessageBox.critical(
                self,
                "Tesseract Not Found",
                "Tesseract-OCR is not installed or not on your PATH.\n\n"
                "Please install it from:\nhttps://github.com/UB-Mannheim/tesseract/wiki"
            )
            self.close()

        self.ocr_lang = "eng"

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.TabPosition.West)
        self.tabs.setStyleSheet("""
            QTabBar::tab {
                background: #1f1f1f;
                color: white;
                padding: 12px;
                margin: 2px;
                border-radius: 8px;
            }
            QTabBar::tab:selected {
                background: #333333;
            }
        """)

        self.tabs.addTab(self.build_capture_tab(), "Capture")
        self.tabs.addTab(self.build_settings_tab(), "Settings")
        self.tabs.addTab(self.build_about_tab(), "About")

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)

    def build_capture_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        btns = QHBoxLayout()
        self.capture_btn = QPushButton("Capture Text")
        self.capture_btn.clicked.connect(self.start_capture)
        btns.addWidget(self.capture_btn)

        self.copy_btn = QPushButton("Copy to Clipboard")
        self.copy_btn.clicked.connect(self.copy_text)
        btns.addWidget(self.copy_btn)

        self.save_btn = QPushButton("Save to File")
        self.save_btn.clicked.connect(self.save_text)
        btns.addWidget(self.save_btn)

        layout.addLayout(btns)

        self.text_output = QTextEdit()
        self.text_output.setPlaceholderText("Captured text will appear here...")
        layout.addWidget(self.text_output)

        tab.setLayout(layout)
        return tab

    def build_settings_tab(self):
        tab = QWidget()
        layout = QFormLayout()

        # OCR Language
        self.lang_input = QComboBox()
        self.lang_input.addItems(["eng", "deu", "fra", "spa"])
        self.lang_input.setCurrentText(self.ocr_lang)
        self.lang_input.currentTextChanged.connect(self.change_lang)

        # Tesseract Path
        self.path_input = QLineEdit(self.tesseract_path or "")
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_tesseract)

        path_layout = QHBoxLayout()
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(browse_btn)

        layout.addRow("OCR Language:", self.lang_input)
        layout.addRow("Tesseract Path:", path_layout)

        tab.setLayout(layout)
        return tab

    def build_about_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        mainlabel = QLabel(
            "Text Capture Tool v2\n"
            "Built with PyQt6 + Tesseract OCR\n\n"
            "© 2025 Twc_Official"
        )
        mainlabel.setStyleSheet("color: #aaaaaa; font-size: 13px;")

        tesseract_label = QLabel(
            "\n\nPlease support Tesseract as without it, this project would not exist!\n"
            "The link to their Github is Below:\n"
        )
        tesseract_label.setStyleSheet("color: #aaaaaa; font-size: 13px;")

        ### Indentation here because I like my code to be neat

        tesseract_edit = QLineEdit("https://github.com/UB-Mannheim/tesseract/wiki")
        tesseract_edit.setReadOnly(True)
        tesseract_edit.setStyleSheet("""
            QLineEdit {
                background-color: #1f1f1f;
                color: #61dafb;
                border: none;
                font-size: 13px;
                padding: 4px;
            }
        """)

        github_edit = QLineEdit("https://placeholder.com")
        ### Placeholder because the Repo does not exist yet
        github_edit.setReadOnly(True)
        github_edit.setStyleSheet("""
            QLineEdit {
                background-color: #1f1f1f;
                color: #61dafb;
                border: none;
                font-size: 13px;
                padding: 4px;
            }
        """)

        layout.addWidget(mainlabel)
        layout.addWidget(github_edit)
        layout.addWidget(tesseract_label)
        layout.addWidget(tesseract_edit)
        layout.addStretch()
        tab.setLayout(layout)
        return tab


    def browse_tesseract(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Tesseract Executable", "", "Executable (*.exe *.bin)")
        if path:
            self.tesseract_path = path
            pytesseract.pytesseract.tesseract_cmd = self.tesseract_path
            self.path_input.setText(path)
            self.show_toast("Tesseract path updated.")

    def change_lang(self, lang):
        self.ocr_lang = lang
        self.show_toast(f"OCR language set to: {lang}")

    def start_capture(self):
        self.hide()
        self.overlay = CaptureOverlay(self.ocr_complete, self.show_toast)
        self.overlay.showFullScreen()

    def ocr_complete(self, image):
        self.show()
        if image:
            temp_path = tempfile.NamedTemporaryFile(suffix=".png", delete=False).name
            image.save(temp_path)
            try:
                text = pytesseract.image_to_string(
                    Image.open(temp_path),
                    lang=self.ocr_lang
                )
            except Exception as e:
                text = f"OCR Error: {e}"
            self.text_output.setPlainText(text)
            self.show_toast("Capture complete!")
        else:
            self.show_toast("Capture cancelled.")

    def copy_text(self):
        text = self.text_output.toPlainText()
        if text:
            QApplication.clipboard().setText(text)
            self.show_toast("Text copied to clipboard.")
        else:
            self.show_toast("No text to copy.")

    def save_text(self):
        text = self.text_output.toPlainText()
        if not text:
            self.show_toast("No text to save.")
            return
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Text", "", "Text Files (*.txt)"
        )
        if filename:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(text)
            self.show_toast(f"Saved to {filename}")

    def show_toast(self, message):
        toast = Toast(message)
        toast.move(self.geometry().center() - toast.rect().center())
        toast.show()

# --- Screen Capture Overlay ---
class CaptureOverlay(QWidget):
    def __init__(self, callback, notify_callback):
        super().__init__()
        self.start_point = QPoint()
        self.end_point = QPoint()
        self.callback = callback
        self.notify_callback = notify_callback
        self.setWindowOpacity(0.3)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet("background-color: black;")

    def mousePressEvent(self, event):
        self.start_point = event.position().toPoint()
        self.end_point = self.start_point
        self.update()

    def mouseMoveEvent(self, event):
        self.end_point = event.position().toPoint()
        self.update()

    def mouseReleaseEvent(self, event):
        rect = QRect(self.start_point, self.end_point).normalized()
        screen = QGuiApplication.primaryScreen()
        screenshot = screen.grabWindow(0, rect.x(), rect.y(), rect.width(), rect.height())
        if screenshot.isNull():
            self.notify_callback("No region selected.")
            self.callback(None)
        else:
            image = screenshot.toImage()
            buffer = image.bits().asstring(image.sizeInBytes())
            img = Image.frombytes(
                "RGBA",
                (image.width(), image.height()),
                buffer,
                "raw",
                "BGRA"
            )
            self.callback(img)
        self.close()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QPen(QColor("red"), 2))
        painter.drawRect(QRect(self.start_point, self.end_point))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Dark Fusion theme
    QApplication.setStyle(QStyleFactory.create("Fusion"))
    window = TextCaptureApp()
    window.show()
    sys.exit(app.exec())
