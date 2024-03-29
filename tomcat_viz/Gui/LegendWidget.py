from PyQt5.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QHBoxLayout
from PyQt5.Qt import Qt, QSize

from tomcat_viz.Gui.Utils import createLabel, createEmptyWidget, createStampedBlockWidget, BlockIconWidget
from tomcat_viz.Common.Constants import Constants


class LegendWidget(QWidget):

    def __init__(self):
        super().__init__()

        self._createWidgets()
        self._configureLayout()

    def _createWidgets(self):
        self._victimsSubtitle = createLabel("VICTIMS", Constants.Font.TINY_REGULAR.value)
        self._markersSubtitle = createLabel("MARKERS", Constants.Font.TINY_REGULAR.value)
        self._miscSubtitle = createLabel("MISC", Constants.Font.TINY_REGULAR.value)
        self._slash1 = createLabel("/", Constants.Font.TINY_REGULAR.value)
        self._slash2 = createLabel("/", Constants.Font.TINY_REGULAR.value)
        self._slash3 = createLabel("/", Constants.Font.TINY_REGULAR.value)

        # Victims
        self._unsavedVictimAIcon = createStampedBlockWidget("A", Constants.Font.TINY_REGULAR.value, "black",
                                                            Constants.Colors.VICTIM_A.value, QSize(10, 10))
        self._savedVictimAIcon = createStampedBlockWidget("A", Constants.Font.TINY_REGULAR.value, "black",
                                                          Constants.Colors.SAFE_VICTIM.value, QSize(10, 10))
        self._unsavedVictimBIcon = createStampedBlockWidget("B", Constants.Font.TINY_REGULAR.value, "black",
                                                            Constants.Colors.VICTIM_B.value, QSize(10, 10))
        self._savedVictimBIcon = createStampedBlockWidget("B", Constants.Font.TINY_REGULAR.value, "black",
                                                          Constants.Colors.SAFE_VICTIM.value, QSize(10, 10))
        self._unsavedCriticalVictimIcon = createStampedBlockWidget("C", Constants.Font.TINY_REGULAR.value, "black",
                                                                   Constants.Colors.CRITICAL_VICTIM.value,
                                                                   QSize(10, 10))
        self._savedCriticalVictimIcon = createStampedBlockWidget("C", Constants.Font.TINY_REGULAR.value, "black",
                                                                 Constants.Colors.SAFE_VICTIM.value, QSize(10, 10))

        self._victimALabel = createLabel("Unsaved/Saved Type A", Constants.Font.TINY_REGULAR.value,
                                         alignment=Qt.AlignLeft)
        self._victimBLabel = createLabel("Unsaved/Saved Type B", Constants.Font.TINY_REGULAR.value,
                                         alignment=Qt.AlignLeft)
        self._criticalVictimLabel = createLabel("Unsaved/Saved Critical", Constants.Font.TINY_REGULAR.value,
                                                alignment=Qt.AlignLeft)

        # Markers
        self._noVictimMarkerIcon = createStampedBlockWidget(Constants.MARKER_TYPE_MAP[Constants.MarkerType.NO_VICTIM],
                                                            Constants.Font.TINY_REGULAR.value, "black",
                                                            Constants.Colors.MARKER.value, QSize(10, 10))
        self._victimAMarkerIcon = createStampedBlockWidget(Constants.MARKER_TYPE_MAP[Constants.MarkerType.VICTIM_A],
                                                           Constants.Font.TINY_REGULAR.value, "black",
                                                           Constants.Colors.MARKER.value, QSize(10, 10))
        self._victimBMarkerIcon = createStampedBlockWidget(Constants.MARKER_TYPE_MAP[Constants.MarkerType.VICTIM_B],
                                                           Constants.Font.TINY_REGULAR.value, "black",
                                                           Constants.Colors.MARKER.value, QSize(10, 10))
        self._regularVictimMarkerIcon = createStampedBlockWidget(
            Constants.MARKER_TYPE_MAP[Constants.MarkerType.REGULAR_VICTIM], Constants.Font.TINY_REGULAR.value, "black",
            Constants.Colors.MARKER.value, QSize(10, 10))
        self._criticalVictimMarkerIcon = createStampedBlockWidget(
            Constants.MARKER_TYPE_MAP[Constants.MarkerType.CRITICAL_VICTIM], Constants.Font.TINY_REGULAR.value, "black",
            Constants.Colors.MARKER.value, QSize(10, 10))
        self._threatMarkerIcon = createStampedBlockWidget(Constants.MARKER_TYPE_MAP[Constants.MarkerType.THREAT_ROOM],
                                                          Constants.Font.TINY_REGULAR.value, "black",
                                                          Constants.Colors.MARKER.value, QSize(10, 10))
        self._sosMarkerIcon = createStampedBlockWidget(Constants.MARKER_TYPE_MAP[Constants.MarkerType.SOS],
                                                       Constants.Font.TINY_REGULAR.value, "black",
                                                       Constants.Colors.MARKER.value, QSize(10, 10))
        self._rubbleMarkerIcon = createStampedBlockWidget(Constants.MARKER_TYPE_MAP[Constants.MarkerType.RUBBLE],
                                                          Constants.Font.TINY_REGULAR.value, "black",
                                                          Constants.Colors.MARKER.value, QSize(10, 10))

        self._noVictimMarkerLabel = createLabel("No Victim", Constants.Font.TINY_REGULAR.value,
                                                alignment=Qt.AlignLeft)
        self._victimAMarkerLabel = createLabel("Victim A", Constants.Font.TINY_REGULAR.value,
                                               alignment=Qt.AlignLeft)
        self._victimBMarkerLabel = createLabel("Victim B", Constants.Font.TINY_REGULAR.value,
                                               alignment=Qt.AlignLeft)
        self._regularVictimMarkerLabel = createLabel("Regular Victim", Constants.Font.TINY_REGULAR.value,
                                                     alignment=Qt.AlignLeft)
        self._criticalVictimMarkerLabel = createLabel("Critical Victim", Constants.Font.TINY_REGULAR.value,
                                                      alignment=Qt.AlignLeft)
        self._threatMarkerLabel = createLabel("Threat", Constants.Font.TINY_REGULAR.value,
                                              alignment=Qt.AlignLeft)
        self._sosMarkerLabel = createLabel("SOS", Constants.Font.TINY_REGULAR.value,
                                           alignment=Qt.AlignLeft)
        self._rubbleMarkerLabel = createLabel("Rubble", Constants.Font.TINY_REGULAR.value,
                                              alignment=Qt.AlignLeft)

        # Misc
        self._rubbleIcon = BlockIconWidget("white", Constants.Colors.RUBBLE.value, QSize(10, 10), Qt.Dense5Pattern,
                                           Constants.Colors.RUBBLE.value)
        self._doorIcon = BlockIconWidget("white", "white", QSize(10, 10), Qt.Dense7Pattern, Constants.Colors.DOOR.value)
        self._signalTriggerIcon = BlockIconWidget("white", "black", QSize(10, 10), None, None, "V", "black",
                                                  Constants.Font.TINY_REGULAR.value)
        self._rubbleCollapseTriggerIcon = createEmptyWidget(Constants.Colors.THREAT_ACTIVATION.value, QSize(10, 10))
        self._rubbleLabel = createLabel("Rubble", Constants.Font.TINY_REGULAR.value, alignment=Qt.AlignLeft)
        self._doorLabel = createLabel("Door", Constants.Font.TINY_REGULAR.value, alignment=Qt.AlignLeft)
        self._signalTriggerLabel = createLabel("Victim Signal Trigger", Constants.Font.TINY_REGULAR.value,
                                               alignment=Qt.AlignLeft)
        self._rubbleCollapseTriggerLabel = createLabel("Rubble Collapse Trigger", Constants.Font.TINY_REGULAR.value,
                                                       alignment=Qt.AlignLeft)

    def _configureLayout(self):
        gridLayout = QGridLayout()
        gridLayout.setContentsMargins(0, 0, 0, 0)
        gridLayout.setColumnStretch(0, 0)
        gridLayout.setColumnStretch(1, 1)

        victimAIconLayout = QHBoxLayout()
        victimAIconLayout.setContentsMargins(0, 0, 0, 0)
        victimAIconLayout.setSpacing(5)
        victimAIconLayout.addWidget(self._unsavedVictimAIcon)
        victimAIconLayout.addWidget(self._slash1)
        victimAIconLayout.addWidget(self._savedVictimAIcon)
        victimAIconLayout.addStretch()

        victimBIconLayout = QHBoxLayout()
        victimBIconLayout.setContentsMargins(0, 0, 0, 0)
        victimBIconLayout.setSpacing(5)
        victimBIconLayout.addWidget(self._unsavedVictimBIcon)
        victimBIconLayout.addWidget(self._slash2)
        victimBIconLayout.addWidget(self._savedVictimBIcon)
        victimBIconLayout.addStretch()

        criticalVictimIconLayout = QHBoxLayout()
        criticalVictimIconLayout.setContentsMargins(0, 0, 0, 0)
        criticalVictimIconLayout.setSpacing(5)
        criticalVictimIconLayout.addWidget(self._unsavedCriticalVictimIcon)
        criticalVictimIconLayout.addWidget(self._slash3)
        criticalVictimIconLayout.addWidget(self._savedCriticalVictimIcon)
        criticalVictimIconLayout.addStretch()

        gridLayout.addWidget(self._miscSubtitle, 0, 0, 1, 2)
        gridLayout.addWidget(self._rubbleIcon, 1, 0)
        gridLayout.addWidget(self._rubbleLabel, 1, 1)
        gridLayout.addWidget(self._doorIcon, 2, 0)
        gridLayout.addWidget(self._doorLabel, 2, 1)
        gridLayout.addWidget(self._signalTriggerIcon, 3, 0)
        gridLayout.addWidget(self._signalTriggerLabel, 3, 1)
        gridLayout.addWidget(self._rubbleCollapseTriggerIcon, 4, 0)
        gridLayout.addWidget(self._rubbleCollapseTriggerLabel, 4, 1)

        gridLayout.addWidget(self._victimsSubtitle, 5, 0, 1, 2)
        gridLayout.addLayout(victimAIconLayout, 6, 0)
        gridLayout.addWidget(self._victimALabel, 6, 1)
        gridLayout.addLayout(victimBIconLayout, 7, 0)
        gridLayout.addWidget(self._victimBLabel, 7, 1)
        gridLayout.addLayout(criticalVictimIconLayout, 8, 0)
        gridLayout.addWidget(self._criticalVictimLabel, 8, 1)

        gridLayout.addWidget(self._markersSubtitle, 0, 2, 1, 2)
        gridLayout.addWidget(self._noVictimMarkerIcon, 1, 2)
        gridLayout.addWidget(self._noVictimMarkerLabel, 1, 3)
        gridLayout.addWidget(self._victimAMarkerIcon, 2, 2)
        gridLayout.addWidget(self._victimAMarkerLabel, 2, 3)
        gridLayout.addWidget(self._victimBMarkerIcon, 3, 2)
        gridLayout.addWidget(self._victimBMarkerLabel, 3, 3)
        gridLayout.addWidget(self._regularVictimMarkerIcon, 4, 2)
        gridLayout.addWidget(self._regularVictimMarkerLabel, 4, 3)
        gridLayout.addWidget(self._criticalVictimMarkerIcon, 5, 2)
        gridLayout.addWidget(self._criticalVictimMarkerLabel, 5, 3)
        gridLayout.addWidget(self._threatMarkerIcon, 6, 2)
        gridLayout.addWidget(self._threatMarkerLabel, 6, 3)
        gridLayout.addWidget(self._sosMarkerIcon, 7, 2)
        gridLayout.addWidget(self._sosMarkerLabel, 7, 3)
        gridLayout.addWidget(self._rubbleMarkerIcon, 8, 2)
        gridLayout.addWidget(self._rubbleMarkerLabel, 8, 3)

        mainLayout = QVBoxLayout(self)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.addLayout(gridLayout)
        mainLayout.addStretch()
