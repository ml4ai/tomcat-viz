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

    def setContentLayout(self, layout):
        lay = self.contentArea.layout()
        del lay
        self.contentArea.setLayout(layout)
        collapsed_height = (
                self.sizeHint().height() - self.contentArea.maximumHeight()
        )
        content_height = layout.sizeHint().height()
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


if __name__ == "__main__":
    import sys
    import random
    import PyQt5.QtWidgets as QtWidgets
    import PyQt5.QtGui as QtGui
    from imap.Gui.TimeSeriesPlotWidget import TimeSeriesPlotWidget
    from imap.Parser.Estimates import TimeSeries

    app = QtWidgets.QApplication(sys.argv)

    w = QtWidgets.QMainWindow()
    w.setCentralWidget(QtWidgets.QWidget())
    dock = QtWidgets.QDockWidget("Collapsible Demo")
    w.addDockWidget(Qt.LeftDockWidgetArea, dock)
    scroll = QtWidgets.QScrollArea()
    dock.setWidget(scroll)
    content = QtWidgets.QWidget()
    scroll.setWidget(content)
    scroll.setWidgetResizable(True)
    vlay = QtWidgets.QVBoxLayout(content)
    for i in range(10):
        box = CollapsiblePanel("Collapsible Box Header-{}".format(i))
        vlay.addWidget(box)
        lay = QtWidgets.QVBoxLayout()
        for j in range(8):
            # label = QtWidgets.QLabel("{}".format(j))
            # label.setMinimumHeight(50)
            label = TimeSeriesPlotWidget(TimeSeries("Test", [[0.1, 0.2, 0.3]]))
            color = QtGui.QColor(*[random.randint(0, 255) for _ in range(3)])
            label.setStyleSheet(
                "background-color: {}; color : white;".format(color.name())
            )
            label.setAlignment(Qt.AlignCenter)
            lay.addWidget(label)
        box.setContentLayout(lay)
    vlay.addStretch()
    w.resize(640, 480)
    w.show()
    sys.exit(app.exec_())
