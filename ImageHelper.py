import cv2
#import imutils
import numpy as np
from cmu_112_graphics import *


### finds distance between people and finds person in the image of live webcam
class ImageHelper():

    def __init__(self):
        self.notSDPerson = 0

    def distanceBetweenEachPerson(self):
        #HOGCV = cv2.HOGDescriptor()
        #HOGCV.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
        #self.bounding_box_cordinates, weights =  HOGCV.detectMultiScale(frame, winStride = (4, 4), padding = (8, 8), scale = 1.03)
        self.notSDPerson = 0
        if len(self.bounding_box_cordinates) < 2:
            notSDPerson = 0
        else:
            #checks where the boxes intersect and distance between
            for i in range(0, len(self.bounding_box_cordinates) - 1):
                x1,y1,w1,h1 = self.bounding_box_cordinates[i]
                for j in range(1, len(self.bounding_box_cordinates)):
                    x2,y2,w2,h2 = self.bounding_box_cordinates[j]
                    if (((x1 <= x2 <= x1 + w1) or (x1 <= x2 + w2 <= x1 + w1)) and 
                        ((y1 <= y2 <= y1 + h1) or (y1 <= y2 + h2 <= y1 + h1))):
                        self.notSDPerson += 1
                        continue
                    if self.distance(x1 + w1/2, y1 + h1/2, x2 +w2/2, y2 + h2/2) < 203.73:
                        self.notSDPerson += 1
                        #print(x1,y1,w1,h1, x2,y2,w2,h2)
        if self.notSDPerson > 0:
            self.notSDPerson -= 1 

    def distance(self, mX, mY, mX2, mY2):
        return ((mX2 - mX)**2 + (mY2 - mY)**2)**0.5
    
    def pixelToFeetConverter(self, image):
        xWidth = image.shape[1]
        yDepth = image.shape[0]
        #NYT = 42 ft by 30 ft
        """
        x/1200px = 6/42ft
        554 px = 6 / 30
        171.42 px = 6ft in the x direction - NYC
        110.1 px = 6ft in the y direction - NYC

        203.73 = (110.1 ^2 + 171.42^2)^1/2
        """



    def detect(self, frame):
        HOGCV = cv2.HOGDescriptor()
        HOGCV.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
        self.bounding_box_cordinates, weights =  HOGCV.detectMultiScale(frame, winStride = (4, 4), padding = (8, 8), scale = 1.03)
        
        self.person = 1
        for x,y,w,h in self.bounding_box_cordinates:
            cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 2)
            cv2.putText(frame, f'person {self.person}', (x,y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1)
            self.person += 1
        
        #cv2.putText(frame, 'Status : Detecting ', (40,40), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255,0,0), 2)
        #cv2.putText(frame, f'Total Persons : {self.person-1}', (40,70), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255,255,255), 2)
        #cv2.imshow('output', frame)
        return frame

    def detectHumans(self, srcImg, outputImgPath):
        image = cv2.imread(srcImg)
        image = self.imageResize(image)
        result_image = self.detect(image)
        if (cv2.haveImageWriter(outputImgPath) == False):
            raise Exception("Failed to write the downloaded image")
        else:
            cv2.imwrite(outputImgPath, result_image)
            width = image.shape[1]
            height = image.shape[0]
            #print(f'width: {width} height: {height}')
            return {"width": width, "height": height}

    def detectFaces(self, srcImg, outputImgPath):
        faceCascade = cv2.CascadeClassifier("Resources/haarcascade_frontalface_default.xml")

        image = cv2.imread(srcImg)
        image = self.imageResize(image)
        imgGray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        faces = faceCascade.detectMultiScale(imgGray, 1.1, 4)
        
        for (x, y, w, h) in faces:
            cv2.rectangle(image, (x,y), (x+w, y+h), (0,255,0), 2)

        if (cv2.haveImageWriter(outputImgPath) == False):
            raise Exception("Failed to write the downloaded image")
        else:
            width = image.shape[1]
            height = image.shape[0]
            cv2.imwrite(outputImgPath, image)
            return {"width": width, "height": height}

    def imageResize(self, image):
        height = image.shape[0]
        scale_decimal = 300 / height
        nWidth = int(image.shape[1] * scale_decimal)
        if (nWidth > 500): #screen width is set to 1000 and image cannot go more than 60%
            nWidth = 500
        nHeight = int(image.shape[0] * scale_decimal)
        dsize = (nWidth, nHeight)
        return cv2.resize(image, dsize)



#imageHelper = ImageHelper()
#imageHelper.detectByPathImage("./Resources/street.jpg", "./Resources/out.jpg")
