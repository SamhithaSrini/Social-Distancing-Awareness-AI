
### Parses thru the risk data to create the covid risk score trend based on time of the day

class RiskParser():
    def __init__(self):
        self.allLocations = []

    def parseData(self):
        inputfilename = "./Resources/risk-dataNew.txt"
        openfile = open(inputfilename, "r")
        dataArr = []
        for line in openfile:
           date, location, sdErrors, numPeople, sdErrorsOverNumPeople = line.split("\t")
           dataArr.append({
                        "date": date, 
                        "location": location, 
                        "sdErrors": sdErrors, 
                        "numPeople": numPeople, 
                        "sdErrorsOverNumPeople": sdErrorsOverNumPeople.replace('\n','')
           })
        
        #seperate dataArr by location
        SanFrancisco = []
        NewYorkTimes = []
        NewOrleans = []
        LasVegas = []
        Hyden = []
        self.allLocations = [SanFrancisco, NewYorkTimes, NewOrleans, LasVegas, Hyden]
        
        for i in range(0, len(dataArr)):
            currLoc = dataArr[i]["location"]
            if currLoc == "1":
                NewYorkTimes.append(dataArr[i])
            elif currLoc == "2":
                SanFrancisco.append(dataArr[i])
            elif currLoc == "3":
                NewOrleans.append(dataArr[i])
            elif currLoc == "4":
                LasVegas.append(dataArr[i])
            else:
                Hyden.append(dataArr[i])
    
    def redrawAll(self, canvas, xCoord, yCoord, locationId, scaleFactor):
        locationId -= 1
        maxY = yCoord #+ 189
        
        if len(self.allLocations) > 0:
            #print(f'xCoord: {xCoord} yCoord: {yCoord} locationId: {locationId}')
            for i in range(0, len(self.allLocations[locationId])):
                date = self.allLocations[locationId][i]["date"]
                positive = float(self.allLocations[locationId][i]["sdErrorsOverNumPeople"])

                dPositive = positive * int(scaleFactor) # y Coord
                if i > 0:
                    prevPositive = float(self.allLocations[locationId][i-1]["sdErrorsOverNumPeople"])
                    dPrevPositive = prevPositive * scaleFactor
                    lX, lY = (xCoord + 1 + 3*i, int(maxY - dPrevPositive))
                    cX, cY = (xCoord + 2 + 3*i, int(maxY - dPositive))
                    canvas.create_line(lX, lY, cX, cY, fill = "indian red")
                    #print(f'{lX} {lY} {cX} {cY} --- positive: {positive} prevPositive: {prevPositive} dPositive: {dPositive}')
        canvas.create_line(xCoord, maxY, xCoord + 230, maxY)
        canvas.create_text(xCoord + 105, maxY + 20, text = "9am  12pm  3pm  6pm  9pm  12am")
        canvas.create_text(xCoord + 120, maxY - 110, text = "Daily Risk Score Trend", font="Helvetica 16 bold", fill = "dark red")
        canvas.create_text(xCoord - 40, maxY - 40, text = "Risk Score", font="Helvetica 10")
        canvas.create_text(xCoord - 25, maxY - 30, text= "max:", font="Helvetica 10")
        canvas.create_text(xCoord - 25, maxY - 20, text="100", font="Helvetica 10")
        canvas.create_line(xCoord, maxY - 100, xCoord, maxY)
