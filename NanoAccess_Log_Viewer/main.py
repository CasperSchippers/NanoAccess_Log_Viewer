import sys
from PyQt5 import QtWidgets, QtCore, QtGui

from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg, NavigationToolbar2QT)
from matplotlib import pyplot

from log_reader import readLogFile


class Viewer(QtWidgets.QMainWindow):

    Data = []

    def __init__(self):
        super().__init__()

        self.setWindowTitle('Log Viewer')
        self.resize(1280, 720)

        self.initMenuBar()
        self.initStatusBar()
        self.initUI()

    def initMenuBar(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu('&File')

        open_file = file_menu.addAction("&Open File")
        open_file.setStatusTip("Select and open file")
        open_file.setIcon(self.style().standardIcon(
            QtWidgets.QStyle.SP_DialogOpenButton))
        open_file.setShortcut("Ctrl+O")
        open_file.triggered.connect(self.openFiles)

        open_file = file_menu.addAction("&Close")
        open_file.setStatusTip("Close application")
        open_file.setIcon(self.style().standardIcon(
            QtWidgets.QStyle.SP_DialogCloseButton))
        open_file.setShortcut("Ctrl+W")
        open_file.triggered.connect(self.close)

    def initStatusBar(self):
        self.statusbar = self.statusBar()
        self.statusbar.showMessage("Ready")

    def initUI(self):
        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)

        central_layout = QtWidgets.QGridLayout(central_widget)

        self.figure, self.ax = pyplot.subplots(1, 1)
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Something')
        self.plot_canvas = FigureCanvasQTAgg(self.figure)
        plot_toolbar = NavigationToolbar2QT(self.plot_canvas, self)

        plot_layout = QtWidgets.QVBoxLayout()
        plot_layout.addWidget(self.plot_canvas)
        plot_layout.addWidget(plot_toolbar)
        central_layout.addLayout(plot_layout, 0, 1, 7, 7)

    def openFiles(self, *, filenames=None):
        if filenames is None:
            self.selectFiles()
        else:
            self.filenames = filenames

        self.log_data = [readLogFile(file) for file in self.filenames]

        self.plotData()

    def selectFiles(self):
        self.filenames, _ = QtWidgets.QFileDialog.getOpenFileNames(
            self, 'Open File')

    def plotData(self):
        self.ax.clear()
        for i, data in enumerate(self.log_data):
            self.ax.plot(data["Time"], data["GENERATOR-PS-41.I[A]"])

        self.plot_canvas.draw()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    viewer = Viewer()
    viewer.show()

    viewer.openFiles(filenames=[
        "../Data/Heating_1hr_480C.prc_2019-03-06_15-19-38" +
        "_ProcessLog-Deposition System - TU Eindhoven.txt",
        "../Data/Heating_1hr_350C_5h_480C.prc_2019-03-13_10-24-11_" +
        "ProcessLog-Deposition System - TU Eindhoven.txt"
    ])

    sys.exit(app.exec_())
