####################################
# Social Distancing Awareness App
# Given a city, it crawls thru the data, finds linear and exponential regression, and 1st and 2nd der.
#
# Please follow the guidelines from README.md for installing and running the application
#
# CovidData.py
# version 0.0.2
# @author Samhitha Srinivasan

# Require Python 3.6 or later


####################################
import math
import numpy as np
import requests
import json

class CovidTrendCrawler():

    def __init__(self, state):
        self.state = state
        self.numOfDays = None
        self.printed = False
        self.filteredStateReport = []
        self.expRegDict = {}
        self.linRegDict = {}
        self.positiveDer = []
        self.positive2ndDer = []


    def getStateReport(self): 
        """
        Download state based COVID data. Then filter the list for needed data points.
        e.g. URL https://api.covidtracking.com/v1/states/ca/daily.json
        """
        cdcUrl = "https://api.covidtracking.com/v1/states/" + self.state + "/daily.json"
        response = requests.get(cdcUrl)
        # print(response.text)
        stateFullReportJson = json.loads(response.text)
        # print(stateFullReportJson)

        self.filteredStateReport = []
        self.maxValues = {}
        maxPositive = 0
        maxDeath = 0
        maxHospitalized = 0
        maxIcu = 0

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
                currDayReport["icu"] = dailyReport["hospitalizedIncrease"]
                if currDayReport["icu"] == None:
                    currDayReport["icu"] = 0

            if currDayReport["positive"] != None:
                if maxPositive < dailyReport["positive"]:
                    maxPositive = dailyReport["positive"]

            if dailyReport["death"] != None:
                if maxDeath < dailyReport["death"]:
                    maxDeath = dailyReport["death"]

            if dailyReport["hospitalizedCurrently"] != None:
                if maxHospitalized < dailyReport["hospitalizedCurrently"]:
                    maxHospitalized = dailyReport["hospitalizedCurrently"]

            if currDayReport["icu"] > 0:
                if maxIcu < currDayReport["icu"]:
                    maxIcu = currDayReport["icu"]

            self.filteredStateReport.append(currDayReport)
        self.filteredStateReport.reverse()
        #print(self.filteredStateReport)
        self.numOfDays = len(self.filteredStateReport)
        #print(self.numOfDays)
        
        self.maxValues["positive"] = maxPositive
        self.maxValues["death"] = maxDeath
        self.maxValues["hospitalized"] = maxHospitalized
        self.maxValues["icu"] = maxIcu
        
        #self.generateExpRegForPositiveCases()
        self.generateLinRegForPositiveCases()
        self.generateLinRegForHospitalizedCases()
        self.generateLinRegForIcuCases()
        self.generateLinRegForDeathCases()


    def getCumulativePositiveCases(self):
        return self.filteredStateReport[self.numOfDays - 1]["positive"]

    def getCumulativeDeathCases(self):
        return self.filteredStateReport[self.numOfDays - 1]["death"]

    def getHospitalized(self):
        return self.filteredStateReport[self.numOfDays - 1]["hospitalized"]

    def getICU(self):
        return self.filteredStateReport[self.numOfDays - 1]["icu"]

    def redrawForCumulativePositive(self, canvas, xCoord, yCoord):
        return self.redrawAll(canvas, xCoord, yCoord, "positive")

    def redrawForCumulativeDeathCases(self, canvas, xCoord, yCoord):
        return self.redrawAll(canvas, xCoord, yCoord, "death")

    def redrawForHospitalized(self, canvas, xCoord, yCoord):
        return self.redrawAll(canvas, xCoord, yCoord, "hospitalized")

    def redrawForICU(self, canvas, xCoord, yCoord):
        return self.redrawAll(canvas, xCoord, yCoord, "icu")
    
    def redrawForDeceased(self, canvas, xCoord, yCoord):
        return self.redrawAll(canvas, xCoord, yCoord, "death")
    
    def redrawAll(self, canvas, xCoord, yCoord, dataType):
        if self.numOfDays != None:
            #canvas.create_line(xCoord, yCoord + 189, xCoord + 300, yCoord + 189) #this is the x-axis line
            canvas.create_line (xCoord, yCoord + 50, xCoord , yCoord + 189)  #this the y-axis line
            canvas.create_text(xCoord - 25, yCoord + 80, text= "max:", font="Helvetica 10")
            canvas.create_text(xCoord - 25, yCoord + 90, text=self.maxValues[dataType], font="Helvetica 10")
            canvas.create_text(xCoord + 100, yCoord + 40, text = f'Cumulative {dataType} COVID-19 Cases', font="Helvetica 14 bold")
            canvas.create_text(xCoord + 150, yCoord + 200, text = "FEB  MAR  APR  MAY  JUN  JUL  AUG  SEPT  OCT  NOV  DEC", font = "Helvetica 10")
            maxY = yCoord + 189
            scaleFactor = 1
            if (self.maxValues[dataType] > 0):
              scaleFactor = 140 / self.maxValues[dataType]
            
            for i in range(0, self.numOfDays):
                date = self.filteredStateReport[i]["date"]
                positive = self.filteredStateReport[i][dataType]

                dPositive = positive * int(scaleFactor) # y Coord
                #print(f'{positive} *{scaleFactor}*')
                if i == 0:
                    lX, lY = (xCoord + 10, maxY)
                    cX = xCoord + 1
                    #print(f'{maxInt} *{dPositive}*')
                    cY = maxY - dPositive
                    canvas.create_line(lX, lY, cX, cY)
                else:
                    prevPositive = self.filteredStateReport[i-1][dataType]
                    dPrevPositive = prevPositive * scaleFactor
                    lX, lY = (xCoord + 1 + i, int(maxY - dPrevPositive))
                    cX, cY = (xCoord + 2 + i, int(maxY - dPositive))
                    canvas.create_line(lX, lY, cX, cY, fill = "indian red")
                    #print(f'{lX} {lY} {cX} {cY}')
    
    def getRegValues(self, startXCoord, xCoord):
        arrayId = xCoord - startXCoord
        if (arrayId < 15):
            arrayId = 15
        elif (arrayId > self.numOfDays-16):
            arrayId = self.numOfDays-16
        
        return self.filteredStateReport[arrayId]

    def getExpRegForPositive(self, startXCoord, xCoord):
        arrayId = xCoord - startXCoord
        if (arrayId < 15):
            arrayId = 15
        elif (arrayId > self.numOfDays-16):
            arrayId = self.numOfDays-16
        
        return {"date": self.filteredStateReport[arrayId]["date"],
                "positive": self.filteredStateReport[arrayId]["positive"],
                "positiveExpReg": self.filteredStateReport[arrayId]["positiveExpReg"]}

    def getRegForPositive(self, startXCoord, xCoord):
        arrayId = xCoord - startXCoord
        if (arrayId < 15):
            arrayId = 15
        elif (arrayId > self.numOfDays-16):
            arrayId = self.numOfDays-16
        
        return {"date": self.filteredStateReport[arrayId]["date"],
                "positive": self.filteredStateReport[arrayId]["positive"],
                "positiveLinReg": self.filteredStateReport[arrayId]["positiveLinReg"],
                "positiveExpReg": self.filteredStateReport[arrayId]["positiveExpReg"]}
    
    def getRegForDeath(self, startXCoord, xCoord):
        arrayId = xCoord - startXCoord
        if (arrayId < 15):
            arrayId = 15
        elif (arrayId > self.numOfDays-16):
            arrayId = self.numOfDays-16
        
        return {"date": self.filteredStateReport[arrayId]["date"],
                "death": self.filteredStateReport[arrayId]["death"],
                "deathLinReg": self.filteredStateReport[arrayId]["deathLinReg"],
                "deathExpReg": self.filteredStateReport[arrayId]["deathExpReg"]}
    
    def getRegForHospitalized(self, startXCoord, xCoord):
        arrayId = xCoord - startXCoord
        if (arrayId < 15):
            arrayId = 15
        elif (arrayId > self.numOfDays-16):
            arrayId = self.numOfDays-16
        
        return {"date": self.filteredStateReport[arrayId]["date"],
                "hospitalized": self.filteredStateReport[arrayId]["hospitalized"],
                "hospitalizedLinReg": self.filteredStateReport[arrayId]["hospitalizedLinReg"],
                "hospitalizedExpReg": self.filteredStateReport[arrayId]["hospitalizedExpReg"]}
    
    def getRegForIcu(self, startXCoord, xCoord):
        arrayId = xCoord - startXCoord
        if (arrayId < 15):
            arrayId = 15
        elif (arrayId > self.numOfDays-16):
            arrayId = self.numOfDays-16
        
        return {"date": self.filteredStateReport[arrayId]["date"],
                "icu": self.filteredStateReport[arrayId]["icu"],
                "icuLinReg": self.filteredStateReport[arrayId]["icuLinReg"],
                "icuExpReg": self.filteredStateReport[arrayId]["icuExpReg"]}
    
    def generateExpRegForPositiveCases(self):
        """
        We will find Exponential Regression for each and every day 
        """
        self.expRegDict = {}
        
        for i in range(15, self.numOfDays-15):
            positive = []
            currDate = self.filteredStateReport[i]["date"]
            for j in range(i-15, i+15): #get the past 15 days and next 15 days for the given day
                positive.append(self.filteredStateReport[j]["positive"])
            self.filteredStateReport[i]["positiveExpReg"] = self.findExpRegForPositiveCases(positive)

    def generateLinRegForPositiveCases(self):
        """
        We will find Linear Regression for each and every day 
        """
        self.linRegDict = {}
        
        for i in range(15, self.numOfDays-15):
            positive = []
            currDate = self.filteredStateReport[i]["date"]
            for j in range(i-15, i+15): #get the past 15 days and next 15 days for the given day
                positive.append(self.filteredStateReport[j]["positive"])
            self.filteredStateReport[i]["positiveExpReg"] = self.findExpRegForCases(positive)
            self.filteredStateReport[i]["positiveLinReg"] = self.findLinRegForCases(positive)
                
    def generateLinRegForHospitalizedCases(self):
        """
        We will find Linear Regression for each and every day 
        """
        self.linRegDict = {}
        
        for i in range(15, self.numOfDays-15):
            positive = []
            currDate = self.filteredStateReport[i]["date"]
            for j in range(i-15, i+15): #get the past 15 days and next 15 days for the given day
                positive.append(self.filteredStateReport[j]["hospitalized"])
            self.filteredStateReport[i]["hospitalizedExpReg"] = self.findExpRegForCases(positive)
            self.filteredStateReport[i]["hospitalizedLinReg"] = self.findLinRegForCases(positive)
                
    def generateLinRegForIcuCases(self):
        """
        We will find Linear Regression for each and every day 
        """
        self.linRegDict = {}
        
        for i in range(15, self.numOfDays-15):
            positive = []
            currDate = self.filteredStateReport[i]["date"]
            for j in range(i-15, i+15): #get the past 15 days and next 15 days for the given day
                positive.append(self.filteredStateReport[j]["icu"])
            self.filteredStateReport[i]["icuExpReg"] = self.findExpRegForCases(positive)
            self.filteredStateReport[i]["icuLinReg"] = self.findLinRegForCases(positive)
                
    def generateLinRegForDeathCases(self):
        """
        We will find Linear Regression for each and every day 
        """
        self.linRegDict = {}
        
        for i in range(15, self.numOfDays-15):
            positive = []
            currDate = self.filteredStateReport[i]["date"]
            for j in range(i-15, i+15): #get the past 15 days and next 15 days for the given day
                positive.append(self.filteredStateReport[j]["death"])
            self.filteredStateReport[i]["deathExpReg"] = self.findExpRegForCases(positive)
            self.filteredStateReport[i]["deathLinReg"] = self.findLinRegForCases(positive)
                
    def findExpRegForCases(self, datatype):
        """
        # adpated from https://gist.github.com/shuklapratik/983898a11b3b26c95bd910d084c31db2
        """
        X = np.arange(0, len(datatype))
        Y = []
        
        for i in range(0, len(datatype)):
            Y.append(datatype[i]) 
        
        n = len(X)
        x_bias = np.ones((n,1))
        
        #print("Shape of x_bias : ",x_bias.shape)
        #print("Shape of X : ",X.shape)
        
        X = np.reshape(X,(n,1))
        #print("Shape of X : ",X.shape)
        
        Y_log = np.log(Y)
        x_new = np.append(x_bias,X,axis=1)
        x_new_transpose = np.transpose(x_new)
        x_new_transpose_dot_x_new = x_new_transpose.dot(x_new)
        temp_1 = np.linalg.inv(x_new_transpose_dot_x_new)
        temp_2 = x_new_transpose.dot(Y_log)
        
        theta = temp_1.dot(temp_2)
        #print("Coefficients : ",theta)
        #print(f'y = {theta[0]} * {theta[1]} ^x')
        return f'y = {round(theta[0], 2)} * {round(theta[1], 2)} ^x'

    def findLinRegForCases(self, datatype):
        X = np.arange(0, len(datatype))
        Y = []
        sumY = 0
        for i in range(0, len(datatype)):
            Y.append(datatype[i])
            sumY += datatype[i]
        meanY = sumY / len(datatype)

        # linear regression formula is y = mx + b
        # m = sum((x - X_)*(y - Y_)) / sum((x - x_)^2)
        sumX = 0
        for i in range(0, len(datatype)):
            sumX += X[i]
        meanX = sumX / len(datatype)

        mNum = 0
        mDen = 0
        for i in range(0, len(datatype)):
            mNum += (X[i] - meanX)*(Y[i] - meanY)
            mDen += (X[i] - meanX) * (X[i] - meanX)
        m = round(mNum / mDen, 2)
        b = round(meanY - m*meanX, 2)

        #r^2 = sum(predY - meanY)^2 / sum (actualY - meanY)^2
        rValueSqrNum = 0
        rValueSqrDen = 0
        for i in range(0, len(datatype)):
            predY = m*(X[i]) + b
            rValueSqrNum += (predY - meanY)*(predY - meanY)
            rValueSqrDen += (Y[i] - meanY)*(Y[i] - meanY)
        rVal = (1 - rValueSqrNum/rValueSqrDen)**0.5
        rVal = round(rVal, 3)
        return f'y = {m}x + {b} R: {rVal}'

    def get1stDerivative(self):
        self.getStateReport()
        self.positiveDer = []
        if self.numOfDays != None:
            for i in range(0, self.numOfDays - 2):
                    date1 = self.filteredStateReport[i]["date"]
                    dataChar1 = self.filteredStateReport[i]["positive"] 
                    date2 = self.filteredStateReport[i + 1]["date"]
                    dataChar2 = self.filteredStateReport[i + 1]["positive"] 
                    slope = (dataChar2 - dataChar1)
                    slope *= 0.0036
                    slope = int(slope)
                    self.positiveDer.append((date1,slope))
        return self.positiveDer 

    def get2ndDerivative(self):
        self.get1stDerivative()
        self.positive2ndDer = []
        if self.numOfDays != None:
            for i in range(0, len(self.positiveDer) - 4):
                    (date1, dataChar1) = self.positiveDer[i] 
                    date2, dataChar2 = self.positiveDer[i + 1] 
                    slope = (dataChar2 - dataChar1) 
                    slope *= 0.036
                    slope = int(slope)
                    self.positive2ndDer.append((date1,slope))
        return self.positive2ndDer

    





