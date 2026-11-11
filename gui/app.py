import os
import sys
from PySide6 import QtWidgets
from PySide6.QtCore import QEvent, QRect, QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QLabel,
    QLineEdit, QVBoxLayout, QWidget)

from gui.ui.main_window_ui2 import Ui_Fog
from fog import fog, wind
from gui.i18n import LANGUAGES, language, set_language, tr
from gui.theme import (IconButton, LoadingOverlay, PasswordToggle, SideDrawer, TitleBar,
    ToggleSlider, alert, apply_theme, confirm, make_icon, tinted_pixmap)
from gui.paths import ICON, LOGO
from gui.tour import Step, TourOverlay

REPO_URL = "https://github.com/WhiteBowlerHat/Fog-Project_POC_WIP"
VERSION = "Version C_0.0.1"   # C = computer; never translated
FILE_DIALOG_OPTIONS = QFileDialog.Option(0)  # native OS dialog (DontUseNativeDialog = themed)


class MainWindow(QtWidgets.QMainWindow, Ui_Fog):
    def __init__(self):
        super(MainWindow, self).__init__()
        # No native title bar: it is replaced by the dark banner (TitleBar)
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint
                            | Qt.WindowMinMaxButtonsHint | Qt.WindowSystemMenuHint)
        self.setWindowTitle("Fog Project")
        self.setWindowIcon(QIcon(ICON))

        # Root = banner + body. The generated UI is drawn in a fixed-size `content`
        # widget, centered in the body (so maximizing keeps it in the middle).
        self.root = QWidget(self)
        self.root.setObjectName("Root")
        self.root.setAttribute(Qt.WA_StyledBackground)
        self.setCentralWidget(self.root)
        root_layout = QVBoxLayout(self.root)
        root_layout.setContentsMargins(1, 1, 1, 1)
        root_layout.setSpacing(0)
        self.titlebar = TitleBar(self, "Fog Project", logo=LOGO)
        root_layout.addWidget(self.titlebar)

        self.body = body = QWidget()
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.addWidget(body, 1)
        content = QWidget()
        self.setupUi(content)
        content.setFixedSize(852, 614)
        body_layout.addWidget(content, 0, Qt.AlignCenter)
        self.resize(852 + 2, 614 + TitleBar.HEIGHT + 2)

        # White logo (smaller), aspect ratio kept, with an italic tagline
        self.label.setScaledContents(False)
        self.label.setGeometry(QRect(321, 16, 210, 73))
        self.label.setPixmap(tinted_pixmap(LOGO).scaled(
            210, 73, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.label.setAlignment(Qt.AlignCenter)
        self.Tagline = QLabel(content)
        self.Tagline.setObjectName("Tagline")
        self.Tagline.setGeometry(QRect(0, 94, 852, 24))
        self.Tagline.setAlignment(Qt.AlignCenter)

        # Software version, bottom right, discreet
        self.VersionLabel = QLabel(VERSION, content)
        self.VersionLabel.setObjectName("VersionLabel")
        self.VersionLabel.setGeometry(QRect(600, 588, 236, 20))
        self.VersionLabel.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        # Settings / Help, top right under the banner
        self.SettingsButton = IconButton("settings", content, QSize(36, 36), round_hover=True)
        self.SettingsButton.setGeometry(QRect(762, 12, 36, 36))
        self.SettingsButton.clicked.connect(self.toggle_settings_drawer)
        self.HelpButton = IconButton("help", content, QSize(36, 36), round_hover=True)
        self.HelpButton.setGeometry(QRect(804, 12, 36, 36))
        self.HelpButton.clicked.connect(self.toggle_help_drawer)

        # Drawers sliding in from the right under the two buttons
        self.HelpDrawer = SideDrawer(body)
        self.TutorialButton = self.HelpDrawer.add_button("", "tour", self.ask_tutorial)
        self.AboutButton = self.HelpDrawer.add_button("", "info", self.show_about)
        self.SettingsDrawer = SideDrawer(body)
        self.LanguageButton = self.SettingsDrawer.add_button("", "globe", self.toggle_language_list)
        self.LanguageOptions = {
            code: self.SettingsDrawer.add_option(name, lambda _=False, c=code: self.choose_language(c))
            for code, name in LANGUAGES.items()
        }
        for option in self.LanguageOptions.values():
            option.hide()
        self.drawers = (self.HelpDrawer, self.SettingsDrawer)
        body.installEventFilter(self)
        self.tour = None
        self.loading = LoadingOverlay(body)

        # Layout of the two boxes (coordinates inside each box)
        LEFT, RIGHT, ROW_H, BTN_W, GAP = 24, 16, 30, 112, 8
        enc_w, dec_w = self.EnryptBox.width(), self.DecryptBox.width()

        # Keys: as wide as the box. Encrypt asks for the key twice.
        self.EncryptConfirmLabel = QLabel(self.EnryptBox)
        self.EncryptConfirmField = QLineEdit(self.EnryptBox)
        for label, field, y, w in ((self.EncryptKeyLabel, self.EncryptKeyField, 40, enc_w),
                                   (self.EncryptConfirmLabel, self.EncryptConfirmField, 98, enc_w),
                                   (self.DecryptKeyLabel, self.DecryptKeyField, 40, dec_w),
                                   (self.DecryptSizeLabel, self.DecryptSizeField, 98, dec_w)):
            label.setGeometry(QRect(LEFT, y, w - LEFT - RIGHT, 18))
            field.setGeometry(QRect(LEFT, y + 20, w - LEFT - RIGHT, ROW_H))
            field.setMinimumHeight(ROW_H)
            field.setMaximumHeight(ROW_H)

        # The keys are passwords: filled circles + show / hide "eye" button
        self.key_toggles = [PasswordToggle(self.EncryptKeyField),
                            PasswordToggle(self.EncryptConfirmField),
                            PasswordToggle(self.DecryptKeyField)]

        # "Nonce in picture" switch: a 2-position slider (right = nonce stored in
        # the PNG metadata, left = not stored, it is then displayed after hiding)
        self.NonceInPictureLabel = QLabel(self.EnryptBox)
        self.NonceInPictureSlider = ToggleSlider(self.EnryptBox)
        self.NonceInPictureSlider.setValue(1)
        self.NonceInPictureState = QLabel(self.EnryptBox)

        # File / folder rows: [choose button] [name only] [folder button: View Path].
        # The generated multi-line fields are replaced by one-line fields showing
        # only the name; the full path is kept in self.paths.
        self.paths = {}
        self.path_buttons = {}
        rows = (("ZipFileToEncryptLabel", self.ZipFileToEncryptButton, self.EnryptBox, 196),
                ("EncryptInputFolderLabel", self.EncryptInputFolderButton, self.EnryptBox, 236),
                ("EncryptOutputFolderLabel", self.EncryptOutputFolderButton, self.EnryptBox, 276),
                ("DecryptInputFolderLabel", self.DecryptInputFolderButton, self.DecryptBox, 196),
                ("DecryptOutputFolderLabel", self.DecryptOutputFolderButton, self.DecryptBox, 236))
        for name, button, box, y in rows:
            getattr(self, name).hide()
            field = QLineEdit(box)
            field.setReadOnly(True)
            setattr(self, name, field)
            view = IconButton("folder", box, QSize(ROW_H, ROW_H), framed=True)
            view.setEnabled(False)
            view.clicked.connect(lambda _=False, f=field: self.view_path(f))
            x_view = box.width() - RIGHT - ROW_H
            button.setGeometry(QRect(LEFT, y, BTN_W, ROW_H))
            field.setGeometry(QRect(LEFT + BTN_W + GAP, y, x_view - GAP - (LEFT + BTN_W + GAP), ROW_H))
            view.move(x_view, y)
            self.paths[field] = ""
            self.path_buttons[field] = view
        self.path_fields = tuple(self.paths)

        # The size field is removed
        self.EncryptSizeLabel.hide()
        self.EncryptSizeField.hide()

        # Field showing the nonce when it is not stored in the images
        self.EncryptNonceLabel = QLabel(self.EnryptBox)
        self.EncryptNonceLabel.setGeometry(QRect(LEFT, 322, BTN_W, 20))
        self.EncryptNonceField = QLineEdit(self.EnryptBox)
        self.EncryptNonceField.setReadOnly(True)
        self.EncryptNonceField.setGeometry(
            QRect(LEFT + BTN_W + GAP, 318, enc_w - RIGHT - (LEFT + BTN_W + GAP), ROW_H))

        # Encrypt / Decrypt: same size, same height in the two boxes (aligned)
        for button, box_w in ((self.EncryptButton, enc_w), (self.DecryptButton, dec_w)):
            button.setGeometry(QRect((box_w - 160) // 2, 376, 160, 32))

        for button in (self.EncryptButton, self.DecryptButton, self.ZipFileToEncryptButton,
                       self.EncryptInputFolderButton, self.EncryptOutputFolderButton,
                       self.DecryptInputFolderButton, self.DecryptOutputFolderButton):
            button.setCursor(Qt.PointingHandCursor)

        self.NonceInPictureSlider.valueChanged.connect(self.update_nonce_mode)

    # Connect button signals to slots
        self.EncryptInputFolderButton.clicked.connect(lambda: self.select_folder("dlg_enc_in", self.EncryptInputFolderLabel))
        self.EncryptOutputFolderButton.clicked.connect(lambda: self.select_folder("dlg_enc_out", self.EncryptOutputFolderLabel))
        self.DecryptInputFolderButton.clicked.connect(lambda: self.select_folder("dlg_dec_in", self.DecryptInputFolderLabel))
        self.DecryptOutputFolderButton.clicked.connect(lambda: self.select_folder("dlg_dec_out", self.DecryptOutputFolderLabel))
        self.ZipFileToEncryptButton.clicked.connect(lambda: self.select_file("dlg_file", self.ZipFileToEncryptLabel))
        self.EncryptButton.clicked.connect(lambda: self.encrypt(self.EncryptKeyField.text(), self.paths[self.ZipFileToEncryptLabel], self.paths[self.EncryptInputFolderLabel], self.paths[self.EncryptOutputFolderLabel]))
        self.DecryptButton.clicked.connect(lambda: self.decrypt(self.DecryptKeyField.text(), self.DecryptSizeField.text(), self.paths[self.DecryptInputFolderLabel], self.paths[self.DecryptOutputFolderLabel]))

        self.retranslate()

    # --- Translation --------------------------------------------------------
    def retranslate(self):
        """Apply the current language to every text of the window."""
        self.titlebar.retranslate()
        self.SettingsButton.setToolTip(tr("settings"))
        self.HelpButton.setToolTip(tr("help"))
        self.EnryptBox.setTitle(tr("encrypt_box"))
        self.DecryptBox.setTitle(tr("decrypt_box"))
        self.EncryptButton.setText(tr("encrypt_btn"))
        self.DecryptButton.setText(tr("decrypt_btn"))
        self.Tagline.setText(tr("tagline"))
        self.EncryptKeyLabel.setText(tr("key"))
        self.EncryptConfirmLabel.setText(tr("confirm_key"))
        self.DecryptKeyLabel.setText(tr("key"))
        for toggle in self.key_toggles:
            toggle.retranslate()
        self.ZipFileToEncryptButton.setText(tr("select_file"))
        self.EncryptInputFolderButton.setText(tr("input_folder"))
        self.DecryptInputFolderButton.setText(tr("input_folder"))
        self.EncryptOutputFolderButton.setText(tr("output_folder"))
        self.DecryptOutputFolderButton.setText(tr("output_folder"))
        for field in self.path_fields:
            field.setPlaceholderText(tr("none"))
            self.path_buttons[field].setToolTip(tr("view_path"))
        self.EncryptNonceLabel.setText(tr("nonce"))
        self.EncryptNonceField.setPlaceholderText(tr("nonce_placeholder"))
        # the size is stored inside the hidden data: decrypting no longer needs it.
        # The field is now an optional nonce (only needed if the metadata was stripped)
        self.DecryptSizeLabel.setText(tr("nonce"))
        self.DecryptSizeField.setPlaceholderText(tr("nonce_optional"))

        # "Nonce in picture": the switch is placed right after its label
        self.NonceInPictureLabel.setText(tr("nonce_in_picture"))
        self.NonceInPictureLabel.adjustSize()
        x = 24 + self.NonceInPictureLabel.width() + 10
        self.NonceInPictureLabel.setGeometry(QRect(24, 160, self.NonceInPictureLabel.width(), 22))
        self.NonceInPictureSlider.move(x, 160)
        self.NonceInPictureState.setGeometry(QRect(x + 52, 160, 60, 22))
        self.update_nonce_mode(clear=False)

        self.HelpDrawer.set_title(tr("help_title"))
        self.TutorialButton.setText("  " + tr("tutorial"))
        self.AboutButton.setText("  " + tr("about"))
        self.SettingsDrawer.set_title(tr("settings_title"))
        self.LanguageButton.setText("  " + tr("language"))
        for code, option in self.LanguageOptions.items():
            selected = code == language()
            option.setIcon(make_icon("check" if selected else "blank", 16))
            option.setProperty("selected", selected)
            option.style().unpolish(option)
            option.style().polish(option)

    def toggle_language_list(self):
        visible = not next(iter(self.LanguageOptions.values())).isVisible()
        for option in self.LanguageOptions.values():
            option.setVisible(visible)

    def choose_language(self, code):
        if code == language():
            return
        if not confirm(self, tr("language_question", lang=LANGUAGES[code]), title=tr("language")):
            return
        self.SettingsDrawer.close_drawer()
        message = tr("translating")   # in the language being left (e.g. "Traduction en cours..")

        def apply():
            set_language(code)
            self.retranslate()

        self.loading.run(message, apply)

    # --- Window -------------------------------------------------------------
    def changeEvent(self, event):
        # keep the maximize/restore icon and the window border in sync
        if event.type() == QEvent.WindowStateChange:
            maxed = self.isMaximized()
            self.titlebar.update_state()
            self.root.setProperty("maxed", maxed)
            self.root.layout().setContentsMargins(*(0, 0, 0, 0) if maxed else (1, 1, 1, 1))
            self.root.style().unpolish(self.root)
            self.root.style().polish(self.root)
        super().changeEvent(event)

    # --- Drawers / tour / about ---------------------------------------------
    def eventFilter(self, obj, event):
        if obj is self.body and event.type() in (QEvent.Resize, QEvent.Show):
            self.place_drawers()
        return super().eventFilter(obj, event)

    def place_drawers(self):
        top = self.HelpButton.mapTo(self.body, self.HelpButton.rect().bottomLeft()).y() + 8
        for drawer in self.drawers:
            drawer.place(top)

    def toggle_drawer(self, drawer):
        # only one drawer open at a time
        self.place_drawers()
        for other in self.drawers:
            if other is not drawer:
                other.close_drawer()
        drawer.toggle()

    def toggle_help_drawer(self):
        self.toggle_drawer(self.HelpDrawer)

    def toggle_settings_drawer(self):
        self.toggle_drawer(self.SettingsDrawer)

    def ask_tutorial(self):
        if confirm(self, tr("tutorial_question"), title=tr("tutorial")):
            self.start_tour()

    def start_tour(self):
        for drawer in self.drawers:
            drawer.close_drawer()
            drawer.hide()
        self.tour = TourOverlay(self.body, self.tour_steps(), on_finish=self.end_tour)
        self.tour.start()

    def end_tour(self):
        self.tour = None

    def tour_steps(self):
        steps = (
            ([self.EnryptBox], "encrypt"),
            ([self.EncryptKeyLabel, self.EncryptKeyField], "key"),
            ([self.EncryptConfirmLabel, self.EncryptConfirmField], "confirm_key"),
            ([self.NonceInPictureLabel, self.NonceInPictureSlider, self.NonceInPictureState],
             "nonce_switch"),
            ([self.ZipFileToEncryptButton, self.ZipFileToEncryptLabel, self.path_buttons[self.ZipFileToEncryptLabel]], "file"),
            ([self.EncryptInputFolderButton, self.EncryptInputFolderLabel, self.path_buttons[self.EncryptInputFolderLabel]], "enc_in"),
            ([self.EncryptOutputFolderButton, self.EncryptOutputFolderLabel, self.path_buttons[self.EncryptOutputFolderLabel]], "enc_out"),
            ([self.EncryptButton], "encrypt_btn"),
            ([self.DecryptBox], "decrypt"),
            ([self.DecryptKeyLabel, self.DecryptKeyField], "dec_key"),
            ([self.DecryptSizeLabel, self.DecryptSizeField], "dec_nonce"),
            ([self.DecryptInputFolderButton, self.DecryptInputFolderLabel, self.path_buttons[self.DecryptInputFolderLabel]], "dec_in"),
            ([self.DecryptOutputFolderButton, self.DecryptOutputFolderLabel, self.path_buttons[self.DecryptOutputFolderLabel]], "dec_out"),
            ([self.DecryptButton], "decrypt_btn"),
            ([self.SettingsButton, self.HelpButton], "help"),
        )
        return [Step(targets, tr(f"tour.{key}.title"), tr(f"tour.{key}.text"))
                for targets, key in steps]

    def show_about(self):
        link = f'<a href="{REPO_URL}" style="color:#ffffff;">{REPO_URL}</a>'
        alert(self, "help", tr("about_text", link=link), title=tr("about"), rich=True)

    # --- Encrypt / decrypt --------------------------------------------------
    def nonce_in_picture(self):
        return self.NonceInPictureSlider.value() == 1

    def update_nonce_mode(self, *_, clear=True):
        stored = self.nonce_in_picture()
        self.NonceInPictureState.setText(tr("yes_state") if stored else tr("no_state"))
        self.EncryptNonceLabel.setVisible(not stored)
        self.EncryptNonceField.setVisible(not stored)
        if clear:
            self.EncryptNonceField.clear()

    def select_folder(self, title_key, labelname):
        folder_path = QFileDialog.getExistingDirectory(
            self, tr(title_key), "", QFileDialog.ShowDirsOnly | FILE_DIALOG_OPTIONS)
        if folder_path:
            self.set_path(labelname, folder_path)

    def select_file(self, title_key, labelname):
        file_path, _ = QFileDialog.getOpenFileName(self, tr(title_key), "", "", "",
                                                   FILE_DIALOG_OPTIONS)
        if file_path:
            self.set_path(labelname, file_path)

    def set_path(self, field, path):
        """Keep the full path, show only the file / folder name."""
        path = os.path.normpath(path)
        self.paths[field] = path
        field.setText(os.path.basename(path.rstrip("\\/")) or path)
        field.setCursorPosition(0)
        self.path_buttons[field].setEnabled(True)

    def view_path(self, field):
        if self.paths[field]:
            alert(self, "info", self.paths[field], title=tr("view_path"), selectable=True)

    def encrypt(self, key, file, input, output):
        if not key:
            alert(self, "warning", tr("enter_key"))
            return
        if key != self.EncryptConfirmField.text():
            alert(self, "warning", tr("keys_mismatch"))
            return
        if not (file.strip() and input.strip() and output.strip()):
            alert(self, "warning", tr("missing_encrypt"))
            return
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            store_nonce = self.nonce_in_picture()
            size, nonce = fog(key, file.strip(), input.strip(), output.strip(),
                              store_nonce=store_nonce)
        except (ValueError, OSError) as exc:
            QApplication.restoreOverrideCursor()
            alert(self, "error", str(exc))
            return
        QApplication.restoreOverrideCursor()
        if store_nonce:
            alert(self, "info", tr("done"))
        else:
            self.EncryptNonceField.setText(nonce)
            alert(self, "info", tr("done_nonce", nonce=nonce), selectable=True)

    def decrypt(self, key, nonce, input, output):
        if not key:
            alert(self, "warning", tr("enter_key"))
            return
        if not (input.strip() and output.strip()):
            alert(self, "warning", tr("missing_decrypt"))
            return
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            path = wind(key, input.strip(), output.strip(), nonce=nonce.strip() or None)
        except (ValueError, OSError) as exc:
            QApplication.restoreOverrideCursor()
            alert(self, "error", str(exc))
            return
        QApplication.restoreOverrideCursor()
        alert(self, "info", tr("recovered", path=path), selectable=True)


def main():
    if sys.platform == "win32":
        # own taskbar identity (Fog icon instead of the Python one)
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("FogProject.Fog")
    app = QtWidgets.QApplication(sys.argv)
    apply_theme(app)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
