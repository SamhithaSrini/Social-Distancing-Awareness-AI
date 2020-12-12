import requests
import json
from cmu_112_graphics import *


### this is not being used by just in case crawler file does not wokr
class DataAnalytics(App):

    def __init__(self):
        App.__init__(self, width=1000, height=800, title="Data Analytics")
      
    def appStarted(self):
        self.state = "ca"
        self.numOfDays = None
        self.printed = False
        self.filteredStateReport = []
        self.positiveDer = []
        self.positive2ndDer = []

    def timerFired(self):
        #if self.positive2ndDer == []:
            #self.get2ndDerivative(self.state)
        if self.positiveDer == []:
            self.get1stDerivative(self.state)


    def getStateReport(self, state): 
        """
        Download state based COVID data. Then filter the list for needed data points.
        e.g. URL https://api.covidtracking.com/v1/states/ca/daily.json
        """
        cdcUrl = "https://api.covidtracking.com/v1/states/" + self.state + "/daily.json"
        response = requests.get(cdcUrl)
        stateFullReportJson = json.loads(response.text)

        self.filteredStateReport = []
        for dailyReport in stateFullReportJson:
            currDayReport = {
                "date": dailyReport["date"],
                "positive": dailyReport["positive"],
                "death": dailyReport["death"],
                "hospitalized": dailyReport["hospitalizedCurrently"],
                "icu": dailyReport["inIcuCurrently"]
                }

            if currDayReport["hospitalized"] == None:
                currDayReport["hospitalized"] = 0

            if currDayReport["death"] == None:
                currDayReport["death"] = 0

            if currDayReport["icu"] == None:
                currDayReport["icu"] = 0

            self.filteredStateReport.append(currDayReport)
        self.filteredStateReport.reverse()
        self.numOfDays = len(self.filteredStateReport)

    def get1stDerivative(self,state):
        self.getStateReport(state)
        if self.numOfDays != None:
            self.positiveDer = []
            for i in range(0, self.numOfDays - 2):
                    date1 = self.filteredStateReport[i]["date"]
                    dataChar1 = self.filteredStateReport[i]["positive"] 
                    date2 = self.filteredStateReport[i + 1]["date"]
                    dataChar2 = self.filteredStateReport[i + 1]["positive"] 
                    slope = (dataChar2 - dataChar1)
                    slope *= 0.0036
                    slope = int(slope)
                    self.positiveDer.append((date1,slope))
                    print(slope)

    def get2ndDerivative(self,state):
        self.get1stDerivative(state)
        if self.numOfDays != None:
            self.positive2ndDer = []
            for i in range(0, self.numOfDays - 3):
                    (date1, dataChar1) = self.positiveDer[i] 
                    date2, dataChar2 = self.positiveDer[i + 1] 
                    slope = (dataChar2 - dataChar1) 
                    slope *= 0.036
                    slope = int(slope)
                    self.positive2ndDer.append((date1,slope))
                    #print(int(slope))

    
    def redrawAll(self, canvas, xCoord = 10, yCoord = 300):
        if self.numOfDays != None:
            canvas.create_line(xCoord, yCoord + 189, xCoord + 300, yCoord + 189) #this is the x-axis line
            canvas.create_line (xCoord, yCoord + 9, xCoord , yCoord + 189)  #this the y-axis line
            canvas.create_text(xCoord + 150, yCoord + 40, text = f'1st Derivative Positive COVID-19 Cases', font="Helvetica 14 bold")
            maxY = yCoord + 189
            listOfCoords = []
            for i in range(0, self.numOfDays - 4):
                date1, der1 = self.positiveDer[i] #self.positive2ndDer[i]
                date2, der2 = self.positiveDer[i+1] #self.positive2ndDer[i + 1]
                canvas.create_line(xCoord + i, - der1 + maxY, xCoord + i + 1, - der2 + maxY)

DataAnalytics()