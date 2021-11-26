from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions
from bs4 import BeautifulSoup
import re
import pandas as pd
import numpy as np
from datetime import date, timedelta, datetime
import time

def scrapeOneWay(origin, destination, startdate, requests):
    
    global results
    
    url = "https://www.kayak.com/flights/" + origin + "-" + destination + "/" + startdate + "?sort=bestflight_a"
    print("\n" + url)

    chrome_options = webdriver.ChromeOptions()
    agents = ["Chrome/73.0.3683.68"]
    print("User agent: " + agents[(requests%len(agents))])
    chrome_options.add_argument('--user-agent=' + agents[(requests%len(agents))] + '"')    
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome("/Users/rohit/DFP/chromedriver", options=chrome_options, desired_capabilities=chrome_options.to_capabilities())
    driver.implicitly_wait(20)
    driver.get(url)

    #Check if Kayak thinks that we're a bot
    time.sleep(5) 
    soup=BeautifulSoup(driver.page_source, 'lxml')

    if soup.find_all('p')[0].getText() == "Please confirm that you are a real KAYAK user.":
        print("Kayak thinks I'm a bot, which I am ... so let's wait a bit and try again")
        driver.close()
        time.sleep(20)
        return "failure"

    time.sleep(20) #wait 20sec for the page to load
    
    soup=BeautifulSoup(driver.page_source, 'lxml')
    
    #get the arrival and departure times
    deptimes = soup.find_all('span', attrs={'class': 'depart-time base-time'})
    arrtimes = soup.find_all('span', attrs={'class': 'arrival-time base-time'})
    meridies = soup.find_all('span', attrs={'class': 'time-meridiem meridiem'})
    airline = soup.find_all('div', attrs={'class': 'bottom','dir':'ltr'})
    
    deptime = []
    for div in deptimes:
        deptime.append(div.getText()[:-1])    
        
    arrtime = []
    for div in arrtimes:
        arrtime.append(div.getText()[:-1])   

    meridiem = []
    for div in meridies:
        meridiem.append(div.getText()) 
    
    airline_list=[]
    for div in airline:
        airline_list.append(div.getText().split('\n')[1])
        
    deptime = np.asarray(deptime)
    arrtime = np.asarray(arrtime)
    meridiem = np.asarray(meridiem)
    meridiem = meridiem.reshape(int(len(meridiem)/2), 2)
    airline_list = np.asarray(airline_list)

    #Get the price
    price_list = soup.find_all('span', attrs={"class":"price-text"})
    #print(price_list)
    price = []
    for div in price_list:
        price.append(div.getText().split('\n')[1].strip())
    
    print(deptime)
    print(arrtime)
    print(meridiem)
    print(price)
    print()

    df = pd.DataFrame({"origin" : origin,
                       "destination" : destination,
                       "startdate" : startdate,
                       "airline" : airline_list,
                       "price": price,
                       "currency": "USD",
                       "departure_time_origin_flight": [m+str(n) for m,n in zip(deptime[:],meridiem[:, 0])],
                       "arrival_time_destintion_flight": [m+str(n) for m,n in zip(arrtime[:],meridiem[:, 1])]
                       })

    results = pd.concat([results, df], sort=False)

    driver.close() #close the browser

    time.sleep(15) #wait 15sec until the next request
    print(df)
    
    return "success"

# #Create an empty dataframe 
results = pd.DataFrame(columns=['origin','destination','startdate','deptime_o','arrtime_d','currency','price'])

requests = 0 

destinations = ['LAX']
startdates = ['2021-11-27']

for destination in destinations:
    for startdate in startdates:   
        requests = requests + 1
        while scrapeOneWay('JFK', destination, startdate, requests) != "success":
            requests = requests + 1