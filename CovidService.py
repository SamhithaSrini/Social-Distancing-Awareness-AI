####################################
# Social Distancing Awareness App
# Chosen a city (or a video stream), based on people's interaction and behavior,
# this app determines the social distancing awareness
#
# Please follow the guidelines from README.md for installing and running the application
#
# CovidService.py
# version 0.0.1
# @author Samhitha Srinivasan

# Require Python 3.6 or later
####################################

import time
from CovidData import CovidData

class CovidService():
    """CovidService is the service class / program for gathering various data thru backend
    Will run every 5 mins (configurable)
    
    Args: None
    
    Returns: None

    """
    def __init__(self):
        self.timerDelay = 60 #1 min in seconds
        
        
    def startService(self):
        """appStarted is an implementation for parent class App to implement when the app is started
        
        Args: None
        
        Returns: None

        """
        timerDelay = 100 # milliseconds; 1 min
        print(f'Starting to run risk analysys in loop')
        self.covidData = CovidData(runAsService=True, timerDelay=timerDelay)

covidService = CovidService()
covidService.startService()
         

  
