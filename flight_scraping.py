#Packages required for flight scraping 
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions
from bs4 import BeautifulSoup
import re
import pandas as pd
import numpy as np
from datetime import date, timedelta, datetime
import time

def scrapeRound(origin, destination, startdate, enddate, requests,results_round):   
    
    #URL to hit kayak.com
    url = "https://www.kayak.com/flights/" + origin + "-" + destination + "/" + startdate + "/" + enddate + "?sort=bestflight_a&fs=stops=0"
    #Setting up the webdriver for chrome and configuring the agent
    chrome_options = webdriver.ChromeOptions()
    agents = ["Chrome/73.0.3683.68"]
    chrome_options.add_argument('--user-agent=' + agents[(requests%len(agents))] + '"')    
    chrome_options.add_experimental_option('useAutomationExtension', False)
    driver = webdriver.Chrome('chromedriver.exe', options=chrome_options, desired_capabilities=chrome_options.to_capabilities())
    driver.implicitly_wait(5)
    #Get on the url generated above
    driver.get(url)

    #Check if Kayak thinks that we're a bot
    time.sleep(5) 
    soup=BeautifulSoup(driver.page_source, 'lxml')
    if soup.find_all('p')[0].getText() == "Please confirm that you are a real KAYAK user.":
        driver.close()
        time.sleep(5)
        #Need to try again
        return "failure"
    
    #Wait time for page to load
    time.sleep(10) 
    
    soup=BeautifulSoup(driver.page_source, 'lxml')
    #Get the arrival and departure times using find_all method 
    departureTimes = soup.find_all('span', attrs={'class': 'depart-time base-time'})
    arrivalTimes = soup.find_all('span', attrs={'class': 'arrival-time base-time'})
    meridies = soup.find_all('span', attrs={'class': 'time-meridiem meridiem'})
    airline=soup.find_all('div', attrs={'class': 'bottom','dir':'ltr'})
    
    #Creating list of departure times and extracting text from departure times list 
    departureTime = []
    for div in departureTimes:
        departureTime.append(div.getText()[:-1])  
    
    #Creating list of arrival times and extracting text from arrival times list  
    arrivalTime = []
    for div in arrivalTimes:
        arrivalTime.append(div.getText()[:-1])   
    
    #Creating list of meridiems to store am/pm values extracted 
    meridiem = []
    for div in meridies:
        meridiem.append(div.getText()) 
    
    #Creating a list of airlines
    airline_list=[]
    for div in airline:
        airline_list.append(div.getText().split('\n')[1])
    
    #Converting to numpy array inorder to reshape the arrays to convert into a single dataframe 
    departureTime = np.asarray(departureTime)
    departureTime = departureTime.reshape(int(len(departureTime)/2), 2)
    
    arrivalTime = np.asarray(arrivalTime)
    arrivalTime = arrivalTime.reshape(int(len(arrivalTime)/2), 2)      
    
    meridiem = np.asarray(meridiem)
    meridiem = meridiem.reshape(int(len(meridiem)/4), 4)
    
    airline_list= np.asarray(airline_list)
    airline_list= airline_list.reshape(int(len(airline_list)/2),2)
    
    #Get the price column and storing the values in price_list
    price_list = soup.find_all('span', attrs={"class":"price-text"})
    price = []
    for div in price_list:
        price_temp=div.getText().split('\n')[1].strip()
        price.append(float(price_temp[1:]))
        
    #Checks for dealing with inconsistency in sight data to create dataframe 
    if airline_list.shape == (1,2):
        df = pd.DataFrame({"origin" : origin,
                   "destination" : destination,
                   "startdate" : startdate,
                   "enddate" : enddate,
                   "price" : price[0],
                   "airline" : airline_list[:,0],
                   "currency": "USD",
                   "departure_time_origin_flight1": [m+str(n) for m,n in zip(departureTime[:,0],meridiem[:,0])],
                   "arrival_time_destintion_flight1": [m+str(n) for m,n in zip(arrivalTime[:,0],meridiem[:,1])],
                   "departure_time_from_destintion_flight2": [m+str(n) for m,n in zip(departureTime[:,1],meridiem[:,2])],
                   "arrival_time_to_origin_flight2": [m+str(n) for m,n in zip(arrivalTime[:,1],meridiem[:,3])]
                   })
    else:
        df = pd.DataFrame({"origin" : origin,
                           "destination" : destination,
                           "startdate" : startdate,
                           "enddate" : enddate,
                           "price" : price,
                           "airline" : airline_list[:,0],
                           "currency": "USD",
                           "departure_time_origin_flight1": [m+str(n) for m,n in zip(departureTime[:,0],meridiem[:,0])],
                           "arrival_time_destintion_flight1": [m+str(n) for m,n in zip(arrivalTime[:,0],meridiem[:,1])],
                           "departure_time_from_destintion_flight2": [m+str(n) for m,n in zip(departureTime[:,1],meridiem[:,2])],
                           "arrival_time_to_origin_flight2": [m+str(n) for m,n in zip(arrivalTime[:,1],meridiem[:,3])]
                           })
    #Concatenation with the results global dataframe 
    results_round = pd.concat([results_round, df], sort=False)
    #Dropping duplicates if any 
    results_round= results_round.drop_duplicates()
    #Close the browser
    driver.close() 
    #Wait for 5 seconds until next request
    time.sleep(10) 
    return "success",results_round

#Function to scrape flights for a single trip 
def scrapeOneWay(origin, destination, startdate, requests,results_single):
    
    
    #URL to hit kayak.com
    url = "https://www.kayak.com/flights/" + origin + "-" + destination + "/" + startdate + "?sort=bestflight_a"
    #Setting up the webdriver for chrome and configuring the agent
    chrome_options = webdriver.ChromeOptions()
    agents = ["Chrome/73.0.3683.68"]
    chrome_options.add_argument('--user-agent=' + agents[(requests%len(agents))] + '"')    
    chrome_options.add_experimental_option('useAutomationExtension', False) 
    driver = webdriver.Chrome("chromedriver.exe", options=chrome_options, desired_capabilities=chrome_options.to_capabilities())
    driver.implicitly_wait(5)
    #Get on the url generated above
    driver.get(url)

    #Check if Kayak thinks that we're a bot
    time.sleep(5) 
    soup=BeautifulSoup(driver.page_source, 'lxml')
    if soup.find_all('p')[0].getText() == "Please confirm that you are a real KAYAK user.":
        print("Kayak thinks I'm a bot, which I am ... so let's wait a bit and try again")
        driver.close()
        time.sleep(10)
        #Need to try again
        return "failure"
    #Wait time for page to load
    time.sleep(10) 
    
    soup=BeautifulSoup(driver.page_source, 'lxml')
    
    #Get the arrival and departure times using find_all method 
    departureTimes = soup.find_all('span', attrs={'class': 'depart-time base-time'})
    arrivalTimes = soup.find_all('span', attrs={'class': 'arrival-time base-time'})
    meridies = soup.find_all('span', attrs={'class': 'time-meridiem meridiem'})
    airline = soup.find_all('div', attrs={'class': 'bottom','dir':'ltr'})
    
    #Creating list of departure times and extracting text from departure times list 
    departuretime = []
    for div in departureTimes:
        departuretime.append(div.getText()[:-1])  
    
    #Creating list of arrival times and extracting text from arrival times list  
    arrivalTime = []
    for div in arrivalTimes:
        arrivalTime.append(div.getText()[:-1])   
    
    #Creating list of meridiems to store am/pm values extracted 
    meridiem = []
    for div in meridies:
        meridiem.append(div.getText()) 
    
    #Creating a list of airlines
    airline_list=[]
    for div in airline:
        airline_list.append(div.getText().split('\n')[1])
    
    #Converting to numpy array inorder to reshape the arrays to convert into a single dataframe 
    departuretime = np.asarray(departuretime)
    arrivalTime = np.asarray(arrivalTime)
    meridiem = np.asarray(meridiem)
    meridiem = meridiem.reshape(int(len(meridiem)/2), 2)
    airline_list = np.asarray(airline_list)

    #Get the price column and storing the values in price_list
    price_list = soup.find_all('span', attrs={"class":"price-text"})
    price = []
    for div in price_list:
        price_temp=div.getText().split('\n')[1].strip()
        price.append(float(price_temp[1:]))
        
    #Creating dataframe 
    df = pd.DataFrame({"origin" : origin,
                       "destination" : destination,
                       "startdate" : startdate,
                       "airline" : airline_list,
                       "price": price,
                       "currency": "USD",
                       "departure_time_origin_flight": [m+str(n) for m,n in zip(departuretime[:],meridiem[:, 0])],
                       "arrival_time_destintion_flight": [m+str(n) for m,n in zip(arrivalTime[:],meridiem[:, 1])]
                       })
    
    #Concatenation with the results global dataframe 
    results_single = pd.concat([results_single, df], sort=False)
    #Dropping duplicates if any 
    results_single= results_single.drop_duplicates()
    #Close the browser
    driver.close()
    #Wait 5 seconds for next request 
    time.sleep(5)  
    return "success",results_single


def call_round_function(origin,destination,startdate,enddate):
    requests = 0
    results_round= pd.DataFrame(columns=['origin','destination','startdate','enddate','price','airline','currency','departure_time_origin_flight1','arrival_time_destintion_flight1','departure_time_from_destintion_flight2','arrival_time_to_origin_flight2'])
    bool_res,result_df= scrapeRound(origin, destination, startdate, enddate, requests,results_round)
    while bool_res != "success":    
        requests = requests + 1
        bool_res,result_df= scrapeRound(origin, destination, startdate, enddate, requests,results_round)
    results_round_df = result_df.rename(columns={'airline': 'Airline', 'price': 'Price','departure_time_origin_flight1':origin+' departure time','arrival_time_destintion_flight1':destination+' arrival time','departure_time_from_destintion_flight2':destination+' departure time','arrival_time_to_origin_flight2':origin+' arrival time','origin':'Origin','destination':'Destination','currency':'Currency'})
    return results_round_df

def call_single_function(origin,destination,startdate):
    requests=0
    results_single = pd.DataFrame(columns=['origin','destination','startdate','airline','price','currency','departure_time_origin_flight','arrival_time_destintion_flight'])
    bool_res,result_df= scrapeOneWay(origin, destination, startdate, requests,results_single)
    while bool_res != "success":    
        requests = requests + 1
        bool_res,result_df= scrapeRound(origin, destination, startdate, enddate, requests,results_round)
    results_single_df = result_df.rename(columns={'airline': 'Airline', 'price': 'Price','departure_time_origin_flight':origin+' departure time','arrival_time_destintion_flight':destination+' arrival time','origin':'Origin','destination':'Destination','currency':'Currency'})
    return results_single_df
    
# if __name__=="__main__":
#     #COMING FROM USER INPUT
#     trip_type="single"
#     if(trip_type=="single"):
#         origin= 'LAX'
#         destination = 'JFK'
#         startdate = '2021-12-08'
#         result_single= call_single_function(origin,destination,startdate)
#         print(result_single)
#     else:      
#         origin= 'LAX'
#         destination = 'JFK'
#         startdate = '2021-12-08'
#         enddate= '2021-12-10'
#         result_round= call_round_function(origin,destination,startdate,enddate)
#         print(result_round)
