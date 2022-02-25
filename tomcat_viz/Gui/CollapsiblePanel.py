"""
Based on code from https://stackoverflow.com/questions/52615115/how-to-create-collapsible-box-in-pyqt
"""

from typing import Any, Callable

from PyQt5.QtCore import QParallelAnimationGroup, QPropertyAnimation, QAbstractAnimation
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget, QToolButton, QScrollArea, QSizePolicy, QFrame

from tomcat_viz.Common.Constants import Constants


class CollapsiblePanel(QWidget):
    def __init__(self, title: str, panelIndex: int, parent: Any = None):
        super(CollapsiblePanel, self).__init__(parent)

        self._panelIndex = panelIndex
        self._hasCentralWidget = False
        self._finished = True
        self._toggleCallback = None

        self.toggleButton = QToolButton(text=title, checkable=True, checked=False)
        self.toggleButton.setFont(Constants.Font.SMALL_REGULAR.value)
        self.toggleButton.setStyleSheet("QToolButton { border: none; }")
        self.toggleButton.setToolButtonStyle(
            Qt.ToolButtonTextBesideIcon
        )
        self.toggleButton.setArrowType(Qt.RightArrow)
        self.toggleButton.pressed.connect(self._onPressed)

        self.contentArea = QScrollArea()
        self.contentArea.setMinimumHeight(0)
        self.contentArea.setMaximumHeight(0)
        self.contentArea.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.contentArea.setFrameShape(QFrame.NoFrame)
        self._contentAreaLayout = QVBoxLayout()
        self.contentArea.setLayout(self._contentAreaLayout)

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
        self.toggleAnimation.finished.connect(self._animationFinished)

    def setCentralWidget(self, widget):
        self._clearContent()

        self._hasCentralWidget = True
        self._contentAreaLayout.addWidget(widget)
        collapsed_height = (
                self.sizeHint().height() - self.contentArea.maximumHeight()
        )

        # Adding a bit of padding to avoid overlapping
        content_height = widget.sizeHint().height() + 20
        for i in range(self.toggleAnimation.animationCount() - 1):
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

    def toggle(self):
        self._onPressed(False)
        self.toggleButton.setChecked(not self.toggleButton.isChecked())

    def setToggleCallback(self, callback: Callable):
        self._toggleCallback = callback

    def _clearContent(self):
        if self._hasCentralWidget:
            currentWidget: QWidget = self.contentArea.layout().takeAt(0).widget()
            currentWidget.deleteLater()

            self.toggleButton.setArrowType(Qt.RightArrow)
            self.toggleButton.setChecked(False)

            for i in range(self.toggleAnimation.animationCount()):
                animation = self.toggleAnimation.animationAt(i)
                animation.setDuration(0)
            self.toggleAnimation.setDirection(QAbstractAnimation.Backward)
            self._finished = False
            self.toggleAnimation.start()
            while not self._finished:
                # Wait until collapse finishes
                pass

    def _onPressed(self, invokeCallback: bool = True):
        if self._hasCentralWidget:
            checked = self.toggleButton.isChecked()
            self.toggleButton.setArrowType(
                Qt.DownArrow if not checked else Qt.RightArrow
            )
            self.toggleAnimation.setDirection(
                QAbstractAnimation.Forward
                if not checked
                else QAbstractAnimation.Backward
            )
            self._finished = False
            self.toggleAnimation.start()

            if invokeCallback and self._toggleCallback is not None:
                self._toggleCallback(self._panelIndex)

    def _animationFinished(self):
        self._finished = True
