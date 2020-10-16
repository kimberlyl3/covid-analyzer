'''
Python code to analyze the relationship between government policy "strictness" and the spread of 
COVID-19 by U.S. state using data on state imposed policies and R-Value data.
'''

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# A class used to represent a State object with data on region, date, and mean R-value

class State:
    def __init__(self, rData, name):
        self.data = rData.loc[rData['region'] == name]
        date = self.data['date']
        avgR = self.data['mean']
        index = self.data['index']
        stateData = {'index' : index, 'date': date, 'mean': avgR}
        self.data = pd.DataFrame(stateData,columns = ['index', 'date', 'mean'])
        self.startDate = self.data.loc[self.data['date'] == "6/4/2020"]['index'].values[0]
        self.endDate = self.data.loc[self.data['date'] == "7/21/2020"]['index'].values[0]
        dropData = self.data[(self.data['index'] < self.startDate)].index
        self.data.drop(dropData, inplace = True)
            
        self.name = name

    def getData(self):
        return self.data
    
    def getName(self):
        return self.name

    def getStart(self):
        return self.startDate

    def getEnd(self):
        return self.endDate
    
    def getDataAtDate(self, date):
        return self.data.loc[self.data['date'] == date]

# A class used to represent a Policy object with data on policies by state

class Policy:
    def __init__(self, state):
        self.pData = pd.DataFrame(columns = ['Stay at Home Order', 'Non-Essential Business Closures',
            'Large Gatherings Ban', 'School Closures', 'Face Covering Requirement'])
        self.state = state

    def getData(self):
        return self.pData

    def getName(self):
        return self.state

    def append(self, newRow):
        self.pData = self.pData.append(newRow, ignore_index=True)

# A class used to represent a Strictness object with data on strictess index by state

class Strictness:
    def __init__(self, state):
        self.sData = pd.DataFrame(columns = ['Strictness Index'])
        self.state = state
    
    def getData(self):
        return self.sData

    def getName(self):
        return self.state

    def append(self, newRow):
        self.sData = self.sData.append(newRow, ignore_index=True)

# Read csv file on R-Value
rData = pd.read_csv('C:/Users/kimmy/OneDrive/Documents/Covid Project/Data/rt.csv')

states = rData.loc[rData['index'] == 0]['region'].values

dataList = []
policyList = []
policyStrictness = []
# Range from 0-51 to create objects for each state including Washington DC
for i in range(0,51):
    state = State(rData, states[i])
    dataList.append(state)
    policy = Policy(states[i])
    policyList.append(policy)
    strictness = Strictness(state)
    policyStrictness.append(strictness)


j = 0
dates = []
# Open directory with policy data files
directory = r'C:/Users/kimmy/OneDrive/Documents/Covid Project/Data/COVID-19-Data-kff_master/State Policy Actions/State Social Distancing Actions/'
for filename in os.listdir(directory):
    if filename.endswith(".csv"):
        filedata = pd.read_csv(directory + filename)

        if filename.endswith("_Social_Distancing.csv"):
            year = filename[:4]
            if filename[5:7].startswith("0"):
                month = filename[6:7]
            else:
                month = filename[5:7]
            if filename[8:10].startswith("0"):
                day = filename[9:10]
            else:
                day = filename[8:10]
            date = month+"/"+day+"/"+year
            dates.append(date)

        filedata.columns.values[0] = 'State'

        startRow = filedata.loc[filedata['State'] == 'Alabama'].index.values[0]
        endRow = filedata.loc[filedata['State'] == 'Wyoming'].index.values[0]

        noneList = []
        for i in range(0, endRow):
            noneList.append(' ')

        # Create datalists of each policy
        stayhome = filedata['Stay at Home Order']
        business = filedata['Non-Essential Business Closures']
        gathering = filedata['Large Gatherings Ban']
        if 'School Closures' in filedata.columns:
            school = filedata['School Closures']
        else:
            school = pd.Series((v[0] for v in noneList))
        if 'Face Covering Requirement' in filedata.columns:
            faceCover = filedata['Face Covering Requirement']
        else:
            faceCover = pd.Series((v[0] for v in noneList))

        for i in range(startRow,endRow):
            if j < 51:
                data = {'Stay at Home Order': stayhome[i], 'Non-Essential Business Closures': business[i], 'Large Gatherings Ban': gathering[i], 'School Closures': school[i], 'Face Covering Requirement': faceCover[i]}
                policyList[j].append(data)

            else:
                continue
        j += 1
        continue
    else:
        continue

# Baseline strictness index per policy based on R-value reduction percentages

stayAtHome = 18
symptomaticTesting = 10
gathering100 = 5
gathering10 = 24
someBusinesses = 34
schoolsClosed = 33
faceCovering = 9

print(endRow)

# Calculating strictness index and graphing scattergrams for each state

for i in range(0, 4): # Range from 0-51 depending on how many state graphs you want to appear (states are in aphabetical order: 0 = AK, 51 = WY)
    '''
    uncomment this section to plot R-Value Histograms for each state

    plt.figure(i)
    plt.title(dataList[i].getName()+' R-Value Histogram')
    dataList[i].getData()['mean'].hist(bins = 20)
    '''
    matchData = pd.DataFrame(columns = ['index', 'date', 'mean'])

    # Create list containing strictness indexes for each datapoint (date) by adding up separate policy values
    for x in range(0,len(dates)):
        dateRow = dataList[i].getDataAtDate(dates[x])
        matchData = matchData.append(dateRow)
        strictnessIndex = symptomaticTesting
        if stayhome[x] == "Statewide":
            strictnessIndex += stayAtHome
        if business[x] == "Some Non-Essential Businesses Permitted to Reopen" or business[x] == "New Business Closures or Limits":
            strictnessIndex += someBusinesses
        if gathering[x] == "Expanded to New Limit Above 25":
            strictnessIndex += gathering100
        elif gathering[x] == ">10 People Prohibited" or gathering[x] == "Expanded to New Limit Below 25":
            strictnessIndex += gathering10
        if school[x] == "Closed for School Year" or school[x] == "Recommended Closure for School Year" or school[x] == "Closed":
            strictnessIndex += schoolsClosed
        if faceCover[x] == "Required for General Public":
            strictnessIndex += faceCovering

        policyStrictness[i].append({'Strictness Index': strictnessIndex})

    # Plotting the scattergrams with strictness on the x-axix and R-Value on the y-axis
    plt.figure(i)
    si = policyStrictness[i].getData()['Strictness Index']
    mr = matchData['mean']
    plt.scatter(si, mr)
    plt.title(dataList[i].getName()+' Scattergram')
    plt.xlabel("Strictness Index")
    plt.ylabel("Mean R-Value")

plt.show()