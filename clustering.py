#Packages to be imported
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
import contextily as cx
from bs4 import BeautifulSoup
# pip install shapely
import geopandas as gpd
from geopandas import GeoDataFrame
import json
import os

'''
Function performs k-means clustering on geo-locations of tourist places, returns a dataframe of locations and their associated clusters
@param: dataframe, days of travel 
        1. dataframe - tourist attractions and their locations (lat,lng)
        2. days of travel - calculated from startdate enddate entered by user
'''

def clusterLoc(df,days):
    df.dropna(axis=0,how='any',subset=['Latitude','Longitude'],inplace=True)
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
    plt.title('Grouping Attractions by Cluster (unique color for each cluster)')
    plt.xticks(rotation = 90)
    plt.show()
    return(df)


'''
Function fetches geo-locations for tourist places using API, returns a dataframe of location names and their associated latitudes and longitudes
@param: state, attractions 
        1. state - destination state of city entered by user
        2. attractions - list of top tourist attractions in the destination_city
'''

def searchLatLng(state, attractions):
    addresses = [i+', '+state for i in attractions]
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


'''
Function fetches top tourist attractions for destination_city by web scraping, returns a list of tourist attractions for that city
@param: city, state 
        1. city - destination city entered by user
        2. state - state of corresponding destination_city
'''        

def touristSpots(city,state):
    city_state = str(city).lower()+'-'+str(state).lower()
    city_state = city_state.replace(' ','-')
    city_state = city_state.replace('_', '-')
    
    if city_state == 'new-york-new-york':
        httpString = 'https://www.attractionsofamerica.com/attractions/new-york-city-top-10-attractions.php'
    else:
        httpString = 'https://www.attractionsofamerica.com/attractions/'+city_state+'-top-10-attractions.php'
    page = requests.get(httpString)
    soup = BeautifulSoup(page.content,'html.parser')
    headers = soup.findAll('h2')
    attractions = list()
    for h in headers:
        if(':' in h.text):
            stripped = h.text.split(': ')[1]
            attractions.append(stripped)
    return(attractions)
        

'''
Function maps destination_city to its corresponding state, returns boolean value if the combination exists in CSV
@param: dest - destination_city entered by user
'''        

def cityStateMapping(dest):
    usercity,userstate = dest.split(',')
    usercity = usercity.strip().lower().replace(" ","_")
    userstate = userstate.strip().lower().replace(" ","_")
    df = pd.read_excel(os.getcwd() + "/data/uscities.xlsx", usecols = 'A,D')
    df['city'] = df['city'].str.replace(" ","_").str.lower()
    df['state_name'] = df['state_name'].str.replace(" ","_").str.lower()
    if(df.loc[df.city == usercity, 'state_name'].values[0].lower() == userstate):
        return (True,usercity,userstate)
    else:
        return (False,0,0)


'''
Function converts dataframe to dictionary by taking cluster_labels as keys and corresponding attractions as values
@param: clustered_df - dataframe contains tourists places and their cluster labels
'''  

def df_to_dict(clustered_df):
    cluster_dict = clustered_df.groupby('cluster_label')['Address'].apply(list)
    cluster_dict = cluster_dict.reset_index()
    area_dict = dict(zip(cluster_dict.cluster_label, cluster_dict.Address))
    return(area_dict)


'''
Function plots clustered tourist attractions on state map using geopandas
'''  

def plotOnMap(df, concatState):
    plotdf = pd.DataFrame(df, columns=['Latitude', 'Longitude'])
    plotdf['Latitude'] = pd.to_numeric(plotdf['Latitude'])
    plotdf['Longitude'] = pd.to_numeric(plotdf['Longitude'])
    geometry = [Point(xy) for xy in zip(plotdf['Longitude'], plotdf['Latitude'])]
    gdf = GeoDataFrame(df, geometry=geometry)   
    
    url = 'https://gist.githubusercontent.com/mshafrir/2646763/raw/8b0dbb93521f5d6889502305335104218454c2bf/states_hash.json'
    response = requests.get(url).text
    response_json = json.loads(response)
    statesJSON = invertJSON(response_json)
    stateCode = statesJSON[concatState]

    usa = gpd.read_file(os.getcwd() + '/shapefiles/states.shp')
    usa = usa[usa.STATE_ABBR == stateCode]
    ax = gdf.plot(ax=usa.plot(figsize = (10, 10)), c = gdf.cluster_label, marker = 'o', markersize = 15, legend = True)
    cx.add_basemap(ax, crs = gdf.crs, zoom = 18)
    plt.title('Cluster Map for State')
    plt.show()
    
def invertJSON(json):
    ret = {}
    for key in json.keys():
        ret[json[key]] = key
    return ret



'''
Function maps city, state to a respective airport using CSV, returns boolean, and airport codes for origin and destination city
@param: origin, dest
        1. origin - origin city
        2. destination - destination city
'''

def airportCode(origin,dest):
    origin = origin.lower().replace(' ','_')
    dest = dest.lower().replace(' ','_')
    col = ['municipality','local_code','type','score']
    df = pd.read_csv(os.getcwd() + "/data/us-airports.csv", usecols = col)
    df = df.iloc[1: , :]
    df_filtered_large = df[df['type'] == 'large_airport']
    df_filtered_medium = df[df['type'] == 'medium_airport']
    df_filtered = pd.concat([df_filtered_large, df_filtered_medium])
    
    
    df_filtered['municipality'] = df_filtered['municipality'].str.lower().str.replace(" ","_")
    origin_df = df_filtered[df_filtered['municipality'] == origin]
    
    if(not origin_df.empty):
        origin_found = True
        origin_code = origin_df['local_code'].loc[origin_df['score'] == origin_df['score'].max()]
        origin_code = origin_code.to_string(index=False)
    else:
        origin_found = False
    
    
    dest_df = df_filtered[df_filtered['municipality'] == dest]
    if(not dest_df.empty):
        dest_found = True
        dest_df['score'] = dest_df['score'].astype(str).astype(int)
        dest_df.sort_values(by=['score'], ascending=False, inplace = True)
        dest_code = dest_df['local_code'].iloc[0]
      
    else:
        dest_found = False
        
    return (origin_found and dest_found, origin_code, dest_code)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
