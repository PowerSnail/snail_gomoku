from typing import Optional

from PySide2 import QtWidgets, QtGui, QtCore
from PySide2.QtCore import Qt
import numpy as np

from snail_gomoku import gomoku_game, const


_BOARD_BG = QtGui.QColor("#f4e8c1")
_LINE = QtGui.QColor("#000000")
_CONFIG_BG = QtGui.QColor("#70a0af")


class GameBoard(QtWidgets.QWidget):
    clicked = QtCore.Signal((int, int))

    def __init__(self, conf: gomoku_game.GameConfig, parent=None):
        super().__init__(parent)
        self.conf = conf
        self._state: Optional[gomoku_game.GameState] = None

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value
        self.update()

    def heightForWidth(self, w):
        return w

    def paintEvent(self, event: QtGui.QPaintEvent):
        rect = event.rect()

        grid_size = rect.width() / self.conf.size
        grid_pos = [grid_size / 2 + i * grid_size for i in range(self.conf.size)]
        grid_lines = [
            *(QtCore.QLineF(grid_pos[0], pos, grid_pos[-1], pos) for pos in grid_pos),
            *(QtCore.QLineF(pos, grid_pos[0], pos, grid_pos[-1]) for pos in grid_pos),
        ]

        ellipses = [grid_lines[self.conf.size // 2].center()]

        piece_imgs = _black_white_img(grid_size, self.devicePixelRatio())

        p = QtGui.QPainter()
        p.begin(self)

        p.fillRect(rect, _BOARD_BG)

        p.setPen(_LINE)
        p.drawLines(grid_lines)

        p.setBrush(_LINE)
        for e in ellipses:
            p.drawEllipse(e, grid_size / 10, grid_size / 10)

        if self._state is None:
            p.end()
            return

        for turn in (gomoku_game.BLACK, gomoku_game.WHITE):
            ys, xs = np.where(self._state.data[turn])
            for x, y in zip(xs, ys):
                p.drawPixmap(x * grid_size, y * grid_size, piece_imgs[turn])
        p.end()

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        grid_size = self.width() // self.conf.size
        p = event.pos()
        self.clicked.emit(
            p.x() // grid_size, p.y() // grid_size,
        )


class DigitalClock(QtWidgets.QWidget):
    spacing = 10

    def __init__(self, icon: QtGui.QPixmap, parent=None):
        super().__init__(parent)
        self.timer = QtCore.QTimer(self)
        self._time = QtCore.QTime(0, 0)
        self._font = QtGui.QFont()
        self.icon = icon
        self.unit_ms = 100
        self.rotate_deg = 0
        self._setup_ui()

    def _setup_ui(self):
        self.font = QtGui.QFont()
        self.clear()
        self.timer.timeout.connect(self.tick)

    @property
    def font(self):
        return self._font

    @font.setter
    def font(self, value):
        self._font = value
        qm = QtGui.QFontMetrics(self._font, self)
        r = qm.boundingRect("00:00:000")

        self.setMinimumHeight(
            max(self.icon.height() / self.devicePixelRatio(), r.height())
        )
        self.setMinimumWidth(
            self.icon.width() / self.devicePixelRatio() + self.spacing + r.width()
        )

    @property
    def time(self):
        return self._time

    @time.setter
    def time(self, value):
        if value == self._time:
            return
        self._time = value
        self.update()

    def paintEvent(self, e: QtGui.QPaintEvent):
        rect = e.rect()
        text = self.time.toString("mm:ss.z")
        icon_width = self.icon.width() / self.devicePixelRatio()

        p = QtGui.QPainter()
        p.begin(self)
        p.setFont(self.font)
        p.rotate(self.rotate_deg)
        p.drawPixmap(0, 0, self.icon)
        p.drawText(
            icon_width + self.spacing,
            0,
            rect.width() - icon_width - self.spacing,
            rect.height(),
            int(Qt.AlignLeft) | int(Qt.AlignVCenter),
            text,
        )
        p.end()

    def clear(self):
        self.time = QtCore.QTime(0, 0)

    def tick(self):
        self.time = self._time.addMSecs(self.unit_ms)

    def start(self):
        self.timer.start(self.unit_ms)

    def pause(self):
        self.timer.stop()

    def is_active(self):
        return self.timer.isActive()


class GameWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.conf = gomoku_game.GameConfig(15)
        self.history = []

        # Widgets
        self.config_panel = QtWidgets.QWidget()
        self.spinbox_size = QtWidgets.QSpinBox()
        self.lbl_black_icon = QtWidgets.QLabel()
        self.lbl_white_icon = QtWidgets.QLabel()
        self.board_parent = QtWidgets.QWidget()
        self.board = GameBoard(self.conf, parent=self.board_parent)

        black_icon = QtGui.QPixmap(const.BLACK_PIECE_PATH).scaled(
            32 * self.devicePixelRatio(),
            32 * self.devicePixelRatio(),
            mode=Qt.SmoothTransformation,
        )
        black_icon.setDevicePixelRatio(self.devicePixelRatio())

        white_icon = QtGui.QPixmap(const.WHITE_PIECE_PATH).scaled(
            32 * self.devicePixelRatio(),
            32 * self.devicePixelRatio(),
            mode=Qt.SmoothTransformation,
        )
        white_icon.setDevicePixelRatio(self.devicePixelRatio())

        font = QtGui.QFont(self.font())
        font.setPointSize(22)
        
        self.timer_black = DigitalClock(black_icon)
        self.timer_white = DigitalClock(white_icon)
        self.timer_black.rotate = 180
        self.timer_black.font = font
        self.timer_white.font = font

        self.btn_new = QtWidgets.QPushButton("New")
        self.btn_reverse = QtWidgets.QPushButton("Ctrl-Z")

        self._setup()

    def _setup_black_timer(self):
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.lbl_black_icon)
        layout.addWidget(self.timer_black)
        layout.setStretch(0, 0)
        layout.setStretch(1, 1)
        return layout

    def _setup_white_timer(self):
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.lbl_white_icon)
        layout.addWidget(self.timer_white)
        layout.setStretch(0, 0)
        layout.setStretch(1, 1)
        return layout

    def _setup_config_panel(self):
        conf_layout = QtWidgets.QVBoxLayout()
        conf_layout.addWidget(self.btn_new)
        conf_layout.addWidget(self.btn_reverse)
        conf_layout.addWidget(self.spinbox_size)
        return conf_layout

    def _setup_sidebar(self):
        black_t = self._setup_black_timer()
        white_t = self._setup_white_timer()
        conf_panel = self._setup_config_panel()

        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(black_t)
        layout.addStretch(1)
        layout.addLayout(conf_panel)
        layout.addStretch(1)
        layout.addLayout(white_t)

        self.config_panel.setLayout(layout)

    def _setup(self):
        self._setup_sidebar()
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.config_panel)
        layout.addWidget(self.board_parent)
        layout.setStretch(1, 1)

        self.setCentralWidget(QtWidgets.QWidget())
        self.centralWidget().setLayout(layout)

        self.btn_new.clicked.connect(self.on_new_clicked)
        self.board.clicked.connect(self.on_board_click)
        self.btn_reverse.clicked.connect(self.on_reverse_clicked)

    def resizeEvent(self, e):
        self.board.setGeometry(_square_within(self.board_parent.rect()))

    def showEvent(self, e):
        self.board.setGeometry(_square_within(self.board_parent.rect()))

    def on_new_clicked(self):
        if len(self.history) == 0:
            self.history = [gomoku_game.new_game(self.conf)]
            self.update_state()
            self.btn_new.setText("Stop")
        else:
            self.history = []
            self.board.state = None
            self.btn_new.setText("New Game")
            self.update_state()
    
    def on_board_click(self, x, y):
        if len(self.history) == 0:
            return
        r = gomoku_game.put(self.conf, self.history[-1], x, y)
        if r.type == gomoku_game.ResultType.Success:
            self.board.state = r.state
            self.history.append(r.state)

        self.update_state()
        # TODO deal with error messages

    def on_reverse_clicked(self):
        if len(self.history) > 0:
            self.history.pop()
            self.update_state()

    def update_state(self):
        if len(self.history) == 0:
            self.board.state = None
            self.timer_black.pause()
            self.timer_white.pause()
            return

        state = self.history[-1]
        self.board.state = state

        if state.ended:
            self.timer_black.pause()
            self.timer_white.pause()
            side_name = "black" if state.turn == gomoku_game.BLACK else "white"
            QtWidgets.QMessageBox.information(
                self, "Game ended", f"{side_name} has won!"
            )
            return

        if state.turn == gomoku_game.BLACK:
            self.timer_black.start()
            self.timer_white.pause()
        else:
            self.timer_white.start()
            self.timer_black.pause()


def _black_white_img(size, scale):
    piece_size = size * scale
    pieces = [
        QtGui.QPixmap(p).scaled(piece_size, piece_size, mode=Qt.SmoothTransformation)
        for p in (const.BLACK_PIECE_PATH, const.WHITE_PIECE_PATH)
    ]

    for p in pieces:
        p.setDevicePixelRatio(scale)

    return pieces


def _square_within(rect):
    side = min(rect.width(), rect.height())
    x = (rect.width() - side) / 2
    y = (rect.height() - side) / 2
    return QtCore.QRect(x, y, side, side)


def main():
    QtCore.QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QtCore.QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    QtCore.QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts, True)
    application = QtWidgets.QApplication()
    conf = gomoku_game.GameConfig(15)
    w = GameWindow()
    w.resize(1000, 800)
    w.show()
    application.exec_()


if __name__ == "__main__":
    main()
