import dash
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input, State
from datetime import date
import re
import json
from sampleData import AttributeData
import os



if not os.path.exists("images"):
    os.mkdir("images")

# pd print settings
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

# reads in the json
data = pd.read_json("finalBusinessData.json")

noGood = ['Dunkin\' Donuts', 'Dunkin\' Donuts & Baskin-Robbins', 'Taco Bella\'s', 'Taco Bell Cantina',
          'Taco Bell and KFC', 'Burger King Restaurant', 'Chipotle Mexican Grill - Austin', 'Starbucks Reserve',
          'Starbucks Florida Hotel', 'Starbucks - The Independent', 'Starbucks Coffee', 'Starbucks Coffee Company']
for n in noGood:
    data = data[data.name != n]
data = data.replace({'Chipotle Mexican Grill': 'Chipotle', 'QDOBA Mexican Eats': 'QDOBA', 'Popeyes Louisiana Kitchen': 'Popeyes'})


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
formattedStars = formattedStars.replace({'Chipotle Mexican Grill': 'Chipotle', 'QDOBA Mexican Eats': 'QDOBA', 'Popeyes Louisiana Kitchen': 'Popeyes'})

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


userAlexData = pd.read_json("userAlexandra.json")
elite = userAlexData.elite.to_list()
revCo = userAlexData.review_count.to_list()
yelpS = userAlexData.yelping_since.to_list()



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
finalCheckins = finalCheckins.replace({'Chipotle Mexican Grill': 'Chipotle', 'QDOBA Mexican Eats': 'QDOBA', 'Popeyes Louisiana Kitchen': 'Popeyes'})


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
                   'Dunkin\'', 'Mcdonald\'s', 'Panera', 'Popeyes', 'Qdoba',
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


# the main meat of the display, all in this weird html/python hybrid (it's how dash works)
app.layout = html.Div(
    children=[
        # Header of Dashboard
        html.Div(
            children=[
                html.Img(
                    src='https://upload.wikimedia.org/wikipedia/commons/thumb/5/5f/NRO.svg/1200px-NRO.svg.png',
                    sizes="small", className="NRO", style={"clear": "right", "float": "right"}
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
                        n_clicks=0, style={"clear": "right", "float": "right", 'display': 'block'}),
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
            dcc.RadioItems(
                id='numStarsRadio',
                options=[
                    {'label': '1 Star', 'value': '1'},
                    {'label': '2 Stars', 'value': '2'},
                    {'label': '3 Stars', 'value': '3'},
                    {'label': '4 Stars', 'value': '4'},
                    {'label': '5 Stars', 'value': '5'},
                ],
                className="radioOptions",
                value="5", style={'display': 'block'}
            )
        ],
        ),
        # Another chart
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
                    value='Starbucks',
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
        html.Div(children=[
            dcc.Dropdown(
                    id='productDropdown',
                    options=dropDownRestaurants,
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
            #     This is annoying
            ),
            ],
            id="productCard",
            className="dropAndCardProduct"
        ),
        html.Div(children=[
            dcc.Dropdown(
                    id='userDropdown',
                    options=dropDownRestaurants,
                    placeholder="Select a User",
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
     Output("checkin-months", "figure"),
     Output('productUsageDownload-csv', 'data'),
     ],
    [Input("newsDropdown", "value"),
     Input("checklist", "value"),
     Input('fileButton', 'n_clicks'),
     State("checkinToggle", "value"),
     State('radios', 'value'),
     ])
def update_bar_chart(dropdown_value, state_chosen, n_clicks, checkin_value, visibility_state):
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

    if visibility_state == 1 and checkin_value == 1 and fileButton.triggered and fileButton.triggered[0]['prop_id'] == 'fileButton.n_clicks':
        checkinsVsDate.write_image('images/checkinsVsDate.pdf')
        return checkinsVsDate, checkinsVsMonth, checkinsVsDay, downloadFile(visibility_state, 1)

    if visibility_state == 1 and checkin_value == 2 and fileButton.triggered and fileButton.triggered[0]['prop_id'] == 'fileButton.n_clicks':
        checkinsVsMonth.write_image('images/checkinsVsMonth.pdf')
        return checkinsVsDate, checkinsVsMonth, checkinsVsDay, downloadFile(visibility_state, 2)

    if visibility_state == 1 and checkin_value == 3 and fileButton.triggered and fileButton.triggered[0]['prop_id'] == 'fileButton.n_clicks':
        checkinsVsDay.write_image('images/checkinsVsDay.pdf')
        return checkinsVsDate, checkinsVsMonth, checkinsVsDay, downloadFile(visibility_state, 3)

    # return all the charts/maps
    return checkinsVsDate, checkinsVsMonth, checkinsVsDay, dash.no_update


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


# Hide download button on map page
@app.callback(Output("fileButton", "style"), [Input("radios", "value")])
def display_value(value):
    if value!=2:
        return {'display': 'block'}
    else:
        return {'display': 'none'}


# Hide card on summary stats page
@app.callback(Output("card", "style"), [Input("radios", "value")])
def display_value(value):
    if value != 5 and value != 6:
        return {'display': 'block'}
    else:
        return {'display': 'none'}


@app.callback(
    Output('bar-chart', 'figure'),
    Output('nameVsReviewDownload-csv', 'data'),
    [Input("checklist", "value"),
     Input('fileButton', 'n_clicks'),
     State('radios', 'value')])
def makeNameVsReviewCount(state_chosen, n_clicks, visibility_state):
    fileButton = dash.callback_context
    dff = data[data["state"].isin(state_chosen)]
    nameVsReviewCount = px.bar(dff, x="review_count", y="name", orientation='h', color="state",
                               title="Products vs. Review Count",
                               labels={
                                   "review_count": "Review Count",
                                   "name": "Product Name",
                                   "state": "State"
                               }
                               )
    if visibility_state == 4 and fileButton.triggered and fileButton.triggered[0]['prop_id'] == 'fileButton.n_clicks':
        nameVsReviewCount.write_image('images/nameVsReviewCount.pdf')
        return nameVsReviewCount, downloadFile(visibility_state, -1)
    return nameVsReviewCount, dash.no_update


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
    return ma

for n in noGood:
    formattedStars = formattedStars[formattedStars.name != n]


@app.callback(
    Output('second-chart', 'figure'),
    Output('nameVsStarsDownload-csv', 'data'),
    [Input("checklist", "value"),
     Input('fileButton', 'n_clicks'),
     State('radios', 'value')])
def makeNameVsStarsChart(state_chosen, n_clicks, visibility_state):
    fileButton = dash.callback_context
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
    if visibility_state == 3 and fileButton.triggered and fileButton.triggered[0]['prop_id'] == 'fileButton.n_clicks':
        nameVsStars.write_image('images/nameVsStars.pdf')
        return nameVsStars, downloadFile(visibility_state, -1)
    return nameVsStars, dash.no_update


# Radio buttons for changing stars in attribute graph
@app.callback(
    Output('third-chart', 'figure'),
    Output('attributeCountDownload-csv', 'data'),
    [Input('numStarsRadio', 'value'),
     Input('checklist', 'value'),
     Input('fileButton', 'n_clicks'),
     State('radios', 'value')])
def update_attribute_chart(star_chosen, state_chosen, n_clicks, visibility_state):
    fileButton = dash.callback_context
    a = AttributeData()
    a.updateStates(state_chosen)
    num_stars = 5
    if star_chosen == '1':
        num_stars = 1
    elif star_chosen == '2':
        num_stars = 2
    elif star_chosen == '3':
        num_stars = 3
    elif star_chosen == '4':
        num_stars = 4
    a.updateStar(num_stars)
    labels, attributesTrue, attributesFalse = a.createAttributeGraphs(False)
    attributeCount = go.Figure(data=[
        go.Bar(name='True', x=labels, y=attributesTrue, marker_color='darkblue'),
        go.Bar(name='False', x=labels, y=attributesFalse, marker_color='lightblue'),
    ])
    attributeCount.update_layout(barmode='group', title='Attributes of ' + str(a.getStar()) + ' Star Products',
                                 yaxis_title="Number of Attributes",
                                 xaxis_title="Attributes")
    if visibility_state == 5 and fileButton.triggered and fileButton.triggered[0]['prop_id'] == 'fileButton.n_clicks':
        attributeCount.write_image('images/AttributeGraph.pdf')
        return attributeCount, downloadFile(visibility_state, -1)
    return attributeCount, dash.no_update


# download report into csv file
def downloadFile(visibility_state, checkin_state):
    if visibility_state == 5:
        return dcc.send_file('images/AttributeGraph.pdf')
    elif visibility_state == 4:
        return dcc.send_file('images/nameVsReviewCount.pdf')
    elif visibility_state == 3:
        return dcc.send_file('images/nameVsStars.pdf')
    else:
        if checkin_state == 1:
            return dcc.send_file('images/checkinsVsDate.pdf')
        elif checkin_state == 2:
            return dcc.send_file('images/checkinsVsMonth.pdf')
        else:
            # df = pd.DataFrame({"a": [1, 2, 3, 4], "b": [2, 1, 5, 6], "c": ["x", "x", "y", "y"]})
            return dcc.send_file('images/checkinsVsDay.pdf')


# Call back to format and update the news API return
@app.callback([Output("card-text", "children"),
               Output("card-title", "children"),
               Output("img", "src"),
               ],
              [Input("newsDropdown", "value"),
               Input('dateRange', 'start_date'),
               Input("dateRange", "end_date")])
def update_card_text(dropdown_value, start_date, end_date):
    article_list = newsDF[newsDF['restaurant'].str.contains(dropdown_value)]['title'].to_list()
    date_list = newsDF[newsDF['restaurant'].str.contains(dropdown_value)]['date'].to_list()
    source_list = newsDF[newsDF['restaurant'].str.contains(dropdown_value)]['source'].to_list()
    url_list = newsDF[newsDF['restaurant'].str.contains(dropdown_value)]['url'].to_list()
    imgList = newsDF[newsDF['restaurant'].str.contains(dropdown_value)]['imageUrl'].to_list()
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
    return each_article, dropdown_value, correct_img


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
    to_return = ""
    if total_columns[overall[1][0]]:
        to_return = total_columns[overall[1][0]][4:]
    return to_return

# @app.callback(Output("newsDropdown", "value"),
#               [Input("checklist", "value"),
#                Input("checkin-months", "restyleData"),
#                ])
# def update_dropdown(state_chosen, months):
#     total_columns = []
#     for option in state_chosen:
#         for col in frequencies.columns:
#             if option in col:
#                 total_columns.append(col)
#     toReturn = ""
#     if total_columns[months[1][0]]:
#         toReturn = total_columns[months[1][0]][4:]
#     return toReturn
#
# @app.callback(Output("newsDropdown", "value"),
#               [Input("checklist", "value"),
#                Input("checkin-days", "restyleData"),
#                ])
# def update_dropdown(state_chosen, days):
#     total_columns = []
#     for option in state_chosen:
#         for col in frequencies.columns:
#             if option in col:
#                 total_columns.append(col)
#     toReturn = ""
#     if total_columns[days[1][0]]:
#         toReturn = total_columns[days[1][0]][4:]
#     return toReturn


# run the app at port 8080
if __name__ == "__main__":
    application.run(debug=True, port=8080)
