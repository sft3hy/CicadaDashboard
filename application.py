import dash
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input, State
import requests
from datetime import date
from plotly.subplots import make_subplots
import re
import json
from sampleData import AttributeData
import os
import pickle

# instagram dataframes
instaNames = ["starbucks", "burgerking", "chickfila", "chipotle", "dunkin", "mcdonalds",
              "panera", "popeyes", "qdoba", "tacobell", "wendys"]
newsNames = ["Starbucks", "Burger King", "Chick-fil-A", "Chipotle", "Dunkin'", "McDonald's", "Panera",
             "Popeyes", "Qdoba", "Taco Bell", "Wendy's"]
socialMediaDFs = []

for n in instaNames:
    tempDF = pd.read_json("socialMediaJson/" + n + ".json")
    socialMediaDFs.append(tempDF)

# save social media images to files
# i = 0
# for l in socialMediaDFs:
#     j = 1
#     for ur in l.url:
#         response = requests.get(ur)
#         file = open("images/"+newsNames[i]+str(j)+".png", "wb")
#         file.write(response.content)
#         file.close()
#         j+=1
#     i+=1

if not os.path.exists("static/images"):
    os.mkdir("static/images")

# pd print settings
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

# reads in the json
data = pd.read_json("finalBusinessData.json")

noGood = ['Dunkin\' Donuts', 'Dunkin\' Donuts & Baskin-Robbins', 'Taco Bella\'s', 'Wendy\'s '
          'Taco Bell Cantina', 'Starbucks ', 'Taco Bell and KFC', 'Burger King Restaurant',
          'Chipotle Mexican Grill - Austin', 'Starbucks Reserve', 'Starbucks Florida Hotel',
          'Starbucks - The Independent', 'Starbucks Coffee', 'Starbucks Coffee Company',
          'Kentucky Fried Chicken', "Dunkin'  Donuts", "Wendy's "]

replacements = {'Chipotle Mexican Grill': 'Chipotle', 'QDOBA Mexican Eats': 'QDOBA', 'Popeyes Louisiana Kitchen': 'Popeyes', 'Panera Bread': 'Panera'}

for n in noGood:
    data = data[data.name != n]
data = data.replace(replacements)

# # get smaller table to work with average stars
# with open("finalBusinessData.json", encoding="UTF-8") as f:
#     sData = json.load(f)
#
# for business in sData:
#     del business['business_id']
#     del business['address']
#     del business['city']
#     del business['review_count']
#     del business['is_open']
#     del business['attributes']
#     del business['postal_code']
#     del business['latitude']
#     del business['longitude']
#     del business['categories']
#     del business['hours']
#
# with open("starsData.json", 'w', encoding="UTF-8") as f:
#     json.dump(sData, f)
#
# # get smaller table to work with map
# with open("finalBusinessData.json", encoding="UTF-8") as f:
#     mData = json.load(f)
#
# for business in mData:
#     del business['address']
#     del business['city']
#     del business['is_open']
#     del business['attributes']
#     del business['postal_code']
#
# with open("mapData.json", 'w', encoding="UTF-8") as f:
#     json.dump(mData, f)
#
# # get smaller table to work with checkins
# with open("finalCheckin.json", encoding="UTF-8") as f:
#     cData = json.load(f)
#
# for business in cData:
#     del business['address']
#     del business['city']
#     del business['postal_code']
#
# with open("checkin.json", 'w', encoding="UTF-8") as f:
#     json.dump(cData, f)

# with open("UsersToTrack.json", encoding="UTF-8") as f:
#     uData = json.load(f)
#
# for user in uData:
#     del user['address']
#     del user['city']
#     del user['postal_code']
#
# with open("usersToTrack.json", 'w', encoding="UTF-8") as f:
#     json.dump(uData, f)


# formatting stuff
# how to run an app with dash/plotly
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP,
               {"href": "https://fonts.googleapis.com/css2?"
                "family=Lato:wght@400;700&display=swap",
                "rel": "stylesheet",
                "href": 'https://codepen.io/chriddyp/pen/bWLwgP.css',
                "rel": "buttons",}],
                assets_folder="static",
                assets_url_path="static")
# ^specify static folder to make CSS work both locally hosted and on AWS

application = app.server

server = app.server

# this is the thing that shows up in the tab
app.title = "CICADA - Understand Your Users"

# initialize map to display lat/long data
map = go.Figure(data=go.Scattergeo(
    lon=data['longitude'],
    lat=data['latitude'],
    text=data['name'],
    mode='markers',
    marker_color=data['stars']
))

# limit the map to only the USA
map.update_layout(
    geo_scope='usa'
)

# alex = pd.read_json("userAlexandra.json")
# dan = pd.read_json("userDaniel.json")
# vince = pd.read_json("userVincent.json")

# userMap = go.Figure(data=go.Scattergeo(
#     lon=alex['longitude'],
#     lat=alex['latitude'],
#     text=alex['name_user'],
#     mode='markers',
#     marker_color=alex['date']
# ))
#
# # limit the map to only the USA
# userMap.update_layout(
#     geo_scope='usa'
# )

# format to get a nice table of states, names, and stars, grouped by  state
stars = pd.read_json("starsData.json")
s = stars.groupby(['state', 'name']).agg({'stars': ['mean']}).reset_index()

starsList = s.stars["mean"].to_list()
statesList = s.state.to_list()
namesList = s.name.to_list()

formattedStars = pd.DataFrame(
    list(zip(starsList, statesList, namesList)), columns=['stars', 'state', 'name'])
formattedStars = formattedStars.replace(replacements)

# format map points to show stars and business name
mapData = pd.read_json("mapData.json")
nams = mapData.name.to_list()
tars = mapData.stars.to_list()
la = mapData.latitude.to_list()
lo = mapData.longitude.to_list()
sta = mapData.state.to_list()
id = mapData.business_id.to_list()
coun = mapData.review_count.to_list()

i = 0
namsNStarsList = []
for n in nams:
    namsNStarsList.append(n + ": " + str(tars[i]) + " Star Average")
    i += 1

mapDF = pd.DataFrame(list(zip(namsNStarsList, la, lo, sta, tars, nams, id, coun)),
                     columns=['nameNStars', 'latitude', 'longitude', 'state', 'stars', 'name', 'business_id',
                              'review_count'])


# format a table to match check ins to business name using business_id
checkins = pd.read_json("checkin.json")
goodIDs = mapDF.business_id.to_list()

for n in noGood:
    checkins = checkins[checkins.name != n]

goodCheckins = checkins[checkins.business_id.isin(goodIDs)]
nameAndCheckin = mapDF.merge(goodCheckins, on="business_id")

finalCheckins = nameAndCheckin[['name_x', 'date', 'state_x']]
finalCheckins = finalCheckins[finalCheckins["date"] != "None"]
finalCheckins = finalCheckins.dropna()
finalCheckins = finalCheckins.groupby(['state_x', 'name_x'])['date'].apply(', '.join).reset_index()
finalCheckins = finalCheckins.replace(replacements)


datesList = finalCheckins.date.to_list()

overallDates = []
lastThreeWeeks = []
lastThreeMonths = []
startOfLastMonths = "2020-11-01"
startOfLastWeeks = "2021-01-05"
endDate = "2021-01-29"
for l in datesList:
    tempList = l.replace(' ', '').split(',')
    allTimeList = []
    dayList = []
    lastThreeMonthList = []
    for date in tempList:
        date = date[0:10]
        if date > startOfLastWeeks < endDate:
            dayList.append(date)
        if date > startOfLastMonths < endDate:
            lastThreeMonthList.append(date)
        date = date[0:7]
        allTimeList.append(date)
    overallDates.append(allTimeList)
    lastThreeWeeks.append(dayList)
    lastThreeMonths.append(lastThreeMonthList)

frequencyList = []
for line in overallDates:
    dictionary = {}
    for date in line:
        if date in dictionary:
            dictionary[date] += 1
        else:
            dictionary[date] = 1
    frequencyList.append(dictionary)

frequencies = pd.DataFrame(frequencyList)
frequencies = frequencies.transpose()

na = finalCheckins.name_x.to_list()
stat = finalCheckins.state_x.to_list()

j = 0
nameState = []
for n in na:
    nameState.append(str(stat[j]) + ": " + n)
    j += 1

mapper = {}
for k in range(len(na)):
    mapper[k] = nameState[k]

frequencies = frequencies.rename(columns=mapper)
frequencies = frequencies.sort_index()

#
dayFrequencyList = []
for line in lastThreeWeeks:
    dictionary = {}
    for date in line:
        if date in dictionary:
            dictionary[date] += 1
        else:
            dictionary[date] = 1
    dayFrequencyList.append(dictionary)

dayFrequencies = pd.DataFrame(dayFrequencyList)
dayFrequencies = dayFrequencies.transpose()

dayFrequencies = dayFrequencies.rename(columns=mapper)
dayFrequencies = dayFrequencies.sort_index()

dayFrequencies = dayFrequencies.fillna(0)
#

#
monthFrequencyList = []
for line in lastThreeMonths:
    dictionary = {}
    for date in line:
        if date in dictionary:
            dictionary[date] += 1
        else:
            dictionary[date] = 1
    monthFrequencyList.append(dictionary)

monthFrequencies = pd.DataFrame(monthFrequencyList)
monthFrequencies = monthFrequencies.transpose()

monthFrequencies = monthFrequencies.rename(columns=mapper)
monthFrequencies = monthFrequencies.sort_index()

monthFrequencies = monthFrequencies.fillna(0)
#
restaurantsList = ['Starbucks', 'Burger King', 'Chick-fil-A', 'Chipotle',
                   'Dunkin\'', 'Mcdonald\'s', 'Panera', 'Popeyes', 'QDOBA',
                   'Taco bell', 'Wendy\'s']

allNews = pd.read_json("currentNews.json")
for i in range(len(allNews['publishedAt'])):
    allNews['publishedAt'][i] = allNews['publishedAt'][i][0:10]

sourceList = []
titleList = []
descriptionList = []
urlList = []
dateList = []
rList = []
imageUrls = []
for r in restaurantsList:
    for i in range(len(allNews['title'])):
        if r in allNews['title'][i]:
            rList.append(r)
            sourceList.append(allNews['source'][i]["name"])
            titleList.append(allNews['title'][i])
            descriptionList.append(allNews['description'][i])
            urlList.append(allNews['url'][i])
            dateList.append(allNews['publishedAt'][i])
            imageUrls.append(allNews['urlToImage'][i])

newsDF = pd.DataFrame(list(zip(sourceList, titleList, descriptionList, urlList, dateList, rList, imageUrls)),
                      columns=['source', 'title', 'description', 'url', 'date', 'restaurant',
                               'imageUrl']).drop_duplicates(
    subset='title')
dropDownRestaurants = []
for r in newsDF.restaurant.unique():
    # dropDownRestaurants.append(dbc.DropdownMenuItem(r, id=r))
    dropDownRestaurants.append({"label": r, 'value': r})
correct_img = ""

with open("selectedTrackingData.json", encoding="UTF-8") as f:
    tracking = json.load(f)

totalProductList = []
nameList = []
for line in tracking:
    if line['name_business'] not in totalProductList:
        totalProductList.append(line['name_business'])
    if {"label": line['name_user'], "value": line['name_user']} not in nameList:
        nameList.append({"label": line['name_user'], "value": line['name_user']})


productDF = pd.read_json("selectedTrackingData.json")
danielDF = pd.read_json("userDaniel.json")

noGood = ['Dunkin\' Donuts', 'Dunkin\' Donuts & Baskin-Robbins', 'Taco Bella\'s', 'Wendy\'s '
          'Taco Bell Cantina', 'Starbucks ', 'Taco Bell and KFC', 'Burger King Restaurant',
          'Chipotle Mexican Grill - Austin', 'Starbucks Reserve', 'Starbucks Florida Hotel',
          'Starbucks - The Independent', 'Starbucks Coffee', 'Starbucks Coffee Company',
          'Kentucky Fried Chicken', "Dunkin'  Donuts", "Wendy's "]

productDF = productDF.replace(replacements)

businessDropdown = [{"label": "All", "value": "All"}]
for b in data.name.unique():
    # dropDownRestaurants.append(dbc.DropdownMenuItem(r, id=r))
    businessDropdown.append({"label": b, 'value': b})



# the main meat of the display, all in this weird html/python hybrid (it's how dash works)
app.layout = html.Div(
    children=[
        # Header of Dashboard
        html.Div(
            children=[
                html.Img(
                    src='https://upload.wikimedia.org/wikipedia/commons/thumb/5/5f/NRO.svg/1200px-NRO.svg.png',
                    sizes="small", className="NRO", style={"clear": "right", ""
                                                                             "oat": "right"}
                ),
                html.Img(src="static/logo.png", className='logo'
                         , style={"clear": "left", "float": "left"}),
                html.P(children="CICADA", className="header-title"),
                html.H6(
                    children="Continuous Intelligence Compilation and Data Analytics",
                    className="header-description",
                ),
            ],
            className="header-title",
        ),
        # Radio buttons to choose state
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(children="Select a region and the specific metrics you want to view:",
                                 className="menu-title"),
                        dcc.Checklist(
                            id="checklist",
                            options=[
                                {"label": state, "value": state}
                                for state in np.sort(data.state.unique())
                            ],
                            value=["FL"],
                            className="body",
                        ),
                    ],
                    style={'textalign': 'center'}
                ),
            ],
            className="menu",
        ),
        # Radio Buttons to choose what analytics to view
        html.Div(
            [
                dbc.RadioItems(
                    id="radios",
                    className="toggle-buttons",
                    labelClassName="btn btn-outline-secondary",
                    style={"clear": "left", "float": "left"},
                    labelCheckedClassName="active",
                    options=[
                        {"label": "Product Usage Over Time", "value": 1},
                        {"label": "Map", "value": 2},
                        {"label": "Products vs. User Ratings", "value": 3},
                        {"label": "Products vs. Review Count", "value": 4},
                        {"label": "Summary Statistics", "value": 5},
                        {"label": "User Tracking", "value": 6},
                    ],
                    value=2,
                ),
                html.Div(id="output"),
            ],
            className="radio-group",
        ),
        # Downloads
        html.Div([
             # Create element to hide/show, in this case an 'Input Component'
             dbc.Button('Download Current Chart', id='fileButton', className='fileButton',
                        n_clicks=0, style={"clear": "left", "float": "left", 'display': 'block'}),
             html.Span(id='outputReport'),
             dcc.Download(id='nameVsStarsDownload-csv'),
             dcc.Download(id='nameVsReviewDownload-csv'),
             dcc.Download(id='attributeCountDownload-csv'),
             dcc.Download(id='productUsageDownload-csv'),
         ],
        ),
        # Toggle checkin view buttons
        html.Div(children=dcc.RadioItems(
            id='checkinToggle',
            options=[
                {'label': 'All Time', 'value': 1},
                {'label': 'Three Months', 'value': 2},
                {'label': 'Three Weeks', 'value': 3},
            ],
            className="radioOptions",
            value=1, style={'display': 'block'}
        )),
        # Checkin all time graph
        html.Div(children=dcc.Graph(
            id="checkin-dates", config={"displayModeBar": False},
        ),
            className="wrapper", style={'display': 'block'}
        ),
        # Checkin Week graph
        html.Div(children=dcc.Graph(
            id="checkin-days", config={"displayModeBar": False},
        ),
            className="wrapper", style={'display': 'block'}
        ),
        # Checkin Month Graph
        html.Div(children=dcc.Graph(
            id="checkin-months", config={"displayModeBar": False},
        ),
            className="wrapper", style={'display': 'block'}
        ),
        # Some bar chart
        html.Div(children=dcc.Graph(
            id="bar-chart", config={"displayModeBar": False},
        ),
            className="wrapper", style={'display': 'block'}
        ),
        # Map
        html.Div(children=[html.Div(
            children=dcc.Graph(
                id='ma',
                figure=map,
            ),
            className="wrapper", style={'display': 'block'}
        ), ],
        ),
        # ANother random chart
        html.Div(
            children=dcc.Graph(
                id="second-chart", config={"displayModeBar": False},
            ),
            className="wrapper", style={'display': 'block'}
        ),
        # Summary Stats choices
        html.Div([
            # Create element to hide/show, in this case an 'Input Component'
            dbc.RadioItems(
                id='numStarsRadio',
                className="btn-group-toggle",
                labelClassName="btn btn-outline-secondary",
                labelCheckedClassName="active",
                options=[
                    {"label": "Attribute Comparison By Stars", "value": 1},
                    {"label": "Attribute Comparison By Product", "value": 2},
                ],
                value=1, style={'display': 'block'}
            ),
            html.Div(id="output2"),
        ],
            className="summaryStatsGroup",
        ),

        html.Div([
            dcc.Dropdown(
                    id='starsDropdown',
                    options=[
                        {"label": "1 Star", "value": 1},
                        {"label": "2 Star", "value": 2},
                        {"label": "3 Star", "value": 3},
                        {"label": "4 Star", "value": 4},
                        {"label": "5 Star", "value": 5},
                    ],
                    value=5,
                    searchable=False,
                    className="sDropdown",
                ),
        ], ),
        html.Div([
            dcc.Dropdown(
                    id='restaurantDropdown1',
                    options=dropDownRestaurants,
                    value='Starbucks',
                    className="starsDropdown1",
                ),
        ], ),
        html.Div([
            dcc.Dropdown(
                    id='restaurantDropdown2',
                    options=dropDownRestaurants,
                    value='Chick-fil-A',
                    className="starsDropdown2",
                ),
        ], ),
        html.Div(
            children=dcc.Graph(
                id="third-chart", config={"displayModeBar": False},
            ),
            className="wrapper", style={'display': 'block'}
        ),
        # UserMap
        html.Div(children=[html.Div(
            children=dcc.Graph(
                id='userMap',
                figure=map,
            ),
            className="wrapper", style={'display': 'block'}
        ), ],
        ),
        # News API and dropdowns
        html.Div(children=[
            dcc.Dropdown(
                    id='newsDropdown',
                    options=dropDownRestaurants,
                    value="Starbucks",
                    className="restaurantDropdown",
                ),
            dcc.DatePickerRange(
                id="dateRange",
                clearable=True,
                with_portal=True,
                start_date="2021-06-01",
                end_date="2021-06-30",
                display_format="YYYY-MM-DD",
            ),
            dbc.Card(
                [dbc.CardImg(id="img", top=True, className="cardImg"),
                 dbc.CardBody(
                     [
                         html.H4(className="card-title", id="card-title"),
                         html.P(
                             className="card-text",
                             id="card-text",
                         ),
                     ]
                 ),
                 ],
                style={"width": "20rem"},
                className="card-place"
            ),
            ], id="card",
            className="dropAndCard"
        ),
        html.Div(dbc.CardGroup([
            dbc.Card(dbc.CardBody([dbc.CardImg(id="post-1-img", top=True, className="cardImg"),
                                   html.H5(className="card-title"),
                        html.P(id="post-1-text",className="card-text",),
                                   ]),style={"width": "14rem"},
            ),
            dbc.Card(dbc.CardBody([dbc.CardImg(id="post-2-img", top=True, className="cardImg"),
                                   html.H5(className="card-title"),
                        html.P(id="post-2-text",className="card-text",),
                        ]),style={"width": "14rem"},
            ),
            dbc.Card(dbc.CardBody([dbc.CardImg(id="post-3-img", top=True, className="cardImg"),
                                   html.H5(className="card-title"),
                        html.P(id="post-3-text",className="card-text",),
                        ]),style={"width": "14rem"},
            ),
            ]),

        id="socialMediaCards",
        className="socialMediaCards"
        ),
        html.Div(html.H6(
            id="IGFeed",
            children="Instagram Feed",
            className="IGFeed",
        )),
        html.Div(children=[
            dcc.Dropdown(
                    id='productDropdown',
                    options=businessDropdown,
                    value='All',
                    placeholder="Select a Product",
                    className="restaurantDropdown",
                ),
            dbc.Card([
                 dbc.CardBody(
                     [
                         html.H4(className="card-title", id="product-title"),
                         html.P(
                             className="card-text",
                             id="product-text",
                         ),
                     ]
                 ), ],
                style={"width": "16rem"},
                className="card-place"
            ),
            ],
            id="productCard",
            className="dropAndCardProduct"
        ),
        html.Div(children=[
            dcc.Dropdown(
                    id='userDropdown',
                    options=nameList,
                    placeholder="Select a User",
                    value="Vincent",
                    className="restaurantDropdown",
                ),
            dbc.Card([
                 dbc.CardBody(
                     [
                         html.H4(className="card-title", id="user-title"),
                         html.P(
                             className="card-text",
                             id="user-text",
                         ),
                     ]
                 ), ],
                style={"width": "16rem"},
                className="card-place"
            ),
            ],
            id="userCard",
            className="dropAndCardUser"
        ),
    ],
    className="background"
)


# make the web-app responsive (so when you click something, it responds)
@app.callback(
    [Output("checkin-dates", "figure"),
     Output("checkin-days", "figure"),
     Output("checkin-months", "figure"),],
    [Input("newsDropdown", "value"),
     Input("checklist", "value")])
def update_bar_chart(dropdown_value, state_chosen):
    # make dataframes that the buttons can update according to user requests
    fileButton = dash.callback_context

    total_columns = []
    for option in state_chosen:
        for col in frequencies.columns:
            if option in col:
                total_columns.append(col)
    check = frequencies[[state for state in total_columns]]
    dayCheck = dayFrequencies[[state for state in total_columns]]
    monthCheck = monthFrequencies[[state for state in total_columns]]
    # plotly bar charts

    productToKeep = []
    for name in total_columns:
        if dropdown_value in name:
            productToKeep.append(name)

    checkinsVsDate = px.line(check, x=check.index, title="Product Usage All Time - Click restaurants on the right to view",
                             y=total_columns,
                             labels={"index": "Date", "variable": "State and Name", "value": "Total Checkins"})
    checkinsVsDate.update_layout(yaxis_title="Number of Checkins")

    checkinsVsDate.for_each_trace(lambda trace: trace.update(visible="legendonly")
                                  if trace.name not in productToKeep else ())

    checkinsVsDay = px.line(dayCheck, x=dayCheck.index, title="Product Usage Last Three Weeks - Click restaurants on the right to view",
                            y=total_columns,
                            labels={"index": "Date", "variable": "State and Name", "value": "Total Checkins"})
    checkinsVsDay.update_layout(yaxis_title="Number of Checkins")

    checkinsVsDay.for_each_trace(lambda trace: trace.update(visible="legendonly")
                                  if trace.name not in productToKeep else ())

    checkinsVsMonth = px.line(monthCheck, x=monthCheck.index, title="Product Usage Last Three Months - Click restaurants on the right to view",
                              y=total_columns,
                              labels={"index": "Date", "variable": "State and Name", "value": "Total Checkins"})
    checkinsVsMonth.update_layout(yaxis_title="Number of Checkins")

    checkinsVsMonth.for_each_trace(lambda trace: trace.update(visible="legendonly")
                                  if trace.name not in productToKeep else ())

    with open('checkinsVsDate.pkl', 'wb') as output:
        pickle.dump(checkinsVsDate, output, pickle.HIGHEST_PROTOCOL)

    with open('checkinsVsMonth.pkl', 'wb') as output:
        pickle.dump(checkinsVsMonth, output, pickle.HIGHEST_PROTOCOL)

    with open('checkinsVsDay.pkl', 'wb') as output:
        pickle.dump(checkinsVsDay, output, pickle.HIGHEST_PROTOCOL)

    # return all the charts/maps
    return checkinsVsDate, checkinsVsMonth, checkinsVsDay


# Hide map if anything but the proper radio button is selected
@app.callback(Output("ma", "style"), [Input("radios", "value")])
def display_value(value):
    if value == 2:
        return {'display': 'block'}
    else:
        return {'display': 'none'}


# Hide chart if anything but the proper radio button is selected
@app.callback(Output("second-chart", "style"), [Input("radios", "value")])
def display_value(value):
    if value == 3:
        return {'display': 'block'}
    else:
        return {'display': 'none'}


# Hide chart if anything but the proper radio button is selected
@app.callback(Output("bar-chart", "style"), [Input("radios", "value")])
def display_value(value):
    if value == 4:
        return {'display': 'block'}
    else:
        return {'display': 'none'}


# Hide chart if anything but the proper radio button is selected
@app.callback(Output("third-chart", "style"), [Input("radios", "value")])
def display_value(value):
    if value == 5:
        return {'display': 'block'}
    else:
        return {'display': 'none'}


# Hide summary Stats selection if anything but the proper radio button is selected
@app.callback(Output("numStarsRadio", "style"), [Input("radios", "value")])
def display_value(value):
    if value == 5:
        return {'display': 'block'}
    else:
        return {'display': 'none'}


# Hide or show checkin charts if chosen
@app.callback(Output("checkinToggle", "style"), [Input("radios", "value")])
def display_value(value):
    if value == 1:
        return {'display': 'block'}
    else:
        return {'display': 'none'}


# Displays User Tracking Map
@app.callback(Output("userMap", "style"), [Input("radios", "value")])
def display_value(value):
    if value == 6:
        return {'display': 'block'}
    else:
        return {'display': 'none'}


# Displays User Tracking Map
@app.callback(Output("productCard", "style"), [Input("radios", "value")])
def display_value(value):
    if value == 6:
        return {'display': 'block'}
    else:
        return {'display': 'none'}


@app.callback(
    Output("userCard", "style"),
    [Input("radios", "value"), Input("productDropdown", "value"),
     ])
def display_value(value, contents):
    if value == 6 and contents:
        return {'display': 'block'}
    else:
        return {'display': 'none'}


# Displays User Tracking Map
@app.callback(Output("checklist", "style"), [Input("radios", "value")])
def display_value(value):
    if value != 6:
        return {'display': 'block'}
    else:
        return {'display': 'none'}


# Hide checkin chart if different time frame is chosen
@app.callback(Output("checkin-dates", "style"), [Input("checkinToggle", "value"), Input("radios", "value")])
def display_value(checkinValue, radiosValue):
    if checkinValue == 1 and radiosValue == 1:
        return {'display': 'block'}
    else:
        return {'display': 'none'}


# Hide checkin chart if different time frame is chosen
@app.callback(Output("checkin-months", "style"), [Input("checkinToggle", "value"), Input("radios", "value")])
def display_value(checkinValue, radiosValue):
    if checkinValue == 3 and radiosValue == 1:
        return {'display': 'block'}
    else:
        return {'display': 'none'}


# Hide checkin chart if different time frame is chosen
@app.callback(Output("checkin-days", "style"), [Input("checkinToggle", "value"), Input("radios", "value")])
def display_value(checkinValue, radiosValue):
    if checkinValue == 2 and radiosValue == 1:
        return {'display': 'block'}
    else:
        return {'display': 'none'}

# @app.callback(Output("fileButton", "style"), [Input("radios", "value")])
# def display_value(value):
#     if value!=2:
#         return {'display': 'block'}
#     else:
#         return {'display': 'none'}

@app.callback(Output("starsDropdown", "style"), [Input("radios", "value"), Input("numStarsRadio", "value")])
def display_value(value, stars_or_no):
    if value==5 and stars_or_no == 1:
        return {}
    else:
        return {'display': 'none'}

@app.callback(Output("restaurantDropdown1", "style"), Output("restaurantDropdown2", "style"), [Input("radios", "value"), Input("numStarsRadio", "value")])
def display_value(value, stars_or_no):
    if value==5 and stars_or_no == 2:
        return {}, {}
    else:
        return {'display': 'none'}, {'display': 'none'}

@app.callback(Output("card", "style"), [Input("radios", "value")])
def display_value(value):
    if value!=2 and value != 5 and value != 6:
        return {'display': 'block'}
    else:
        return {'display': 'none'}

@app.callback(Output("IGFeed", "style"), [Input("radios", "value")])
def display_value(value):
    if value==1:
        return {'display': 'block'}
    else:
        return {'display': 'none'}


@app.callback(
    Output('bar-chart', 'figure'),
    [Input("checklist", "value")])
def makeNameVsReviewCount(state_chosen):
    dff = data[data["state"].isin(state_chosen)]
    nameVsReviewCount = px.bar(dff, x="review_count", y="name", orientation='h', color="state",
                               title="Products vs. Review Count",
                               labels={
                                   "review_count": "Review Count",
                                   "name": "Product Name",
                                   "state": "State"
                               }
                               )
    with open('nameVsReviewCount.pkl', 'wb') as output:
        pickle.dump(nameVsReviewCount, output, pickle.HIGHEST_PROTOCOL)
    return nameVsReviewCount


# Populates User Map
@app.callback(
    Output('userMap', 'figure'),
    [Input("userDropdown", "value"),
     Input("productDropdown", "value")])
def makeUserMap(user_Chosen, productChosen):
    if productChosen == "All":
        productData = productDF[productDF["name_user"] == user_Chosen]
    else:
        productData = productDF[productDF["name_user"] == user_Chosen]
        productData = productData[productData["name_business"] == productChosen]
    userMapFill = px.scatter_mapbox(productData, lat="latitude", lon="longitude", hover_name="name_business",
                           hover_data=["stars_user", "review_count"],
                           color="stars_business", zoom=4, height=500, title="Individual Products", labels={
            "stars_user": "Stars", "review_count": "Review Count", "latitude": "Latitude",
            "longitude": "Longitude"
        })
    userMapFill.update_layout(mapbox_style="open-street-map")
    userMapFill.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    with open('userMapFill.pkl', 'wb') as output:
        pickle.dump(userMapFill, output, pickle.HIGHEST_PROTOCOL)
    return userMapFill


@app.callback(
    Output('ma', 'figure'),
    [Input("checklist", "value")])
def makeMap(state_chosen):
    m = mapDF[mapDF["state"].isin(state_chosen)]
    ma = px.scatter_mapbox(m, lat="latitude", lon="longitude", hover_name="name",
                           hover_data=["state", "stars", "review_count"],
                           color="stars", zoom=4, height=500, title="Individual Products", labels={
            "stars": "Average Stars", "state": "State", "review_count": "Review Count", "latitude": "Latitude",
            "longitude": "Longitude"
        })
    ma.update_layout(mapbox_style="open-street-map")
    ma.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    with open('ma.pkl', 'wb') as output:
        pickle.dump(ma, output, pickle.HIGHEST_PROTOCOL)
    return ma

for n in noGood:
    formattedStars = formattedStars[formattedStars.name != n]


@app.callback(
    Output('second-chart', 'figure'),
    [Input("checklist", "value")])
def makeNameVsStarsChart(state_chosen):
    st = formattedStars[formattedStars["state"].isin(state_chosen)]
    nameVsStars = px.bar(st, x="stars", y="name", orientation='h',
                         color="state", barmode='group',
                         title="Products vs. User Ratings",
                         labels={
                             "stars": "Average Stars",
                             "name": "Product Name",
                             "state": "State"
                         }
                         )
    with open('nameVsStars.pkl', 'wb') as output:
        pickle.dump(nameVsStars, output, pickle.HIGHEST_PROTOCOL)
    return nameVsStars



# Radio buttons for changing stars in attribute graph
@app.callback(
    Output('third-chart', 'figure'),
    [Input('starsDropdown', 'value'),
     Input('checklist', 'value'),
     Input('numStarsRadio', 'value'),
     Input('restaurantDropdown1', 'value'),
     Input('restaurantDropdown2', 'value'),
     State('radios', 'value')])
def update_attribute_chart(star_chosen, state_chosen, version_shown, restaurant1, restaurant2, visibility_state):
    a = AttributeData()
    a.updateStates(state_chosen)
    if version_shown == 1:
        a.updateStar(star_chosen)
        labels, attributesTrue, attributesFalse = a.createAttributeGraphs(False)
        attributeCount = go.Figure(data=[
            go.Bar(name='True', x=labels, y=attributesTrue, marker_color='darkblue'),
            go.Bar(name='False', x=labels, y=attributesFalse, marker_color='lightblue'),
        ])
        attributeCount.update_layout(height=600, barmode='group', title='Attributes of ' + str(star_chosen) + ' Star Products',
                                     yaxis_title="Number of Attributes",
                                     xaxis_title="Attributes")
        with open('attributeCount.pkl', 'wb') as output:
            pickle.dump(attributeCount, output, pickle.HIGHEST_PROTOCOL)
        return attributeCount
    else:
        a.updateRestaurant(restaurant1)
        labels, attributesTrue, attributesFalse = a.createAttributeGraphs(True)
        attributeCount = make_subplots(rows=2, cols=1, vertical_spacing=.3)

        attributeCount.add_trace(
                go.Bar(name='True', x=labels, y=attributesTrue, marker_color='darkblue'),
            row=1, col=1
        )
        attributeCount.add_trace(
            go.Bar(name='False', x=labels, y=attributesFalse, marker_color='lightblue'),
            row=1, col=1
        )

        a.updateRestaurant(restaurant2)
        labels, attributesTrue, attributesFalse = a.createAttributeGraphs(True)

        attributeCount.add_trace(
            go.Bar(showlegend=False, x=labels, y=attributesTrue, marker_color='darkblue'),
            row=2, col=1
        )

        attributeCount.add_trace(
            go.Bar(showlegend=False, x=labels, y=attributesFalse, marker_color='lightblue'),
            row=2, col=1
        )

        attributeCount.update_layout(showlegend=True, height=1000, width=800, title_text=str(restaurant1) + " vs " + str(restaurant2))
        with open('attributeCount.pkl', 'wb') as output:
            pickle.dump(attributeCount, output, pickle.HIGHEST_PROTOCOL)
    return attributeCount



# download report into csv file
@app.callback(
    Output('attributeCountDownload-csv', 'data'),
    [Input('fileButton', 'n_clicks'),
     State('radios', 'value'),
     State("checkinToggle", "value")],
    prevent_initial_call=True)
def downloadFile(n_clicks, visibility_state, checkin_state):
    if visibility_state == 5:
        with open('attributeCount.pkl', 'rb') as input:
            attributeCount = pickle.load(input)
            attributeCount.write_image('static/images/SummaryStatistics.pdf')
        return dcc.send_file('static/images/SummaryStatistics.pdf')
    elif visibility_state == 4:
        with open('nameVsReviewCount.pkl', 'rb') as input:
            nameVsReviewCount = pickle.load(input)
            nameVsReviewCount.write_image('static/images/ProductsVsReviewCount.pdf')
        return dcc.send_file('static/images/ProductsVsReviewCount.pdf')
    elif visibility_state == 3:
        with open('nameVsStars.pkl', 'rb') as input:
            nameVsStars = pickle.load(input)
            nameVsStars.write_image('static/images/ProductsVsUserRatings.pdf')
        return dcc.send_file('static/images/ProductsVsUserRatings.pdf')
    elif visibility_state == 2:
        with open('ma.pkl', 'rb') as input:
            map = pickle.load(input)
            map.write_image('static/images/Map.pdf')
        return dcc.send_file('static/images/Map.pdf')
    else:
        if checkin_state == 1:
            with open('checkinsVsDate.pkl', 'rb') as input:
                checkinsVsDate = pickle.load(input)
                checkinsVsDate.write_image('static/images/ProductUsageAllTime.pdf')
            return dcc.send_file('static/images/ProductUsageAllTime.pdf')
        elif checkin_state == 2:
            with open('checkinsVsMonth.pkl', 'rb') as input:
                checkinsVsMonth = pickle.load(input)
                checkinsVsMonth.write_image('static/images/ProductUsageLastThreeMonths.pdf')
            return dcc.send_file('static/images/ProductUsageLastThreeMonths.pdf')
        else:
            with open('checkinsVsDay.pkl', 'rb') as input:
                checkinsVsDay = pickle.load(input)
                checkinsVsDay.write_image('static/images/ProductUsageLastThreeWeeks.pdf')
            # df = pd.DataFrame({"a": [1, 2, 3, 4], "b": [2, 1, 5, 6], "c": ["x", "x", "y", "y"]})
            return dcc.send_file('static/images/ProductUsageLastThreeWeeks.pdf')

@app.callback([Output("post-1-text", "children"),
               Output("post-2-text", "children"),
               Output("post-3-text", "children"),
               Output("card-text", "children"),
               Output("card-title", "children"),
               Output("img", "src"),
               Output("post-1-img", "src"),
               Output("post-2-img", "src"),
               Output("post-3-img", "src"),
               ],
              [Input("newsDropdown", "value"),
               Input('dateRange', 'start_date'),
               Input("dateRange", "end_date"),
               ])
def update_card_text(dropdown_value, start_date, end_date):
    article_list = newsDF[newsDF['restaurant'].str.contains(dropdown_value)]['title'].to_list()
    date_list = newsDF[newsDF['restaurant'].str.contains(dropdown_value)]['date'].to_list()
    source_list = newsDF[newsDF['restaurant'].str.contains(dropdown_value)]['source'].to_list()
    url_list = newsDF[newsDF['restaurant'].str.contains(dropdown_value)]['url'].to_list()
    imgList = newsDF[newsDF['restaurant'].str.contains(dropdown_value)]['imageUrl'].to_list()

    post1url = "static/images/" + dropdown_value + "1" + ".png"
    post2url = "static/images/" + dropdown_value + "2" + ".png"
    post3url = "static/images/" + dropdown_value + "3" + ".png"

    caption1 = socialMediaDFs[newsNames.index(dropdown_value)].caption.to_list()[0]
    if(len(caption1) > 350):
        caption1 = caption1[0:350] + "..."
    caption1 +=" Date: "+ str(socialMediaDFs[newsNames.index(dropdown_value)].date.to_list()[0])

    caption2 = socialMediaDFs[newsNames.index(dropdown_value)].caption.to_list()[1]
    if (len(caption2) > 350):
        caption2 = caption2[0:350] + "..."
    caption2 += " Date: " + str(socialMediaDFs[newsNames.index(dropdown_value)].date.to_list()[1])

    caption3 = socialMediaDFs[newsNames.index(dropdown_value)].caption.to_list()[2]
    if (len(caption3) > 350):
        caption3 = caption3[0:350] + "..."
    caption3 += " Date: " + str(socialMediaDFs[newsNames.index(dropdown_value)].date.to_list()[2])


    try:
        correct_img = imgList[1]
    except IndexError:
        imgList = newsDF[newsDF['restaurant'].str.contains(dropdown_value)]['imageUrl'].to_list()
        correct_img = imgList[0]
    all_titles = ""
    each_article = []
    for i in range(len(article_list)):
        if start_date <= date_list[i] <= end_date:
            each_article.append(dbc.ListGroupItem(article_list[i] + ": " + "Date: " + date_list[i] + ", Source: " + source_list[i] +  ".", href=url_list[i], target="_blank"))
    return caption1, caption2, caption3, each_article, dropdown_value, correct_img, post1url, post2url, post3url



# make the dropdown propagate with the trace selected on the graph
@app.callback(Output("newsDropdown", "value"),
              [Input("checklist", "value"),
               Input("checkin-dates", "restyleData"),
               ])
def update_dropdown(state_chosen, overall):

    total_columns = []
    for option in state_chosen:
        for col in frequencies.columns:
            if option in col:
                total_columns.append(col)
    toReturn = "Starbucks"
    try:
        toReturn = total_columns[overall[1][0]][4:]
    except TypeError:
        print("")
    return toReturn

@app.callback(Output("socialMediaCards", "style"), Input("radios", "value"))
def display_value(radiosValue):
    if radiosValue == 1:
        return {'display': 'block'}
    else:
        return {'display': 'none'}

# run the app at port 8080
if __name__ == "__main__":
    application.run(debug=True, port=8080)