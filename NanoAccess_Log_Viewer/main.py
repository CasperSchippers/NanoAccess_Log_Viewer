import sys
from PyQt5 import QtWidgets, QtCore, QtGui
import pyqtgraph as pg


pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')


class Viewer(QtWidgets.QMainWindow):
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

    def initStatusBar(self):
        self.statusbar = self.statusBar()
        self.statusbar.showMessage("Ready")

    def initUI(self):
        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)

        central_layout = QtWidgets.QGridLayout(central_widget)

        self.file_system = QtWidgets.QFileSystemModel()
        self.file_system.setRootPath('D:/Git/')
        self.file_tree = QtWidgets.QTreeView()
        self.file_tree.setModel(self.file_system)
        central_layout.addWidget(self.file_tree, 0, 0)

        self.plot_widget = pg.PlotWidget()
        plotItem = self.plot_widget.getPlotItem()
        plotItem.showAxis('right')
        plotItem.showAxis('top')
        central_layout.addWidget(self.plot_widget, 0, 1, 1, 7)

    def openFiles(self):
        self.selectFiles()

    def selectFiles(self):
        self.filenames, _ = QtWidgets.QFileDialog.getOpenFileNames(
            self, 'Open File')

    def selectDir(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory(
            self, 'Select Directory')
        self.file_tree.setRootIndex(self.file_system.index(directory))


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    viewer = Viewer()
    viewer.show()
    sys.exit(app.exec_())
