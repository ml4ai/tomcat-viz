from PyQt5.Qt import QMenu, QAction
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QMainWindow

from imap.Gui.TomcatVisualizerWidget import TomcatVisualizerWidget


class MainWindow(QMainWindow):
    LEFT_PANEL_PROP = 80
    MAP_HEIGHT_PROP = 80

    def __init__(self):
        super().__init__()

        self.setWindowTitle('ToMCAT Visualizer')
        self.setGeometry(0, 0, 1800, 1020)
        self._tomcatWidget = TomcatVisualizerWidget()
        self.setCentralWidget(self._tomcatWidget)

        self._createMenu()

    def closeEvent(self, event):
        self._tomcatWidget.closeApp()
        event.accept()

    def _createMenu(self):
        self._createTrialMenu()
        self._createEstimatesMenu()

    def _createTrialMenu(self):
        menuBar = self.menuBar()
        trialMenu = QMenu("&Trial", self)

        # Load options
        loadMenu = QMenu("&Load", self)
        loadFromMetadataAction = QAction("&From Metadata...", self)
        loadFromPackageAction = QAction("&From Package...", self)
        loadFromMetadataAction.triggered.connect(self._loadTrialFromMetadataAction)
        loadFromPackageAction.triggered.connect(self._loadTrialFromPackageAction)
        loadMenu.addAction(loadFromMetadataAction)
        loadMenu.addAction(loadFromPackageAction)
        trialMenu.addMenu(loadMenu)
        menuBar.addMenu(trialMenu)

        # Dump option
        self._dumpAction = QAction("&Dump...", self)
        self._dumpAction.setEnabled(False)
        self._dumpAction.triggered.connect(self._dumpTrialAction)
        trialMenu.addAction(self._dumpAction)

    def _createEstimatesMenu(self):
        menuBar = self.menuBar()
        trialMenu = QMenu("&Estimates", self)

        # Load options
        loadAction = QAction("&Load...", self)
        loadAction.triggered.connect(self._loadEstimatesAction)
        trialMenu.addAction(loadAction)
        menuBar.addMenu(trialMenu)

    def _loadTrialFromMetadataAction(self, value):
        filepath = QFileDialog.getOpenFileName(self, "Select Metadata File", ".", "Metadata File (*.metadata)")[0]
        if self._tomcatWidget.loadTrialFromMetadata(filepath):
            self._dumpAction.setEnabled(True)

    def _loadTrialFromPackageAction(self, value):
        filepath = QFileDialog.getOpenFileName(self, "Select Package File", ".", "Package File (*.pkl)")[0]
        if self._tomcatWidget.loadTrialFromPackage(filepath):
            self._dumpAction.setEnabled(True)

    def _dumpTrialAction(self, value):
        filepath = QFileDialog.getSaveFileName(self, "Save Package File", ".", "Package File (*.pkl)")[0]
        self._tomcatWidget.dumpTrial(filepath)

    def _loadEstimatesAction(self):
        filepath = QFileDialog.getOpenFileName(self, "Select Estimates File", ".", "Package File (*.json)")[0]
        self._tomcatWidget.loadEstimates(filepath)
