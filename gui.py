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

from clustering import *
from weather import *
from pandas_Model import *
from flight_scraping import *
import sys
import os
import pandas as pd

userCity2 = ''
userState2 = ''

def displayReturnDateLabel():
    if roundTrip.isChecked():
        returnDateLabel.setText('Return Date: ')
        returnDate.show()
    else:
        returnDateLabel.setText(' ')
        returnDate.hide()

def fetchFlights():
    global userCity2
    global userState2

    startDate = originDate.date()
    startDate_formatted = str(startDate.toPyDate())
    if origin.text() == '' or dest.text() == '':
        statusLabel.move(130,35)
        statusLabel.setText("Please enter an origin and destination city")
        statusLabel.adjustSize()
    else:
        originPlace = origin.text()
        destPlace = dest.text()
        booleanVal, userCity, userState = cityStateMapping(originPlace)
        booleanVal2, userCity2, userState2 = cityStateMapping(destPlace)
        
        print(userCity, userCity2)

        if booleanVal==False or booleanVal2==False:
            statusLabel.setText('Enter valid city-state combination')
        else:
            found, originCode, destCode = airportCode(userCity, userCity2)
            print(found, originCode, destCode)
            if found == True:
                if roundTrip.isChecked():
                    endDate = returnDate.date()
                    endDate_formatted = str(endDate.toPyDate())
                    print(endDate_formatted)
                    df = call_round_function(originCode, destCode, startDate_formatted, endDate_formatted)
                    # statusLabel.setText('Could not fetch flights from server. Try Again.')
                else:
                    df = call_single_function(originCode, destCode, startDate_formatted)
                    # statusLabel.setText('Could not fetch flights from server. Try Again.')

            print(df)
            model = pandasModel(df)
            view = QTableView()
            view.setModel(model)
            view.resize(800, 600)
            statusLabel.setText("")
            newWindow = QWidget(view)
            newWindow.resize(800, 800)
            newLayout = QVBoxLayout(view)
            newLayout.addWidget(newWindow)
            newWindow.show()

            newLayout.addWidget(view)
            view.show()
            # app2.show()
            #sys.exit(app2.exec_())

def displayWeather():
    if dest.text() == '':
        statusLabel.move(110,35)
        statusLabel.setText('Please enter destination city to check weather forecast')
        statusLabel.adjustSize()
    else:
        weatherForecast = fetchWeather(dest.text())
        print(weatherForecast)
        statusLabel.setText('')
        weatherWindow = QWidget()
        weatherWindow.setWindowTitle('Weather Forecast')
        weatherWindow.resize(1150, 200)
        weatherLayout = QHBoxLayout()
        weatherLayout.addWidget(weatherWindow)
        pic = QLabel(weatherWindow)
        pic.setGeometry(20, 20, 200, 200)
        #use full ABSOLUTE path to the image, not relative
        picture = weather_mode(weatherForecast)
        if (picture == 'clouds'):
            pic.setPixmap(QPixmap(os.getcwd() + "/cloudy.png"))
        elif (picture == 'rain'):
            pic.setPixmap(QPixmap(os.getcwd() + "/rainy.png"))
        elif (picture == 'sunny'):
            pic.setPixmap(QPixmap(os.getcwd() + "/sunny.png"))
        elif (picture == 'snow'):
            pic.setPixmap(QPixmap(os.getcwd() + "/snowflake.png"))
        else:
            pic.setPixmap(QPixmap(os.getcwd() + "/sunny_cloudy.png"))
        weatherStatus = QLabel(weatherWindow)
        if weatherForecast.empty:
            weatherStatus.setText('Could not fetch weather forecast data')
        elif originDate.date() >= datetime.now().date() + timedelta(days = 5):
            weatherStatus.setText('Weather forecast not available for the given dates')
        elif originDate.date() <= datetime.now().date() + timedelta(days = 5):
            toDisplay = ''
            for i, rows in weatherForecast.iterrows():
                toDisplay = toDisplay + str(rows['date_column']) + '\t\tMinimum: ' + str(round(rows['Min Temperature'], 2)) + '\t\tMaximum: ' + str(round(rows['Max Temperature'], 2)) + '\t\tAvg. Temperature: ' + str(round(rows['Temperature'], 2)) + '\t\tForecast: ' + rows['Description'] + '\n'
            weatherStatus.setText(toDisplay)
        weatherStatus.move(220, 40)
        weatherWindow.show()


app = QApplication([])
app.setStyle('Fusion')
app.setPalette(DarkPalette())
win = QMainWindow()
win.setGeometry(400, 400, 500, 500)
win.setWindowTitle('TravelBug')

statusLabel = QLabel(win)
statusLabel.setText('')
statusLabel.adjustSize()
statusLabel.move(130,35)


originLabel = QLabel(win)
originLabel.setText('Origin City, State')
originLabel.adjustSize()
originLabel.move(20,86)
origin = QLineEdit(win)
origin.move(160, 80)

destLabel = QLabel(win)
destLabel.setText('Destination City, State')
destLabel.adjustSize()
destLabel.move(20,156)
dest = QLineEdit(win)
dest.move(160, 150)

weatherButton = QPushButton(win)
weatherButton.setText("Check Weather Forecast")
weatherButton.adjustSize()
weatherButton.move(280, 115)
weatherButton.clicked.connect(displayWeather)

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
 
roundTrip = QRadioButton(win)
roundTrip.setText("Round")
roundTrip.move(40,310)
roundTrip.clicked.connect(displayReturnDateLabel)
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