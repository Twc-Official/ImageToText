import sys
import pytesseract
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QTextEdit, QVBoxLayout, QFileDialog
)
from PyQt6.QtGui import QPixmap, QPainter, QColor, QPen, QGuiApplication
from PyQt6.QtCore import Qt, QRect, QPoint
from PIL import Image
import tempfile

class ScreenCapture(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Text Capture Tool")
        self.setFixedSize(600, 400)
        self.setStyleSheet("""
            QWidget {
                background-color: #121212;
                color: #ffffff;
                font-family: 'Segoe UI', sans-serif;
                font-size: 14px;
            }
            QPushButton {
                background-color: #1f1f1f;
                border: 1px solid #3c3c3c;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #333333;
            }
            QTextEdit {
                background-color: #1f1f1f;
                border: 1px solid #3c3c3c;
                border-radius: 8px;
                padding: 10px;
            }
        """)

        layout = QVBoxLayout()

        self.capture_button = QPushButton("Capture Text")
        self.capture_button.clicked.connect(self.start_capture)
        layout.addWidget(self.capture_button)

        self.output = QTextEdit()
        self.output.setPlaceholderText("Captured text will appear here...")
        layout.addWidget(self.output)

        self.setLayout(layout)

    def start_capture(self):
        self.hide()
        self.capture_window = CaptureOverlay(self.ocr_finished)
        self.capture_window.showFullScreen()

    def ocr_finished(self, image):
        self.show()
        if image:
            temp_path = tempfile.NamedTemporaryFile(suffix=".png", delete=False).name
            image.save(temp_path)
            text = pytesseract.image_to_string(Image.open(temp_path))
            self.output.setPlainText(text)
        else:
            self.output.setPlainText("Capture canceled.")

class CaptureOverlay(QWidget):
    def __init__(self, callback):
        super().__init__()
        self.start_point = QPoint()
        self.end_point = QPoint()
        self.selection_rect = QRect()
        self.callback = callback
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
        self.end_point = event.position().toPoint()
        self.update()
        rect = QRect(self.start_point, self.end_point).normalized()
        screen = QGuiApplication.primaryScreen()
        screenshot = screen.grabWindow(0, rect.x(), rect.y(), rect.width(), rect.height())
        if screenshot.isNull():
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
    window = ScreenCapture()
    window.show()
    sys.exit(app.exec())
