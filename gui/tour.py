"""Guided tour: dark mask over the window, a hole around the current field, a
white line from an explanation bubble to the field, and Previous / Next buttons.

While the tour runs, the overlay swallows every mouse and keyboard event, so
nothing under it can be used: only the tour navigation works (the banner above
stays usable to move / close the window).
"""
from dataclasses import dataclass
from typing import List

from PySide6.QtCore import QEvent, QPoint, QPointF, QRect, QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from gui.i18n import tr

MASK = QColor(0, 0, 0, 185)
WHITE = QColor("#ffffff")
PAD = 8            # space between the field and the highlight
GAP = 70           # horizontal length of the white line
BUBBLE_WIDTH = 310
MARGIN = 14


@dataclass
class Step:
    targets: List[QWidget]          # widgets to highlight together
    title: str
    text: str
    side: str = "auto"              # where the bubble goes: auto, left, right


class TourOverlay(QWidget):
    def __init__(self, host: QWidget, steps: List[Step], on_finish=None):
        super().__init__(host)
        self.host = host
        self.steps = steps
        self.on_finish = on_finish
        self.index = 0
        self.setFocusPolicy(Qt.StrongFocus)
        self.setMouseTracking(True)
        host.installEventFilter(self)

        self.bubble = QFrame(self)
        self.bubble.setObjectName("TourBubble")
        self.bubble.setAttribute(Qt.WA_StyledBackground)
        self.bubble.setFixedWidth(BUBBLE_WIDTH)
        lay = QVBoxLayout(self.bubble)
        lay.setContentsMargins(16, 14, 16, 14)
        lay.setSpacing(8)
        top = QHBoxLayout()
        self.title = QLabel()
        self.title.setObjectName("TourTitle")
        self.title.setWordWrap(True)
        top.addWidget(self.title, 1)
        self.counter = QLabel()
        top.addWidget(self.counter, 0, Qt.AlignTop)
        lay.addLayout(top)
        self.text = QLabel()
        self.text.setObjectName("TourText")
        self.text.setWordWrap(True)
        self.text.setTextFormat(Qt.RichText)
        lay.addWidget(self.text)
        nav = QHBoxLayout()
        nav.setContentsMargins(0, 6, 0, 0)
        self.quit_btn = QPushButton()
        self.prev_btn = QPushButton()
        self.next_btn = QPushButton()
        self.next_btn.setProperty("primary", True)
        for b in (self.quit_btn, self.prev_btn, self.next_btn):
            b.setCursor(Qt.PointingHandCursor)
            b.setFocusPolicy(Qt.NoFocus)
            b.setMinimumHeight(28)
        nav.addWidget(self.quit_btn)
        nav.addStretch()
        nav.addWidget(self.prev_btn)
        nav.addWidget(self.next_btn)
        lay.addLayout(nav)
        self.quit_btn.clicked.connect(self.finish)
        self.prev_btn.clicked.connect(self.previous)
        self.next_btn.clicked.connect(self.next)
        self.hide()

    # --- navigation --------------------------------------------------------
    def start(self):
        self.setGeometry(self.host.rect())
        self.show()
        self.raise_()
        self.setFocus()
        self.grabKeyboard()          # no Tab into the fields under the mask
        self.go(0)

    def go(self, i):
        self.index = max(0, min(i, len(self.steps) - 1))
        step = self.steps[self.index]
        self.title.setText(step.title)
        self.text.setText(step.text)
        self.counter.setText(f"{self.index + 1} / {len(self.steps)}")
        self.prev_btn.setEnabled(self.index > 0)
        last = self.index == len(self.steps) - 1
        self.next_btn.setText(tr("tour_finish") if last else tr("tour_next"))
        self.prev_btn.setText(tr("tour_prev"))
        self.quit_btn.setText(tr("tour_quit"))
        self.layout_bubble()
        self.update()

    def next(self):
        if self.index == len(self.steps) - 1:
            self.finish()
        else:
            self.go(self.index + 1)

    def previous(self):
        self.go(self.index - 1)

    def finish(self):
        self.releaseKeyboard()
        self.host.removeEventFilter(self)
        self.hide()
        self.deleteLater()
        if self.on_finish:
            self.on_finish()

    # --- geometry ----------------------------------------------------------
    def hole(self) -> QRect:
        rect = QRect()
        for w in self.steps[self.index].targets:
            if w.isVisible():
                # map through the host (a common ancestor), then into the overlay
                top_left = w.mapTo(self.host, QPoint(0, 0)) - self.pos()
                rect = rect.united(QRect(top_left, w.size()))
        return rect.adjusted(-PAD, -PAD, PAD, PAD)

    def bubble_on_right(self, hole: QRect) -> bool:
        side = self.steps[self.index].side
        if side in ("left", "right"):
            return side == "right"
        return hole.center().x() < self.width() / 2

    def layout_bubble(self):
        self.bubble.adjustSize()
        hole = self.hole()
        bw, bh = self.bubble.width(), self.bubble.height()
        if self.bubble_on_right(hole):
            x = hole.right() + GAP
        else:
            x = hole.left() - GAP - bw
        x = max(MARGIN, min(x, self.width() - bw - MARGIN))
        y = hole.center().y() - bh // 2
        y = max(MARGIN, min(y, self.height() - bh - MARGIN))
        self.bubble.move(x, y)

    def eventFilter(self, obj, event):
        if obj is self.host and event.type() == QEvent.Resize:
            self.setGeometry(self.host.rect())
            self.layout_bubble()
        return False

    # --- painting ----------------------------------------------------------
    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        hole = QRectF(self.hole())

        # mask everywhere except the highlighted field
        mask = QPainterPath()
        mask.addRect(QRectF(self.rect()))
        cut = QPainterPath()
        cut.addRoundedRect(hole, 10, 10)
        p.fillPath(mask.subtracted(cut), MASK)

        # white outline around the field
        p.setPen(QPen(WHITE, 2))
        p.setBrush(Qt.NoBrush)
        p.drawRoundedRect(hole, 10, 10)

        # white line from the bubble to the field
        b = QRectF(self.bubble.geometry())
        if b.left() >= hole.right():
            start_x, end_x = b.left(), hole.right()
        else:
            start_x, end_x = b.right(), hole.left()
        end_y = hole.center().y()
        start_y = max(b.top() + 22, min(end_y, b.bottom() - 22))
        start, end = QPointF(start_x, start_y), QPointF(end_x, end_y)
        p.setPen(QPen(WHITE, 2))
        p.drawLine(start, end)
        p.setPen(Qt.NoPen)
        p.setBrush(WHITE)
        p.drawEllipse(end, 4.5, 4.5)
        p.drawEllipse(start, 3, 3)
        p.end()

    # --- block everything under the mask -----------------------------------
    def mousePressEvent(self, e):
        e.accept()

    def mouseReleaseEvent(self, e):
        e.accept()

    def mouseDoubleClickEvent(self, e):
        e.accept()

    def wheelEvent(self, e):
        e.accept()

    def focusNextPrevChild(self, _next):
        return True   # Tab / Shift+Tab must not reach the fields under the mask

    def keyPressEvent(self, e):
        key = e.key()
        if key in (Qt.Key_Right, Qt.Key_Return, Qt.Key_Enter, Qt.Key_Space):
            self.next()
        elif key == Qt.Key_Left:
            self.previous()
        elif key == Qt.Key_Escape:
            self.finish()
        e.accept()
