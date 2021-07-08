from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette
import sys

# to add parameters to a function slot do this or use lambda:
# btn.clicked.connect(functools.partial(greeting, 'World!'))

class Window(QMainWindow):
    """Main Window."""
    def __init__(self):
        """Initializer."""
        super().__init__()
        self.setWindowTitle('PLC Tag Read/Write')
        #self.setFixedSize(235, 235)
        self._centralWidget = QWidget(self)
        self.setCentralWidget(self._centralWidget)
        self._createMenu()
        #self._createToolBar()
        self._createStatusBar()
        self.layout = QGridLayout()
        self._centralWidget.setLayout(self.layout)
        self._createReadButton()
        self._createWriteButton()
        self._createTable()
        

    def on_read_clicked(self):
        alert = QMessageBox()
        alert.setText('You clicked the read button!')
        alert.exec()
        
    def on_write_clicked(self):
        alert = QMessageBox()
        alert.setText('You clicked the write button!')
        alert.exec()
        
    def _createMenu(self):
        self.menu = self.menuBar().addMenu("&Menu")
        self.menu.addAction('&Exit', self.close)

    def _createToolBar(self):
        tools = QToolBar()
        self.addToolBar(tools)
        tools.addAction('Exit', self.close)

    def _createStatusBar(self):
        status = QStatusBar()
        status.showMessage("I'm the Status Bar")
        self.setStatusBar(status)
        
    def _createTable(self):
        table = QTableWidget()
        table.setRowCount(5)
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(['TAG', 'VALUE'])
        table.cellChanged.connect(self.data_entered)
        self.layout.addWidget(table, 1, 0, 1, 2)
        
    def _createReadButton(self):
        read_button = QPushButton('Read Tag(s)')
        self.layout.addWidget(read_button, 0, 1)
        read_button.clicked.connect(self.on_read_clicked)
        
    def _createWriteButton(self):
        write_button = QPushButton('Write Tag(s)')
        self.layout.addWidget(write_button, 0, 0)
        write_button.clicked.connect(self.on_write_clicked)
        
    def data_entered(row, column):
        print(f'{row}, {column}')

        
app = QApplication([])
app.setStyle('Fusion')

window = Window()
window.show()
app.exec()