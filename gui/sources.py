"""Input images of the encryption and of the decryption: folders and / or PNG images.

SourcesPicker is the "Input images" selector of a panel; SourcesDialog lists them (name, path, number of images, size on disk, capacity)
and lets the user remove one, or all of them.
"""
import os

from PySide6.QtCore import QRect, QSize, Qt
from PySide6.QtWidgets import (QDialog, QFileDialog, QFrame, QHBoxLayout, QLabel, QMenu,
    QPushButton, QScrollArea, QVBoxLayout, QWidget)

from fog import (BYTES_PER_PIXEL, LARGE_IMAGE_PIXELS, NATIVE_EXTENSIONS, check_image,
    image_size, list_images, required_bits)
from gui.device import IS_ANDROID, fit_width, to_local_path
from gui.i18n import format_size, tr
from gui.theme import WARNING, IconButton, TitleBar, alert, confirm, make_icon


def same_path(a, b):
    return os.path.normcase(os.path.realpath(a)) == os.path.normcase(os.path.realpath(b))


def allowed(path, exts):
    return os.path.splitext(path)[1].lower() in exts


def source_files(source, exts=NATIVE_EXTENSIONS):
    """Image files given by one source (a folder or an image) in the allowed formats."""
    if os.path.isdir(source):
        return list_images(source, exts)
    return [source] if os.path.isfile(source) and allowed(source, exts) else []


def image_problems(source, exts=NATIVE_EXTENSIONS):
    """Images of `source` that cannot be used: [(file, "unreadable" | "format")]."""
    if os.path.isfile(source) and not allowed(source, exts):
        return [(source, "format")]
    problems = []
    for f in source_files(source, exts):
        try:
            check_image(f)
        except (OSError, ValueError):
            problems.append((f, "unreadable"))
    return problems


def large_images_of(sources, exts=NATIVE_EXTENSIONS):
    """[(file, (width, height))] of the very large images (accepted, but they need
    a lot of memory and time)."""
    found = []
    for f in unique_files(sources, exts):
        try:
            w, h = image_size(f)
        except (OSError, ValueError):
            continue
        if w * h >= LARGE_IMAGE_PIXELS:
            found.append((f, (w, h)))
    return found


def memory_needed(large):
    """Memory estimate (in bits, for format_size) to load the given large images."""
    return 8 * BYTES_PER_PIXEL * sum(w * h for _, (w, h) in large)


def large_lines(large, base=None):
    """"• name : 29500 × 29500 (870 Mpx)" lines for an alert or a tooltip."""
    lines = []
    for f, (w, h) in large:
        name = os.path.basename(f)
        lines.append("• " + tr("large_line", name=name, w=w, h=h, mpx=round(w * h / 1e6)))
    return lines


def disk_bits(files):
    """Size on disk of `files`, in bits (so that format_size can display it)."""
    return 8 * sum(os.path.getsize(f) for f in files if os.path.isfile(f))


def unique_files(sources, exts=NATIVE_EXTENSIONS):
    """Distinct image files of all the sources (an image listed twice counts once)."""
    files, seen = [], set()
    for source in sources:
        for f in source_files(source, exts):
            key = os.path.normcase(os.path.realpath(f))
            if key not in seen:
                seen.add(key)
                files.append(f)
    return files


def safe_capacity(sources, exts=NATIVE_EXTENSIONS):
    """Capacity in bits (1 bit per pixel); unreadable images count for 0."""
    total = 0
    for f in unique_files(sources, exts):
        try:
            total += check_image(f)
        except (OSError, ValueError):
            pass
    return total


def total_images(sources, exts=NATIVE_EXTENSIONS):
    return len(unique_files(sources, exts))


def add_sources(sources, new_paths):
    """Append the paths that are not already in `sources`. Returns how many were added."""
    added = 0
    for path in new_paths:
        path = os.path.normpath(path)
        if not any(same_path(path, s) for s in sources):
            sources.append(path)
            added += 1
    return added


class _SourceRow(QFrame):
    def __init__(self, path, on_remove, exts=NATIVE_EXTENSIONS, parent=None):
        super().__init__(parent)
        self.setObjectName("SourceRow")
        self.setAttribute(Qt.WA_StyledBackground)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(10, 6, 6, 6)
        lay.setSpacing(10)

        is_dir = os.path.isdir(path)
        files = source_files(path, exts)
        icon = QLabel()
        icon.setPixmap(make_icon("folder" if is_dir else "image", 20).pixmap(20, 20))
        lay.addWidget(icon)

        text = QVBoxLayout()
        text.setSpacing(0)
        name = QLabel(os.path.basename(path.rstrip("\\/")) or path)
        name.setObjectName("SourceName")
        full = QLabel(path)
        full.setObjectName("SourcePath")
        full.setToolTip(path)
        full.setMinimumWidth(10)
        text.addWidget(name)
        text.addWidget(full)
        lay.addLayout(text, 1)

        # kind / number of images, then size on disk and capacity
        info = QVBoxLayout()
        info.setSpacing(0)
        kind = QLabel(tr("folder_count", n=len(files)) if is_dir else tr("single_image"))
        kind.setObjectName("SourceCount")
        kind.setAlignment(Qt.AlignRight)
        sizes = QLabel(tr("source_sizes", size=format_size(disk_bits(files)),
                          capacity=format_size(safe_capacity([path], exts))))
        sizes.setObjectName("SourceCount")
        sizes.setAlignment(Qt.AlignRight)
        info.addWidget(kind)
        info.addWidget(sizes)
        large = large_images_of([path], exts)
        if large:
            warning = QLabel(tr("large_marker"))
            warning.setObjectName("SourceWarning")
            warning.setAlignment(Qt.AlignRight)
            warning.setToolTip(tr("large_tooltip") + "\n" + "\n".join(large_lines(large)))
            info.addWidget(warning)
        lay.addLayout(info)

        remove = IconButton("trash", self, QSize(30, 30), framed=True)
        remove.setToolTip(tr("remove"))
        remove.clicked.connect(lambda: on_remove(path))
        lay.addWidget(remove)


class SourcesDialog(QDialog):
    """Themed alert listing the input images; changes `sources` in place."""

    def __init__(self, parent, sources, on_change=None, exts=NATIVE_EXTENSIONS):
        super().__init__(parent)
        self.sources = sources
        self.exts = exts
        self.on_change = on_change
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
        bar = TitleBar(self, tr("sources_title"), minimize=False, maximize=False)
        bar.close_btn.setFixedSize(QSize(42, 34))
        bar.setFixedHeight(34)
        lay.addWidget(bar)

        body = QVBoxLayout()
        body.setContentsMargins(20, 16, 20, 8)
        body.setSpacing(10)
        self.summary = QLabel()
        self.summary.setObjectName("SourcesSummary")
        body.addWidget(self.summary)

        self.list_widget = QWidget()
        self.list_layout = QVBoxLayout(self.list_widget)
        self.list_layout.setContentsMargins(0, 0, 4, 0)
        self.list_layout.setSpacing(6)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setWidget(self.list_widget)
        scroll.setMinimumSize(fit_width(560), 220)
        scroll.setMaximumHeight(320)
        body.addWidget(scroll)
        lay.addLayout(body)

        row = QHBoxLayout()
        row.setContentsMargins(20, 6, 20, 18)
        self.remove_all = QPushButton(make_icon("trash", 16), "  " + tr("remove_all"))
        self.remove_all.setProperty("danger", True)
        self.remove_all.setCursor(Qt.PointingHandCursor)
        self.remove_all.clicked.connect(self.clear_all)
        row.addWidget(self.remove_all)
        row.addStretch()
        close = QPushButton(tr("close"))
        close.setProperty("primary", True)
        close.setMinimumWidth(90)
        close.setCursor(Qt.PointingHandCursor)
        close.setDefault(True)
        close.clicked.connect(self.accept)
        row.addWidget(close)
        lay.addLayout(row)
        self.refresh()

    def refresh(self):
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        for path in self.sources:
            self.list_layout.addWidget(_SourceRow(path, self.remove, self.exts))
        if not self.sources:
            empty = QLabel(tr("no_sources"))
            empty.setAlignment(Qt.AlignCenter)
            self.list_layout.addWidget(empty)
        self.list_layout.addStretch()
        files = unique_files(self.sources, self.exts)
        self.summary.setText(tr("sources_summary", sources=len(self.sources), images=len(files),
                                size=format_size(disk_bits(files)),
                                capacity=format_size(safe_capacity(self.sources, self.exts))))
        self.remove_all.setEnabled(bool(self.sources))

    def remove(self, path):
        self.sources[:] = [s for s in self.sources if s != path]
        self._changed()

    def clear_all(self):
        if confirm(self, tr("remove_all_question"), title=tr("remove_all")):
            self.sources.clear()
            self._changed()

    def _changed(self):
        self.refresh()
        if self.on_change:
            self.on_change()


# --- "Input images" selector (used by the encryption and the decryption) ----
class SourcesPicker:
    """'Input images :' label, then [+ Add v] [info field] [list button] in `box`.

    `message` (encryption only) returns the path of the file to hide: the field
    then shows the capacity and whether the message fits (green) or what is
    missing (red). Without it (decryption) the field shows the number of images
    and their size on disk.
    """

    def __init__(self, window, box, y_label, y_row, left, right, row_h, btn_w, gap,
                 file_dialog_options, message=None):
        self.window, self.box = window, box
        self.options = file_dialog_options
        self.message = message
        self.sources = []
        self.extensions = NATIVE_EXTENSIONS   # formats accepted (see set_extensions)
        width = box.width()
        x_field = left + btn_w + gap
        x_view = width - right - row_h

        self.label = QLabel(box)
        self.label.setGeometry(QRect(left, y_label, width - left - right, 18))
        self.add_button = QPushButton(make_icon("plus", 16), "", box)
        self.add_button.setGeometry(QRect(left, y_row, btn_w, row_h))
        self.add_button.setCursor(Qt.PointingHandCursor)
        self.menu = QMenu(window)
        self.add_images_action = self.menu.addAction(make_icon("image", 18), "", self.add_images)
        self.add_folder_action = self.menu.addAction(make_icon("folder", 18), "", self.add_folder)
        # an Android folder picker gives an address whose files cannot be listed
        self.add_folder_action.setVisible(not IS_ANDROID)
        self.add_button.clicked.connect(
            lambda: self.menu.exec(self.add_button.mapToGlobal(self.add_button.rect().bottomLeft())))

        self.info = QFrame(box)
        self.info.setObjectName("InfoField")
        self.info.setAttribute(Qt.WA_StyledBackground)
        self.info.setGeometry(QRect(x_field, y_row, x_view - gap - x_field, row_h))
        info_layout = QHBoxLayout(self.info)
        info_layout.setContentsMargins(8, 0, 8, 0)
        self.text = QLabel()
        self.text.setObjectName("InfoText")
        self.text.setTextFormat(Qt.RichText)
        self.state = QLabel()
        self.state.setObjectName("InfoState")
        info_layout.addWidget(self.text, 1)
        info_layout.addWidget(self.state)

        self.list_button = IconButton("list", box, QSize(row_h, row_h), framed=True)
        self.list_button.move(x_view, y_row)
        self.list_button.clicked.connect(self.manage)

    def widgets(self):
        """Widgets of the selector (to highlight them in the guided tour)."""
        return [self.label, self.add_button, self.info, self.list_button]

    def retranslate(self):
        self.label.setText(tr("input_images"))
        self.add_button.setText(" " + tr("add_more"))
        self.add_images_action.setText(tr("add_images"))
        self.add_folder_action.setText(tr("add_folder"))
        self.list_button.setToolTip(tr("manage_sources"))
        self.update()

    # --- adding / removing ---------------------------------------------------
    def add_images(self):
        patterns = " ".join("*" + e for e in self.extensions)
        files, _ = QFileDialog.getOpenFileNames(self.window, tr("dlg_add_images"), "",
                                                tr("images_filter", patterns=patterns), "",
                                                self.options)
        if files:
            try:
                files = [to_local_path(f) for f in files]   # Android: copies of the picks
            except OSError as exc:
                alert(self.window, "error", str(exc))
                return
            self.add_checked(files)

    def add_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self.window, tr("dlg_add_folder"), "", QFileDialog.ShowDirsOnly | self.options)
        if folder:
            self.add_checked([folder])

    def add_checked(self, paths):
        """Add the sources whose images can all be read; tell which ones are refused
        (unreadable) and warn about very large images."""
        accepted, lines, folder_refused = [], [], False
        for path in paths:
            problems = image_problems(path, self.extensions)
            if not problems:
                accepted.append(path)
                continue
            is_dir = os.path.isdir(path)
            folder_refused |= is_dir
            for f, kind in problems:
                name = os.path.basename(f)
                if is_dir:
                    name = f"{os.path.basename(os.path.normpath(path))}{os.sep}{name}"
                lines.append(f"• {name} : {tr('reason_' + kind)}")
        if add_sources(self.sources, accepted):
            self.update()
        large = large_images_of(accepted, self.extensions)
        if large:   # accepted, but the user is warned
            listed = large_lines(large)
            if len(listed) > 10:
                listed = listed[:10] + [tr("and_more", n=len(listed) - 10)]
            alert(self.window, "warning", tr("large_images_warning",
                                             mem=format_size(memory_needed(large)),
                                             list="\n".join(listed)))
        if lines:
            if len(lines) > 10:
                lines = lines[:10] + [tr("and_more", n=len(lines) - 10)]
            text = tr("images_refused", list="\n".join(lines))
            if folder_refused:
                text += "\n\n" + tr("folder_refused_hint")
            alert(self.window, "warning", text)

    def manage(self):
        SourcesDialog(self.window, self.sources, on_change=self.update,
                      exts=self.extensions).exec()

    def set_extensions(self, exts):
        """Change the accepted formats. Single images whose format is no longer
        accepted are removed from the list; returns them."""
        self.extensions = tuple(exts)
        removed = [s for s in self.sources if os.path.isfile(s) and not allowed(s, exts)]
        self.sources[:] = [s for s in self.sources if s not in removed]
        self.update()
        return removed

    # --- display ---------------------------------------------------------------
    def update(self):
        has_sources = bool(self.sources)
        self.list_button.setEnabled(has_sources)
        state, tooltip, large = "", "", []
        if not has_sources:
            self.text.setText(tr("no_sources"))
        elif self.message is None:          # decryption: number of images, size on disk
            files = unique_files(self.sources, self.extensions)
            text = tr("images_short", n=len(files), size=format_size(disk_bits(files)))
            large = large_images_of(self.sources, self.extensions)
            if large:
                text += f' <span style="color:{WARNING};">⚠</span>'
            self.text.setText(text)
            tooltip = tr("decrypt_images_hint")
        else:                               # encryption: capacity, does the message fit?
            capacity = safe_capacity(self.sources, self.extensions)
            text = tr("capacity_short", size=format_size(capacity),
                      n=total_images(self.sources, self.extensions))
            large = large_images_of(self.sources, self.extensions)
            if large:   # orange warning sign: very large image(s)
                text += f' <span style="color:{WARNING};">⚠</span>'
            self.text.setText(text)
            tooltip = tr("capacity_hint", cap=format_size(capacity))
            message = self.message() or ""
            try:
                need = required_bits(message) if message else None
            except (OSError, ValueError):
                need = None
            if need is not None:
                if need <= capacity:
                    state, label = "ok", tr("fits_short")
                    tooltip = tr("fits", need=format_size(need), cap=format_size(capacity))
                else:
                    state, label = "missing", "−" + format_size(need - capacity)
                    tooltip = tr("missing", missing=format_size(need - capacity),
                                 need=format_size(need), cap=format_size(capacity))
                self.state.setText(label)
        if not state:
            self.state.clear()
        if large:
            tooltip += "\n\n" + tr("large_tooltip") + "\n" + "\n".join(large_lines(large))
        self.info.setToolTip(tooltip)
        for widget, prop, value in ((self.text, "empty", not has_sources),
                                    (self.state, "state", state)):
            widget.setProperty(prop, value)
            widget.style().unpolish(widget)
            widget.style().polish(widget)
