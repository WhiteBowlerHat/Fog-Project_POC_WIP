import sys
from PySide6 import QtWidgets
from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt,  QSignalMapper)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QGroupBox, QLabel, QLineEdit,
    QPushButton, QSizePolicy, QWidget, QFileDialog, QMessageBox)



from main_window_ui2 import Ui_Fog

from fastfog import fog, wind

class MainWindow(QtWidgets.QMainWindow, Ui_Fog):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)

    # Adapt the generated UI to the current protocol
        # any file type can be hidden, not only zip files
        self.ZipFileToEncryptButton.setText("Select File")
        # the size is stored inside the hidden data: decrypting no longer needs it.
        # The field is now an optional nonce (only needed if the metadata was stripped)
        self.DecryptSizeLabel.setText("Nonce :")
        self.DecryptSizeField.setPlaceholderText("optional (read from the images if empty)")

    # Connect button signals to slots
        self.EncryptSizeField.setText("<Run the program to get the size>")
        self.EncryptInputFolderButton.clicked.connect(lambda: self.select_folder("Encrypt Input Folder", self.EncryptInputFolderLabel))
        self.EncryptOutputFolderButton.clicked.connect(lambda: self.select_folder("Encrypt Output Folder", self.EncryptOutputFolderLabel))
        self.DecryptInputFolderButton.clicked.connect(lambda: self.select_folder("Decrypt Input Folder", self.DecryptInputFolderLabel))
        self.DecryptOutputFolderButton.clicked.connect(lambda: self.select_folder("Decrypt Output Folder", self.DecryptOutputFolderLabel))
        self.ZipFileToEncryptButton.clicked.connect(lambda: self.select_file("File To Hide", self.ZipFileToEncryptLabel))
        self.EncryptButton.clicked.connect(lambda: self.encrypt(self.EncryptKeyField.text(), self.ZipFileToEncryptLabel.toPlainText(), self.EncryptInputFolderLabel.toPlainText(), self.EncryptOutputFolderLabel.toPlainText()))
        self.DecryptButton.clicked.connect(lambda: self.decrypt(self.DecryptKeyField.text(), self.DecryptSizeField.text(), self.DecryptInputFolderLabel.toPlainText(), self.DecryptOutputFolderLabel.toPlainText()))

    def select_folder(self, title, labelname):
        folder_path = QFileDialog.getExistingDirectory(self, title)
        if folder_path:
            labelname.setText(folder_path)

    def select_file(self, title, labelname):
        file_path, _ = QFileDialog.getOpenFileName(self, title)
        if file_path:
            labelname.setText(file_path)

    def encrypt(self, key, file, input, output):
        if not key:
            QMessageBox.warning(self, "Fog Project", "Please enter a key.")
            return
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            size, _nonce = fog(key, file.strip(), input.strip(), output.strip())
        except (ValueError, OSError) as exc:
            QMessageBox.critical(self, "Fog Project", str(exc))
            return
        finally:
            QApplication.restoreOverrideCursor()
        self.EncryptSizeField.setText(f"{size} bytes")
        QMessageBox.information(
            self, "Fog Project",
            "Done. Send all the images of the output folder to the receiver, "
            "and give them the key through another channel.")

    def decrypt(self, key, nonce, input, output):
        if not key:
            QMessageBox.warning(self, "Fog Project", "Please enter a key.")
            return
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            path = wind(key, input.strip(), output.strip(), nonce=nonce.strip() or None)
        except (ValueError, OSError) as exc:
            QMessageBox.critical(self, "Fog Project", str(exc))
            return
        finally:
            QApplication.restoreOverrideCursor()
        QMessageBox.information(self, "Fog Project", f"Recovered file written to:\n{path}")

app = QtWidgets.QApplication(sys.argv)

window = MainWindow()
window.show()
app.exec()
