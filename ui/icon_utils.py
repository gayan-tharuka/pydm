"""
Icon Utils - Vector icon generation for PyDM

Provides scalable, hand-drawn vector icons using QPainter to avoid
dependency on external image files or crash-prone emojis.
"""

from PyQt6.QtGui import (
    QIcon, QPainter, QColor, QPixmap, QPen,
    QPainterPath, QBrush, QPolygonF
)
from PyQt6.QtCore import Qt, QPointF, QRectF, QSize


class IconUtils:
    """Utility class for generating vector icons"""
    
    @staticmethod
    def icon(name: str, color: str = "#FFFFFF", size: int = 24) -> QIcon:
        """Create a QIcon with the given name and color"""
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw icon based on name
        if name == "play" or name == "resume":
            IconUtils._draw_play(painter, color, size)
        elif name == "pause":
            IconUtils._draw_pause(painter, color, size)
        elif name == "stop" or name == "cancel" or name == "remove":
            IconUtils._draw_close(painter, color, size)
        elif name == "add":
            IconUtils._draw_add(painter, color, size)
        elif name == "folder":
            IconUtils._draw_folder(painter, color, size)
        elif name == "file":
            IconUtils._draw_file(painter, color, size)
        elif name == "video":
            IconUtils._draw_video_file(painter, color, size)
        elif name == "audio":
            IconUtils._draw_audio_file(painter, color, size)
        elif name == "image":
            IconUtils._draw_image_file(painter, color, size)
        elif name == "archive":
            IconUtils._draw_archive_file(painter, color, size)
        elif name == "settings":
            IconUtils._draw_settings(painter, color, size)
        elif name == "clear":
            IconUtils._draw_trash(painter, color, size)
        
        painter.end()
        return QIcon(pixmap)
    
    # --- Drawing primitives ---
    
    @staticmethod
    def _draw_play(p: QPainter, color: str, s: int):
        p.setBrush(QBrush(QColor(color)))
        p.setPen(Qt.PenStyle.NoPen)
        
        # Triangle
        padding = s * 0.2
        path = QPainterPath()
        path.moveTo(padding, padding)
        path.lineTo(s - padding, s / 2)
        path.lineTo(padding, s - padding)
        path.closeSubpath()
        p.drawPath(path)

    @staticmethod
    def _draw_pause(p: QPainter, color: str, s: int):
        p.setBrush(QBrush(QColor(color)))
        p.setPen(Qt.PenStyle.NoPen)
        
        w = s * 0.2
        h = s * 0.6
        gap = s * 0.2
        x1 = (s - (2 * w + gap)) / 2
        
        p.drawRoundedRect(QRectF(x1, (s-h)/2, w, h), 2, 2)
        p.drawRoundedRect(QRectF(x1 + w + gap, (s-h)/2, w, h), 2, 2)

    @staticmethod
    def _draw_close(p: QPainter, color: str, s: int):
        pen = QPen(QColor(color))
        pen.setWidthF(2.5)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(pen)
        
        padding = s * 0.25
        p.drawLine(QPointF(padding, padding), QPointF(s - padding, s - padding))
        p.drawLine(QPointF(s - padding, padding), QPointF(padding, s - padding))

    @staticmethod
    def _draw_add(p: QPainter, color: str, s: int):
        pen = QPen(QColor(color))
        pen.setWidthF(2.5)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(pen)
        
        padding = s * 0.2
        mid = s / 2
        p.drawLine(QPointF(mid, padding), QPointF(mid, s - padding))
        p.drawLine(QPointF(padding, mid), QPointF(s - padding, mid))

    @staticmethod
    def _draw_folder(p: QPainter, color: str, s: int):
        p.setPen(QPen(QColor(color), 1.5))
        p.setBrush(QBrush(QColor(color).lighter(150)))
        
        margin = s * 0.15
        width = s - 2 * margin
        height = s * 0.55
        
        # Folder tab
        path = QPainterPath()
        path.moveTo(margin, margin + s * 0.2)
        path.lineTo(margin + width * 0.4, margin + s * 0.2)
        path.lineTo(margin + width * 0.5, margin + s * 0.3)
        path.lineTo(s - margin, margin + s * 0.3)
        path.lineTo(s - margin, s - margin)
        path.lineTo(margin, s - margin)
        path.closeSubpath()
        
        p.drawPath(path)

    @staticmethod
    def _draw_file(p: QPainter, color: str, s: int):
        pen = QPen(QColor(color), 1.5)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        p.setPen(pen)
        
        margin = s * 0.2
        width = s - 2 * margin
        height = s * 0.75
        
        # Document shape with fold
        path = QPainterPath()
        path.moveTo(margin, margin)
        path.lineTo(margin + width * 0.6, margin)
        path.lineTo(s - margin, margin + width * 0.4)
        path.lineTo(s - margin, s - margin)
        path.lineTo(margin, s - margin)
        path.closeSubpath()
        p.drawPath(path)
        
        # Fold line
        p.drawLine(QPointF(margin + width * 0.6, margin), QPointF(margin + width * 0.6, margin + width * 0.4))
        p.drawLine(QPointF(margin + width * 0.6, margin + width * 0.4), QPointF(s - margin, margin + width * 0.4))

    @staticmethod
    def _draw_video_file(p: QPainter, color: str, s: int):
        IconUtils._draw_file(p, color, s)
        # Play triangle in center
        p.setBrush(QBrush(QColor(color)))
        p.setPen(Qt.PenStyle.NoPen)
        
        mid = s / 2
        sz = s * 0.15
        
        path = QPainterPath()
        path.moveTo(mid - sz/2, mid - sz)
        path.lineTo(mid + sz, mid)
        path.lineTo(mid - sz/2, mid + sz)
        path.closeSubpath()
        p.drawPath(path)

    @staticmethod
    def _draw_audio_file(p: QPainter, color: str, s: int):
        IconUtils._draw_file(p, color, s)
        # Simple note
        p.setPen(QPen(QColor(color), 1.5))
        mid = s / 2
        off = s * 0.1
        
        p.drawLine(QPointF(mid - off, mid + off), QPointF(mid - off, mid - off))
        p.drawLine(QPointF(mid - off, mid - off), QPointF(mid + off, mid - off))
        p.drawLine(QPointF(mid + off, mid - off), QPointF(mid + off, mid + off))

    @staticmethod
    def _draw_image_file(p: QPainter, color: str, s: int):
        IconUtils._draw_file(p, color, s)
        # Mountains
        p.setPen(QPen(QColor(color), 1))
        mid = s / 2
        sz = s * 0.2
        
        path = QPainterPath()
        path.moveTo(mid - sz, mid + sz)
        path.lineTo(mid - sz/2, mid)
        path.lineTo(mid, mid + sz)
        path.lineTo(mid + sz/2, mid - sz/2)
        path.lineTo(mid + sz, mid + sz)
        p.drawPath(path)

    @staticmethod
    def _draw_archive_file(p: QPainter, color: str, s: int):
        IconUtils._draw_file(p, color, s)
        # Zipper lines
        p.setPen(QPen(QColor(color), 1))
        mid = s / 2
        p.drawLine(QPointF(mid, mid - s*0.1), QPointF(mid, mid + s*0.2))
        p.drawLine(QPointF(mid - 2, mid - s*0.1), QPointF(mid + 2, mid - s*0.1))
        p.drawLine(QPointF(mid - 2, mid), QPointF(mid + 2, mid))

    @staticmethod
    def _draw_settings(p: QPainter, color: str, s: int):
        pen = QPen(QColor(color))
        pen.setWidth(2)
        p.setPen(pen)
        
        margin = s * 0.25
        p.drawEllipse(QPointF(s/2, s/2), s/2 - margin, s/2 - margin)
        p.drawPoint(QPointF(s/2, s/2))

    @staticmethod
    def _draw_trash(p: QPainter, color: str, s: int):
        pen = QPen(QColor(color))
        pen.setWidthF(1.5)
        p.setPen(pen)
        
        m = s * 0.25
        # Lid
        p.drawLine(QPointF(m, m), QPointF(s-m, m))
        p.drawLine(QPointF(s/2 - 2, m), QPointF(s/2 - 2, m-3))
        p.drawLine(QPointF(s/2 + 2, m), QPointF(s/2 + 2, m-3))
        p.drawLine(QPointF(s/2 - 2, m-3), QPointF(s/2 + 2, m-3))
        
        # Bin
        p.drawRoundedRect(QRectF(m + 2, m, s - 2*m - 4, s - 2*m), 2, 2)
        
        # Lines
        p.drawLine(QPointF(s/2, m+3), QPointF(s/2, s-m-3))
