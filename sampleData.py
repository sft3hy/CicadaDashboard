import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
import json
import math
#import dash
#import dash_core_components as dcc
#import dash_html_components as html
##import plotly.express as px
#import plotly.graph_objects as go
#from dash.dependencies import Output, Input
#import application

class AttributeData:

    def __init__(self):
        self.star = 5
        self.data = pd.read_json('finalBusinessData.json')
        self.states = [state for state in np.sort(self.data.state.unique())]

    def updateStar(self, starNum):
        self.star = starNum

    def updateStates(self, listOfStates):
        self.states = listOfStates

    def getStar(self):
        return self.star

    # imports JSON file and returns the data in a data frame
    # def readInJSONFile(self, path):
    #     data = pd.read_json(path)
    #     return data


    # gets random colors for plots 
    def getColors(self, N):
        df = pd.Series(np.random.randint(10,50,N), index=np.arange(1,N+1))
        cmap = plt.cm.tab10
        return cmap(np.arange(len(df))%cmap.N)


    # plots the average ratings for each business based on their average number
    # of stars, shows the plot if show=TRUE, and saves the graph as a png
    def plotAverageRatings(self, data, show):
        #plt.figure(figsize=(4,6))
        colors = self.getColors(13)
        plt.barh(data['name'], data['stars'], color=colors)
        plt.ylabel('Business Name')
        plt.xlabel('Average Ratings (stars)')
        plt.tight_layout()
        plt.savefig('graphAverageRatings.png')
        # if show:
        #     plt.show()


    # plots the number of reviews for each business that their average number
    # of stars is calculated from (I think), shows the plot if show=TRUE, 
    # and saves the graph as a png
    def plotNumberOfReviews(self, data, show):
        #plt.figure(figsize=(4,6))
        colors = self.getColors(13)
        plt.barh(data['name'], data['review_count'], color=colors)
        plt.ylabel('Business Name')
        plt.xlabel('Number of Reviews')
        plt.tight_layout()
        plt.savefig('graphNumberOfReviews.png')
        # if show:
        #     plt.show()


    # createes a writer and opens up the excel sheet
    def openExcelSheetWriter(self, nameOfExcelFile):
        writer = pd.ExcelWriter(nameOfExcelFile, engine = 'xlsxwriter')
        return writer

    # puts the data into the excelt sheet at the start row
    # integer that is passed in then sets up worksheet
    def putDataFrameIntoExcelSheet(self, data, writer, startRow):
        data.to_excel(writer, sheet_name='Sheet1', startrow=startRow) 
        worksheet = writer.sheets['Sheet1']
        return worksheet


    # adds text to the worksheet in the specifed place that is
    # passed in through linePos (string)
    def addText(self, worksheet, linePos, text):
        worksheet.write(linePos, text) 

    # inserts picture passed in through pictureName (string- png) to the worksheet 
    # in the specifed place that is passed in through linePos (string)
    def insertPicture(self, worksheet, linePos, pictureName):
        worksheet.insert_image(linePos,pictureName) # linePos = 'AB1', pictureName = 'graphAverageRatings.png'
        # linePos = 'AL1', pictureName = 'graphNumberOfReviews.png'


    # runs through the dictionary and prints out
    # the key and value at that key
    def runThroughDictionary(self, dictionary):
        for key in dictionary:
            print(key + ': ' + str(dictionary[key]))


    # rounds a number up every time if its tenths place
    # is 5 or greater
    def round_up(self, n, decimals=0):
        multiplier = 10 ** decimals
        return math.ceil(n * multiplier) / multiplier


    # either inserts the key passed in into the dictionary and
    # states whether or not the value is true or false for that variable
    # or updates the value of the preexisting key that matches the
    # one passed in to include another true or false in the format [false, true]
    def insertInDictionary(self, key, true, dictionary):
        if key in dictionary:
            if true == 1:
                dictionary[key][1] += 1
            else:
                dictionary[key][0] += 1
        else:
            if true == 1:
                dictionary[key] = [0, 1]
            else:
                dictionary[key] = [1, 0]


    # checks to see if the key is relevant to know even
    # if there are no true responses for the element and sets
    # the value of the passed in key to [-1, -1] so it can later
    # be removed if that is the case
    # i.e. if everyone says false to dogs allowed, then that
    # variable will not be visualized in the plot
    def checkIfRelevant(self, key, dictionary):
        irrelevant = ['BusinessParking: valet', 'BusinessParking: street', 'BusinessParking: validated',
        'BusinessParking: lot', 'BusinessParking: garage', 'HasTV', 'ByAppointmentOnly',
        'RestaurantGoodForGroups', 'HappyHour', 'DogsAllowed', 'BestNights: monday', 'BestNights: tuesday',
        'BestNights: friday', 'BestNights: wednesday', 'BestNights: thursday', 'BestNights: sunday',
        'BestNights: saturday', 'Music: background_music', 'Music: no_music', 'Music: jukebox', 
        'Music: live', 'Music: video', 'Music: karaoke', 'BusinessAcceptsBitcoin', 'Caters', 
        'GoodForMeal: dessert', 'GoodForMeal: latenight', 'GoodForMeal: lunch', 'GoodForMeal: dinner',
        'GoodForMeal: brunch', 'GoodForMeal: breakfast', 'Ambience: romantic', 'Ambience: intimate', 
        'Ambience: classy', 'Ambience: hipster', 'Ambience: divey', 'Ambience: touristy', 'Ambience: trendy', 
        'Ambience: upscale', 'Ambience: casual', 'RestaurantsDelivery', 'GoodForMeal', 'BYOBCorkage', 'Ambience', 'BYOB', 
        'BusinessParking', 'Corkage']

        if key in irrelevant:
            if dictionary[key][1] == 0:
                dictionary[key] = [-1, -1]


    # determines whether or not the value of the key is positive
    # or negative and then calls on insertDictionary to 
    # insert the key into the dictionary with that information
    def posOrNeg(self, key, value, dictionary):
        #alcohol = ['full_bar', 'u\'beer_and_wine', 'beer_and_wine', 'u\'none', 'none']
        #noiseLevel = ['u\'average', 'average', 'u\'quiet', 'u\'very_loud', 'loud', 'u\'loud', 'very_loud']
        #priceRange = ['1', '2', '3', '4']
        #wifi = ['u\'free', 'u\'no', 'free', 'paid']
        #attire = ['u\'casual', 'casual', 'u\'dressy', 'u\'formal', 'dressy']
        #delivery = ['None']
        #BYOBCorkage = ['no', 'yes_free']
        #BusinessParking = ['None']
        #Ambience = ['None']
        #GoodForMeal = ['None']

        if key == 'Alcohol':
            if value == 'full_bar':
                self.insertInDictionary('Alcohol: Full Bar', 1, dictionary)
            elif value == 'u\'beer_and_wine' or  value == 'beer_and_wine':
                self.insertInDictionary('Alcohol: Beer and Wine', 1, dictionary)
            else:
                self.insertInDictionary('Alcohol', 0, dictionary)
        elif key == 'RestaurantsPriceRange2':
            temp = 'Price Range ' + str(value) 
            self.insertInDictionary(temp, 1, dictionary)
        elif key == 'NoiseLevel':
            if value == 'u\'quiet':
                self.insertInDictionary('NoiseLevel: Quiet', 1, dictionary)
            elif value == 'u\'average' or value == 'average':
                self.insertInDictionary('NoiseLevel: Average', 1, dictionary)
            else:
                self.insertInDictionary('NoiseLevel: Loud', 1, dictionary)
        elif key == 'WiFi':
            if value == 'u\'no':
                self.insertInDictionary('WiFi', 0, dictionary)
            elif value == 'paid':
                self.insertInDictionary('WiFi: Not Free', 1, dictionary)
            else:
                self.insertInDictionary('Free WiFi', 1, dictionary)
        elif key == 'RestaurantsAttire':
            if value == 'u\'dressy' or value == 'dressy':
                self.insertInDictionary('Dressy', 1, dictionary)
            elif value == 'u\'formal':
                self.insertInDictionary('Formal', 1, dictionary)
            else:
                self.insertInDictionary('Casual', 1, dictionary)
        else:
            if value == 'True' or value == 'yes_free':
                self.insertInDictionary(key, 1, dictionary)
            else:
                self.insertInDictionary(key, 0, dictionary)


    # for attributes that have a string dictionary as a value
    # this function turns those strings into an acutal
    # dictionary and inserts them into the main dictionary
    # realNotPractice and inputKey are used when simply running through
    # the attributes for runThroughAttributeKeysOrValues but do not affect the actual dictionary
    # line is the value of the original key here
    def makeDict(self, originalKey, line, dictionary, realNotPractice = True, keysNotValues = True):
        line = line.replace("'", '"')
        line = line.replace('True', '"True"')
        line = line.replace('False', '"False"')
        line = line.replace('None', '"None"')
        convertedDict = json.loads(str(line))
        for key in convertedDict:
            if realNotPractice:
                self.posOrNeg(originalKey + ': ' + key, convertedDict[key], dictionary)
            else:
                if keysNotValues:
                    inputKey = originalKey + ': ' + key
                else:
                    inputKey = originalKey + ': ' + key + ': ' + convertedDict[key]
                if inputKey in dictionary:
                    dictionary[inputKey] += 1
                else:
                    dictionary[inputKey] = 1


    # iterates through the attributes of the data from the JSON file
    # and adds them to the dictionary
    def getAttributes(self, data, lineNum, dictionary):
        if data.iloc[lineNum]['attributes'] is not None:
            line = data.iloc[lineNum]['attributes']
            for key in line:
                if key == 'HairSpecializesIn':
                    continue
                elif '{' in line[key]:
                    self.makeDict(key, line[key], dictionary)
                else:
                    self.posOrNeg(key, line[key], dictionary)


    # runs through either all the attribute keys or attribute values
    # and prints them out to show how many of each label there are
    def runThroughAttributeKeysOrValues(self, data, keysNotValues):
        tempDictionary = {}
        for i in data.index:
            if data.iloc[i]['attributes'] is not None:
                line = data.iloc[i]['attributes']
                for key in line:
                    if keysNotValues:
                        inputKey = key
                    else:
                        inputKey = key + ': ' + line[key]
                    if '{' in line[key]:
                        self.makeDict(key, line[key], tempDictionary, False, keysNotValues)
                    else:
                        if inputKey in tempDictionary:
                            tempDictionary[inputKey] += 1
                        else:
                            tempDictionary[inputKey] = 1
        
        self.runThroughDictionary(tempDictionary)


    # takes info for graphs from createAttributeGraohs and 
    # plots that info, showing the graphs only if show=TRUE
    def plotAttributeGraphs(self, data, stars, labels, attributesTrue, attributesFalse, show):
        y = np.arange(len(labels))  # the label locations
        width = 0.45  # the width of the bars
        fig, ax = plt.subplots()
        ax.barh(y - width/2, attributesTrue, width, label='True', align='edge')
        ax.barh(y + width/2, attributesFalse, width, label='False', align='edge')

        # adds labeling information to graph
        ax.set_xlabel('Number of ' + str(stars) + ' Star Attributes')
        ax.set_ylabel('Attributes')
        ax.set_title('Attributes for ' + str(stars) + ' Star Reviews')
        ax.set_yticks(y)
        ax.set_yticklabels(labels)
        ax.legend()
        fig.tight_layout()

        plt.savefig('graph' + str(stars) + 'StarAttributes.png')

        # if show:
        #     plt.show()


    # creates graphs of the attributes for each star rating
    def createAttributeGraphs(self, show):
        labels = []
        attributesTrue = []
        attributesFalse = []
        dictionary = {}

        # fills the dictionary with all the attributes found in 
        # reviews with the star rating passed in or those that round up
        # or down to the star rating passed in
        for i in self.data.index:
            if self.round_up(self.data.iloc[i]['stars']) == self.star and self.data.iloc[i]['state'] in self.states:
                self.getAttributes(self.data, i, dictionary)
        
        # gets rid of irrelevant data and fills arrays needed to plot data
        for key in dictionary:
            self.checkIfRelevant(key, dictionary)
            if dictionary[key][0] != -1:
                labels.append(key)
                attributesFalse.append(dictionary[key][0])
                attributesTrue.append(dictionary[key][1])

        return labels, attributesTrue, attributesFalse
        #self.plotAttributeGraphs(data, stars, labels, attributesTrue, attributesFalse, show)
        #runThroughDictionary(dictionary)


    # plot all the attribute graphs for each star rating and add them
    # to the excel spreadsheet
    def plotAllAttributeGraphs(self, data, worksheet, startLetter, startRow, graphsPerLine):
        excelCell = startRow 
        excelLetter = startLetter
        counter = 1 
        if graphsPerLine > 1:
            nextLine = False
        else:
            nextLine = True

        for i in range(1,6):    
            self.createAttributeGraphs(data, i, False)
            self.insertPicture(worksheet, 'A' + excelLetter + str(excelCell), 'graph' + str(i) + 'StarAttributes.png')
            if nextLine:
                excelCell += 25
                counter = 1
                excelLetter = startLetter
                nextLine = False
            else:
                counter += 1
                excelLetter = chr(ord('B') + 10)
                if counter == graphsPerLine:
                    nextLine = True


    # saves the changes to the excel sheet when done editing it
    def saveExcelSheet(self, writer):
        writer.save()


#if __name__ == "__main__":

    #a = AttributeData()

    # reads in the JSON file
    #data = a.readInJSONFile("finalBusinessData.json")

    # plots the average ratings and number of reviews graphs
    #a.plotAverageRatings(data, False)
    #a.plotNumberOfReviews(data, False)

    # opens up an excel file and puts the data from the JSON file
    # into the excel sheet starting at row 2 then adds a heading
    # and pictures of the graphs created above
    #writer = a.openExcelSheetWriter('python_plot.xlsx')
    #worksheet = a.putDataFrameIntoExcelSheet(data, writer, 2)
    #a.addText(worksheet, 'A1', 'Data Analysis of Bigger Sample Data')
    #a.insertPicture(worksheet, 'AB1', 'graphAverageRatings.png')
    #a.insertPicture(worksheet, 'AL1', 'graphNumberOfReviews.png')

    # plots all the attribute graphs for each star rating and puts them in the excel file
    #a.plotAllAttributeGraphs(data, worksheet, 'B', 25, 2)

    # saves the changes to the excel sheet when done
    #a.saveExcelSheet(writer)

    # run through attributes and responses to those attributes to understand
    # data being worked with
    #runThroughAttributeKeysOrValues(data, False)