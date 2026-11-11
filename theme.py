"""Dark theme for the Fog Project GUI.

Contains the colours, the global stylesheet, the custom title bar (banner) that
replaces the native one, a toggle-like slider and themed alert dialogs.
"""
import math

from PySide6.QtCore import (QEasingCurve, QPoint, QPointF, QPropertyAnimation, QRectF,
    QSize, Qt)
from PySide6.QtGui import (QAction, QColor, QFont, QIcon, QPainter, QPainterPath, QPalette,
    QPen, QPixmap)
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QFrame, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QSlider, QToolButton, QVBoxLayout, QWidget)
from PySide6.QtCore import QTimer

from i18n import tr

# --- Colours ---------------------------------------------------------------
BACKGROUND = "#19191a"   # window background
BANNER = "#0f0f10"       # title bar, a shade darker than the background
PANEL = "#1f1f21"        # group boxes
FIELD = "#111112"        # inputs (inset look)
BORDER = "#2e2e33"
BORDER_HOVER = "#45454d"
BUTTON = "#2a2a2f"
BUTTON_HOVER = "#35353b"
ACCENT = "#5b7cfa"       # muted "fog" blue
ACCENT_HOVER = "#7190ff"
ACCENT_PRESSED = "#4a68dc"
WARNING = "#d9a441"
ERROR = "#e05555"
TEXT = "#ffffff"
CLOSE_HOVER = "#e81123"

STYLESHEET = f"""
* {{
    color: {TEXT};
    font-family: "Segoe UI";
    font-size: 9pt;
}}
QMainWindow, QDialog {{ background: {BACKGROUND}; }}
#Root {{ background: {BACKGROUND}; border: 1px solid {BORDER}; }}
#Root[maxed="true"] {{ border: none; }}
#TitleBar {{ background: {BANNER}; border-bottom: 1px solid {BORDER}; }}
#TitleText {{ font-size: 10pt; font-weight: 600; }}

QGroupBox {{
    background: {PANEL};
    border: 1px solid {BORDER};
    border-radius: 10px;
    margin-top: 14px;
    font-size: 11pt;
    font-weight: 600;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 16px;
    padding: 0 6px;
    background: {BACKGROUND};
    border-radius: 4px;
}}
QLabel {{ background: transparent; }}

QLineEdit, QTextEdit, QPlainTextEdit {{
    background: {FIELD};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 3px 6px;
    selection-background-color: {ACCENT};
    selection-color: {TEXT};
}}
QLineEdit:hover, QTextEdit:hover {{ border-color: {BORDER_HOVER}; }}
QLineEdit:focus, QTextEdit:focus {{ border-color: {ACCENT}; }}
QLineEdit:read-only {{ background: #151517; }}
QLineEdit {{ lineedit-password-character: 9679; }}  /* filled white circles */
QLineEdit QToolButton {{ background: transparent; border: none; padding: 0 2px; }}
QLineEdit QToolButton:hover {{ background: {BUTTON_HOVER}; border-radius: 4px; }}

/* Help side drawer */
#SideDrawer {{
    background: {BANNER};
    border: 1px solid {BORDER};
    border-right: none;
    border-top-left-radius: 10px;
    border-bottom-left-radius: 10px;
}}
#DrawerTitle {{ font-size: 11pt; font-weight: 600; }}
#DrawerButton {{
    text-align: left;
    padding: 10px 12px;
    font-size: 10pt;
    background: transparent;
    border: 1px solid transparent;
    border-radius: 6px;
}}
#DrawerButton:hover {{ background: {BUTTON_HOVER}; border-color: {BORDER_HOVER}; }}
#DrawerOption {{
    text-align: left;
    padding: 7px 10px;
    margin-left: 28px;
    background: {FIELD};
    border: 1px solid {BORDER};
    border-radius: 6px;
}}
#DrawerOption:hover {{ border-color: {BORDER_HOVER}; }}
#DrawerOption[selected="true"] {{ border-color: {ACCENT}; font-weight: 600; }}
#LoadingCard {{ background: {PANEL}; border: 1px solid {BORDER}; border-radius: 12px; }}
#LoadingText {{ font-size: 11pt; font-weight: 600; }}

/* Tagline under the logo, software version */
#Tagline {{ font-size: 10pt; font-style: italic; color: rgba(255, 255, 255, 190); }}
#VersionLabel {{ font-size: 8pt; color: rgba(255, 255, 255, 80); }}

/* Guided tour */
#TourBubble {{ background: {PANEL}; border: 1px solid {TEXT}; border-radius: 10px; }}
#TourTitle {{ font-size: 11pt; font-weight: 600; }}
#TourText {{ font-size: 10pt; }}

QPushButton {{
    background: {BUTTON};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 4px 4px;
}}
QPushButton:hover {{ background: {BUTTON_HOVER}; border-color: {BORDER_HOVER}; }}
QPushButton:pressed {{ background: {BORDER}; }}
QPushButton:focus {{ border-color: {ACCENT}; }}
#EncryptButton, #DecryptButton, QPushButton[primary="true"] {{
    background: {ACCENT};
    border: 1px solid {ACCENT};
    font-weight: 600;
}}
#EncryptButton:hover, #DecryptButton:hover, QPushButton[primary="true"]:hover {{
    background: {ACCENT_HOVER}; border-color: {ACCENT_HOVER};
}}
#EncryptButton:pressed, #DecryptButton:pressed, QPushButton[primary="true"]:pressed {{
    background: {ACCENT_PRESSED};
}}

/* Toggle slider */
QSlider#ToggleSlider::groove:horizontal {{
    height: 20px; border-radius: 10px; background: #3a3a41;
}}
QSlider#ToggleSlider[on="true"]::groove:horizontal {{ background: {ACCENT}; }}
QSlider#ToggleSlider::sub-page:horizontal, QSlider#ToggleSlider::add-page:horizontal {{
    background: transparent;
}}
QSlider#ToggleSlider::handle:horizontal {{
    background: {TEXT}; width: 16px; height: 16px; margin: 2px; border-radius: 8px;
}}

/* Alerts */
#DialogFrame {{ background: {BACKGROUND}; border: 1px solid {BORDER}; }}
#DialogText {{ font-size: 10pt; }}

/* Non-native file dialog and other generic widgets */
QTreeView, QListView {{
    background: {FIELD}; border: 1px solid {BORDER}; border-radius: 6px;
    selection-background-color: {ACCENT}; alternate-background-color: {PANEL};
}}
QHeaderView::section {{ background: {PANEL}; border: none; border-right: 1px solid {BORDER}; padding: 4px; }}
QComboBox {{
    background: {FIELD}; border: 1px solid {BORDER}; border-radius: 6px; padding: 3px 6px;
}}
QComboBox QAbstractItemView {{ background: {PANEL}; selection-background-color: {ACCENT}; }}
QToolButton {{ background: transparent; border: 1px solid transparent; border-radius: 4px; padding: 2px; }}
QToolButton:hover {{ background: {BUTTON_HOVER}; }}
QMenu {{ background: {PANEL}; border: 1px solid {BORDER}; }}
QMenu::item:selected {{ background: {ACCENT}; }}
QScrollBar:vertical {{ background: transparent; width: 10px; }}
QScrollBar:horizontal {{ background: transparent; height: 10px; }}
QScrollBar::handle {{ background: #3a3a41; border-radius: 4px; min-height: 24px; min-width: 24px; }}
QScrollBar::handle:hover {{ background: #4a4a52; }}
QScrollBar::add-line, QScrollBar::sub-line {{ width: 0; height: 0; }}
QScrollBar::add-page, QScrollBar::sub-page {{ background: none; }}
QToolTip {{ background: {PANEL}; color: {TEXT}; border: 1px solid {BORDER}; padding: 4px; }}
"""


def apply_theme(app: QApplication):
    """Fusion style + dark palette + stylesheet for the whole application."""
    app.setStyle("Fusion")
    pal = QPalette()
    for role, color in (
        (QPalette.Window, BACKGROUND), (QPalette.Base, FIELD), (QPalette.AlternateBase, PANEL),
        (QPalette.Button, BUTTON), (QPalette.Highlight, ACCENT), (QPalette.ToolTipBase, PANEL),
        (QPalette.WindowText, TEXT), (QPalette.Text, TEXT), (QPalette.ButtonText, TEXT),
        (QPalette.BrightText, TEXT), (QPalette.HighlightedText, TEXT), (QPalette.ToolTipText, TEXT),
        (QPalette.Link, TEXT),
    ):
        pal.setColor(role, QColor(color))
    pal.setColor(QPalette.PlaceholderText, QColor(255, 255, 255, 115))
    app.setPalette(pal)
    app.setStyleSheet(STYLESHEET)


def tinted_pixmap(path: str, color: str = TEXT) -> QPixmap:
    """Load an image and repaint its opaque pixels in `color` (the logo is black)."""
    src = QPixmap(path)
    out = QPixmap(src.size())
    out.fill(Qt.transparent)
    p = QPainter(out)
    p.drawPixmap(0, 0, src)
    p.setCompositionMode(QPainter.CompositionMode_SourceIn)
    p.fillRect(out.rect(), QColor(color))
    p.end()
    return out


# --- Icons (drawn by hand: no dependency on icon fonts) ------------------
def draw_icon(p: QPainter, kind: str, c: QPointF, color: str = TEXT):
    """Draw a white line icon centred on `c` (about 20x20 px).

    kind: minimize, maximize, restore, close, settings, help, info, eye, eye_off, tour
    """
    pen = QPen(QColor(color), 1.3)
    pen.setCapStyle(Qt.RoundCap)
    pen.setJoinStyle(Qt.RoundJoin)
    p.setPen(pen)
    p.setBrush(Qt.NoBrush)
    x, y = c.x(), c.y()
    if kind == "minimize":
        p.drawLine(QPointF(x - 5, y), QPointF(x + 5, y))
    elif kind == "maximize":
        p.drawRect(QRectF(x - 5, y - 5, 10, 10))
    elif kind == "restore":
        p.drawRect(QRectF(x - 5, y - 3, 8, 8))
        p.drawPolyline([QPointF(x - 3, y - 5), QPointF(x + 5, y - 5), QPointF(x + 5, y + 3)])
    elif kind == "close":
        p.drawLine(QPointF(x - 5, y - 5), QPointF(x + 5, y + 5))
        p.drawLine(QPointF(x + 5, y - 5), QPointF(x - 5, y + 5))
    elif kind in ("help", "info"):
        p.setPen(QPen(QColor(color), 1.6))
        p.drawEllipse(c, 9, 9)
        f = QFont("Segoe UI", 10)
        f.setBold(True)
        p.setFont(f)
        p.drawText(QRectF(x - 9, y - 9, 18, 18), Qt.AlignCenter, "?" if kind == "help" else "i")
    elif kind == "settings":
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(color))
        gear = QPainterPath()
        teeth, r_out, r_in = 8, 10.0, 7.5
        steps = teeth * 4
        for i in range(steps + 1):
            a = 2 * math.pi * i / steps
            rad = r_out if (i // 2) % 2 == 0 else r_in
            pt = QPointF(x + rad * math.cos(a), y + rad * math.sin(a))
            gear.moveTo(pt) if i == 0 else gear.lineTo(pt)
        hole = QPainterPath()
        hole.addEllipse(c, 3.5, 3.5)
        p.drawPath(gear.subtracted(hole))
    elif kind in ("eye", "eye_off"):
        p.setPen(QPen(QColor(color), 1.5))
        eye = QPainterPath()
        eye.moveTo(x - 8, y)
        eye.quadTo(x, y - 9, x + 8, y)
        eye.quadTo(x, y + 9, x - 8, y)
        p.drawPath(eye)
        p.setBrush(QColor(color))
        p.drawEllipse(c, 2.4, 2.4)
        if kind == "eye_off":
            p.drawLine(QPointF(x - 7, y + 7), QPointF(x + 7, y - 7))
    elif kind == "globe":
        p.setPen(QPen(QColor(color), 1.4))
        p.drawEllipse(c, 9, 9)
        p.drawEllipse(c, 4, 9)
        p.drawLine(QPointF(x - 9, y), QPointF(x + 9, y))
        p.drawLine(QPointF(x - 7.5, y - 4.5), QPointF(x + 7.5, y - 4.5))
        p.drawLine(QPointF(x - 7.5, y + 4.5), QPointF(x + 7.5, y + 4.5))
    elif kind == "check":
        p.setPen(QPen(QColor(color), 2))
        p.drawPolyline([QPointF(x - 5, y), QPointF(x - 1.5, y + 4), QPointF(x + 5.5, y - 4)])
    elif kind == "blank":
        pass
    elif kind == "folder":
        p.setPen(QPen(QColor(color), 1.4))
        folder = QPainterPath()
        folder.moveTo(x - 8, y + 6)
        folder.lineTo(x - 8, y - 6)
        folder.lineTo(x - 3, y - 6)
        folder.lineTo(x - 1, y - 4)
        folder.lineTo(x + 8, y - 4)
        folder.lineTo(x + 8, y + 6)
        folder.closeSubpath()
        p.drawPath(folder)
        p.drawLine(QPointF(x - 8, y - 1), QPointF(x + 8, y - 1))
    elif kind == "tour":   # "play" in a circle
        p.setPen(QPen(QColor(color), 1.6))
        p.drawEllipse(c, 9, 9)
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(color))
        p.drawPolygon([QPointF(x - 2.5, y - 4.5), QPointF(x + 4.5, y), QPointF(x - 2.5, y + 4.5)])


def make_icon(kind: str, size: int = 20, color: str = TEXT) -> QIcon:
    """QIcon from draw_icon (for actions and regular buttons)."""
    dpr = 2  # sharp on high-DPI screens
    pm = QPixmap(size * dpr, size * dpr)
    pm.setDevicePixelRatio(dpr)
    pm.fill(Qt.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    draw_icon(p, kind, QPointF(size / 2, size / 2), color)
    p.end()
    return QIcon(pm)


class IconButton(QAbstractButton):
    """Flat button painting a white vector icon.

    kind: minimize, maximize, restore, close, settings, help
    """

    def __init__(self, kind: str, parent=None, size=QSize(46, 40), round_hover=False,
                 framed=False):
        super().__init__(parent)
        self.kind = kind
        self.round_hover = round_hover
        self.framed = framed
        self.setFixedSize(size)
        self.setCursor(Qt.PointingHandCursor)
        self.setFocusPolicy(Qt.NoFocus)
        self.setAttribute(Qt.WA_Hover)

    def setKind(self, kind):
        self.kind = kind
        self.update()

    def enterEvent(self, e):
        self.update()
        super().enterEvent(e)

    def leaveEvent(self, e):
        self.update()
        super().leaveEvent(e)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        r = QRectF(self.rect())
        if not self.isEnabled():
            p.setOpacity(0.35)
        if self.framed:   # looks like the other buttons of the form
            p.setPen(QPen(QColor(BORDER_HOVER if self.underMouse() else BORDER), 1))
            p.setBrush(QColor(BUTTON_HOVER if self.underMouse() and self.isEnabled() else BUTTON))
            p.drawRoundedRect(r.adjusted(0.5, 0.5, -0.5, -0.5), 6, 6)
        elif self.underMouse():
            bg = QColor(CLOSE_HOVER) if self.kind == "close" else QColor(255, 255, 255, 30)
            if self.isDown():
                bg = bg.darker(130)
            p.setPen(Qt.NoPen)
            p.setBrush(bg)
            if self.round_hover:
                p.drawRoundedRect(r.adjusted(1, 1, -1, -1), 8, 8)
            else:
                p.drawRect(r)

        draw_icon(p, self.kind, r.center())
        p.end()


# --- Title bar (banner) ----------------------------------------------------
class TitleBar(QWidget):
    """Dark banner replacing the native title bar: drag to move, double-click to
    maximize, minimize / maximize / close buttons."""

    HEIGHT = 40

    def __init__(self, window, title="Fog Project", logo=None, minimize=True, maximize=True):
        super().__init__(window)
        self._window = window
        self.setObjectName("TitleBar")
        self.setAttribute(Qt.WA_StyledBackground)
        self.setFixedHeight(self.HEIGHT)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(14, 0, 0, 0)
        lay.setSpacing(10)
        if logo:
            icon = QLabel()
            icon.setPixmap(tinted_pixmap(logo).scaledToHeight(14, Qt.SmoothTransformation))
            lay.addWidget(icon)
        self.title = QLabel(title)
        self.title.setObjectName("TitleText")
        lay.addWidget(self.title)
        lay.addStretch()

        self.min_btn = self.max_btn = None
        if minimize:
            self.min_btn = IconButton("minimize", self)
            self.min_btn.clicked.connect(window.showMinimized)
            lay.addWidget(self.min_btn)
        if maximize:
            self.max_btn = IconButton("maximize", self)
            self.max_btn.clicked.connect(self.toggle_maximize)
            lay.addWidget(self.max_btn)
        self.close_btn = IconButton("close", self)
        self.close_btn.clicked.connect(window.close)
        lay.addWidget(self.close_btn)

        self.retranslate()

    def retranslate(self):
        if self.min_btn:
            self.min_btn.setToolTip(tr("minimize"))
        self.close_btn.setToolTip(tr("close"))
        self.update_state()

    def toggle_maximize(self):
        if not self.max_btn:
            return
        w = self._window
        w.showNormal() if w.isMaximized() else w.showMaximized()

    def update_state(self):
        if self.max_btn:
            maxed = self._window.isMaximized()
            self.max_btn.setKind("restore" if maxed else "maximize")
            self.max_btn.setToolTip(tr("restore") if maxed else tr("maximize"))

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            handle = self._window.windowHandle()
            if handle is not None:
                handle.startSystemMove()   # native move: keeps Windows snapping
            e.accept()

    def mouseDoubleClickEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.toggle_maximize()


# --- Toggle slider ---------------------------------------------------------
class ToggleSlider(QSlider):
    """Two-position slider styled as a switch; a click anywhere toggles it."""

    def __init__(self, parent=None):
        super().__init__(Qt.Horizontal, parent)
        self.setObjectName("ToggleSlider")
        self.setRange(0, 1)
        self.setPageStep(1)
        self.setFixedSize(44, 22)
        self.setCursor(Qt.PointingHandCursor)
        self.valueChanged.connect(self._update_style)
        self._update_style()

    def _update_style(self):
        # the whole groove is coloured from the "on" property (no partial fill)
        self.setProperty("on", self.value() == 1)
        self.style().unpolish(self)
        self.style().polish(self)

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.setValue(1 - self.value())
            e.accept()

    def mouseMoveEvent(self, e):
        e.accept()

    def mouseReleaseEvent(self, e):
        e.accept()


# --- Alerts ----------------------------------------------------------------
_KINDS = {
    "info": (ACCENT, "i"),
    "warning": (WARNING, "!"),
    "error": (ERROR, "×"),
    "help": (ACCENT, "?"),
}


class _Badge(QWidget):
    def __init__(self, color, glyph, parent=None):
        super().__init__(parent)
        self.color, self.glyph = QColor(color), glyph
        self.setFixedSize(38, 38)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setPen(Qt.NoPen)
        p.setBrush(self.color)
        p.drawEllipse(QRectF(self.rect()).adjusted(1, 1, -1, -1))
        f = QFont("Segoe UI", 14)
        f.setBold(True)
        p.setFont(f)
        p.setPen(QColor(TEXT))
        p.drawText(self.rect(), Qt.AlignCenter, self.glyph)
        p.end()


class ThemedDialog(QDialog):
    """Frameless alert with the same banner as the main window."""

    def __init__(self, parent, kind, text, title="Fog Project", selectable=False, rich=False,
                 buttons=None):
        """buttons: (text, primary, result code) from left to right."""
        super().__init__(parent)
        buttons = buttons or ((tr("ok"), True, QDialog.Accepted),)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setWindowTitle(title)
        self.setModal(True)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        frame = QWidget(self)
        frame.setObjectName("DialogFrame")
        frame.setAttribute(Qt.WA_StyledBackground)
        outer.addWidget(frame)

        lay = QVBoxLayout(frame)
        lay.setContentsMargins(1, 1, 1, 1)
        lay.setSpacing(0)
        bar = TitleBar(self, title, minimize=False, maximize=False)
        bar.close_btn.setFixedSize(QSize(42, 34))
        bar.setFixedHeight(34)
        lay.addWidget(bar)

        body = QHBoxLayout()
        body.setContentsMargins(20, 20, 20, 10)
        body.setSpacing(16)
        color, glyph = _KINDS.get(kind, _KINDS["info"])
        body.addWidget(_Badge(color, glyph), 0, Qt.AlignTop)
        label = QLabel(text)
        label.setObjectName("DialogText")
        label.setWordWrap(True)
        label.setMinimumWidth(440 if rich else 320)
        label.setMaximumWidth(480)
        if rich:
            label.setTextFormat(Qt.RichText)
            label.setOpenExternalLinks(True)
            label.setTextInteractionFlags(Qt.TextBrowserInteraction)
        else:
            label.setTextFormat(Qt.PlainText)
            if selectable:
                label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        body.addWidget(label, 1)
        lay.addLayout(body)

        row = QHBoxLayout()
        row.setContentsMargins(20, 6, 20, 18)
        row.addStretch()
        for text_, primary, code in buttons:
            btn = QPushButton(text_)
            btn.setProperty("primary", primary)
            btn.setMinimumWidth(90)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setDefault(primary)
            btn.clicked.connect(lambda _=False, c=code: self.done(c))
            row.addWidget(btn)
        lay.addLayout(row)


def alert(parent, kind, text, title="Fog Project", selectable=False, rich=False):
    """Show a themed alert. kind: info, warning, error, help."""
    return ThemedDialog(parent, kind, text, title, selectable, rich).exec()


def confirm(parent, text, title="Fog Project", yes=None, no=None) -> bool:
    """Themed yes / no question. Returns True for yes."""
    yes, no = yes or tr("yes"), no or tr("no")
    dlg = ThemedDialog(parent, "help", text, title,
                       buttons=((no, False, QDialog.Rejected), (yes, True, QDialog.Accepted)))
    return dlg.exec() == QDialog.Accepted


# --- Password field ----------------------------------------------------------
class PasswordToggle:
    """Hide a QLineEdit's text (filled circles) and add a show / hide "eye" button."""

    def __init__(self, field: QLineEdit):
        self.field = field
        field.setEchoMode(QLineEdit.Password)
        self.action = QAction(make_icon("eye"), "", field)
        self.action.triggered.connect(self.toggle)
        field.addAction(self.action, QLineEdit.TrailingPosition)
        for btn in field.findChildren(QToolButton):
            btn.setCursor(Qt.PointingHandCursor)
        self.retranslate()

    def toggle(self):
        hidden = self.field.echoMode() == QLineEdit.Password
        self.field.setEchoMode(QLineEdit.Normal if hidden else QLineEdit.Password)
        self.action.setIcon(make_icon("eye_off" if hidden else "eye"))
        self.retranslate()

    def retranslate(self):
        hidden = self.field.echoMode() == QLineEdit.Password
        text = tr("show_key") if hidden else tr("hide_key")
        self.action.setText(text)
        self.action.setToolTip(text)


# --- Side drawer -------------------------------------------------------------
class SideDrawer(QFrame):
    """Panel sliding in from the right edge of its parent."""

    WIDTH = 230

    def __init__(self, parent, title="Aide"):
        super().__init__(parent)
        self.setObjectName("SideDrawer")
        self.setAttribute(Qt.WA_StyledBackground)
        self.setFixedWidth(self.WIDTH)
        self.is_open = False
        self.top = 0

        lay = QVBoxLayout(self)
        lay.setContentsMargins(12, 10, 6, 12)
        lay.setSpacing(4)
        head = QHBoxLayout()
        self.title_label = QLabel(title)
        self.title_label.setObjectName("DrawerTitle")
        head.addWidget(self.title_label)
        head.addStretch()
        self.close_btn = IconButton("close", self, QSize(30, 30), round_hover=True)
        self.close_btn.setToolTip(tr("close"))
        self.close_btn.clicked.connect(self.close_drawer)
        head.addWidget(self.close_btn)
        lay.addLayout(head)
        lay.addSpacing(6)
        self._lay = lay
        self._stretch_added = False

        self.anim = QPropertyAnimation(self, b"pos", self)
        self.anim.setDuration(200)
        self.anim.setEasingCurve(QEasingCurve.OutCubic)
        self.anim.finished.connect(lambda: self.setVisible(self.is_open))
        self.hide()

    def add_button(self, text, icon_kind, slot):
        btn = QPushButton(make_icon(icon_kind), "  " + text)
        btn.setObjectName("DrawerButton")
        btn.setIconSize(QSize(20, 20))
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(slot)
        self._lay.addWidget(btn)
        return btn

    def add_option(self, text, slot):
        """Sub-choice shown under a drawer button (e.g. a language)."""
        btn = QPushButton(text)
        btn.setObjectName("DrawerOption")
        btn.setIconSize(QSize(16, 16))
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(slot)
        self._lay.addWidget(btn)
        return btn

    def set_title(self, title):
        self.title_label.setText(title)
        self.close_btn.setToolTip(tr("close"))

    def _positions(self):
        host = self.parentWidget()
        y = self.top
        shown = QPoint(host.width() - self.WIDTH, y)
        hidden = QPoint(host.width(), y)
        return shown, hidden

    def place(self, top):
        """Re-place after a resize of the parent. `top`: y of the drawer's top."""
        if not self._stretch_added:
            self._lay.addStretch()
            self._stretch_added = True
        self.top = top
        self.setFixedHeight(max(120, self.parentWidget().height() - top - 12))
        if self.anim.state() != QPropertyAnimation.Running:
            shown, hidden = self._positions()
            self.move(shown if self.is_open else hidden)

    def _animate(self, opening):
        self.is_open = opening
        shown, hidden = self._positions()
        self.anim.stop()
        self.anim.setStartValue(self.pos())
        self.anim.setEndValue(shown if opening else hidden)
        self.show()
        self.raise_()
        self.anim.start()

    def open_drawer(self):
        self._animate(True)

    def close_drawer(self):
        if self.is_open:
            self._animate(False)

    def toggle(self):
        self._animate(not self.is_open)


# --- Loading overlay -------------------------------------------------------
class _Spinner(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(34, 34)
        self.angle = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)

    def _tick(self):
        self.angle = (self.angle + 12) % 360
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        r = QRectF(self.rect()).adjusted(4, 4, -4, -4)
        p.setPen(QPen(QColor(255, 255, 255, 40), 3.5))
        p.drawEllipse(r)
        pen = QPen(QColor(TEXT), 3.5)
        pen.setCapStyle(Qt.RoundCap)
        p.setPen(pen)
        p.drawArc(r, -self.angle * 16, 100 * 16)
        p.end()


class LoadingOverlay(QWidget):
    """Semi-transparent mask with a centred card: spinner + message.

    Blocks the mouse and the keyboard while it is shown."""

    def __init__(self, host: QWidget):
        super().__init__(host)
        self.host = host
        self.setFocusPolicy(Qt.StrongFocus)
        self.card = QFrame(self)
        self.card.setObjectName("LoadingCard")
        self.card.setAttribute(Qt.WA_StyledBackground)
        lay = QHBoxLayout(self.card)
        lay.setContentsMargins(24, 20, 28, 20)
        lay.setSpacing(16)
        self.spinner = _Spinner(self.card)
        lay.addWidget(self.spinner)
        self.label = QLabel()
        self.label.setObjectName("LoadingText")
        lay.addWidget(self.label)
        self.hide()

    def run(self, text, action, duration=900):
        """Show `text`, call `action` once the overlay is painted, hide after `duration` ms."""
        self.label.setText(text)
        self.setGeometry(self.host.rect())
        self.card.adjustSize()
        self.card.move((self.width() - self.card.width()) // 2,
                       (self.height() - self.card.height()) // 2)
        self.show()
        self.raise_()
        self.setFocus()
        self.grabKeyboard()
        self.spinner.timer.start(16)
        QTimer.singleShot(250, action)
        QTimer.singleShot(duration, self.finish)

    def finish(self):
        self.spinner.timer.stop()
        self.releaseKeyboard()
        self.hide()

    def paintEvent(self, _):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor(0, 0, 0, 170))
        p.end()

    def mousePressEvent(self, e):
        e.accept()

    def mouseReleaseEvent(self, e):
        e.accept()

    def wheelEvent(self, e):
        e.accept()

    def keyPressEvent(self, e):
        e.accept()

    def focusNextPrevChild(self, _next):
        return True
