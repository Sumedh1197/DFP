# from PyQt5.QtWidgets import *
# from PyQt5.QtCore import Qt
# from PyQt5.QtGui import QPalette
# from PyQt5.QtWidgets import QApplication, QPushButton
# importing libraries
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from darktheme.widget_template import DarkPalette

from pandas_Model import *
from flight_scraping import *
import sys
import pandas as pd

def displayReturnDateLabel():
    if round.isChecked():
        returnDateLabel.setText('Return Date: ')
        returnDate.show()
    else:
        returnDateLabel.setText(' ')
        returnDate.hide()

def fetchFlights():
    if origin.text() == '' or dest.text() == '':
        statusLabel.setText("Please enter an origin and destination city")
        statusLabel.adjustSize()
    else:
        df = call_single_function('JFK', 'LAX', '2021-12-10')
        # print(df)
        # data = {'col1':['1','2','3'], 'col2':['4','5','6'], 'col3':['7','8','9']}
        print(df)
        model = pandasModel(df)
        view = QTableView()
        view.setModel(model)
        view.resize(800, 600)
        statusLabel.setText("")
        newWindow = QWidget(view)
        newLayout = QVBoxLayout(view)
        newLayout.addWidget(newWindow)
        newWindow.show()

        newLayout.addWidget(view)
        view.show()
        # app2.show()
        #sys.exit(app2.exec_())


app = QApplication([])
app.setStyle('Fusion')
app.setPalette(DarkPalette())
win = QMainWindow()
win.setGeometry(400, 400, 500, 500)
win.setWindowTitle('TravelBug')
# win.setStyleSheet('background-color: #666666')

statusLabel = QLabel(win)
statusLabel.setText("")
statusLabel.adjustSize()
statusLabel.move(130,35)


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

weatherButton = QPushButton(win)
weatherButton.setText("Check Weather Forecast")
weatherButton.adjustSize()
weatherButton.move(280, 115)

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
d1 = QDate(2099, 10, 10)
originDate.setDateRange(QtCore.QDate.currentDate(), d1)
originDate.setDateTime(QtCore.QDateTime.currentDateTime())
originDate.setGeometry(100, 360, 130, 30)

returnDateLabel = QLabel(win)
returnDateLabel.setText(' ')
returnDateLabel.move(250, 360)
returnDate = QDateEdit(win, calendarPopup = True)
returnDate.setDateTime(QtCore.QDateTime.currentDateTime())
returnDate.setGeometry(330, 360, 130, 30)
returnDate.hide()

searchButton = QPushButton(win)
searchButton.setText('Search Flights')
searchButton.adjustSize()
searchButton.move(200, 430)
searchButton.clicked.connect(fetchFlights)

userAttractionsButton = QPushButton(win)
userAttractionsButton.setText('See Tourist Attractions')
userAttractionsButton.adjustSize()
userAttractionsButton.move(173, 465)
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