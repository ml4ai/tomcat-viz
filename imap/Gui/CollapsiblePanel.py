"""
Based on code from https://stackoverflow.com/questions/52615115/how-to-create-collapsible-box-in-pyqt
"""

from PyQt5.QtWidgets import QWidget, QToolButton, QScrollArea, QSizePolicy, QFrame
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtCore import QParallelAnimationGroup, QPropertyAnimation, QAbstractAnimation


class CollapsiblePanel(QWidget):
    def __init__(self, title="", parent=None):
        super(CollapsiblePanel, self).__init__(parent)

        self.toggleButton = QToolButton(text=title, checkable=True, checked=False)
        self.toggleButton.setStyleSheet("QToolButton { border: none; }")
        self.toggleButton.setToolButtonStyle(
            Qt.ToolButtonTextBesideIcon
        )
        self.toggleButton.setArrowType(Qt.RightArrow)
        self.toggleButton.pressed.connect(self.onPressed)

        self.contentArea = QScrollArea()
        self.contentArea.setMinimumHeight(0)
        self.contentArea.setMaximumHeight(0)
        self.contentArea.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.contentArea.setFrameShape(QFrame.NoFrame)
        self.contentArea.setLayout(QVBoxLayout())

        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.toggleButton)
        layout.addWidget(self.contentArea)

        self.toggleAnimation = QParallelAnimationGroup(self)
        self.toggleAnimation.addAnimation(
            QPropertyAnimation(self, b"minimumHeight")
        )
        self.toggleAnimation.addAnimation(
            QPropertyAnimation(self, b"maximumHeight")
        )
        self.toggleAnimation.addAnimation(
            QPropertyAnimation(self.contentArea, b"maximumHeight")
        )

    @pyqtSlot()
    def onPressed(self):
        checked = self.toggleButton.isChecked()
        self.toggleButton.setArrowType(
            Qt.DownArrow if not checked else Qt.RightArrow
        )
        self.toggleAnimation.setDirection(
            QAbstractAnimation.Forward
            if not checked
            else QAbstractAnimation.Backward
        )
        self.toggleAnimation.start()

    def setCentralWidget(self, widget):
        if self.contentArea.layout().count() > 0:
            currentWidget: QWidget = self.contentArea.layout().takeAt(0)
            currentWidget.deleteLater()
        self.contentArea.layout().addWidget(widget)
        collapsed_height = (
                self.sizeHint().height() - self.contentArea.maximumHeight()
        )

        # Adding a bit of padding to avoid overlapping
        content_height = widget.sizeHint().height() + 20
        for i in range(self.toggleAnimation.animationCount()):
            animation = self.toggleAnimation.animationAt(i)
            animation.setDuration(500)
            animation.setStartValue(collapsed_height)
            animation.setEndValue(collapsed_height + content_height)

        content_animation = self.toggleAnimation.animationAt(
            self.toggleAnimation.animationCount() - 1
        )
        content_animation.setDuration(500)
        content_animation.setStartValue(0)
        content_animation.setEndValue(content_height)

