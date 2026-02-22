"""Custom-painted timeline widget for the video editor."""

from PySide6.QtWidgets import QWidget, QScrollArea, QVBoxLayout
from PySide6.QtCore import Qt, Signal, QRect, QRectF, QPoint
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QMouseEvent

from apps.video.models import VideoProject, Clip, TrackType

TRACK_HEADER_WIDTH = 80
TRACK_HEIGHT = 50
RULER_HEIGHT = 24
CLIP_MARGIN = 2
PLAYHEAD_COLOR = QColor("#e74c3c")
TRIM_HANDLE_WIDTH = 8


def ms_to_timecode(ms: int) -> str:
    total_s = ms // 1000
    h = total_s // 3600
    m = (total_s % 3600) // 60
    s = total_s % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


class TimelineCanvas(QWidget):
    playhead_moved = Signal(int)   # ms
    clip_selected = Signal(object)  # Clip or None

    def __init__(self, project: VideoProject, parent=None):
        super().__init__(parent)
        self._project = project
        self._pixels_per_ms = 0.1  # default zoom
        self._selected_clip: Clip | None = None
        self._dragging_clip: Clip | None = None
        self._drag_offset_ms = 0
        self._trimming_clip: Clip | None = None
        self._trim_side: str = ""  # "left" or "right"
        self._trim_start_ms = 0

        self.setAcceptDrops(True)
        self.setMouseTracking(True)
        self.setMinimumHeight(RULER_HEIGHT + TRACK_HEIGHT * 4 + 10)
        self._update_size()

    def set_project(self, project: VideoProject):
        self._project = project
        self._update_size()
        self.update()

    def set_zoom(self, pixels_per_ms: float):
        self._pixels_per_ms = max(0.01, min(1.0, pixels_per_ms))
        self._update_size()
        self.update()

    def zoom_in(self):
        self.set_zoom(self._pixels_per_ms * 1.3)

    def zoom_out(self):
        self.set_zoom(self._pixels_per_ms / 1.3)

    def _update_size(self):
        w = TRACK_HEADER_WIDTH + int(self._project.duration_ms * self._pixels_per_ms) + 100
        h = RULER_HEIGHT + TRACK_HEIGHT * len(self._project.tracks) + 10
        self.setMinimumWidth(w)
        self.setMinimumHeight(h)

    def ms_to_x(self, ms: int) -> float:
        return TRACK_HEADER_WIDTH + ms * self._pixels_per_ms

    def x_to_ms(self, x: float) -> int:
        return max(0, int((x - TRACK_HEADER_WIDTH) / self._pixels_per_ms))

    def track_at_y(self, y: float) -> int:
        idx = int((y - RULER_HEIGHT) / TRACK_HEIGHT)
        if idx < 0 or idx >= len(self._project.tracks):
            return -1
        return idx

    def clip_at(self, pos: QPoint) -> Clip | None:
        track_idx = self.track_at_y(pos.y())
        if track_idx < 0:
            return None
        ms = self.x_to_ms(pos.x())
        track = self._project.tracks[track_idx]
        for clip in track.clips:
            if clip.position_ms <= ms <= clip.position_ms + clip.duration_ms:
                return clip
        return None

    def _trim_side_at(self, pos: QPoint, clip: Clip) -> str:
        x_start = self.ms_to_x(clip.position_ms)
        x_end = self.ms_to_x(clip.position_ms + clip.duration_ms)
        if abs(pos.x() - x_start) < TRIM_HANDLE_WIDTH:
            return "left"
        if abs(pos.x() - x_end) < TRIM_HANDLE_WIDTH:
            return "right"
        return ""

    # --- Paint ---

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Ruler
        self._draw_ruler(painter)

        # Tracks
        for i, track in enumerate(self._project.tracks):
            self._draw_track(painter, i, track)

        # Playhead
        self._draw_playhead(painter)

        painter.end()

    def _draw_ruler(self, painter: QPainter):
        painter.fillRect(0, 0, self.width(), RULER_HEIGHT, QColor("#222222"))
        painter.setPen(QPen(QColor("#888888"), 1))
        painter.setFont(QFont("Segoe UI", 8))

        # Draw tick marks every second, labels every 5 seconds
        step_ms = 1000
        ms = 0
        while ms <= self._project.duration_ms:
            x = self.ms_to_x(ms)
            if ms % 5000 == 0:
                painter.drawLine(int(x), 0, int(x), RULER_HEIGHT)
                painter.drawText(int(x) + 2, RULER_HEIGHT - 4, ms_to_timecode(ms))
            else:
                painter.drawLine(int(x), RULER_HEIGHT - 8, int(x), RULER_HEIGHT)
            ms += step_ms

    def _draw_track(self, painter: QPainter, index: int, track):
        y = RULER_HEIGHT + index * TRACK_HEIGHT
        # Track background
        bg = QColor("#2a2a2a") if index % 2 == 0 else QColor("#252525")
        painter.fillRect(0, y, self.width(), TRACK_HEIGHT, bg)

        # Track header
        painter.fillRect(0, y, TRACK_HEADER_WIDTH, TRACK_HEIGHT, QColor("#1e1e1e"))
        painter.setPen(QPen(QColor("#aaaaaa"), 1))
        painter.setFont(QFont("Segoe UI", 10, QFont.Bold))
        painter.drawText(QRect(0, y, TRACK_HEADER_WIDTH, TRACK_HEIGHT),
                         Qt.AlignCenter, track.name)

        # Border
        painter.setPen(QPen(QColor("#333333"), 1))
        painter.drawLine(0, y + TRACK_HEIGHT - 1, self.width(), y + TRACK_HEIGHT - 1)

        # Clips
        for clip in track.clips:
            self._draw_clip(painter, clip, y)

    def _draw_clip(self, painter: QPainter, clip: Clip, track_y: int):
        x = self.ms_to_x(clip.position_ms)
        w = clip.duration_ms * self._pixels_per_ms
        y = track_y + CLIP_MARGIN
        h = TRACK_HEIGHT - 2 * CLIP_MARGIN

        # Clip body
        color = QColor(clip.color)
        is_selected = (clip is self._selected_clip)
        if is_selected:
            color = color.lighter(130)

        painter.setBrush(QBrush(color))
        border_color = QColor("#ffffff") if is_selected else QColor("#555555")
        painter.setPen(QPen(border_color, 2 if is_selected else 1))
        painter.drawRoundedRect(QRectF(x, y, w, h), 4, 4)

        # Clip label
        painter.setPen(QPen(QColor("#ffffff"), 1))
        painter.setFont(QFont("Segoe UI", 8))
        text_rect = QRectF(x + 4, y + 2, w - 8, h - 4)
        painter.drawText(text_rect, Qt.AlignLeft | Qt.AlignVCenter,
                         painter.fontMetrics().elidedText(clip.name, Qt.ElideRight, int(w - 8)))

        # Trim handles
        if is_selected:
            handle_color = QColor("#e67e22")
            painter.fillRect(QRectF(x, y, TRIM_HANDLE_WIDTH, h), handle_color)
            painter.fillRect(QRectF(x + w - TRIM_HANDLE_WIDTH, y, TRIM_HANDLE_WIDTH, h), handle_color)

    def _draw_playhead(self, painter: QPainter):
        x = self.ms_to_x(self._project.playhead_ms)
        painter.setPen(QPen(PLAYHEAD_COLOR, 2))
        painter.drawLine(int(x), 0, int(x), self.height())

        # Playhead triangle
        painter.setBrush(QBrush(PLAYHEAD_COLOR))
        painter.setPen(Qt.NoPen)
        from PySide6.QtGui import QPolygon
        triangle = QPolygon([
            QPoint(int(x) - 6, 0),
            QPoint(int(x) + 6, 0),
            QPoint(int(x), 10),
        ])
        painter.drawPolygon(triangle)

    # --- Mouse Events ---

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() != Qt.LeftButton:
            return
        pos = event.position().toPoint()

        # Click on ruler = move playhead
        if pos.y() < RULER_HEIGHT:
            ms = self.x_to_ms(pos.x())
            self._project.playhead_ms = ms
            self.playhead_moved.emit(ms)
            self.update()
            return

        clip = self.clip_at(pos)
        if clip:
            trim_side = self._trim_side_at(pos, clip)
            if trim_side and clip is self._selected_clip:
                self._trimming_clip = clip
                self._trim_side = trim_side
                self._trim_start_ms = self.x_to_ms(pos.x())
            else:
                self._selected_clip = clip
                self._dragging_clip = clip
                self._drag_offset_ms = self.x_to_ms(pos.x()) - clip.position_ms
                self.clip_selected.emit(clip)
        else:
            self._selected_clip = None
            self.clip_selected.emit(None)
            # Move playhead
            ms = self.x_to_ms(pos.x())
            self._project.playhead_ms = ms
            self.playhead_moved.emit(ms)

        self.update()

    def mouseMoveEvent(self, event: QMouseEvent):
        pos = event.position().toPoint()

        if self._dragging_clip:
            ms = max(0, self.x_to_ms(pos.x()) - self._drag_offset_ms)
            self._dragging_clip.position_ms = ms
            # Check track change
            track_idx = self.track_at_y(pos.y())
            if track_idx >= 0 and track_idx != self._dragging_clip.track_index:
                old_track = self._project.tracks[self._dragging_clip.track_index]
                new_track = self._project.tracks[track_idx]
                if self._dragging_clip in old_track.clips:
                    old_track.clips.remove(self._dragging_clip)
                    new_track.clips.append(self._dragging_clip)
                    self._dragging_clip.track_index = track_idx
            self.update()
            return

        if self._trimming_clip:
            ms = self.x_to_ms(pos.x())
            if self._trim_side == "left":
                delta = ms - self._trim_start_ms
                new_pos = self._trimming_clip.position_ms + delta
                new_dur = self._trimming_clip.duration_ms - delta
                if new_dur > 100 and new_pos >= 0:
                    self._trimming_clip.position_ms = new_pos
                    self._trimming_clip.duration_ms = new_dur
                    self._trimming_clip.in_point_ms += delta
                    self._trim_start_ms = ms
            elif self._trim_side == "right":
                delta = ms - self._trim_start_ms
                new_dur = self._trimming_clip.duration_ms + delta
                if new_dur > 100:
                    self._trimming_clip.duration_ms = new_dur
                    self._trimming_clip.out_point_ms += delta
                    self._trim_start_ms = ms
            self.update()
            return

        # Cursor hint
        clip = self.clip_at(pos)
        if clip and clip is self._selected_clip:
            side = self._trim_side_at(pos, clip)
            if side:
                self.setCursor(Qt.SizeHorCursor)
            else:
                self.setCursor(Qt.ArrowCursor)
        else:
            self.setCursor(Qt.ArrowCursor)

    def mouseReleaseEvent(self, event: QMouseEvent):
        self._dragging_clip = None
        self._trimming_clip = None
        self._trim_side = ""

    # --- Drag & Drop ---

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("application/x-creative-suite-media-id"):
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event):
        mime = event.mimeData()
        if not mime.hasFormat("application/x-creative-suite-media-id"):
            return
        media_id = bytes(mime.data("application/x-creative-suite-media-id")).decode("utf-8")
        media_item = self._project.get_media_item(media_id)
        if not media_item:
            return

        pos = event.position().toPoint()
        track_idx = self.track_at_y(pos.y())
        if track_idx < 0:
            track_idx = 0
        position_ms = self.x_to_ms(pos.x())

        self._project.add_clip_to_track(track_idx, media_item, position_ms)
        self._update_size()
        self.update()
        event.acceptProposedAction()

    # --- Public API ---

    def set_playhead(self, ms: int):
        self._project.playhead_ms = ms
        self.update()


class TimelineWidget(QWidget):
    """Scrollable timeline container."""
    playhead_moved = Signal(int)
    clip_selected = Signal(object)

    def __init__(self, project: VideoProject, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self._scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self._canvas = TimelineCanvas(project)
        self._canvas.playhead_moved.connect(self.playhead_moved.emit)
        self._canvas.clip_selected.connect(self.clip_selected.emit)

        self._scroll.setWidget(self._canvas)
        layout.addWidget(self._scroll)

    @property
    def canvas(self) -> TimelineCanvas:
        return self._canvas

    def set_playhead(self, ms: int):
        self._canvas.set_playhead(ms)

    def set_project(self, project: VideoProject):
        self._canvas.set_project(project)

    def zoom_in(self):
        self._canvas.zoom_in()

    def zoom_out(self):
        self._canvas.zoom_out()
