import sys
from PyQt5 import QtWidgets, QtCore, QtGui
import pyqtgraph as pg
from log_reader import readLogFile

pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')


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

        # date_axis = pg.graphicsItems.DateAxisItem.DateAxisItem(
        #     orientation='bottom')
        self.plot_widget = pg.PlotWidget(
            # axisItems={"bottom": date_axis}
        )
        plotItem = self.plot_widget.getPlotItem()
        plotItem.showAxis('right')
        plotItem.showAxis('top')
        central_layout.addWidget(self.plot_widget, 0, 1, 1, 7)

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
        # plotitem = self.plot_widget.getPlotItem()

        self.plot_widget.clear()
        for i, data in enumerate(self.log_data):
            self.plot_widget.plot(
                data["Time"].dt.total_seconds() / 60,
                data["GAUGE-G41.p[mBar]"],
                pen=(i, len(self.log_data)),
            )


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    viewer = Viewer()
    viewer.show()
    sys.exit(app.exec_())
