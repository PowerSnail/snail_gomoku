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

class App:
    def __init__(self):
        self.q_app = QApplication()
        ui_file = QFile(str(_find_ui()))
        ui_file.open(QFile.ReadOnly)
        loader = QUiLoader()
        self.window = loader.load(ui_file)
        ui_file.close()

        self.b = Board(15)
        self.bw = BoardWrapper(self.b)

        self.window.centralPanel.setLayout(self.layout)

    def run(self):
        self.window.show()
        return self.q_app.exec_()


def main():
    QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication()

    const.load_imgs(app.devicePixelRatio())

    window = MainWindow()
    window.show()


    return app.exec_()
