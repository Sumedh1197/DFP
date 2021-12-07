
# Introduction
1. This is an instructions/guide document on how to run the Travel Bug app on the system.
2. This tool uses a GUI which opens as a separate window as soon as the code is executed.
3. All the output is displayed on the GUI.
4. User must input a combination of  "City, State" in the US for Origin and Destination
5. If the entered combination is valid, the user can check for three things:
	a. Check the weather forecast of the destination city for the next 5 	 days.
	b. Scrape for flights for the given dates. User will be returned a tabular format of the best flights scraped from Kayak.com. 
	c. User can retrieve the destination city attractions clustered by their location based on a geolocational mapping function.

# How to Run
1. Instruction: Run TravelBug.py file 
2. Instruction Video: 

# Installing Additional Packages
1. **Dependent Packages Installation**
To install the dependencies, there is a requirements.txt in the repository. Using the following command all can be installed using pip-
>`pip install -r requirements.txt`
2.  **Install ChromeDriver**
ChromeDriver is required for the code written on Selenium for scraping Kayak.com for flights. The Selenium web driver speaks directly to the browser using the browser’s own engine to control it.
- Download Chrome WebDriver:
- Visit https://sites.google.com/a/chromium.org/chromedriver/download
- Select the compatible driver for your Chrome version
- To check the Chrome version you are using, click on the three vertical dots on the top right corner
- Then go to Help -> About Google Chrome
- Move the driver file to a PATH:
- Go to the downloads directory, unzip the file, and move it to usr/local/bin PATH
