# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'first-ww.ui'
##
## Created by: Qt User Interface Compiler version 6.6.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QGroupBox, QLabel,
    QLineEdit, QPushButton, QSizePolicy, QTextEdit,
    QWidget)

class Ui_Fog(object):
    def setupUi(self, Fog):
        if not Fog.objectName():
            Fog.setObjectName(u"Fog")
        Fog.resize(852, 614)
        
        # Encrypt Section
        self.EnryptBox = QGroupBox(Fog)
        self.EnryptBox.setObjectName(u"EnryptBox")
        self.EnryptBox.setGeometry(QRect(40, 150, 371, 431))
        
        self.EncryptButton = QPushButton(self.EnryptBox)
        self.EncryptButton.setObjectName(u"EncryptButton")
        self.EncryptButton.setGeometry(QRect(100, 370, 151, 24))

        self.EncryptKeyField = QLineEdit(self.EnryptBox)
        self.EncryptKeyField.setObjectName(u"EncryptKeyField")
        self.EncryptKeyField.setGeometry(QRect(30, 60, 231, 22))
        
        self.EncryptKeyLabel = QLabel(self.EnryptBox)
        self.EncryptKeyLabel.setObjectName(u"EncryptKeyLabel")
        self.EncryptKeyLabel.setGeometry(QRect(30, 40, 49, 16))

        self.ZipFileToEncryptButton = QPushButton(self.EnryptBox)
        self.ZipFileToEncryptButton.setObjectName(u"ZipFileToEncryptButton")
        self.ZipFileToEncryptButton.setGeometry(QRect(30, 120, 91, 24))

        self.ZipFileToEncryptLabel = QTextEdit(self.EnryptBox)
        self.ZipFileToEncryptLabel.setObjectName(u"ZipFileToEncryptLabel")
        self.ZipFileToEncryptLabel.setGeometry(QRect(130, 120, 221, 41))
        self.ZipFileToEncryptLabel.setAutoFillBackground(False)
        self.ZipFileToEncryptLabel.setStyleSheet(u"background-color: rgba(255, 255, 255, 0);")
        self.ZipFileToEncryptLabel.setFrameShape(QFrame.NoFrame)
        self.ZipFileToEncryptLabel.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.ZipFileToEncryptLabel.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.ZipFileToEncryptLabel.setLineWrapMode(QTextEdit.NoWrap)
        self.ZipFileToEncryptLabel.setReadOnly(True)
        self.ZipFileToEncryptLabel.setAcceptRichText(False)

        self.EncryptInputFolderButton = QPushButton(self.EnryptBox)
        self.EncryptInputFolderButton.setObjectName(u"EncryptInputFolderButton")
        self.EncryptInputFolderButton.setGeometry(QRect(30, 180, 91, 24))

        self.EncryptInputFolderLabel = QTextEdit(self.EnryptBox)
        self.EncryptInputFolderLabel.setObjectName(u"EncryptInputFolderLabel")
        self.EncryptInputFolderLabel.setGeometry(QRect(130, 180, 221, 41))
        self.EncryptInputFolderLabel.setAutoFillBackground(False)
        self.EncryptInputFolderLabel.setStyleSheet(u"background-color: rgba(255, 255, 255, 0);")
        self.EncryptInputFolderLabel.setFrameShape(QFrame.NoFrame)
        self.EncryptInputFolderLabel.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.EncryptInputFolderLabel.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.EncryptInputFolderLabel.setLineWrapMode(QTextEdit.NoWrap)
        self.EncryptInputFolderLabel.setReadOnly(True)
        self.EncryptInputFolderLabel.setAcceptRichText(False)

        self.EncryptOutputFolderButton = QPushButton(self.EnryptBox)
        self.EncryptOutputFolderButton.setObjectName(u"EncryptOutputFolderButton")
        self.EncryptOutputFolderButton.setGeometry(QRect(30, 240, 91, 24))

        self.EncryptOutputFolderLabel = QTextEdit(self.EnryptBox)
        self.EncryptOutputFolderLabel.setObjectName(u"EncryptOutputFolderLabel")
        self.EncryptOutputFolderLabel.setGeometry(QRect(130, 240, 221, 41))
        self.EncryptOutputFolderLabel.setAutoFillBackground(False)
        self.EncryptOutputFolderLabel.setStyleSheet(u"background-color: rgba(255, 255, 255, 0);")
        self.EncryptOutputFolderLabel.setFrameShape(QFrame.NoFrame)
        self.EncryptOutputFolderLabel.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.EncryptOutputFolderLabel.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.EncryptOutputFolderLabel.setLineWrapMode(QTextEdit.NoWrap)
        self.EncryptOutputFolderLabel.setReadOnly(True)
        self.EncryptOutputFolderLabel.setAcceptRichText(False)

        self.EncryptSizeLabel = QLabel(self.EnryptBox)
        self.EncryptSizeLabel.setObjectName(u"EncryptSizeLabel")
        self.EncryptSizeLabel.setGeometry(QRect(30, 300, 49, 16))
        self.EncryptSizeLabel.setText(QCoreApplication.translate("Fog", u"Size :", None))

        self.EncryptSizeField = QTextEdit(self.EnryptBox)
        self.EncryptSizeField.setObjectName(u"EncryptSizeField")
        self.EncryptSizeField.setGeometry(QRect(130, 300, 221, 41))
        self.EncryptSizeField.setAutoFillBackground(False)
        self.EncryptSizeField.setStyleSheet(u"background-color: rgba(255, 255, 255, 0);")
        self.EncryptSizeField.setFrameShape(QFrame.NoFrame)
        self.EncryptSizeField.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.EncryptSizeField.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.EncryptSizeField.setLineWrapMode(QTextEdit.NoWrap)
        self.EncryptSizeField.setReadOnly(True)
        self.EncryptSizeField.setAcceptRichText(False)

        
        
        # Decrypt Section
        self.DecryptBox = QGroupBox(Fog)
        self.DecryptBox.setObjectName(u"DecryptBox")
        self.DecryptBox.setGeometry(QRect(430, 150, 391, 431))

        self.DecryptButton = QPushButton(self.DecryptBox)
        self.DecryptButton.setObjectName(u"DecryptButton")
        self.DecryptButton.setGeometry(QRect(140, 370, 151, 24))
        
        self.DecryptKeyLabel = QLabel(self.DecryptBox)
        self.DecryptKeyLabel.setObjectName(u"DecryptKeyLabel")
        self.DecryptKeyLabel.setGeometry(QRect(40, 40, 49, 16))

        self.DecryptKeyField = QLineEdit(self.DecryptBox)
        self.DecryptKeyField.setObjectName(u"DecryptKeyField")
        self.DecryptKeyField.setGeometry(QRect(40, 60, 231, 22))

        self.DecryptInputFolderButton = QPushButton(self.DecryptBox)
        self.DecryptInputFolderButton.setObjectName(u"DecryptInputFolderButton")
        self.DecryptInputFolderButton.setGeometry(QRect(40, 150, 91, 24))
        
        self.DecryptSizeField = QLineEdit(self.DecryptBox)
        self.DecryptSizeField.setObjectName(u"DecryptSizeField")
        self.DecryptSizeField.setGeometry(QRect(40, 110, 231, 22))
        
        self.DecryptSizeLabel = QLabel(self.DecryptBox)
        self.DecryptSizeLabel.setObjectName(u"DecryptSizeLabel")
        self.DecryptSizeLabel.setGeometry(QRect(40, 90, 49, 16))

        self.DecryptOutputFolderButton = QPushButton(self.DecryptBox)
        self.DecryptOutputFolderButton.setObjectName(u"DecryptOutputFolderButton")
        self.DecryptOutputFolderButton.setGeometry(QRect(40, 210, 91, 24))
        
        self.DecryptInputFolderLabel = QTextEdit(self.DecryptBox)
        self.DecryptInputFolderLabel.setObjectName(u"DecryptInputFolderLabel")
        self.DecryptInputFolderLabel.setGeometry(QRect(140, 150, 221, 41))
        self.DecryptInputFolderLabel.setAutoFillBackground(False)
        self.DecryptInputFolderLabel.setFrameShape(QFrame.NoFrame)
        self.DecryptInputFolderLabel.setReadOnly(True)
        
        self.DecryptOutputFolderLabel = QTextEdit(self.DecryptBox)
        self.DecryptOutputFolderLabel.setObjectName(u"DecryptOutputFolderLabel")
        self.DecryptOutputFolderLabel.setGeometry(QRect(140, 210, 221, 41))
        self.DecryptOutputFolderLabel.setAutoFillBackground(False)
        self.DecryptOutputFolderLabel.setFrameShape(QFrame.NoFrame)
        self.DecryptOutputFolderLabel.setReadOnly(True)
        
        self.label = QLabel(Fog)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(310, 10, 211, 121))
        self.label.setPixmap(QPixmap(u"logo.png"))
        self.label.setScaledContents(True)
        self.label.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

        self.retranslateUi(Fog)
        QMetaObject.connectSlotsByName(Fog)
        
    def retranslateUi(self, Fog):
        Fog.setWindowTitle(QCoreApplication.translate("Fog", u"Fog Project", None))
        self.EnryptBox.setTitle(QCoreApplication.translate("Fog", u"Encrypt", None))
        self.EncryptButton.setText(QCoreApplication.translate("Fog", u"Encrypt", None))
        self.EncryptKeyLabel.setText(QCoreApplication.translate("Fog", u"Key :", None))
        self.EncryptInputFolderButton.setText(QCoreApplication.translate("Fog", u"Input Folder", None))
        self.EncryptOutputFolderButton.setText(QCoreApplication.translate("Fog", u"Output Folder", None))
        self.EncryptInputFolderLabel.setHtml(QCoreApplication.translate("Fog", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">None</p></body></html>", None))
        self.EncryptOutputFolderLabel.setHtml(QCoreApplication.translate("Fog", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">None</p></body></html>", None))
        self.ZipFileToEncryptButton.setText(QCoreApplication.translate("Fog", u"Select Zip File", None))
        self.ZipFileToEncryptLabel.setHtml(QCoreApplication.translate("Fog", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">None</p></body></html>", None))
        self.DecryptBox.setTitle(QCoreApplication.translate("Fog", u"Decrypt", None))
        self.DecryptButton.setText(QCoreApplication.translate("Fog", u"Decrypt", None))
        self.DecryptKeyLabel.setText(QCoreApplication.translate("Fog", u"Key :", None))
        self.DecryptInputFolderButton.setText(QCoreApplication.translate("Fog", u"Input Folder", None))
        self.DecryptSizeField.setText("")
        self.DecryptSizeLabel.setText(QCoreApplication.translate("Fog", u"Size :", None))
        self.DecryptOutputFolderButton.setText(QCoreApplication.translate("Fog", u"Output Folder", None))
        self.DecryptInputFolderLabel.setHtml(QCoreApplication.translate("Fog", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">None</p></body></html>", None))
        self.DecryptOutputFolderLabel.setHtml(QCoreApplication.translate("Fog", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">None</p></body></html>", None))
        self.label.setText("")
