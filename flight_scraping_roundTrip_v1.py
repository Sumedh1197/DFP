
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions
from bs4 import BeautifulSoup
import re
import pandas as pd
import numpy as np
from datetime import date, timedelta, datetime
import time

def scrape_round(origin, destination, startdate, days, requests):
    
    global results
    
    enddate = datetime.strptime(startdate, '%Y-%m-%d').date() + timedelta(days)
    enddate = enddate.strftime('%Y-%m-%d')

    url = "https://www.kayak.com/flights/" + origin + "-" + destination + "/" + startdate + "/" + enddate + "?sort=bestflight_a&fs=stops=0"
    print("\n" + url)

    chrome_options = webdriver.ChromeOptions()
    agents = ["Chrome/73.0.3683.68"]
    print("User agent: " + agents[(requests%len(agents))])
    chrome_options.add_argument('--user-agent=' + agents[(requests%len(agents))] + '"')    
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome("chromedriver.exe", options=chrome_options, desired_capabilities=chrome_options.to_capabilities())
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

    time.sleep(5) #wait 20sec for the page to load
    
    soup=BeautifulSoup(driver.page_source, 'lxml')
    
    #get the arrival and departure times
    deptimes = soup.find_all('span', attrs={'class': 'depart-time base-time'})
    arrtimes = soup.find_all('span', attrs={'class': 'arrival-time base-time'})
    meridies = soup.find_all('span', attrs={'class': 'time-meridiem meridiem'})
    airline=soup.find_all('div', attrs={'class': 'bottom','dir':'ltr'})
    
    airline_list=[]
    for div in airline:
        airline_list.append(div.getText().split('\n')[1])
    
    deptime = []
    for div in deptimes:
        deptime.append(div.getText()[:-1])    
        
    arrtime = []
    for div in arrtimes:
        arrtime.append(div.getText()[:-1])   

    meridiem = []
    for div in meridies:
        meridiem.append(div.getText())  
    
        
    deptime = np.asarray(deptime)
    deptime = deptime.reshape(int(len(deptime)/2), 2)
    
    arrtime = np.asarray(arrtime)
    arrtime = arrtime.reshape(int(len(arrtime)/2), 2)      
    
    meridiem = np.asarray(meridiem)
    meridiem = meridiem.reshape(int(len(meridiem)/4), 4)
    
    airline_list= np.asarray(airline_list)
    airline_shape= airline_list.reshape(int(len(airline_list)/2),2)
        
    #Get the price
    price_list = soup.find_all('span', attrs={"class":"price-text"})
    
    price = []
    for div in price_list:
        price_temp=div.getText().split('\n')[1].strip()
        print(price_temp)
        price.append(float(price_temp[1:])) 
    
    
    print([m+str(n) for m,n in zip(deptime[:,0],meridiem[:,0])])
    

    df = pd.DataFrame({"origin" : origin,
                       "destination" : destination,
                       "startdate" : startdate,
                       "enddate" : enddate,
                       "price": price,
                       "currency": "USD",
                       "departure_time_origin_flight1": [m+str(n) for m,n in zip(deptime[:,0],meridiem[:,0])],
                       "arrival_time_destintion_flight1": [m+str(n) for m,n in zip(arrtime[:,0],meridiem[:,1])],
                       "departure_time_from_destintion_flight2": [m+str(n) for m,n in zip(deptime[:,1],meridiem[:,2])],
                       "arrival_time_to_origin_flight2": [m+str(n) for m,n in zip(arrtime[:,1],meridiem[:,3])],
                       "airline":airline_shape[:,0]
                       })

    results = pd.concat([results, df], sort=False)

    #driver.close() #close the browser

    time.sleep(15) #wait 15sec until the next request
    print(df)
    
    return "success"

#Create an empty dataframe 
results = pd.DataFrame(columns=['origin','destination','startdate','enddate','deptime_o','arrtime_d','deptime_d','arrtime_o','currency','price'])

requests = 0 

destinations = ['LAX']
startdates = ['2021-11-27']

for destination in destinations:
    for startdate in startdates:   
        requests = requests + 1
        while scrape_round('JFK', destination, startdate, 1, requests) != "success":
            requests = requests + 1