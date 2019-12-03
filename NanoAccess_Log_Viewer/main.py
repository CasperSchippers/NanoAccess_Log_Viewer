import sys
from PyQt5 import QtWidgets, QtCore, QtGui

import configparser
from pathlib import Path

import pyqtgraph as pg
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')

from log_reader import readLogFile

config = configparser.ConfigParser()
config.read("locations.ini")


class Viewer(QtWidgets.QMainWindow):
    proc_log_path = Path(config["DEFAULT"]["process_logs"])
    syst_log_path = Path(config["DEFAULT"]["system_logs"])

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

        open_dir = file_menu.addAction("&Open Dir")
        open_dir.setStatusTip("Select and open directory")
        open_dir.setIcon(self.style().standardIcon(
            QtWidgets.QStyle.SP_DirOpenIcon))
        open_dir.setShortcut("Ctrl+D")
        open_dir.triggered.connect(self.selectDir)

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
        central_layout = QtWidgets.QHBoxLayout(central_widget)

        self.initFileTree()

        self.plot_widget = pg.PlotWidget()

        self.x_data_selector = QtWidgets.QComboBox(self)
        self.x_data_selector.setMinimumWidth(200)
        self.y_data_selector = QtWidgets.QComboBox(self)
        self.y_data_selector.setMinimumWidth(200)
        self.x_data_selector.currentIndexChanged.connect(self.plotData)
        self.y_data_selector.currentIndexChanged.connect(self.plotData)

        plot_layout_widget = QtWidgets.QWidget()
        plot_layout = QtWidgets.QVBoxLayout(plot_layout_widget)
        plot_layout.addWidget(self.plot_widget)
        plot_layout.addWidget(self.x_data_selector)
        plot_layout.addWidget(self.y_data_selector)

        central_splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        central_splitter.addWidget(self.file_tree)
        central_splitter.setStretchFactor(0, 2)
        central_splitter.addWidget(plot_layout_widget)
        central_splitter.setStretchFactor(1, 3)
        central_layout.addWidget(central_splitter)

    def initFileTree(self):
        self.file_tree = QtWidgets.QTreeView()

        self.fs_model = QtWidgets.QFileSystemModel(self.file_tree)
        self.fs_model.setNameFilterDisables(False)
        self.fs_model.setRootPath(str(self.proc_log_path))

        self.file_tree.setModel(self.fs_model)
        self.file_tree.hideColumn(1)
        self.file_tree.hideColumn(2)
        self.file_tree.setColumnWidth(0, 200)

        self.fs_model.setNameFilters(["*.txt"])

        self.showDir(str(self.proc_log_path))

        self.file_tree.setSortingEnabled(True)
        self.file_tree.sortByColumn(3, 0)


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

    def selectDir(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory(
            self, 'Select Directory')
        self.showDir(directory)

    def showDir(self, directory):
        self.file_tree.setRootIndex(self.fs_model.index(directory))

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
