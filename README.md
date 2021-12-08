
# Introduction
1. This is an instructions/guide document on how to run the Travel Bug app on the system.
2. This tool uses a GUI which opens as a separate window as soon as the code is executed.
3. All the output is displayed on the GUI.
4. User must input a combination of  "City, State" in the US for Origin and Destination
5. If the entered combination is valid, the user can check for three things:
	a. Check the weather forecast of the destination city for the next 5 days.
	b. Scrape for flights for the given dates. User will be returned a tabular format of the best flights scraped from Kayak.com. 
	c. User can retrieve the destination city attractions clustered by their location based on a geolocational mapping function.

# Installing Additional Packages
1. **Dependent Packages Installation**
To install the dependencies, there is a requirements.txt in the repository. Using the following command all can be installed using pip/pip3 in the terminal-
>`pip install -r requirements.txt`
2.  **Install ChromeDriver**
ChromeDriver is required for the code written on Selenium for scraping Kayak.com for flights. Weh have provided the chromedriver for MAC OS and Windows however below is the link for downloading it separately. The Selenium web driver speaks directly to the browser using the browser’s own engine to control it.
- Download Chrome WebDriver according to your existing version - https://sites.google.com/a/chromium.org/chromedriver/download
- Chrome agent used: Chrome/73.0.3683.68
3. **Installing Geopandas and Contextily on Windows**
Installation of geopandas and Contextily on MAC OS can be done using pip install geopandas and pip install contextily. However on window's we suggest to follow the link below as it is a little more complex: 
Window's Geopandas installation: https://stackoverflow.com/questions/56958421/pip-install-geopandas-on-windows/60936148
or 
Window's Installation for both we first need to download the binaries from https://www.lfd.uci.edu/~gohlke/pythonlibs/ and then run the following commands:
>`pip install GDAL-2.3.3-cp36-cp36m-win32.whl && setx GDAL_VERSION "2.3.3"`
>`pip install Fiona-1.8.4-cp36-cp36m-win32.whl`
>`pip install geopandas-0.4.0-py2.py3-none-any.whl`
>`pip install proj`
>`pip install Shapely-1.6.4.post1-cp36-cp36m-win32.whl`
>`pip install Cartopy-0.17.0-cp36-cp36m-win32.whl`
>`pip install rasterio-1.0.13-cp36-cp36m-win32.whl`
>`pip install contextily`

# How to Run
1. Instruction:
Run  gui.py file 
>`python gui.py`
>`python3 gui.py`
2. Demonstration Video: https://youtu.be/laB0nQxFThk
