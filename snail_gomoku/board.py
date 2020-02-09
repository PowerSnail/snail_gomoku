from PySide2.QtWidgets import QApplication, QWidget, QGraphicsDropShadowEffect
from PySide2.QtGui import (
    QMouseEvent,
    QPaintEvent,
    QPainter,
    QColor,
    QResizeEvent,
    QImage,
)
from PySide2.QtCore import QLine, QMargins, Signal, Slot, QRect, QPoint, Qt
import numpy as np
from snail_gomoku import const as C


LINE_PEN = QColor.fromRgb(0, 0, 0)
BG_PEN = QColor.fromRgb(255, 255, 222)


class Board(QWidget):
    clicked = Signal((int, int))
    piece_set = Signal((int, int, int))

    def __init__(self, size, *args):
        super().__init__(*args)
        self.size = size
        self.data = np.zeros((self.size, self.size), np.int8)

    def __getitem__(self, index):
        x, y = index
        return self.data[y, x]

    def __setitem__(self, index, value):
        x, y = index
        if value not in {0, -1, 1}:
            raise ValueError()
        if self.data[y, x] == value:
            return
        self.data[y, x] = value
        self.piece_set.emit(x, y, value)
        self.update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        x = int(event.localPos().x() / (self.width() / self.size))
        y = int(event.localPos().y() / (self.height() / self.size))
        self.clicked.emit(x, y)

    def paintEvent(self, event: QPaintEvent):
        rect = event.rect()
        grid_size = rect.width() / self.size
        padding = grid_size / 2
        p = QPainter(self)
        p.setRenderHints(
            QPainter.Antialiasing
            | QPainter.SmoothPixmapTransform
            | QPainter.HighQualityAntialiasing
        )
        p.fillRect(rect, BG_PEN)
        p.setPen(LINE_PEN)
        coords = [padding + i * grid_size for i in range(self.size)]

        coord_start = padding
        coord_end = grid_size * self.size - padding
        h_lines = (QLine(coord_start, c, coord_end, c) for c in coords)
        v_lines = (QLine(c, coord_start, c, coord_end) for c in coords)
        lines = [*h_lines, *v_lines]
        lines = [line.translated(rect.x(), rect.y()) for line in lines]
        p.drawLines(lines)

        center_coord = lines[self.size // 2].y1()
        p.setBrush(LINE_PEN)
        p.drawEllipse(
            QPoint(center_coord, center_coord), grid_size / 10, grid_size / 10
        )

        for side in [C.SIDE_BLACK, C.SIDE_WHITE]:
            img = C.IMG_BLACK_PIECE if C.SIDE_BLACK == side else C.IMG_WHITE_PIECE
            img = img.scaled(
                grid_size * img.devicePixelRatio(),
                grid_size * img.devicePixelRatio(),
                mode=Qt.SmoothTransformation,
            )
            for y, x in zip(*np.where(self.data == side)):
                p.drawPixmap(x * grid_size, y * grid_size, img)
        p.end()


class BoardWrapper(QWidget):
    def __init__(self, board, *args):
        super().__init__(*args)
        self.board: Board = board
        self.board.setParent(self)

    def resizeEvent(self, event: QResizeEvent):
        w = event.size().width()
        h = event.size().height()
        board_size = min(w, h) - 48
        x = (w - board_size) // 2
        y = (h - board_size) // 2
        self.board.setGeometry(x, y, board_size, board_size)
