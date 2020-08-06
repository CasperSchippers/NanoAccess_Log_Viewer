import sys
from PyQt5 import QtWidgets, QtCore, QtGui, QtTest

import configparser
from pathlib import Path
from multiprocessing import Pool
from time import sleep

import pyqtgraph as pg
pg.setConfigOption("background", "w")
pg.setConfigOption("foreground", "k")

from log_reader import readLogFile

config = configparser.ConfigParser()
config.read("locations.ini")

columns = [
    "Time",
    "MOTOR-M-SST2.Pos[mm]",
    "HEATER-ETS-41.Mode",
    "HEATER-ETS-41.WSP",
    "HEATER-ETS-41.PV1",
    "HEATER-ETS-41.SPP",
    "GENERATOR-PS-41.P[W]",
    "GENERATOR-PS-41.U[V]",
    "GENERATOR-PS-41.I[A]",
    "GAUGE-G41.p[mBar]",
    "CHAMBER-PREP.State",
    'GENERATOR-DCS-22.P[W]', 'GENERATOR-DCS-22.U[V]',
       'GENERATOR-DCS-22.I[mA]', 'GENERATOR-DCS-22.Source',
       'GENERATOR-DCS-21.P[W]', 'GENERATOR-DCS-21.U[V]',
       'GENERATOR-DCS-21.I[mA]', 'GENERATOR-DCS-21.Source',
       'GENERATOR-DCS-23.P[W]', 'GENERATOR-DCS-23.U[V]',
       'GENERATOR-DCS-23.I[mA]', 'GENERATOR-DCS-23.Source',
       'GENERATOR-DCS-24.P[W]', 'GENERATOR-DCS-24.U[V]',
       'GENERATOR-DCS-24.I[mA]', 'GENERATOR-DCS-24.Source',
       'GENERATOR-DCS-25.P[W]', 'GENERATOR-DCS-25.U[V]',
       'GENERATOR-DCS-25.I[mA]', 'GENERATOR-DCS-25.Source',
       'GENERATOR-DCS-26.P[W]', 'GENERATOR-DCS-26.U[V]',
       'GENERATOR-DCS-26.I[mA]', 'GENERATOR-DCS-26.Source',
       'GENERATOR-RFAE-21.P[W]', 'GENERATOR-RFAE-21.Source',
       'GENERATOR-RFAE-23.P[W]', 'GENERATOR-RFAE-23.Source',
       'GENERATOR-RFAE-22.P[W]', 'GENERATOR-RFAE-22.Source',
       'GAUGE-G22.p[mBar]', 'MAGNETRON-MAGN-201.Material',
       'MAGNETRON-MAGN-202.Material', 'MAGNETRON-MAGN-203.Material',
       'MAGNETRON-MAGN-204.Material', 'MAGNETRON-MAGN-205.Material',
       'MAGNETRON-MAGN-206.Material', 'MAGNETRON-MAGN-207.Material',
       'MAGNETRON-MAGN-208.Material', 'MAGNETRON-MAGN-209.Material',
       'MAGNETRON-MAGN-210.Material', 'MAGNETRON-MAGN-211.Material',
       'MAGNETRON-MAGN-212.Material', 'MOTOR-M-MT2.Pos[mm]',
       'MOTOR-M-MR2.Pos[°]', 'MOTOR-M-SST2.Pos[mm]', 'MOTOR-M-SR2.Pos[°]',
       'MOTOR-M-SR2.Pos[°].1'
]


class Viewer(QtWidgets.QMainWindow):
    proc_log_path = Path(config["DEFAULT"]["process_logs"])
    syst_log_path = Path(config["DEFAULT"]["system_logs"])

    selected_files = list()

    Data = []

    def __init__(self):
        super().__init__()

        self.pool = Pool(4)

        self.setWindowTitle("Log Viewer")
        self.resize(1280, 720)

        self.initMenuBar()
        self.initStatusBar()
        self.initUI()

    def initMenuBar(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu("&File")

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
        self.x_data_selector.addItems(columns)
        self.y_data_selector.addItems(columns)
        self.x_data_selector.setCurrentIndex(3)
        self.y_data_selector.setCurrentIndex(1)
        self.x_data_selector.currentIndexChanged.connect(self.plotData)
        self.y_data_selector.currentIndexChanged.connect(self.plotData)

        plot_layout_widget = QtWidgets.QWidget()
        plot_layout = QtWidgets.QVBoxLayout(plot_layout_widget)
        plot_layout.addWidget(self.plot_widget)
        plot_layout.addWidget(self.x_data_selector)
        plot_layout.addWidget(self.y_data_selector)

        central_layout.addWidget(plot_layout_widget)

        ftree_widget = QtWidgets.QDockWidget("File Tree", self)
        ftree_widget.setWidget(self.file_tree)
        ftree_widget.setFeatures(ftree_widget.features() & ~QtWidgets.QDockWidget.DockWidgetClosable)

        plot_select_widget = QtWidgets.QDockWidget("Plot Selector", self)
        plot_select_widget.setFeatures(plot_select_widget.features() & ~QtWidgets.QDockWidget.DockWidgetClosable)

        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, ftree_widget)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, plot_select_widget)




    def initFileTree(self):
        self.file_tree = QtWidgets.QTreeView()

        self.fs_model = QtWidgets.QFileSystemModel(self.file_tree)
        self.fs_model.setNameFilterDisables(False)
        self.fs_model.setRootPath(str(self.proc_log_path))

        self.file_tree.setModel(self.fs_model)
        self.file_tree.hideColumn(1)
        self.file_tree.hideColumn(2)
        self.file_tree.setColumnWidth(0, 200)

        self.file_tree.setSelectionMode(
            QtGui.QAbstractItemView.ExtendedSelection)

        self.file_tree.selectionModel().selectionChanged.connect(
            self.loadSelection)

        self.fs_model.setNameFilters(["*.txt"])
        # self.fs_model

        self.showDir(str(self.proc_log_path))

        self.file_tree.setSortingEnabled(True)
        self.file_tree.sortByColumn(3, 0)

    def loadSelection(self, selected, deselected):
        for index in selected.indexes():
            file_index = self.fs_model.index(index.row(), 0, index.parent())
            file = Path(self.fs_model.filePath(file_index))

            if file.is_file() and file not in self.selected_files:
                self.selected_files.append(file)

        for index in deselected.indexes():
            file_index = self.fs_model.index(index.row(), 0, index.parent())
            file = Path(self.fs_model.filePath(file_index))

            try:
                self.selected_files.remove(file)
            except ValueError:
                pass

        self.openFiles(filenames=self.selected_files)
        self.plotData()

    # def readSelection(self):
    #     results = self.pool.map_async(readLogFile, self.selected_files)

    #     while not results.ready():
    #         QtTest.QTest.qWait(1)

    #     self.data = [result for result in results.get() if result is not None]

    def plotSelection(self):
        pass

    def openFiles(self, *, filenames=None):
        if filenames is None:
            self.selectFiles()
        else:
            self.filenames = filenames

        if len(filenames) == 0:
            return

        results = self.pool.map_async(readLogFile, self.selected_files)

        while not results.ready():
            QtTest.QTest.qWait(10)

        self.log_data = [result for result in results.get()
                         if result is not None]

        print(self.log_data[0].columns)

        # self.plotData()

    def selectFiles(self):
        self.filenames, _ = QtWidgets.QFileDialog.getOpenFileNames(
            self, "Open File")

    def selectDir(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Select Directory")
        self.showDir(directory)

    def showDir(self, directory):
        self.file_tree.setRootIndex(self.fs_model.index(directory))

    def plotData(self):
        if len(self.log_data) == 0:
            return

        x_col = "Time"
        y_col = self.y_data_selector.currentText()

        try:
            for i, data in enumerate(self.log_data):
                x_data = data[x_col]
                y_data = data[y_col]
                print(x_data.dtype)
                self.plot_widget.plot(x_data, y_data)
        except KeyError:
            return


if __name__ == "__main__":
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
