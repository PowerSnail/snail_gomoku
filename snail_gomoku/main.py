from pathlib import Path
import sys
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication, QWidget, QSizePolicy, QGridLayout, QLabel
from PySide2.QtCore import QFile, QCoreApplication, Qt
from PySide2.QtGui import QGuiApplication
from snail_gomoku.board import Board, BoardWrapper
import typing as T
from snail_gomoku.mainwindow import MainWindow
from snail_gomoku import const


def main():
    QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication()

    const.load_imgs(app.devicePixelRatio())

    window = MainWindow()
    window.show()

    return app.exec_()
