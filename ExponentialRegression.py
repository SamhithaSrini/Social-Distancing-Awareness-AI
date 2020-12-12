import math
import numpy as np
# adpated from https://gist.github.com/shuklapratik/983898a11b3b26c95bd910d084c31db2
import requests
import json

# This is how I developed my exponential regression values

cdcUrl = "https://api.covidtracking.com/v1/states/" + "ca" + "/daily.json"
response = requests.get(cdcUrl)
stateFullReportJson = json.loads(response.text)

filteredStateReport = []
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

    filteredStateReport.append(currDayReport)
filteredStateReport.reverse()
numOfDays = len(filteredStateReport)

# adpated from https://gist.github.com/shuklapratik/983898a11b3b26c95bd910d084c31db2
X = np.arange(0,numOfDays//2)
Y = []
for i in range(0, numOfDays//2):
    Y.append(filteredStateReport[numOfDays - 1]["positive"]) 


n = len(X)
x_bias = np.ones((n,1))

#print("Shape of x_bias : ",x_bias.shape)
#print("Shape of X : ",X.shape)

X = np.reshape(X,(n,1))
#print("Shape of X : ",X.shape)

yLog = np.log(Y)
x_new = np.append(x_bias,X,axis=1)
x_new_transpose = np.transpose(x_new)
x_new_transpose_dot_x_new = x_new_transpose.dot(x_new)
temp_1 = np.linalg.inv(x_new_transpose_dot_x_new)
temp_2 = x_new_transpose.dot(yLog)
theta = temp_1.dot(temp_2)
#print("Coefficients : ",theta)
#print(f'y = {theta[0]}     *     {theta[1]}   ^x')

X = np.arange(numOfDays//2, numOfDays)
Y = []
for i in range(numOfDays//2, numOfDays):
    Y.append(filteredStateReport[numOfDays - 1]["positive"]) 


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
#print(f'y = {theta[0]}     *     {theta[1]}   ^x')
