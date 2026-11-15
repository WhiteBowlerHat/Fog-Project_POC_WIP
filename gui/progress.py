"""Encryption / decryption in a background thread, with a themed progress alert.

The window stays responsive (the work is done in a QThread) and the user can
cancel until the output starts being written (fog and wind write nothing before
their "save" / "write" stage).
"""
from PySide6.QtCore import QSize, Qt, QThread, Signal
from PySide6.QtWidgets import (QDialog, QHBoxLayout, QLabel, QProgressBar, QPushButton,
    QVBoxLayout, QWidget)

from fog import fog, wind
from gui.device import fit_width
from gui.i18n import tr
from gui.theme import TitleBar, make_icon


WRITE_STAGES = ("save", "write")   # output being written: too late to cancel


class Cancelled(Exception):
    """Raised from the progress callback to stop fog() / wind()."""


class TaskWorker(QThread):
    """Runs func(*args, progress=..., **kwargs) in a background thread."""
    progress = Signal(str, float)      # stage, fraction (0..1)
    succeeded = Signal(object)         # result of func
    failed = Signal(object)            # exception
    cancelled = Signal()

    def __init__(self, func, args, kwargs, parent=None):
        super().__init__(parent)
        self.func, self.args, self.kwargs = func, args, kwargs
        self.cancel_requested = False
        self.stage = ""

    def _report(self, stage, fraction):
        self.stage = stage
        if self.cancel_requested and stage not in WRITE_STAGES:
            raise Cancelled
        self.progress.emit(stage, fraction)

    def run(self):
        try:
            result = self.func(*self.args, progress=self._report, **self.kwargs)
        except Cancelled:
            self.cancelled.emit()
        except Exception as exc:          # shown to the user by the dialog's owner
            self.failed.emit(exc)
        else:
            self.succeeded.emit(result)


class ProgressDialog(QDialog):
    """Themed alert: stage, progress bar with percentage, Cancel button."""

    def __init__(self, parent, title):
        super().__init__(parent)
        self.worker = None
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
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

        body = QVBoxLayout()
        body.setContentsMargins(22, 18, 22, 8)
        body.setSpacing(10)
        self.stage = QLabel(tr("stage_load"))
        self.stage.setObjectName("DialogText")
        self.stage.setMinimumWidth(fit_width(380, margin=80))
        body.addWidget(self.stage)
        self.bar = QProgressBar()
        self.bar.setRange(0, 1000)
        self.bar.setValue(0)
        self.bar.setFormat("0 %")
        self.bar.setAlignment(Qt.AlignCenter)
        self.bar.setFixedHeight(22)
        body.addWidget(self.bar)
        lay.addLayout(body)

        row = QHBoxLayout()
        row.setContentsMargins(22, 6, 22, 18)
        row.addStretch()
        self.cancel_btn = QPushButton(make_icon("close", 16), " " + tr("cancel"))
        self.cancel_btn.setProperty("danger", True)
        self.cancel_btn.setCursor(Qt.PointingHandCursor)
        self.cancel_btn.setMinimumWidth(110)
        self.cancel_btn.clicked.connect(self.request_cancel)
        row.addWidget(self.cancel_btn)
        lay.addLayout(row)

    def attach(self, worker: TaskWorker):
        self.worker = worker
        worker.progress.connect(self.update_progress)
        for signal in (worker.succeeded, worker.failed, worker.cancelled):
            signal.connect(lambda *_: self.accept())

    def update_progress(self, stage, fraction):
        if not (self.worker and self.worker.cancel_requested):
            self.stage.setText(tr("stage_" + stage))
        self.bar.setValue(int(fraction * 1000))
        self.bar.setFormat(f"{fraction * 100:.0f} %")
        if stage in WRITE_STAGES:   # output being written: too late to cancel
            self.cancel_btn.setEnabled(False)
            self.cancel_btn.setToolTip(tr("no_cancel_while_saving"))

    def request_cancel(self):
        if self.worker and self.worker.stage not in WRITE_STAGES:
            self.worker.cancel_requested = True
            self.cancel_btn.setEnabled(False)
            self.stage.setText(tr("cancelling"))

    def reject(self):
        # Escape or the banner's close button: cancel instead of hiding the dialog
        self.request_cancel()

    def closeEvent(self, event):
        if self.worker and self.worker.isRunning():
            self.request_cancel()
            event.ignore()
        else:
            super().closeEvent(event)


def run_task(parent, title, func, args, kwargs=None):
    """Run func with a progress alert.
    Returns ("ok", result) | ("error", exception) | ("cancelled", None)."""
    outcome = {}
    dialog = ProgressDialog(parent, title)
    worker = TaskWorker(func, args, kwargs or {}, parent)
    worker.succeeded.connect(lambda r: outcome.update(kind="ok", value=r))
    worker.failed.connect(lambda e: outcome.update(kind="error", value=e))
    worker.cancelled.connect(lambda: outcome.update(kind="cancelled", value=None))
    dialog.attach(worker)
    worker.start()
    dialog.exec()
    worker.wait()
    worker.deleteLater()
    return outcome.get("kind", "cancelled"), outcome.get("value")


def run_encryption(parent, args, kwargs=None):
    return run_task(parent, tr("progress_title"), fog, args, kwargs)


def run_decryption(parent, args, kwargs=None):
    return run_task(parent, tr("decrypt_progress_title"), wind, args, kwargs)
