import os
import sys
import time
import traceback
from PySide6 import QtWidgets
from PySide6.QtCore import QEvent, QRect, QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (QApplication, QButtonGroup, QFileDialog, QHBoxLayout, QLabel,
    QFrame, QLineEdit, QMenu, QPushButton, QScrollArea, QStackedWidget, QVBoxLayout, QWidget)

from gui.ui.main_window_ui2 import Ui_Fog
from fog import CONVERTIBLE_FORMATS, NATIVE_EXTENSIONS, extensions_for
from gui.i18n import LANGUAGES, format_size, language, set_language, tr
from gui.theme import (WARNING, IconButton, LoadingOverlay, PasswordToggle, SideDrawer, TitleBar,
    ToggleSlider, alert, apply_theme, confirm, make_icon, tinted_pixmap)
from gui.paths import ICON, LOGO
from gui.device import (IS_ANDROID, MOBILE, PHONE_SIZE, default_output_folder, screen_width,
    to_local_path)
from gui.prefs import FORMAT_LABELS, conversion_formats, set_conversion_format
from gui.progress import run_decryption, run_encryption
from gui.sources import SourcesPicker
from gui.tour import Step, TourOverlay

REPO_URL = "https://github.com/WhiteBowlerHat/Fog-Project_POC_WIP"
VERSION = "Version C_0.0.2"   # C = computer; never translated
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
        if IS_ANDROID:
            self.titlebar.hide()
        else:
            root_layout.addWidget(self.titlebar)

        self.body = body = QWidget()
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.addWidget(body, 1)
        content = QWidget()
        self.setupUi(content)
        if MOBILE:
            # phone: one panel at a time, as wide as the screen (the rows below are
            # laid out from the width of the boxes)
            box_w = min(PHONE_SIZE[0], screen_width()) - 24
            for box in (self.EnryptBox, self.DecryptBox):
                box.resize(box_w, box.height())
            body_layout.addWidget(content)
            if not IS_ANDROID:   # trying the phone layout on a PC
                self.resize(PHONE_SIZE[0] + 2, PHONE_SIZE[1] + TitleBar.HEIGHT + 2)
        else:
            content.setFixedSize(852, 614)
            body_layout.addWidget(content, 0, Qt.AlignCenter)
            self.resize(852 + 2, 614 + TitleBar.HEIGHT + 2)
        self.content, self.body_layout = content, body_layout

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
        # Image conversion: formats converted to PNG when "non-native images" is on
        self.ConversionButton = self.SettingsDrawer.add_button("", "image",
                                                               self.toggle_conversion_list)
        enabled = conversion_formats()
        self.ConversionRows = {}
        for fmt in CONVERTIBLE_FORMATS:
            row, _label, switch = self.SettingsDrawer.add_toggle(
                FORMAT_LABELS[fmt], fmt in enabled,
                lambda on, f=fmt: self.set_conversion(f, on))
            row.hide()
            self.ConversionRows[fmt] = (row, switch)
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
        for label, field, y, w in ((self.EncryptKeyLabel, self.EncryptKeyField, 36, enc_w),
                                   (self.EncryptConfirmLabel, self.EncryptConfirmField, 92, enc_w),
                                   (self.DecryptKeyLabel, self.DecryptKeyField, 36, dec_w),
                                   (self.DecryptSizeLabel, self.DecryptSizeField, 92, dec_w)):
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
        # "Non-native images": JPG, TIFF... (formats chosen in Settings) converted to PNG
        self.NonNativeLabel = QLabel(self.EnryptBox)
        self.NonNativeSlider = ToggleSlider(self.EnryptBox)
        self.NonNativeSlider.setValue(0)
        self.NonNativeState = QLabel(self.EnryptBox)
        self.NonNativeSlider.valueChanged.connect(lambda _v: self.apply_non_native())

        # File / folder rows: [choose button] [name only] [folder button: View Path].
        # The generated multi-line fields are replaced by one-line fields showing
        # only the name; the full path is kept in self.paths.
        self.paths = {}
        self.path_buttons = {}
        rows = (("ZipFileToEncryptLabel", self.ZipFileToEncryptButton, self.EnryptBox, 204),
                ("EncryptOutputFolderLabel", self.EncryptOutputFolderButton, self.EnryptBox, 304),
                ("DecryptOutputFolderLabel", self.DecryptOutputFolderButton, self.DecryptBox, 212))
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

        # Input images (several folders / images), same selector in the two panels:
        # "Input images :" then [+ Add more v] [info field] [list: view / remove]
        for widget in (self.EncryptInputFolderButton, self.EncryptInputFolderLabel,
                       self.DecryptInputFolderButton, self.DecryptInputFolderLabel):
            widget.hide()   # replaced by the selector
        layout = dict(left=LEFT, right=RIGHT, row_h=ROW_H, btn_w=BTN_W, gap=GAP,
                      file_dialog_options=FILE_DIALOG_OPTIONS)
        self.EncryptSources = SourcesPicker(   # capacity + does the message fit?
            self, self.EnryptBox, message=lambda: self.paths.get(self.ZipFileToEncryptLabel),
            y_label=240, y_row=260, **layout)
        # decryption: right under the Nonce field (same spacing as the encryption panel)
        self.DecryptSources = SourcesPicker(self, self.DecryptBox, y_label=148, y_row=168,
                                            **layout)

        # The size field is removed
        self.EncryptSizeLabel.hide()
        self.EncryptSizeField.hide()

        # Field showing the nonce when it is not stored in the images
        self.EncryptNonceLabel = QLabel(self.EnryptBox)
        self.EncryptNonceLabel.setGeometry(QRect(LEFT, 350, BTN_W, 20))
        self.EncryptNonceField = QLineEdit(self.EnryptBox)
        self.EncryptNonceField.setReadOnly(True)
        self.EncryptNonceField.setGeometry(
            QRect(LEFT + BTN_W + GAP, 346, enc_w - RIGHT - (LEFT + BTN_W + GAP), ROW_H))

        # Encrypt / Decrypt: same size, same height in the two boxes (aligned)
        for button, box_w in ((self.EncryptButton, enc_w), (self.DecryptButton, dec_w)):
            button.setGeometry(QRect((box_w - 160) // 2, 384, 160, 32))

        for button in (self.EncryptButton, self.DecryptButton, self.ZipFileToEncryptButton,
                       self.EncryptOutputFolderButton, self.DecryptOutputFolderButton):
            button.setCursor(Qt.PointingHandCursor)

        self.NonceInPictureSlider.valueChanged.connect(self.update_nonce_mode)

    # Connect button signals to slots
        self.EncryptOutputFolderButton.clicked.connect(lambda: self.select_folder("dlg_enc_out", self.EncryptOutputFolderLabel))
        self.DecryptOutputFolderButton.clicked.connect(lambda: self.select_folder("dlg_dec_out", self.DecryptOutputFolderLabel))
        self.ZipFileToEncryptButton.clicked.connect(lambda: self.select_file("dlg_file", self.ZipFileToEncryptLabel))
        self.EncryptButton.clicked.connect(lambda: self.encrypt(self.EncryptKeyField.text(), self.paths[self.ZipFileToEncryptLabel], list(self.EncryptSources.sources), self.paths[self.EncryptOutputFolderLabel]))
        self.DecryptButton.clicked.connect(lambda: self.decrypt(self.DecryptKeyField.text(), self.DecryptSizeField.text(), list(self.DecryptSources.sources), self.paths[self.DecryptOutputFolderLabel]))

        if MOBILE:
            self.build_mobile_layout()
        if IS_ANDROID:   # results go to the phone's storage (Documents/Fog/...)
            try:
                self.set_path(self.EncryptOutputFolderLabel, default_output_folder("encrypted"))
                self.set_path(self.DecryptOutputFolderLabel, default_output_folder("decrypted"))
            except OSError:
                pass
        self.retranslate()

    # --- Phone layout -------------------------------------------------------
    def build_mobile_layout(self):
        """One column: logo + Settings / Help, tagline, [Encrypt | Decrypt] buttons,
        then the chosen panel; everything scrolls if the screen is too short."""
        content = self.content
        self.body_layout.removeWidget(content)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setWidget(content)
        self.body_layout.addWidget(scroll)

        lay = QVBoxLayout(content)
        lay.setContentsMargins(12, 10, 12, 8)
        lay.setSpacing(8)
        header = QHBoxLayout()
        self.label.setFixedSize(130, 45)
        self.label.setPixmap(tinted_pixmap(LOGO).scaled(
            130, 45, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        header.addWidget(self.label)
        header.addStretch()
        header.addWidget(self.SettingsButton)
        header.addWidget(self.HelpButton)
        lay.addLayout(header)
        self.Tagline.setMinimumHeight(20)
        lay.addWidget(self.Tagline)

        # [Encrypt | Decrypt]: shows the chosen panel
        seg = QHBoxLayout()
        seg.setSpacing(0)
        self.ModeEncrypt, self.ModeDecrypt = QPushButton(), QPushButton()
        self.ModeGroup = QButtonGroup(self)
        for button, side, panel in ((self.ModeEncrypt, "left", "encrypt"),
                                    (self.ModeDecrypt, "right", "decrypt")):
            button.setObjectName("SegButton")
            button.setProperty("side", side)
            button.setCheckable(True)
            button.setMinimumHeight(42)
            button.setCursor(Qt.PointingHandCursor)
            button.clicked.connect(lambda _=False, p=panel: self.show_panel(p))
            self.ModeGroup.addButton(button)
            seg.addWidget(button)
        lay.addLayout(seg)

        self.Panels = QStackedWidget()
        for box in (self.EnryptBox, self.DecryptBox):
            box.setFixedSize(box.size())
            page = QWidget()
            page_layout = QVBoxLayout(page)
            page_layout.setContentsMargins(0, 4, 0, 0)
            page_layout.addWidget(box, 0, Qt.AlignHCenter | Qt.AlignTop)
            page_layout.addStretch()
            self.Panels.addWidget(page)
        lay.addWidget(self.Panels)
        lay.addStretch()
        lay.addWidget(self.VersionLabel)
        self.show_panel("encrypt")

    def show_panel(self, panel):
        """Phone layout: show the encryption or the decryption panel."""
        if not MOBILE or panel not in ("encrypt", "decrypt"):
            return
        self.Panels.setCurrentIndex(0 if panel == "encrypt" else 1)
        self.ModeEncrypt.setChecked(panel == "encrypt")
        self.ModeDecrypt.setChecked(panel == "decrypt")

    # --- Translation --------------------------------------------------------
    def retranslate(self):
        """Apply the current language to every text of the window."""
        self.titlebar.retranslate()
        self.SettingsButton.setToolTip(tr("settings"))
        self.HelpButton.setToolTip(tr("help"))
        self.EnryptBox.setTitle(tr("encrypt_box"))
        if MOBILE:
            self.ModeEncrypt.setText(tr("encrypt_box"))
            self.ModeDecrypt.setText(tr("decrypt_box"))
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
        self.EncryptOutputFolderButton.setText(tr("output_folder"))
        self.DecryptOutputFolderButton.setText(tr("output_folder"))
        for field in self.path_fields:
            field.setPlaceholderText(tr("none"))
            self.path_buttons[field].setToolTip(tr("view_path"))
        self.EncryptSources.retranslate()
        self.DecryptSources.retranslate()
        self.EncryptNonceLabel.setText(tr("nonce"))
        self.EncryptNonceField.setPlaceholderText(tr("nonce_placeholder"))
        # the size is stored inside the hidden data: decrypting no longer needs it.
        # The field is now an optional nonce (only needed if the metadata was stripped)
        self.DecryptSizeLabel.setText(tr("nonce"))
        self.DecryptSizeField.setPlaceholderText(tr("nonce_optional"))

        # "Nonce in picture": the switch is placed right after its label
        self.NonceInPictureLabel.setText(tr("nonce_in_picture"))
        self.NonceInPictureLabel.adjustSize()
        # two switches: "Nonce in the metadata" (y = 150) and "Non-native images" (y = 174)
        self.NonNativeLabel.setText(tr("non_native"))
        for label, switch, state, y in (
                (self.NonceInPictureLabel, self.NonceInPictureSlider, self.NonceInPictureState, 150),
                (self.NonNativeLabel, self.NonNativeSlider, self.NonNativeState, 174)):
            label.adjustSize()
            x = 24 + label.width() + 10
            label.setGeometry(QRect(24, y, label.width(), 18))
            switch.move(x, y)
            state.setGeometry(QRect(x + switch.width() + 8, y, 60, 18))
        self.update_nonce_mode(clear=False)
        self.update_non_native_texts()

        self.HelpDrawer.set_title(tr("help_title"))
        self.TutorialButton.setText("  " + tr("tutorial"))
        self.AboutButton.setText("  " + tr("about"))
        self.SettingsDrawer.set_title(tr("settings_title"))
        self.LanguageButton.setText("  " + tr("language"))
        self.ConversionButton.setText("  " + tr("conversion"))
        self.ConversionButton.setToolTip(tr("conversion_hint"))
        for code, option in self.LanguageOptions.items():
            selected = code == language()
            option.setIcon(make_icon("check" if selected else "blank", 16))
            option.setProperty("selected", selected)
            option.style().unpolish(option)
            option.style().polish(option)

    # --- Image conversion (Settings) / non-native images (Encrypt panel) ----
    def toggle_conversion_list(self):
        rows = [row for row, _ in self.ConversionRows.values()]
        visible = not rows[0].isVisible()
        for row in rows:
            row.setVisible(visible)

    def set_conversion(self, fmt, on):
        set_conversion_format(fmt, on)
        self.apply_non_native()

    def non_native_extensions(self):
        """Formats accepted for the encryption: PNG, plus the converted formats when
        "non-native images" is on."""
        if self.NonNativeSlider.value() == 1:
            return extensions_for(conversion_formats())
        return NATIVE_EXTENSIONS

    def apply_non_native(self):
        removed = self.EncryptSources.set_extensions(self.non_native_extensions())
        self.update_non_native_texts()
        if removed:
            lines = "\n".join("• " + os.path.basename(f) for f in removed[:10])
            if len(removed) > 10:
                lines += "\n" + tr("and_more", n=len(removed) - 10)
            alert(self, "info", tr("non_native_removed", list=lines))

    def update_non_native_texts(self):
        on = self.NonNativeSlider.value() == 1
        self.NonNativeState.setText(tr("yes_state") if on else tr("no_state"))
        names = ", ".join(FORMAT_LABELS[f] for f in conversion_formats()) or tr("no_format")
        tip = tr("non_native_tip", formats=names)
        for widget in (self.NonNativeLabel, self.NonNativeSlider, self.NonNativeState):
            widget.setToolTip(tip)

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
        self.tour = TourOverlay(self.body, self.tour_steps(), on_finish=self.end_tour,
                                on_step=lambda step: self.show_panel(step.panel))
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
            ([self.NonNativeLabel, self.NonNativeSlider, self.NonNativeState], "non_native"),
            ([self.ZipFileToEncryptButton, self.ZipFileToEncryptLabel, self.path_buttons[self.ZipFileToEncryptLabel]], "file"),
            (self.EncryptSources.widgets(), "add_more"),
            ([self.EncryptOutputFolderButton, self.EncryptOutputFolderLabel, self.path_buttons[self.EncryptOutputFolderLabel]], "enc_out"),
            ([self.EncryptButton], "encrypt_btn"),
            ([self.DecryptBox], "decrypt"),
            ([self.DecryptKeyLabel, self.DecryptKeyField], "dec_key"),
            ([self.DecryptSizeLabel, self.DecryptSizeField], "dec_nonce"),
            (self.DecryptSources.widgets(), "dec_in"),
            ([self.DecryptOutputFolderButton, self.DecryptOutputFolderLabel, self.path_buttons[self.DecryptOutputFolderLabel]], "dec_out"),
            ([self.DecryptButton], "decrypt_btn"),
            ([self.SettingsButton, self.HelpButton], "help"),
        )
        result, panel = [], "encrypt"
        for targets, key in steps:
            if key == "decrypt":
                panel = "decrypt"
            elif key == "help":
                panel = None
            result.append(Step(targets, tr(f"tour.{key}.title"), tr(f"tour.{key}.text"),
                               panel=panel))
        return result

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
        if IS_ANDROID:
            # an Android folder picker gives a "content://" address the engine cannot
            # write to: the results go to a folder of the phone's storage instead
            alert(self, "info", tr("android_output", path=self.paths.get(labelname, "")),
                  selectable=True)
            return
        folder_path = QFileDialog.getExistingDirectory(
            self, tr(title_key), "", QFileDialog.ShowDirsOnly | FILE_DIALOG_OPTIONS)
        if folder_path:
            self.set_path(labelname, folder_path)

    def select_file(self, title_key, labelname):
        file_path, _ = QFileDialog.getOpenFileName(self, tr(title_key), "", "", "",
                                                   FILE_DIALOG_OPTIONS)
        if file_path:
            try:
                file_path = to_local_path(file_path)   # Android: copy of the picked file
            except OSError as exc:
                alert(self, "error", str(exc))
                return
            self.set_path(labelname, file_path)

    def set_path(self, field, path):
        """Keep the full path, show only the file / folder name."""
        path = os.path.normpath(path)
        self.paths[field] = path
        field.setText(os.path.basename(path.rstrip("\\/")) or path)
        field.setCursorPosition(0)
        self.path_buttons[field].setEnabled(True)
        if field is self.ZipFileToEncryptLabel:
            self.EncryptSources.update()   # does the message fit in the images?

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
        if not input:
            alert(self, "warning", tr("missing_images"))
            return
        if not (file.strip() and output.strip()):
            alert(self, "warning", tr("missing_encrypt"))
            return
        store_nonce = self.nonce_in_picture()
        if IS_ANDROID:   # one sub-folder per run: never mix the images of two runs
            output = os.path.join(output.strip(), time.strftime("%Y%m%d-%H%M%S"))
        # runs in a background thread, with a progress alert (cancel possible)
        kind, value = run_encryption(self, (key, file.strip(), input, output.strip()),
                                     {"store_nonce": store_nonce,
                                      "extensions": self.EncryptSources.extensions})
        if kind == "cancelled":
            alert(self, "info", tr("encrypt_cancelled"))
            return
        if kind == "error":
            self.show_task_error(value)
            return
        size, nonce = value
        where = ("\n\n" + tr("written_to", path=output)) if IS_ANDROID else ""
        if store_nonce:
            alert(self, "info", tr("done") + where, selectable=IS_ANDROID)
        else:
            self.EncryptNonceField.setText(nonce)
            alert(self, "info", tr("done_nonce", nonce=nonce) + where, selectable=True)

    def show_task_error(self, exc):
        """Error of a background encryption / decryption."""
        if isinstance(exc, (ValueError, OSError)):
            alert(self, "error", str(exc))
        else:
            alert(self, "error", tr("unexpected_error", error=f"{type(exc).__name__}: {exc}"))

    def decrypt(self, key, nonce, input, output):
        if not key:
            alert(self, "warning", tr("enter_key"))
            return
        if not input:
            alert(self, "warning", tr("missing_images"))
            return
        if not output.strip():
            alert(self, "warning", tr("missing_decrypt"))
            return
        # runs in a background thread, with a progress alert (cancel possible)
        kind, value = run_decryption(self, (key, input, output.strip()),
                                     {"nonce": nonce.strip() or None})
        if kind == "cancelled":
            alert(self, "info", tr("decrypt_cancelled"))
            return
        if kind == "error":
            self.show_task_error(value)
            return
        path = value
        alert(self, "info", tr("recovered", path=path), selectable=True)


def _show_unexpected_error(exc_type, exc, tb):
    """Last safety net: an unexpected error is shown in an alert instead of being
    lost (the .exe has no console)."""
    traceback.print_exception(exc_type, exc, tb)
    try:
        alert(QApplication.activeWindow(), "error",
              tr("unexpected_error", error=f"{exc_type.__name__}: {exc}"))
    except Exception:
        pass


def main():
    sys.excepthook = _show_unexpected_error
    if sys.platform == "win32":
        # own taskbar identity (Fog icon instead of the Python one)
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("FogProject.Fog")
    app = QtWidgets.QApplication(sys.argv)
    apply_theme(app)
    window = MainWindow()
    if IS_ANDROID:
        window.showMaximized()
    else:
        window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
