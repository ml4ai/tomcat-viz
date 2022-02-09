import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QFormLayout, QLayout
from PyQt5.QtWidgets import QCheckBox, QSlider, QFileDialog
from PyQt5.Qt import Qt, QFont, QMenu, QAction

from Gui.Utils import createLabel
from Common.Format import secondsToTime
from Gui.MapWidget import MapWidget


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle('ToMCAT Visualizer')
        self.setFixedSize(1800, 1000)
        self._centralWidget = QWidget(self)
        self.setCentralWidget(self._centralWidget)

        self._boldLabelFont = QFont("Arial", 14, QFont.Bold)
        self._regularLabelFont = QFont("Arial", 14)

        self._createWidgets()
        self._configureLayout()
        self._createMenu()

    def _createWidgets(self):
        self._trialLabel = createLabel("T00001", self._regularLabelFont)
        self._teamLabel = createLabel("TM00063", self._regularLabelFont)

        self._scoreLabel = createLabel("250", self._regularLabelFont)
        self._perturbationCheckbox = QCheckBox()
        self._perturbationCheckbox.setEnabled(False)
        self._redPlayerLabel = createLabel("P00432", self._boldLabelFont, "red", Qt.AlignCenter)
        self._greenPlayerLabel = createLabel("P00433", self._boldLabelFont, "green", Qt.AlignCenter)
        self._bluePlayerLabel = createLabel("P00431", self._boldLabelFont, "blue", Qt.AlignCenter)

        self._mapWidget = MapWidget()

        # self._timerField = QLineEdit("00:00")
        self._timerField = createLabel("00:00", self._regularLabelFont, alignment=Qt.AlignCenter)
        self._timerField.setEnabled(False)

    def _configureLayout(self):
        sidePanelLayout = QHBoxLayout()

        leftPanelLayout = QVBoxLayout()
        rightPanelLayout = QVBoxLayout()

        sidePanelLayout.addLayout(leftPanelLayout, 80)
        sidePanelLayout.addLayout(rightPanelLayout, 20)

        # Widgets on the left side of the window
        self._createTrialInfoPanel(leftPanelLayout)
        self._createScorePanel(leftPanelLayout)
        self._createMapPanel(leftPanelLayout)
        self._createSliderPanel(leftPanelLayout)

        # Widgets on the right side of the window
        speechAreaWidget = self.createWidget("magenta")
        inferenceAreaWidget = self.createWidget("gray")

        rightPanelLayout.addWidget(speechAreaWidget)
        rightPanelLayout.addWidget(inferenceAreaWidget)

        self._centralWidget.setLayout(sidePanelLayout)

    def _createTrialInfoPanel(self, parentLayout: QLayout):
        layout = QFormLayout()
        layout.setLabelAlignment(Qt.AlignLeft)
        layout.setFormAlignment(Qt.AlignLeft)
        layout.addRow(createLabel("Trial:", self._boldLabelFont), self._trialLabel)
        layout.addRow(createLabel("Team:", self._boldLabelFont), self._teamLabel)
        parentLayout.addLayout(layout, 5)

    def _createScorePanel(self, parentLayout: QLayout):
        layout = QHBoxLayout()
        centerInfoLayout = QVBoxLayout()

        # Score and Perturbation
        upper_info = QHBoxLayout()
        upper_info.setAlignment(Qt.AlignCenter)
        score_layout = QFormLayout()
        score_layout.addRow(createLabel("Score:", self._boldLabelFont), self._scoreLabel)
        perturbation_layout = QFormLayout()
        perturbation_layout.addRow(createLabel("Perturbation:", self._boldLabelFont), self._perturbationCheckbox)
        upper_info.addLayout(score_layout)
        upper_info.addLayout(perturbation_layout)
        centerInfoLayout.addLayout(upper_info)

        # Player IDs
        bottom_info = QHBoxLayout()
        bottom_info.addWidget(self._redPlayerLabel)
        bottom_info.addWidget(self._greenPlayerLabel)
        bottom_info.addWidget(self._bluePlayerLabel)
        centerInfoLayout.addLayout(bottom_info)

        layout.addWidget(QWidget(), 30)
        layout.addLayout(centerInfoLayout, 40)
        layout.addWidget(QWidget(), 30)

        parentLayout.addLayout(layout, 5)

    def _createMapPanel(self, parentLayout: QLayout):
        parentLayout.addWidget(self._mapWidget, 80)

    def _createSliderPanel(self, parentLayout: QLayout):
        layout = QHBoxLayout()
        sliderWidget = QSlider(Qt.Horizontal)
        sliderWidget.setRange(0, 899)
        sliderWidget.setSingleStep(1)
        layout.addWidget(sliderWidget, 95)
        layout.addWidget(self._timerField, 5)

        sliderWidget.valueChanged.connect(self._updateTimerAction)

        parentLayout.addLayout(layout, 5)

    def _createMenu(self):
        menuBar = self.menuBar()
        fileMenu = QMenu("&File", self)
        openAction = QAction("&Open...", self)
        openAction.triggered.connect(self._openMapFileAction)
        fileMenu.addAction(openAction)
        menuBar.addMenu(fileMenu)

    # Actions
    def _updateTimerAction(self, value):
        self._timerField.setText(secondsToTime(value))

    def _openMapFileAction(self, value):
        options = QFileDialog.Options()
        filepath, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                                  "Grid Map File (*.txt)", options=options)
        self._mapWidget.gridFilepath = filepath
        self._mapWidget.update()

    def createWidget(self, color: str):
        widget = QWidget()
        widget.setStyleSheet(f"background-color:{color};")
        widget.show()

        return widget


if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
