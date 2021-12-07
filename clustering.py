# -*- coding: utf-8 -*-
"""
Created on Thu Nov 18 19:21:11 2021

@author: Noopur Latkar
"""

import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.cluster import MiniBatchKMeans
import seaborn as sns; sns.set()
import csv
import requests
import urllib.parse
import sys
import requests
from bs4 import BeautifulSoup
# pip install shapely
from shapely.geometry import Point
#pip install geopandas



def clusterLoc(df,days):
    df.dropna(axis=0,how='any',subset=['Latitude','Longitude'],inplace=True)
    print(df)
    
    K_clusters = range(1,5)
    kmeans = [KMeans(n_clusters=i) for i in K_clusters]
    Y_axis = df[['Latitude']]
    X_axis = df[['Longitude']]
    score = [kmeans[i].fit(X_axis).score(Y_axis) for i in range(len(kmeans))]
    # Visualize the elbox curve
    plt.plot(K_clusters, score)
    plt.xlabel('Number of Clusters')
    plt.ylabel('Score')
    plt.title('Elbow Curve')
    plt.show()
    
    kmeans = KMeans(n_clusters = days, init ='k-means++')
    # Compute k-means clustering
    kmeans.fit(df[df.columns[1:3]])     
    df['cluster_label'] = kmeans.fit_predict(df[df.columns[1:3]])
    # Labels of each point
    labels = kmeans.predict(df[df.columns[1:3]]) 
    df.plot.scatter(x = 'Latitude', y = 'Longitude', c=labels, s=50, cmap='viridis')
    print(df)
    return(df)



def searchLatLng(state, attractions):
    addresses = [i+', '+state for i in attractions]
    print(addresses)
    locations = list()
   
    for address in addresses:
        try:
            url = 'https://nominatim.openstreetmap.org/search/' + urllib.parse.quote(address) +'?format=json'
            response = requests.get(url).json()
            locations.append([address.split(',')[0], response[0]["lat"], response[0]["lon"]])
        except Exception:
            print("Invalid address : " + address)
    df = pd.DataFrame(locations, columns = ['Address', 'Latitude', 'Longitude'])
    return(df)
    
        


def touristSpots(city,state):
    city_state = str(city).lower()+'-'+str(state).lower()
    city_state = city_state.replace(' ','-')
    print(city_state)
    
    httpString = 'https://www.attractionsofamerica.com/attractions/'+city_state+'-top-10-attractions.php'
    page = requests.get(httpString)
    soup = BeautifulSoup(page.content,'html.parser')
    #container = soup.findAll("div", {"class": "pl10 pr10 pb10"})
    
    headers = soup.findAll('h2')
    attractions = list()
    for h in headers:
        if(':' in h.text):
            stripped = h.text.split(': ')[1]
            attractions.append(stripped)
    return(attractions)
        
    

def cityStateMapping(dest):
    df = pd.read_excel("uscities_short.xlsx", usecols = 'A,D')
    state = df['state_name'].loc[df['city'].str.lower() == dest.lower()]
    state = state.to_string(index=False)
    return(dest,state)


def df_to_dict(clustered_df):
    cluster_dict = clustered_df.groupby('cluster_label')['Address'].apply(list)
    cluster_dict = cluster_dict.reset_index()
    area_dict = dict(zip(cluster_dict.cluster_label, cluster_dict.Address))
    print(area_dict)
    return(area_dict)


def airportCode(origin,dest):
    col = ['municipality','local_code','type','score']
    df = pd.read_csv("us-airports.csv", usecols = col)
    df = df.iloc[1: , :]
    df_filtered_large = df[df['type'] == 'large_airport']
    df_filtered_medium = df[df['type'] == 'medium_airport']
    df_filtered = pd.concat([df_filtered_large, df_filtered_medium])
    print(df_filtered)
    
    origin_df = df_filtered[df_filtered['municipality'].str.lower() == origin.lower()]
    if(not origin_df.empty):
        origin_found = True
        origin_code = origin_df['local_code'].loc[origin_df['score'] == origin_df['score'].max()]
        origin_code = origin_code.to_string(index=False)
    else:
        origin_found = False
    
    
    dest_df = df_filtered[df_filtered['municipality'].str.lower() == dest.lower()]
    if(not dest_df.empty):
        dest_found = True
        dest_code = dest_df['local_code'].loc[dest_df['score'] == dest_df['score'].max()]
        dest_code = dest_code.to_string(index=False)
    else:
        dest_found = False
        
    print(origin_found and dest_found, origin_code, dest_code)
    return(origin_found and dest_found, origin_code, dest_code)
    
        
def main():
    dest_city = 'Dallas' #from user
    city,state = cityStateMapping(dest_city)
    attractions = touristSpots(city,state)
    
    # Number of Travel days entered by user
    days = 3 #from user
    
    #attractions = ['Mount Washington','The Andy Warhol Museum','Heinz Field','Phipps Conservatory','Point State Park','Pittsburgh Zoo & PPG Aquarium','Carnegie Mellon University']
    
    df = searchLatLng(state,attractions)
    clustered_df = clusterLoc(df,days)
    df_to_dict(clustered_df)
    airportCode('Chicago', 'New York')
    
    

if __name__ == '__main__':
    main()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    