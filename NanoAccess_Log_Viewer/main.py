import sys
from PyQt5 import QtWidgets, QtCore, QtGui

import pyqtgraph as pg
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')

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

        self.plot_widget = pg.PlotWidget()


        plot_layout = QtWidgets.QVBoxLayout()
        plot_layout.addWidget(self.plot_widget)
        self.x_data_selector = QtWidgets.QComboBox(self)
        self.x_data_selector.setMinimumWidth(200)
        self.y_data_selector = QtWidgets.QComboBox(self)
        self.y_data_selector.setMinimumWidth(200)
        self.x_data_selector.currentIndexChanged.connect(self.plotData)
        self.y_data_selector.currentIndexChanged.connect(self.plotData)
        central_layout.addLayout(plot_layout, 0, 1, 7, 7)

    def openFiles(self, *, filenames=None):
        if filenames is None:
            self.selectFiles()
        else:
            self.filenames = filenames

        self.log_data = [readLogFile(file) for file in self.filenames]

        columns = self.log_data[0].columns
        self.x_data_selector.addItems(columns)
        self.y_data_selector.addItems(columns)

        self.x_data_selector.setCurrentIndex(0)
        self.y_data_selector.setCurrentIndex(1)

        # self.plotData()

    def selectFiles(self):
        self.filenames, _ = QtWidgets.QFileDialog.getOpenFileNames(
            self, 'Open File')

    def plotData(self):
        x_col = self.x_data_selector.currentText()
        y_col = self.y_data_selector.currentText()

        try:
            for i, data in enumerate(self.log_data):
                self.plot_widget.plot(data[x_col], data[y_col])
        except KeyError:
            return



if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    viewer = Viewer()
    viewer.show()

    # viewer.openFiles(filenames=[
    #     "../Data/Heating_1hr_480C.prc_2019-03-06_15-19-38" +
    #     "_ProcessLog-Deposition System - TU Eindhoven.txt",
    #     "../Data/Heating_1hr_350C_5h_480C.prc_2019-03-13_10-24-11_" +
    #     "ProcessLog-Deposition System - TU Eindhoven.txt"
    # ])

    sys.exit(app.exec_())
