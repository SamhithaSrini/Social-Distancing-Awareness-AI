import datetime
from datetime import timedelta


### this print the help icon and the info need for UI
class HelpIcon():
    def __init__(self, xCoord, yCoord, helpIconImg, msg):
        self.helpIconImg = helpIconImg
        self.display = False
        self.xCoord = xCoord
        self.yCoord = yCoord
        self.imgSize = 24
        self.msg = msg
        self.startTimer = None
    
    def drawHelpIcon(self, canvas):
        if (self.display):
            canvas.create_rectangle(self.xCoord-230, self.yCoord-110, 
                    self.xCoord+100, self.yCoord + 10, fill = "blue4", 
                    width=2, outline="white")
            canvas.create_text(self.xCoord-65, self.yCoord-96, text="Info", 
                               fill = "white", font="Helvetica 20")
            canvas.create_rectangle(self.xCoord-230, self.yCoord-80, 
                    self.xCoord+100, self.yCoord + 40, fill = "MistyRose2", width=2, outline="white") #MistyRose2
            if (self.msg != None):
                canvas.create_text(self.xCoord-65, self.yCoord-20, text=self.msg)
        else:
            canvas.create_image(self.xCoord, self.yCoord, image=self.helpIconImg)

    def attemptToggle(self, event):
        #print(f'event:{event} btn xCoord: {self.xCoord} yCoord: {self.yCoord}')
        if ((self.xCoord - 12 <= event.x < self.xCoord + 12)
                and (self.yCoord - 12 <= event.y < self.yCoord + 12)):
            self.display = not self.display
            self.startTimer = datetime.datetime.now()
            return True

    def hideHelpBox(self):
        if (self.display):
            endTime = datetime.datetime.now()
            
            timeDiff = endTime - self.startTimer
            timeDiffSeconds = timeDiff.total_seconds() * 1000

            #print(f'timeDiff: {timeDiff}    timeDiffSeconds: {timeDiffSeconds}')
            if (timeDiffSeconds >= 8000):
                self.display = False