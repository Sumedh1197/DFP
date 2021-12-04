# from PyQt5.QtWidgets import *
# from PyQt5.QtCore import Qt
# from PyQt5.QtGui import QPalette
# from PyQt5.QtWidgets import QApplication, QPushButton
# importing libraries
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys

def displayReturnDateLabel():
    if round.isChecked():
        returnDateLabel.setText('Return Date: ')
        
    else:
        returnDateLabel.setText(' ')

app = QApplication([])
app.setStyle('Fusion')
win = QMainWindow()
win.setGeometry(400, 400, 500, 500)
win.setWindowTitle('TravelBug')

originLabel = QLabel(win)
originLabel.setText("Origin City")
originLabel.adjustSize()
originLabel.move(20,86)
origin = QLineEdit(win)
origin.move(130, 80)

destLabel = QLabel(win)
destLabel.setText("Destination City")
destLabel.adjustSize()
destLabel.move(20,156)
dest = QLineEdit(win)
dest.move(130, 150)

layout = QGridLayout()
 
tripTypeLabel = QLabel(win)
tripTypeLabel.setText("Trip Type:")
tripTypeLabel.adjustSize()
tripTypeLabel.move(20,220)

single = QRadioButton(win)
single.setText("One-Way")
single.move(40,260)
single.setChecked(True)
single.clicked.connect(displayReturnDateLabel)
layout.addWidget(single, 0, 0)
 
round = QRadioButton(win)
round.setText("Round")
round.move(40,310)
round.clicked.connect(displayReturnDateLabel)
layout.addWidget(single, 0, 1)

originDateLabel = QLabel(win)
originDateLabel.setText('Origin Date: ')
originDateLabel.move(20, 360)
originDate = QDateEdit(win, calendarPopup = True)
originDate.setDateTime(QtCore.QDateTime.currentDateTime())
originDate.setGeometry(100, 360, 130, 30)

returnDateLabel = QLabel(win)
returnDateLabel.setText(' ')
returnDateLabel.move(250, 360)
# palette = QPalette()
# palette.setColor(QPalette.ButtonText, Qt.red)
# app.setPalette(palette)

win.show()
sys.exit(app.exec_())
# window = QWidget()
# layout = QVBoxLayout()
# layout.addWidget(QPushButton('Top'))
# layout.addWidget(QPushButton('Bottom'))
# layout.addWidget(QPushButton('Hello World'))
# window.setLayout(layout)
# window.show()
# app.exec()