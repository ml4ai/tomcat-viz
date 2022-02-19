from PyQt5.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.Qt import Qt, QSize, QPixmap, QPalette, QColor
from pkg_resources import resource_string

from imap.Gui.Utils import createLabel, createEmptyWidget, createStampedBlockWidget, BlockIconWidget
from imap.Common.Constants import Constants


class EquippedItemWidget(QWidget):

    def __init__(self, width: int, height: int):
        super().__init__()

        self.setFixedSize(QSize(width, height))
        self.setAutoFillBackground(True)

        self._createWidgets()
        self._configureLayout()

    def setItem(self, item: Constants.EquippedItem):
        data, markerType = None, None
        if item == Constants.EquippedItem.HAMMER:
            data = resource_string("imap.Resources.Images.Items", "hammer.png")
        elif item == Constants.EquippedItem.MEDICAL_KIT:
            data = resource_string("imap.Resources.Images.Items", "medical_kit.png")
        elif item == Constants.EquippedItem.STRETCHER:
            data = resource_string("imap.Resources.Images.Items", "stretcher.png")
        elif item == Constants.EquippedItem.NO_VICTIM:
            markerType = Constants.MarkerType.NO_VICTIM
        elif item == Constants.EquippedItem.VICTIM_A:
            markerType = Constants.MarkerType.VICTIM_A
        elif item == Constants.EquippedItem.VICTIM_B:
            markerType = Constants.MarkerType.VICTIM_B
        elif item == Constants.EquippedItem.REGULAR_VICTIM:
            markerType = Constants.MarkerType.REGULAR_VICTIM
        elif item == Constants.EquippedItem.CRITICAL_VICTIM:
            markerType = Constants.MarkerType.CRITICAL_VICTIM
        elif item == Constants.EquippedItem.THREAT_ROOM:
            markerType = Constants.MarkerType.THREAT_ROOM
        elif item == Constants.EquippedItem.SOS:
            markerType = Constants.MarkerType.SOS
        elif item == Constants.EquippedItem.RUBBLE:
            markerType = Constants.MarkerType.RUBBLE

        if data is not None:
            # We display an image
            palette = QPalette()
            palette.setColor(QPalette.Active, QPalette.Window, Qt.transparent)
            self.setPalette(palette)
            pixmap = QPixmap()
            pixmap.loadFromData(data)
            self._itemIcon.setPixmap(pixmap)
            self._itemIcon.resize(self.size())
            self._itemIcon.setVisible(True)
            self._markerLetter.setVisible(False)
        else:
            palette = QPalette()
            palette.setColor(QPalette.Active, QPalette.Window, QColor(Constants.Colors.MARKER.value))
            self.setPalette(palette)
            self._markerLetter.setText(Constants.MARKER_TYPE_MAP.get(markerType, "X"))
            self._itemIcon.setVisible(False)
            self._markerLetter.setVisible(True)

    def _createWidgets(self):
        self._markerLetter = createLabel("", Constants.Font.SMALL_REGULAR.value, "black", Qt.AlignCenter)
        self._markerLetter.setVisible(False)

        self._itemIcon = QLabel()
        self._itemIcon.setAlignment(Qt.AlignCenter)
        self._itemIcon.setVisible(False)

    def _configureLayout(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._markerLetter)
        layout.addWidget(self._itemIcon)
