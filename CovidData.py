####################################
# Social Distancing Awareness App
# Chosen a city (or a video stream), based on people's interaction and behavior,
# this app determines the social distancing awareness
#
# Please follow the guidelines from README.md for installing and running the application
#
# CovidData.py
# version 0.0.2
# @author Samhitha Srinivasan

# Require Python 3.6 or later

#https://www.pngitem.com/pimgs/m/463-4637103_icon-info-transparent-svg-new-icon-hd-png.png

####################################
import requests
import sys
import os.path
from os import path
from bs4 import BeautifulSoup
from cmu_112_graphics import *

from selenium import webdriver
from selenium.webdriver.common.keys import Keys 
import time
import datetime
import shutil
import cv2
from ImageHelper import *
from CovidTrendCrawler import *
from RiskParser import *
from HelpIcon import *

class CovidData(App):
    """CovidData is the main class / program for calculating Social Distancing Awareness
    User is allowed to chose an location. Based on the location, this program uses various
    algorithms and techniques (e.g. web crawling, snapshot, face detection, etc) to find the 
    social distancing awareness.
    
    Args: None
    
    Returns: None

    """
    def __init__(self, runAsService, timerDelay):
        self.runAsService = runAsService
        if (timerDelay != None):
          self.timerDelay = timerDelay
          
        App.__init__(self, width=1000, height=800, title="Social Distancing Awareness")
      
        if (self.runAsService == True):
            self.appStarted()
        
    def appStarted(self):
        """appStarted is an implementation for parent class App to implement when the app is started
        
        Args: None
        
        Returns: None

        """
        self.debug = False
        self.locations = {
            "nyc": {
                "id": 1,
                "name": "New York",
                "state": "ny",
                "covidReportUrl": "https://news.google.com/covid19/map?hl=en-US&mid=%2Fm%2F02_286&gl=US&ceid=US%3Aen",
                "videCamUrl": "https://www.earthcam.com/cams/newyork/timessquare/?cam=tsstreet",
                "videCamUrl-new": "https://www.earthcam.com/cams/newyork/timessquare/?cam=tsrobo1",
                "totalPop" : 8330000
            },
            "sfo": {
                "id": 2,
                "name": "Miami",
                "state": "fl",
                "covidReportUrl": "https://news.google.com/covid19/map?hl=en-US&mid=%2Fm%2F0jhy9&gl=US&ceid=US%3Aen",
                "videCamUrl": "https://www.earthcam.com/usa/florida/fortlauderdale/marina/?cam=lauderdalemarina",
                "totalPop" : 883305
            },
            "New Orleans": {
                "id": 3,
                "name": "New Orleans",
                "state": "la",
                "covidReportUrl": "https://news.google.com/covid19/map?hl=en-US&mid=%2Fm%2F04ly1&gl=US&ceid=US%3Aen",
                "videCamUrl": "https://www.earthcam.com/usa/louisiana/neworleans/bourbonstreet/?cam=catsmeow2",
                "totalPop" : 301048
            },
            "Las Vegas": {
                "id": 4,
                "name": "Las Vegas",
                "state": "nv",
                "covidReportUrl": "https://news.google.com/covid19/map?hl=en-US&mid=%2Fm%2F059_c&gl=US&ceid=US%3Aen",
                "videCamUrl": "https://www.earthcam.com/usa/nevada/lasvegas/fremontstreet/?cam=catsmeow_lv_fremont",
                "totalPop" : 644644
            },
            "Hyden ": {
                "id": 5,
                "name": "Hyden",
                "state": "ky",
                "covidReportUrl": "https://news.google.com/covid19/map?hl=en-US&mid=%2Fm%2F0498y&gl=US&ceid=US%3Aen",
                "videCamUrl": "https://www.earthcam.com/usa/kentucky/hyden/?cam=hyden",
                "totalPop" : 338
            }
        }

        self.userButtonForGraph = {
            "xStart": 430,
            "width": 110,
            "height": 50,
            "btnSpacing": 20,
            "buttons": [
                {
                    "id": 1,
                    "displayName": "Positive",
                },
                {
                    "id": 2,
                    "displayName": "Hospitalized",
                },
                {
                    "id": 3,
                    "displayName": "ICU",
                },
                {
                    "id": 4,
                    "displayName": "Deceased",
                }
            ]
        }
        self.chosenButton = self.userButtonForGraph["buttons"][0]
        self.lineHeight = 30
        self.locationRectXStart = 100
        self.locationRectXEnd = 400
        self.clickedYCoord = 0
        self.getCovidReport = False
        self.processLoc = False
        self.covidTrendCrawler = None
        self.chosenLocation = None
        self.capturedImgName = None
        self.processedImgObj = None
        self.processedImgName = None
        self.reportedNumCases = None
        self.totalNumCases = None
        self.totalDeaths = None
        self.trends = None
        self.covidRiskScore = 0
        self.notSDPerson = None 
        self.persons = None
        self.chooseLocationMessage = '1. Choose one of the below locations: '
        self.statusMessage = None

        self.graphLinReg = None
        self.graphStartXCoord = 600
        self.graphStartYCoord = 245
        self.graphEndXCoord = self.width
        self.riskParser = RiskParser()
        
        image = self.loadImage("./Resources/info-icon.png")
        helpIconImg = ImageTk.PhotoImage(image)
        self.graph1HelpIcon = HelpIcon(850, 300, helpIconImg, 
                    msg="1. This dynamic graph pulled this year data\n"
                        + "    using covidtracking API\n"
                        + "2. Data is updated daily by the state(s)\n"
                        + "3. Calculated LinExp & ExpReg values for each day\n"
                        + "4. Hover over the graph to get the calculated values")

        self.graph2HelpIcon = HelpIcon(820, 495, helpIconImg, 
                    msg="The risk score factors number of people,\n"
                        + "dist.between them, and city COVID data\n"
                        + " & state COVID data\n")

        self.graph3HelpIcon = HelpIcon(820, 625, helpIconImg, 
                    msg="1. Ran it as a background service for\n"
                        + "    12 hrs to collect risk score data.\n"
                        + "2. Used this data to create hourly trends.\n")

        self.graph4HelpIcon = HelpIcon(350, 450, helpIconImg, 
                    msg="1. Used Selenium to take snapshot of live webcam.\n"
                        + "2. Identified people using OpenCV\n"
                        + "3. Measured distance btw ppl using pixel-feet ratio")

        self.graph5HelpIcon = HelpIcon(350, 315, helpIconImg, 
                    msg="1. Used Webscraping to get city data from Google\n"
                        + "2. Used this data to calculate risk score\n")
        
        self.reinit()
        self.chosenLocation = "nyc"
        self.getCovidReport = True
        

    def timerFired(self):
        if (self.runAsService == True):
            for myLocation in self.locations:
                self.reinit()
                self.chosenLocation = myLocation
                locationId = self.locations[self.chosenLocation]["name"]
                #print(f'Running risk analysys for {locationId}')
                self.getCovidReportedCasesForLocation()
                self.runRiskAnalysys()
        else:
            if (self.getCovidReport == True):
                self.getCovidReportedCasesForLocation()
                self.getCovidReport = False
                self.processLoc = True #next time when timerFired, we can processLoc
            elif (self.processLoc == True):
                self.runRiskAnalysys()
                self.processLoc = False
            """
            check if helpIcons clicked
            """
            self.graph1HelpIcon.hideHelpBox()
            self.graph2HelpIcon.hideHelpBox()
            self.graph3HelpIcon.hideHelpBox()
            self.graph4HelpIcon.hideHelpBox()
            self.graph5HelpIcon.hideHelpBox()

        
      
    def getLocationFromMouseClick(self, event):
        """
        getLocationFromMouseClick get the location based on the mouse click
        Args:
            event: Mouse clicked event

        Returns:
        Chosen location as str. If no location found, then returns None
        """
        self.clickedXCoord, self.clickedYCoord = event.x, event.y
        locationStartYCoord = 100
        locationEndYCoord = locationStartYCoord + self.lineHeight
        chosenLocation = None
        
        self.locationRectXStart = 100
        self.locationRectXEnd = 400

        # identify if user pressed a location
        for myLocation in self.locations:
            if ((locationStartYCoord <= self.clickedYCoord < locationEndYCoord) 
            and (self.locationRectXStart <= self.clickedXCoord < self.locationRectXEnd)):
                chosenLocation = myLocation
                break
            else:
                locationStartYCoord += self.lineHeight
                locationEndYCoord = locationStartYCoord + self.lineHeight

        return chosenLocation


    def getButtonForMouseClick(self, event):
        #identify if user pressed a button
        yCoordStart = 80
        y1 = yCoordStart + 2.5*self.lineHeight +20
        xCoordStart = self.userButtonForGraph["xStart"]
        xCoordEnd = xCoordStart + self.userButtonForGraph["width"]
        btnHeight = self.userButtonForGraph["height"]
        btnSpacing = self.userButtonForGraph["btnSpacing"]
        chosenButton = None

        #print(f'Mouse Clicked: {self.clickedXCoord} {self.clickedYCoord}')
        for currButton in self.userButtonForGraph["buttons"]:
            #print(f'Button: {xCoordStart} {y1} {xCoordEnd} {y1 + btnHeight}')
            if ((y1 <= self.clickedYCoord < y1 + btnHeight)
            and (xCoordStart <= self.clickedXCoord < xCoordEnd)):
                chosenButton = currButton
                break
            else:
                xCoordStart += self.userButtonForGraph["width"] + btnSpacing
                xCoordEnd = xCoordStart + + self.userButtonForGraph["width"]

        #print(f'Getting COVID trend graph for {chosenButton["displayName"]}' )
        return chosenButton


    def mousePressed(self, event):
        """mousePressed is an implementation for parent class App to implement mouse pressed event
        
        Args: event
        
        Returns: None

        """
        chosenLocation = self.getLocationFromMouseClick(event)
        
        if (chosenLocation != None):
            if chosenLocation in self.locations:
                self.reinit()
                self.chosenLocation = chosenLocation
                self.getCovidReport = True
        else:
            chosenButton = self.getButtonForMouseClick( event)
            if (chosenButton != None):
                self.chosenButton = chosenButton
            else:
                """
                check if helpIcons clicked
                """
                btnClicked = self.graph1HelpIcon.attemptToggle(event)
                btnClicked = self.graph2HelpIcon.attemptToggle(event)
                btnClicked = self.graph3HelpIcon.attemptToggle(event)
                btnClicked = self.graph4HelpIcon.attemptToggle(event)
                btnClicked = self.graph5HelpIcon.attemptToggle(event)
                if (not btnClicked):
                    """
                    check for graph mouse click
                    Graph Y starts at yCoord + 189 - 150, ends at yCoord + 200 
                    """
                    if ((self.graphStartYCoord + 189 - 150 <= event.y < self.graphStartYCoord + 200)
                              and (self.graphStartXCoord <= event.x < self.graphEndXCoord)):
                        self.graphLinReg = self.covidTrendCrawler.getRegValues(self.graphStartXCoord, event.x)
                        '''
                        if (self.chosenButton["id"] == 1):
                            self.graphLinReg = self.covidTrendCrawler.getRegForPositive(self.graphStartXCoord, event.x)
                        elif (self.chosenButton["id"] == 2):
                            self.graphLinReg = self.covidTrendCrawler.getRegForHospitalized(self.graphStartXCoord, event.x)
                        elif (self.chosenButton["id"] == 3):
                            self.graphLinReg = self.covidTrendCrawler.getRegForIcu(self.graphStartXCoord, event.x)
                        else:
                            self.graphLinReg = self.covidTrendCrawler.getRegForDeath(self.graphStartXCoord, event.x)
                        '''

    def mouseMoved(self, event):
      """
      check for graph mouse click
      Graph Y starts at yCoord + 189 - 150, ends at yCoord + 200 
      """
      if ((self.graphStartYCoord + 189 - 150 <= event.y < self.graphStartYCoord + 200)
                and (self.graphStartXCoord <= event.x < self.graphEndXCoord)):
          self.graphLinReg = self.covidTrendCrawler.getRegValues(self.graphStartXCoord, event.x)
          '''
          if (self.chosenButton["id"] == 1):
              self.graphLinReg = self.covidTrendCrawler.getRegForPositive(self.graphStartXCoord, event.x)
          elif (self.chosenButton["id"] == 2):
              self.graphLinReg = self.covidTrendCrawler.getRegForHospitalized(self.graphStartXCoord, event.x)
          elif (self.chosenButton["id"] == 3):
              self.graphLinReg = self.covidTrendCrawler.getRegForIcu(self.graphStartXCoord, event.x)
          else:
              self.graphLinReg = self.covidTrendCrawler.getRegForDeath(self.graphStartXCoord, event.x)
          '''

    def redrawAll(self,canvas):
        """redrawAll is an implementation for parent class App to redraw the screen
        is called by redrawAll
        
        Args: canvas
        
        Returns: None

        """
        #canvas.create_rectangle(0,0,self.width, self.height, fill = "MistyRose2")
        canvas.create_rectangle(20, 70, self.width - 20, self.height /4 + 90, fill = "dark grey", width = 0)

        canvas.create_text(self.width // 2, 30, text = self._title, font="Helvetica 24 bold", fill = "dark red", width = 0)

        yCoordStart = 80  #will start with 20
        yCoord = yCoordStart 

        canvas.create_text(250, yCoord + 15, text = self.chooseLocationMessage)
        yCoord += self.lineHeight/2 #give some extra space
    
        for myLocation in self.locations:
            yCoord += self.lineHeight
            canvas.create_rectangle(self.locationRectXStart, yCoord - 15, self.locationRectXEnd, yCoord + 15, 
                                    fill = "dark red" , outline = "dark grey", width = "5")
            canvas.create_text(200, yCoord, text = self.locations[myLocation]["name"], justify = 'left', 
                               anchor = 'w', fill = "white")

        self.drawGraphButtonOptions(canvas, yCoordStart)
        
        xCoord = 245
        self.drawCovidTrendInfo(canvas, xCoord, yCoord + (yCoord - yCoordStart))
        
        yCoord = self.drawCovidRiskForLocation(canvas, self.graphStartYCoord)

        if (self.processedImgObj != None):
          self.graph1HelpIcon.drawHelpIcon(canvas)
          self.graph2HelpIcon.drawHelpIcon(canvas)
          self.graph3HelpIcon.drawHelpIcon(canvas)
          self.graph4HelpIcon.drawHelpIcon(canvas)
          self.graph5HelpIcon.drawHelpIcon(canvas)
        """
        if self.statusMessage != None:
            yCoord += self.lineHeight
            canvas.create_text(200, yCoord, text = f'({self.statusMessage})')
        """

    def drawCovidTrendInfo(self, canvas, yCoordStart, currYCoord):
        if (self.chosenLocation != None):
            rectXStart = 100
            dataYCoord = yCoordStart #60
            dataYCoord += 50
  
            # canvas.create_rectangle(20, yCoordStart + 1.5 * self.lineHeight, 
            #                         self.width - 20, currYCoord + 45, 
            #                         outline = "light grey", width = 1)
            # canvas.create_rectangle(530, yCoordStart + 1.5 * self.lineHeight, 
            #                         self.width - 20, currYCoord + 45, 
            #                         fill = "light grey", width=0)

            dataYCoord += 20
            canvas.create_text(rectXStart + 115, dataYCoord, 
                               text = f'{self.locations[self.chosenLocation]["name"]} COVID Trend', 
                               font="Helvetica 20 bold", fill = "dark red", width = 0)

            dataYCoord += self.lineHeight
            canvas.create_text(rectXStart, dataYCoord, text = f'Reported Cases Today: {self.reportedNumCases}',
                               justify = 'left', anchor = 'w')
    
            dataYCoord += self.lineHeight
            canvas.create_text(rectXStart, dataYCoord, 
                               text = f'Total Number of Cases: {self.totalNumCases}',
                               justify = 'left', anchor = 'w')
    
            dataYCoord += self.lineHeight
            canvas.create_text(rectXStart, dataYCoord, text = f'Total Deaths: {self.totalDeaths}',
                               justify = 'left', anchor = 'w')
            
            
    def drawCovidRiskForLocation(self, canvas, yCoord):
        xCoord = self.graphStartXCoord 
        
        if self.processedImgObj != None:
            #print(f'Getting COVID trend graph for {self.chosenButton["displayName"]}' )
            datatype = ""
            LinRegDatatype = ""
            expRegDatatype = ""
            
            yCoord += self.lineHeight / 2
            if (self.chosenButton["id"] == 1):
                self.covidTrendCrawler.redrawForCumulativePositive(canvas, xCoord, yCoord)
                datatype = "positive"
                linRegDatatype = "positiveLinReg"
                expRegDatatype = "positiveExpReg"
            elif (self.chosenButton["id"] == 2):
                self.covidTrendCrawler.redrawForHospitalized(canvas, xCoord, yCoord)
                datatype = "hospitalized"
                linRegDatatype = "hospitalizedLinReg"
                expRegDatatype = "hospitalizedExpReg"
            elif (self.chosenButton["id"] == 3):
                self.covidTrendCrawler.redrawForICU(canvas, xCoord, yCoord)
                datatype = "icu"
                linRegDatatype = "icuLinReg"
                expRegDatatype = "icuExpReg"
            else:
                self.covidTrendCrawler.redrawForDeceased(canvas, xCoord, yCoord)
                datatype = "death"
                linRegDatatype = "deathLinReg"
                expRegDatatype = "deathExpReg"

            if (self.graphLinReg != None):
                #canvas.create_text(xCoord + 100, yCoord + 60, text = f'Linear Regression')
                rawDate = int(self.graphLinReg["date"])
                formattedDate = f'{rawDate % 10000 // 100}/{rawDate % 100}'
                canvas.create_text(xCoord + 100, yCoord + 60, text = f'Date: {formattedDate}', font="Helvetica 10", fill = "DeepSkyBlue4")
                canvas.create_text(xCoord + 100, yCoord + 75, text = f'{datatype}: {self.graphLinReg[datatype]}', font="Helvetica 10", fill = "DeepSkyBlue4")
                canvas.create_text(xCoord + 100, yCoord + 90, text = f'{self.graphLinReg[linRegDatatype]}', font="Helvetica 10", fill = "DeepSkyBlue4")
                canvas.create_text(xCoord + 100, yCoord + 105, text = f'{self.graphLinReg[expRegDatatype]}', font="Helvetica 10", fill = "DeepSkyBlue4")
                      
            yCoord += self.lineHeight /2
            yCoord += 200
            coordsAfterImg = self.drawImage(canvas, self.processedImgObj, 100, yCoord)

            xCoord = coordsAfterImg["xCoord"]

            xCoord = 540
            # canvas.create_line(20, yCoord, self.width - 20, yCoord)
            canvas.create_rectangle(xCoord - 20, yCoord, self.width - 20, coordsAfterImg["yCoord"], 
                                    fill = "light grey", width=0)

            yCoord += 20
            canvas.create_text(xCoord + 200, yCoord, 
                               text = f'COVID Risk', 
                               font="Helvetica 20 bold", fill = "dark red")

            yCoord += self.lineHeight
            textStart = xCoord+50
            canvas.create_text(textStart, yCoord, text = f'Risk score: {self.covidRiskScore}',
                                justify = 'left', anchor = 'w')
            
            yCoord += self.lineHeight
            canvas.create_text(textStart, yCoord, text = f'Non-socially distanced occurrences: {self.notSDPerson}',
                                justify = 'left', anchor = 'w')
            
            yCoord += self.lineHeight
            canvas.create_text(textStart, yCoord, text = f'Total number of people in the frame: {self.persons}',
                                justify = 'left', anchor = 'w')
        
            yCoord += 100 
            self.riskParser.redrawAll(canvas, self.graphStartXCoord, yCoord + 50, self.locations[self.chosenLocation]["id"], 25)
        return yCoord
        
    def drawImage(self, canvas, image, xCoord, cy):
        """drawImageWithSizeBelowIt is a helper function to draw the image
        is called by redrawAll
        
        Args: canvas, image, xCoord, cy
        
        Returns: None

        """
        imgMidXCoord = xCoord + self.processedImgdim["width"]/3 + 10
        imgMidyCoord = cy + self.processedImgdim["height"]/2
        canvas.create_image(imgMidXCoord, imgMidyCoord, 
                        image=ImageTk.PhotoImage(image))

        imageWidth, imageHeight = image.size

        xCoord += self.processedImgdim["width"]
        yCoord = cy + imageHeight
        return {"xCoord": xCoord, "yCoord": yCoord}

    def drawGraphButtonOptions(self, canvas, yCoordStart):
        canvas.create_text(700, 150, text = "2. Select the data you wish to see visualized:")
        y1 = yCoordStart + 2.5*self.lineHeight +20
        xCoordStart = self.userButtonForGraph["xStart"]
        xCoordEnd = xCoordStart + self.userButtonForGraph["width"]
        btnHeight = self.userButtonForGraph["height"]
        btnSpacing = self.userButtonForGraph["btnSpacing"]

        for currButton in self.userButtonForGraph["buttons"]:
            canvas.create_rectangle(xCoordStart, y1, xCoordEnd, y1 + btnHeight, fill = "DeepSkyBlue4")
            canvas.create_text(xCoordStart + 55, y1 + 25, text = currButton["displayName"], fill = "white")
            xCoordStart += self.userButtonForGraph["width"] + btnSpacing
            xCoordEnd = xCoordStart + + self.userButtonForGraph["width"]

    def logMessage(self, msg):
        """logMessage is called to report a message to console and to user interface 
        This is a helper function
        
        Args: None
        
        Returns: None

        """
        print(msg)
        self.statusMessage = msg
      
    def runRiskAnalysys(self):
        """runRiskAnalysys is the driver function to perform various steps for getting the
        risk data for a particular location and calculating the risk score 
        
        Args: None
        
        Returns: None

        """
        self.getLocationImageSnapshot()

        self.processSnapshotImage()
        self.getCovidRiskScore()
        self.riskParser.parseData()

    def getCovidReportedCasesForLocation(self):
        """
        getCovidReportedCasesForLocation finds the number of reported COVID cases in that nearest chosen city.
        This function uses webcrawler to grab the information
        
        Args: None
        
        Returns: None
        """

        state = self.locations[self.chosenLocation]["state"]
        self.covidTrendCrawler = CovidTrendCrawler(state)
        self.covidTrendCrawler.getStateReport()

        covidReportUrl = self.locations[self.chosenLocation]["covidReportUrl"]
        response = requests.get(covidReportUrl)
        soup = BeautifulSoup(response.text, 'html.parser')
        self.reportedNumCasesDiv = soup.find("div", class_ = "tIUMlb")
        self.reportedNumCases = soup.find("strong").text
        
        numCasesS = soup.find("div", class_ = "UvMayb").text
        self.totalNumCases = int(numCasesS.replace(',',''))
        #print(f'totalNumCases: *{self.totalNumCases}*')

        self.totalDeaths = self.covidTrendCrawler.getCumulativeDeathCases()
        #totalDeathsS = soup.findall("div", class_ = "UvMayb").text
        #self.totalDeaths = int(totalDeathsS.replace(',',''))
        #self.trends = soup.find("div", class_ = "dt3Iuf zC7z7b FS6bed").text

        usCasesPer1MTable = soup.find('table', class_ = "pH8O4c")
        usCasesPer1MRow = usCasesPer1MTable.find('tr', {"data-id": "/m/09c7w0"})
        self.usCasesPer1MColVal = int(usCasesPer1MRow.find_all('td')[3].text.replace(',', ''))

        listOfUSData = soup.find_all('td', class_ = "l3HOY")
        #soup.find("div", class_ = "l3HOY")
        #self.numOfCasesPerMillionUS = listOfUSData[4]
        #print(listOfUSData)

    def getCovidRiskScore(self): 
        # need to get total population -> self.locations[self.chosenLocation]["totalPop"]
        # number of total covid cases -> self.totalNumCases
        # number of cases in the past 14 days -> self.reportedNumCases
        # 0.084% chance of exposed to covid
        # 0.41% of Americans catch the flu every week

        # number of persons in the frame
        # number of not-socially distanced people / num of persons in frame

        #imageHelper = ImageHelper()
        #self.notSDPerson = imageHelper.distanceBetweenEachPerson()
        #print(f'there are {self.notSDPerson} non-socially distanced occurences')
        #print(f'There are a total of {self.persons} people in the frame')
        state = self.locations[self.chosenLocation]["state"]
        if self.persons == 0:
            self.sdRisk = 0
            self.covidRiskScore = 0
        else:
            self.sdRisk = self.notSDPerson / self.persons
            totalPopulation = self.locations[self.chosenLocation]["totalPop"]
            self.covidRiskScore = self.sdRisk * (self.totalNumCases / totalPopulation) 
            self.covidRiskScore *= 0.084 # percentage of people who have covid that don't know it
            self.covidRiskScore *= self.usCasesPer1MColVal
            self.covidRiskScore = int(self.covidRiskScore)
            
            firstDerList = self.covidTrendCrawler.get1stDerivative()
            secondDerList = self.covidTrendCrawler.get2ndDerivative()
            date1, firstDerOfToday = firstDerList[len(firstDerList) - 1]
            date2, secondDerOfToday = secondDerList[len(secondDerList) - 1]
            
            #print(f'firstDerOfToday: {firstDerOfToday}, secondDerOfToday: {secondDerOfToday}')
            if firstDerOfToday > 0 and secondDerOfToday > 0:
                self.covidRiskScore += 30
            elif firstDerOfToday < 0 and secondDerOfToday > 0:
                self.covidRiskScore += 20
            elif firstDerOfToday > 0 and secondDerOfToday < 0:
                self.covidRiskScore += 10
            else:
                self.covidRiskScore -= 20
            if (self.covidRiskScore < 0):
                self.covidRiskScore = 0
            if (self.covidRiskScore > 100):
                self.covidRiskScore = 100


            self.saveData()
            
    def saveData(self):
        """
        1. save image to images folder
        2. append analyzed data to the file
        """
        self.outfile = "./Resources/risk-data.txt"
        
        currDateTime = datetime.datetime.now()
        #print datetime in YYYYMMDD-HHMMSS format
        currDateTimeS = currDateTime.strftime("%Y%m%d-%H%M%S")
        
        currLocationId = self.locations[self.chosenLocation]["id"]
        srcFile = f'./{self.capturedImgName}'
        tgtFile = f'./Resources/images/{currLocationId}-{currDateTimeS}{self.cpaturedImgFileExtension}'
        shutil.copy(srcFile, tgtFile)
        
        #append to the existing file
        with open(self.outfile, "a") as riskDataFile:
            row = currDateTimeS
            row += f'\t{currLocationId}'
            row += f'\t{self.notSDPerson}'
            row += f'\t{self.persons}'
            row += f'\t{self.sdRisk}'
            row += f'\n'
            riskDataFile.write(row)

    def getLocationImageSnapshot(self):
        """getLocationImageSnapshot creates a image snapshot of the video.
        This function uses ChromeDriver to load the video. Then uses
        selenium to take a snapshot of the image  
        
        Args: None
        
        Returns: None

        """
        self.logMessage("Getting video image snapshot...")

        chromeDriver = "./Resources/chromedriver"
        if (path.exists(chromeDriver) == False):
          raise Exception('Chrome driver not found under Resources folder. Please download ChromeDriver')
        
        videoUrl = self.locations[self.chosenLocation]["videCamUrl"]
        #self.statusMessage = videoUrl
        print(videoUrl)

        driver = webdriver.Chrome(chromeDriver)
        driver.get(videoUrl)
        
        self.logMessage("Waiting to load video cam...")

        time.sleep(35)
        self.logMessage("Taking snapshot of the video...")

        driver.save_screenshot(self.capturedImgName)
        
        driver.close()

    def processSnapshotImage(self):
        """processSnapshotImage processes an image and calculates the social distancing  
        
        Args: None
        
        Returns: None

        """
        self.logMessage("Processing image snapshot...")

        imageName = self.capturedImgName

        faceCascade = cv2.CascadeClassifier("Resources/haarcascade_frontalface_default.xml")
        
        if (cv2.haveImageReader(imageName) == False):
            raise Exception("Failed to read the downloaded image")
        else:
            imageHelper = ImageHelper()
            # imageHelper.detectFaces(imageName, self.processedImgName)
            
            self.processedImgdim = imageHelper.detectHumans(imageName, self.processedImgName)
            #print(f'Image***: {self.processedImgdim}')
            
            self.processedImgObj = self.loadImage(self.processedImgName)
            
            imageHelper.distanceBetweenEachPerson()
            self.notSDPerson = imageHelper.notSDPerson
            self.persons = (imageHelper.person) - 1
            
    def reinit(self):
        """reinit should be called for every mouse click event. 
        reinit will reinitialize all the member variables that is used for processing
        
        Args: None
        
        Returns: None

        """
        self.getCovidReport = False
        self.processLoc = False
        self.covidTrendCrawler = None
        self.clickedYCoord = 0
        self.chosenLocation = None
        self.cpaturedImgFileExtension = ".png"
        self.capturedImgName = "./Resources/capturedImg.png"

        self.processedImgObj = None
        self.processedImgName = "./Resources/processedImg.png"
        self.processedImgdim = {"width": 0, "height": 0}

        self.reportedNumCases = None
        self.totalNumCases = None
        self.totalDeaths = None
        self.trends = None
        self.notSDPerson = None 
        self.persons = None
        self.covidRiskScore = 0
        self.statusMessage = None
        self.graphLinReg = None

