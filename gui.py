# importing libraries
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys
import os
import pandas as pd

# .py file imports
from clustering import *
from weather import *
from pandas_Model import *
from flight_scraping import *


userCity2 = ''
userState2 = ''

'''
Function enables the return date label depending
on whether the roundTrip radio button is checked
'''
def displayReturnDateLabel():
    if roundTrip.isChecked():
        returnDateLabel.setText('Return Date: ')
        returnDate.show()
    else:
        returnDateLabel.setText(' ')
        returnDate.hide()

'''
Function fetches flights and display the new window
with the DataFrame of flights with parameters that the user enters
'''
def fetchFlights():
    global userCity2
    global userState2

    df = pd.DataFrame()
    startDate = originDate.date()
    startDate_formatted = str(startDate.toPyDate())
    if origin.text() == '' or dest.text() == '':
        statusLabel.move(160,160)
        statusLabel.setText("Please enter an origin and destination city")
        statusLabel.adjustSize()
    else:
        originPlace = origin.text()
        destPlace = dest.text()
        if ',' in originPlace and ',' in destPlace:
            booleanVal, userCity, userState = cityStateMapping(originPlace)
            booleanVal2, userCity2, userState2 = cityStateMapping(destPlace)
        else:
            booleanVal = False
            booleanVal2 = False
            statusLabel.move(160,160)
            statusLabel.setText('Make sure input is in correct <city>,<state> format')
            statusLabel.adjustSize()
        # Debug:
        # print(userCity, userCity2)

        if booleanVal==False or booleanVal2==False:
            statusLabel.move(160,160)
            statusLabel.setText('Enter valid city-state combination in <city>,<state> format')
            statusLabel.adjustSize()
        else:
            found, originCode, destCode = airportCode(userCity, userCity2)

            # Debug:
            # print(found, originCode, destCode)

            if found == True:
                if roundTrip.isChecked():
                    endDate = returnDate.date()
                    endDate_formatted = str(endDate.toPyDate())
                    if endDate_formatted < startDate_formatted:

                        # Debug:
                        # print('Date error')
                        # print(startDate_formatted, endDate_formatted)

                        statusLabel.move(160,160)
                        statusLabel.setText('Please make sure return date is after origin date')
                        statusLabel.adjustSize()
                    else:
                        # Debug:
                        # print(endDate_formatted)
                        df = call_round_function(originCode, destCode, startDate_formatted, endDate_formatted)
                else:
                    df = call_single_function(originCode, destCode, startDate_formatted)

                # Debug:
                # print(df)

                model = pandasModel(df)
                view = QTableView()
                view.setModel(model)
                view.resize(800, 600)
                statusLabel.setText("")
                newWindow = QWidget(view)
                newWindow.resize(800, 800)
                newWindow.setWindowTitle('Flight Information')
                newLayout = QVBoxLayout(view)
                newLayout.addWidget(newWindow)
                newWindow.show()
                newLayout.addWidget(view)
                view.show()
            else:
                statusLabel.setText('These cities have no connecting flights')
                statusLabel.adjustSize()

'''
Function error checks and displays the weather forecast
window in the GUI.
'''
def displayWeather():
    if dest.text() == '':
        statusLabel.move(160,300)
        statusLabel.setText('Please enter destination city to check weather forecast')
        statusLabel.adjustSize()
    else:
        weatherForecast = fetchWeather(dest.text())

        # Debug:
        # print(weatherForecast)

        statusLabel.setText('')
        weatherWindow = QWidget()
        weatherWindow.setWindowTitle('Weather Forecast for ' + dest.text() + ' in Degrees Farenheit')
        weatherWindow.resize(1150, 200)
        weatherLayout = QHBoxLayout()
        weatherLayout.addWidget(weatherWindow)
        pic = QLabel(weatherWindow)
        pic.setGeometry(20, 20, 200, 200)
        picture = weather_mode(weatherForecast)
        if (picture == 'clouds'):
            pic.setPixmap(QPixmap(os.getcwd() + "/weatherimages/cloudy.png"))
        elif (picture == 'rain'):
            pic.setPixmap(QPixmap(os.getcwd() + "/weatherimages/rainy.png"))
        elif (picture == 'sunny'):
            pic.setPixmap(QPixmap(os.getcwd() + "/weatherimages/sunny.png"))
        elif (picture == 'snow'):
            pic.setPixmap(QPixmap(os.getcwd() + "/weatherimages/snowflake.png"))
        else:
            pic.setPixmap(QPixmap(os.getcwd() + "/weatherimages/sunny_cloudy.png"))
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

'''
Function displays userAttraction plots and geoPlotting maps
also pops up a window with the cluster labels and attractions
'''
def showUserAttractions():
    found,city,state = cityStateMapping(dest.text())
    # Debug:
    # print(concatState)

    if found:
        stateAPI = state.replace('_', ' ')
        stateAPI = stateAPI.split()
        concatState = ''
        for s in stateAPI:
            concatState = concatState + s[0:1].upper() + s[1:] + ' '
        concatState = concatState.strip()
        if roundTrip.isChecked():
            statusLabel.setText('')
            days = int(abs(returnDate.date().toPyDate() - originDate.date().toPyDate()).days)
            if days>3:
                days = 3
            elif days == 0:
                days = 1
            attractions = touristSpots(city,state)
            dfTourist = searchLatLng(state,attractions)
            clustered_df = clusterLoc(dfTourist,days)
            plotOnMap(clustered_df, concatState)
            df_to_dict(clustered_df)
            clustered_df.drop(['Latitude', 'Longitude', 'geometry'], axis = 1, inplace = True)
            clustered_df.sort_values(by = 'cluster_label', inplace=True)
            finalClustered = clustered_df.rename(columns={'cluster_label': 'Day of Trip'})
            touristSpotsModel = pandasModel(finalClustered)
            touristView = QTableView()
            touristView.setModel(touristSpotsModel)
            touristView.resize(350, 400)
            touristWindow = QWidget(touristView)
            touristWindow.resize(3500, 400)
            touristLayout = QVBoxLayout(touristView)
            touristLayout.addWidget(touristWindow)
            touristWindow.show()
            touristLayout.addWidget(touristView)
            touristView.show()
        else:
            statusLabel.move(160,160)
            statusLabel.setText('Please select a round trip')
            statusLabel.adjustSize()

# Init Main Application Window and set style along with size
app = QApplication([])
app.setStyle('Fusion')
win = QMainWindow()
win.setGeometry(400, 400, 650, 650)
win.setWindowTitle('TravelBug')
banner = QLabel(win)
banner.setGeometry(0, 0, 650, 150)
banner.setPixmap(QPixmap(os.getcwd() + "/banner.png"))

# Init status label
statusLabel = QLabel(win)
statusLabel.setText('')
statusLabel.adjustSize()
statusLabel.move(160,300)

# Init origin label
originLabel = QLabel(win)
originLabel.setText('Origin City, State')
originLabel.adjustSize()
originLabel.move(20,236)
# Init origin text box
origin = QLineEdit(win)
origin.setGeometry(210, 230, 200, 30)

# Init destination label
destLabel = QLabel(win)
destLabel.setText('Destination City, State')
destLabel.adjustSize()
destLabel.move(20,306)
# Init destination text box
dest = QLineEdit(win)
dest.setGeometry(210, 300, 200, 30)

# Init fetch weather button
weatherButton = QPushButton(win)
weatherButton.setText("Check Weather Forecast")
weatherButton.adjustSize()
weatherButton.move(430, 265)
weatherButton.clicked.connect(displayWeather)

# Layout
layout = QGridLayout()
 
 # Init trip type label
tripTypeLabel = QLabel(win)
tripTypeLabel.setText("Trip Type:")
tripTypeLabel.adjustSize()
tripTypeLabel.move(20, 370)

# Init one way trip radio button
single = QRadioButton(win)
single.setText("One-Way")
single.move(40, 410)
single.setChecked(True)
single.clicked.connect(displayReturnDateLabel)
layout.addWidget(single, 0, 0)
 
# Init round trip radio button
roundTrip = QRadioButton(win)
roundTrip.setText("Round")
roundTrip.move(40,460)
roundTrip.clicked.connect(displayReturnDateLabel)
layout.addWidget(single, 0, 1)

# Origin Date Labels and Date Box
originDateLabel = QLabel(win)
originDateLabel.setText('Origin Date: ')
originDateLabel.move(40, 510)
originDate = QDateEdit(win, calendarPopup = True)
d1 = QDate(2099, 10, 10)
originDate.setDateRange(QtCore.QDate.currentDate(), d1)
originDate.setDateTime(QtCore.QDateTime.currentDateTime())
originDate.setGeometry(150, 510, 130, 30)

# Return Date Labels and Date Box
returnDateLabel = QLabel(win)
returnDateLabel.setText(' ')
returnDateLabel.move(320, 510)
returnDate = QDateEdit(win, calendarPopup = True)
returnDate.setDateTime(QtCore.QDateTime.currentDateTime())
returnDate.setGeometry(430, 510, 130, 30)
returnDate.hide()

# Init search button
searchButton = QPushButton(win)
searchButton.setText('Search Flights')
searchButton.adjustSize()
searchButton.move(42, 590)
searchButton.clicked.connect(fetchFlights)

# Init tourist attractions button
userAttractionsButton = QPushButton(win)
userAttractionsButton.setText('See Tourist Attractions')
userAttractionsButton.adjustSize()
userAttractionsButton.move(235, 590)
userAttractionsButton.clicked.connect(showUserAttractions)

# Display main window
win.show()
# Start App
sys.exit(app.exec_())
