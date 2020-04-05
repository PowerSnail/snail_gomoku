from pathlib import Path
from PySide2.QtGui import QPixmap, QIcon
from PySide2.QtCore import Qt

PROJECT_DIR = Path(__file__).parent.parent
IMG_DIR = PROJECT_DIR.joinpath("img")
BLACK_PIECE_PATH = str(IMG_DIR.joinpath("black-piece.svg"))
WHITE_PIECE_PATH = str(IMG_DIR.joinpath("white-piece.svg"))

CLOCK_NONE = 0
CLOCK_LEFT = 1
CLOCK_RIGHT = 2

SIDE_EMPTY = 0
SIDE_BLACK = -1
SIDE_WHITE = 1

IMG_BLACK_PIECE: QPixmap = None
IMG_WHITE_PIECE: QPixmap = None

ICON_NEW : QIcon = None
ICON_EXCHANGE : QIcon = None


def load_imgs(dpi):
    global IMG_BLACK_PIECE
    IMG_BLACK_PIECE = QPixmap(str(img_path.joinpath("black-piece.svg")))
    IMG_BLACK_PIECE.setDevicePixelRatio(dpi)
    global IMG_WHITE_PIECE
    IMG_WHITE_PIECE = QPixmap(str(img_path.joinpath("white-piece.svg")))
    IMG_WHITE_PIECE.setDevicePixelRatio(dpi)
    global ICON_NEW
    _icon = QPixmap(str(img_path.joinpath("new.svg")))
    _icon.setDevicePixelRatio(dpi)
    _icon = _icon.scaled(128, 128, mode=Qt.SmoothTransformation)
    ICON_NEW = QIcon(_icon)
    global ICON_EXCHANGE
    _icon = QPixmap(str(img_path.joinpath("exchange.svg")))
    _icon.setDevicePixelRatio(dpi)
    _icon = _icon.scaled(128, 128, mode=Qt.SmoothTransformation)
    ICON_EXCHANGE = QIcon(_icon)
