from PySide2.QtWidgets import (
    QApplication,
    QWidget,
    QGraphicsDropShadowEffect,
    QMainWindow,
    QLCDNumber,
    QGridLayout,
    QMessageBox,
    QPushButton,
    QLabel,
    QToolButton,
    QCheckBox,
    QVBoxLayout,
)
from PySide2.QtGui import (
    QMouseEvent,
    QPaintEvent,
    QPainter,
    QColor,
    QResizeEvent,
    QPixmap,
)
from PySide2.QtCore import QLine, QMargins, Signal, Slot, QRect
from PySide2.QtCore import QLine, QMargins, QTimer, QTime, Qt
from snail_gomoku.board import BoardWrapper, Board
from snail_gomoku import const as C
import numpy as np
from scipy import signal

HFILTER = np.ones((1, 5), dtype=np.int8)
VFILTER = np.ones((5, 1), dtype=np.int8)
DIAG1 = np.eye(5, dtype=np.int8)
DIAG2 = np.rot90(DIAG1)


def has_five(data, side):
    return (
        np.any(signal.convolve2d(data, HFILTER, mode="valid") == side * 5)
        or np.any(signal.convolve2d(data, VFILTER, mode="valid") == side * 5)
        or np.any(signal.convolve2d(data, DIAG1, mode="valid") == side * 5)
        or np.any(signal.convolve2d(data, DIAG2, mode="valid") == side * 5)
    )


class DigitalClock(QLCDNumber):
    def __init__(self, parent):
        super().__init__(parent)
        self.setSegmentStyle(DigitalClock.Filled)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.start_time = QTime(0, 0)
        self.icon = None
        self.setStyleSheet(
        """QFrame {
            border: solid 1px ligthgray;
        }"""
        )
        self.clear()

    def show_time(self):
        text = self.time.toString("mm:ss")
        self.display(text)

    def clear(self):
        self.time = QTime(0, 0)
        self.show_time()

    def tick(self):
        self.time = self.time.addMSecs(50)
        self.show_time()

    def start(self):
        self.timer.start(50)

    def pause(self):
        self.timer.stop()

    def is_active(self):
        return self.timer.isActive()


class TopBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.clock_l = DigitalClock(self)
        self.clock_r = DigitalClock(self)
        self.clock_l.setMinimumHeight(48)
        self.clock_l.setMinimumWidth(100)
        self.clock_r.setMinimumHeight(48)
        self.clock_r.setMinimumWidth(100)

        self.icon_l = QLabel()
        self.icon_l.setPixmap(
            C.IMG_BLACK_PIECE.scaled(64, 64, mode=Qt.SmoothTransformation)
        )

        self.icon_r = QLabel()
        self.icon_r.setPixmap(
            C.IMG_WHITE_PIECE.scaled(64, 64, mode=Qt.SmoothTransformation)
        )

        self.btn_new = QToolButton()
        self.btn_new.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.btn_new.setIcon(C.ICON_NEW)
        self.btn_new.setText("New Game")
        self.btn_new.setMinimumHeight(48)
        self.btn_new.setMinimumWidth(48)
        self.btn_exchange = QToolButton()
        self.btn_exchange.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.btn_exchange.setIcon(C.ICON_EXCHANGE)
        self.btn_exchange.setText("Exchange")
        self.btn_exchange.setMinimumHeight(48)
        self.btn_exchange.setMinimumWidth(48)

        self.cbGoMode = QCheckBox()
        self.cbGoMode.setText("Go Mode")

        layout = QGridLayout()
        layout.addWidget(self.icon_l, 0, 0, alignment=Qt.AlignLeft)
        layout.addWidget(self.clock_l, 0, 1, alignment=Qt.AlignLeft)
        layout.addWidget(self.btn_new, 0, 2, alignment=Qt.AlignCenter)
        layout.addWidget(self.btn_exchange, 0, 3, alignment=Qt.AlignCenter)
        layout.addWidget(self.cbGoMode, 0, 4, alignment=Qt.AlignCenter)
        layout.addWidget(self.clock_r, 0, 5, alignment=Qt.AlignRight)
        layout.addWidget(self.icon_r, 0, 6, alignment=Qt.AlignRight)
        layout.setColumnStretch(0, 0)
        layout.setColumnMinimumWidth(0, 48)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(2, 0)
        layout.setColumnStretch(3, 0)
        layout.setColumnStretch(4, 0)
        layout.setColumnStretch(5, 1)
        layout.setColumnStretch(6, 0)
        layout.setColumnMinimumWidth(6, 48)
        self.setLayout(layout)

    def switch_side(self):
        if self.clock_l.is_active():
            self.clock_l.pause()
            self.clock_r.start()
        else:
            self.clock_r.pause()
            self.clock_l.start()

    def set_lr_side(self, lr, side):
        i = self.icon_l if lr == C.CLOCK_LEFT else self.icon_r
        img = C.IMG_BLACK_PIECE if side == C.SIDE_BLACK else C.IMG_WHITE_PIECE
        i.setPixmap(img)


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.go_mode = False
        self.topbar = TopBar(self)
        self.board = Board(19)
        self.board_w = BoardWrapper(self.board)
        self.current_side = C.SIDE_EMPTY
        self.side_to_lr = {
            C.SIDE_BLACK: C.CLOCK_LEFT,
            C.SIDE_WHITE: C.CLOCK_RIGHT,
        }

        layout = QGridLayout()
        layout.addWidget(self.topbar, 0, 0)
        layout.addWidget(self.board_w, 2, 0)
        layout.setRowStretch(2, 1)

        central_widget = QWidget(self)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.setGeometry(0, 0, 800, 600)
        self.build_event()

    def build_event(self):
        self.topbar.btn_new.clicked.connect(self.start_new_game)
        self.topbar.cbGoMode.stateChanged.connect(self.set_go_mode)

    def set_go_mode(self, state:int):
        if state == Qt.Checked:
            self.go_mode = True
        else:
            self.go_mode = False

    @Slot(int, int)
    def on_board_clicked(self, x, y):
        if self.board[x, y] == C.SIDE_EMPTY:
            self.drop_piece(x, y, self.current_side)
            self.switch_side()
        else:
            self.board[x, y] = C.SIDE_EMPTY

    @Slot()
    def switch_side(self):
        self.current_side = (-1) * self.current_side
        lr = self.side_to_lr[self.current_side]
        self.activate_clock(lr)

    @Slot(int)
    def activate_clock(self, side):
        if side == C.CLOCK_NONE:
            self.topbar.clock_l.pause()
            self.topbar.clock_r.pause()
        elif side == C.CLOCK_LEFT:
            self.topbar.clock_l.start()
            self.topbar.clock_r.pause()
        elif side == C.CLOCK_RIGHT:
            self.topbar.clock_r.start()
            self.topbar.clock_l.pause()
        else:
            assert False

    @Slot()
    def clear_clock(self):
        self.topbar.clock_l.pause()
        self.topbar.clock_r.pause()
        self.topbar.clock_l.clear()
        self.topbar.clock_r.clear()

    @Slot(int, int, int)
    def drop_piece(self, x, y, side):
        assert side == C.SIDE_BLACK or side == C.SIDE_WHITE
        self.board[x, y] = side
        if not self.go_mode and has_five(self.board.data, side):
            side_name = "Black" if side == C.SIDE_BLACK else "White"
            QMessageBox.information(self, "Congratulations!", f"{side_name} has won!")
            self.board.clicked.disconnect(self.on_board_clicked)
            self.topbar.clock_l.pause()
            self.topbar.clock_r.pause()

    @Slot()
    def start_new_game(self):
        self.clear_clock()
        self.current_side = C.SIDE_BLACK
        self.board.data = np.zeros((self.board.size, self.board.size), np.int8)
        self.activate_clock(C.CLOCK_LEFT)
        self.board.clicked.connect(self.on_board_clicked)
        self.board.update()
