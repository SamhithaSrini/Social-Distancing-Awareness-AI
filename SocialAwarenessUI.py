####################################
# Social Distancing Awareness App
# Choose a city (or a video stream), based on people's interaction and behavior,
# this app determines the social distancing awareness
#This is the MAIN file to be RUN!!!
#
# Please follow the guidelines from README.md for installing and running the application
#
# SocialAwarenessUI.py
# version 0.0.1
# @author Samhitha Srinivasan

# Require Python 3.6 or later
####################################

from cmu_112_graphics import *
from CovidData import CovidData

class SocialAwarenessUI(App):
    """SocialAwarenessUI is the User interface class / program for displaying the 
    awareness / risks that was gathered, analyzed through the backend
    
    Args: None
    
    Returns: None

    """
    def __init__(self):
        timerDelay = None
        self.covidData = CovidData(runAsService=False, timerDelay=timerDelay)
  
SocialAwarenessUI()