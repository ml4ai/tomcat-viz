from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QMainWindow, QLabel, QMenu, QAction, \
    QFileDialog, QGridLayout, QScrollArea
from map_widget import MapWidget
from PyQt5.QtCore import Qt

app = QApplication([])


class Window(QMainWindow):

    def __init__(self, width: int, height: int):
        super().__init__()

        self._width = width
        self._height = height

        self._configure_window()
        self._create_actions()
        self._create_menu_bar()
        # self._draw_map()

        self.show()

    def open_file(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                                  "ASIST Mission File (*.metadata)", options=options)
        if fileName:
            print(fileName)

    def _configure_window(self):
        self.setWindowTitle("ASIST Mission Replay")

        self.setStyleSheet("background-color: white;")

        widget = QWidget()
        layout = QGridLayout(widget)

        # Fixed window size
        # self.setFixedWidth(self._width)
        # self.setFixedHeight(self._height)

        self._scroll_widget = QScrollArea()
        self._scroll_widget.setWidgetResizable(True)
        map_widget = MapWidget('data/maps/Saturn_2.1_3D_sm_v1.0.json', 'data/maps/MapBlocks_SaturnA_2.3_xyz.csv',
                               20, True)
        self._scroll_widget.setWidget(map_widget)
        layout.addWidget(self._scroll_widget, 0, 0)

        # layout.addWidget(WidgetTwo(), 1, 1)
        self.setCentralWidget(widget)
        self.resize(self._width, self._height)

    def _create_actions(self):
        self.open_action = QAction("&Open...", self)
        self.open_action.triggered.connect(self.open_file)

    def _create_menu_bar(self):
        menu_bar = self.menuBar()
        file_menu = QMenu("&File", self)
        file_menu.addAction(self.open_action)
        menu_bar.addMenu(file_menu)

    def _draw_map(self):
        map_widget = MapWidget('data/maps/Saturn_2.1_3D_sm_v1.0.json')
        self._scroll_widget.setWidget(map_widget)


window = Window(1500, 1000)
app.exec()
