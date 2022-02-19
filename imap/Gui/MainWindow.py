from PyQt5.QtWidgets import QMainWindow, QWidget, QScrollArea, QFrame
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QFormLayout, QLayout
from PyQt5.QtWidgets import QCheckBox, QSlider, QFileDialog, QPushButton, QSplitter
from PyQt5.Qt import Qt, QFont, QMenu, QAction

from imap.Gui.Utils import createLabel
from imap.Gui.TextMessageWidget import TextMessageWidget
from imap.Gui.EstimatesWidget import EstimatesWidget
from imap.Common.Format import secondsToTime
from imap.Common.Constants import Constants
from imap.Gui.MapWidget import MapWidget
from imap.Parser.Map import Map
from imap.Parser.Trial import Trial
from imap.Parser.Estimates import Estimates
from imap.Gui.HeaderWidget import HeaderWidget
from imap.Gui.TimeSliderWidget import TimeSliderWidget
from imap.Gui.TomcatVisualizerWidget import TomcatVisualizerWidget

import json
import numpy as np
from pkg_resources import resource_stream
import codecs


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
