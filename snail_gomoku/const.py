from pathlib import Path
from PySide2.QtGui import QPixmap

PROJECT_DIR = Path(__file__).parent

CLOCK_NONE = 0
CLOCK_LEFT = 1
CLOCK_RIGHT = 2

SIDE_EMPTY = 0
SIDE_BLACK = -1
SIDE_WHITE = 1

IMG_BLACK_PIECE : QPixmap = None
IMG_WHITE_PIECE : QPixmap = None


def load_imgs(dpi):
    global IMG_BLACK_PIECE
    IMG_BLACK_PIECE = QPixmap(str(PROJECT_DIR.joinpath("img").joinpath("black-piece.svg"))).scaled(256,256)
    IMG_BLACK_PIECE.setDevicePixelRatio(dpi)
    global IMG_WHITE_PIECE
    IMG_WHITE_PIECE = QPixmap(str(PROJECT_DIR.joinpath("img").joinpath("white-piece.svg"))).scaled(256, 256)
    IMG_WHITE_PIECE.setDevicePixelRatio(dpi)
