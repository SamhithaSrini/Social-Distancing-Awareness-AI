Social Distancing Awareness App
 The purpose of my project is to determine whether people in public places are socially distanced using person recognition. Not only will I be able to calculate whether people are 6 ft apart from each other, I will webscrape live covid data in the city of the webcam to create a risk score (i.e. how likely covid will spread) for the people in that location. 

VIDEO URL : https://youtu.be/PhiBRXYxUj0

Setup:
To install the program do the following
1. Require Python 3.6 or later
2. Need to have Chrome browser installed
3. Download source code
4. Download Chrome driver from https://chromedriver.storage.googleapis.com/index.html?path=87.0.4280.20/ into Resources folder
5.1. MAC users - make sure to go to menu "system preferences -> security" to allow to run the downloaded chromedriver program
6. Import all the dependent packages using command `pip install -U -r requirements.txt`
7. Require a monitor that has min. 1000 x 800 resolution


Run:
Run the program using command `python SocialAwarenessUI.py`
1. To run the program with UI (TA use this method, run the SocialAwarenessUI.py file

	a. New York Times Square is the default to start
	
	b. The live webcam will pop-up (sometimes there is ads but after 30s, it will		 still work. 
	
	c. In the pop-up, you can zoom, move camera L, R, U & D.
	
	d. After 30s, you will automatically move to the UI
	
	e. [City] COVID trend is daily webscraped from news.google
	
	f. Cumulative [dataType] Cases graph uses covidTrackingProject API and it has 		   daily data from Feb 1st to curr day (this is also webscraped)
	g. You can hover over any points in the graph and it will show you the data, 		number of cases of [dataType], linear regression line (based on 30 days window of	 specific date), exponential regression line, and R-value. 
	
	h. You can click on different types data (#2. Blue bar) and this will change the 	cumulative graph. 
	
	i. Now, look at the webcam live image. The green boxes refer to the people
	 detected (algorithm using OpenCV and selenium)
	 
	j. In Covid Risk box, I display the number of people and number of non-socially
	   distanced occurences. And I also display a Covid Risk Score
	   
		a. Covid Risk Score: uses webcam data, 1st and 2nd derivative values of
		 cumulative positive cases for [city]. 
			a. If 1st der > 0, this means positive cases are increasing
			b. If 2nd der > 0 and 1st der >0, cases are increasing at an				   increasing rate
			c. Uses conditionals based on 1st and 2nd der to alter risk score
		b. riskScore *= number of total covid-cases [city] / total pop. of [city]
		c. riskScore *= US covid cases per 1M ppl
		d. riskScore *= (factoring in reported positive cases [city] in past 14
		    days)
		e. Please refer to getCovidRiskScore() for all details
		
	k. Using the service (#2 below), I ran my program for 15 hours to track how my
	 covid risk score in all cities changes depending on time of the day. This trend
	 is displayed in "Daily Risk Score Trend".
	 
	l. To choose a diff. city, click on the red box to restart.
	
	m. If you click on the info icon (orange), you will see how I generate that info
	
	n. Enjoy! :-)


2.To run the program as service (this will run program byitself without UI in a loop and generate risk score data / city -> 25 data points per hour
	a. I ran this program to track how my covid risk score in all cities changes 		   depending on time of the day 
