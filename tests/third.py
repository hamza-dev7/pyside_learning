import sys

from PySide6.QtWidgets import (
    QApplication,
    QGroupBox,
    QLabel,
    QLineEdit,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("My App")

        self.label = QLabel()

        self.input = QLineEdit()
        self.input.textChanged.connect(self.label.setText)

        box1 = QGroupBox("Editor")
        box2 = QGroupBox("Output")
        box1_layout = QVBoxLayout()
        box2_layout = QVBoxLayout()
        box1_layout.addWidget(self.input)
        box2_layout.addWidget(self.label)
        box1.setLayout(box1_layout)
        box2.setLayout(box2_layout)

        layout = QVBoxLayout()
        layout.addWidget(box1)
        layout.addWidget(box2)

        layout.setStretch(0, 1)
        layout.setStretch(1, 9)

        container = QWidget()
        container.setLayout(layout)

        self.setCentralWidget(container)

app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()
