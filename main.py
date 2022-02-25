from PyQt5.QtWidgets import QApplication, QMainWindow

from imap.Gui.MainWindow import MainWindow
from imap.Gui.TimeSliderWidget import TimeSliderWidget

if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    # slider = TimeSliderWidget(lambda x : print(x))
    # slider.setTimeSteps(20)
    # window = QMainWindow()
    # window.setCentralWidget(slider)
    window.show()
    app.exec()
