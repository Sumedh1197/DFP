# -*- coding: utf-8 -*-
"""
Created on Thu Nov 18 19:21:11 2021

@author: Noopur
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
import geopandas as gpd
from geopandas import GeoDataFrame


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
    print(df)
    return(df)
    df.plot.scatter(x = 'Latitude', y = 'Longitude', c=labels, s=50, cmap='viridis')
    

def plotOnMap(df):
    plotdf = pd.DataFrame(df, columns=['Latitude', 'Longitude'])
    
    plotdf['Latitude'] = pd.to_numeric(plotdf['Latitude'])
    plotdf['Longitude'] = pd.to_numeric(plotdf['Longitude'])
    print(type(plotdf['Latitude'].iloc[0]))
    geometry = [Point(xy) for xy in zip(plotdf['Longitude'], plotdf['Latitude'])]
    gdf = GeoDataFrame(df, geometry=geometry)   
    
    #this is a simple map that goes with geopandas
    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
    gdf.plot(ax=world.plot(figsize=(10, 6)), marker='o', color='red', markersize=15)
    world.plot()


def searchLatLng(dest_state, attractions):

    addresses = [i+', '+dest_state for i in attractions]
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
    
        


def touristSpots(df,dest):
    result_df = df[df['city'] == dest]
    dest_state = result_df['state_name'].to_string(index=False)
    city_state = result_df['city-state']
    city_state = city_state.to_string(index=False)
   
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
    return(attractions,dest_state)
        
    

def cityStateMapping(dest):
    df = pd.read_excel("uscities_short.xlsx", usecols = 'A,D')
    df['city-state'] = df['city'].str.lower()+'-'+df['state_name'].str.lower()
    df['city-state']=df['city-state'].str.replace(' ','-')
    return(df)
    
    
def main():
    dest_city = 'Miami' #from user
    city_state_map = cityStateMapping(dest_city)
    attractions,dest_state = touristSpots(city_state_map,dest_city)
    
    # Number of Travel days entered by user
    days = 3 #from user
    
    #attractions = ['Mount Washington','The Andy Warhol Museum','Heinz Field','Phipps Conservatory','Point State Park','Pittsburgh Zoo & PPG Aquarium','Carnegie Mellon University']
    df = searchLatLng(dest_state,attractions)
    clustered_df = clusterLoc(df,days)
    plotOnMap(clustered_df)

if __name__ == '__main__':
    main()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    