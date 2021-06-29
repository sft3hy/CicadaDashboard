import dash
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input, State
import re
import json
from sampleData import AttributeData
import os
import pickle



if not os.path.exists("images"):
    os.mkdir("images")

attributeCount = ''
# pd print settings
# pd.set_option('display.max_columns', None)
# pd.set_option('display.max_rows', None)

# reads in the json
data = pd.read_json("finalBusinessData.json")

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

# format to get a nice table of states, names, and stars, grouped by  state
stars = pd.read_json("starsData.json")
s = stars.groupby(['state', 'name']).agg({'stars': ['mean']}).reset_index()

starsList = s.stars["mean"].to_list()
statesList = s.state.to_list()
namesList = s.name.to_list()

formattedStars = pd.DataFrame(
    list(zip(starsList, statesList, namesList)), columns=['stars', 'state', 'name'])

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

goodCheckins = checkins[checkins.business_id.isin(goodIDs)]
nameAndCheckin = mapDF.merge(goodCheckins, on="business_id")

finalCheckins = nameAndCheckin[['name_x', 'date', 'state_x']]
finalCheckins = finalCheckins[finalCheckins["date"] != "None"]
finalCheckins = finalCheckins.dropna()
finalCheckins = finalCheckins.groupby(['state_x', 'name_x'])['date'].apply(', '.join).reset_index()

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
                    ],
                    value=2,
                ),
                html.Div(id="output"),
            ],
            className="radio-group",
        ),
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
        # html.Div(
        #     [
        #         dbc.RadioItems(
        #             id="summaryStatsRadio",
        #             className="toggle-buttons",
        #             labelClassName="btn btn-secondary",
        #             labelCheckedClassName="active",
        #
        #             options=[
        #                 {"label": "Attribute Comparison By Stars", "value": 1},
        #                 {"label": "Attribute Comparison By Product", "value": 2},
        #             ],
        #             value=2,
        #         ),
        #         html.Div(id="output2"),
        #     ],
        #     style={'display': 'block'},
        #     className="radio-group",
        # ),
        html.Div(children=dcc.Graph(
            id="checkin-dates", config={"displayModeBar": False},
        ),
            className="wrapper", style={'display': 'block'}
        ),
        html.Div(children=dcc.Graph(
            id="checkin-days", config={"displayModeBar": False},
        ),
            className="wrapper", style={'display': 'block'}
        ),
        html.Div(children=dcc.Graph(
            id="checkin-months", config={"displayModeBar": False},
        ),
            className="wrapper", style={'display': 'block'}
        ),
        html.Div(children=dcc.Graph(
            id="bar-chart", config={"displayModeBar": False},
        ),
            className="wrapper", style={'display': 'block'}
        ),
        html.Div(children=[html.Div(
            children=dcc.Graph(
                id='ma',
                figure=map,
            ),
            className="wrapper", style={'display': 'block'}
        ),
        ],
        ),
        html.Div(
            children=dcc.Graph(
                id="second-chart", config={"displayModeBar": False},
            ),
            className="wrapper", style={'display': 'block'}
        ),
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

        # html.Div(
        #     [
        #         dbc.RadioItems(
        #             id="summaryStatsRadio",
        #             className="toggle-buttons",
        #             labelClassName="btn btn-secondary",
        #             labelCheckedClassName="active",
        #
        #             options=[
        #                 {"label": "Attribute Comparison By Stars", "value": 1},
        #                 {"label": "Attribute Comparison By Product", "value": 2},
        #             ],
        #             value=2,
        #         ),
        #         html.Div(id="output2"),
        #     ],
        #     style={'display': 'block'},
        #     className="radio-group",
        # ),

        html.Div([
            dcc.Dropdown(
                    id='starsDropdown',
                    options=['1 Star', '2'],
                    value='Starbucks',
                    className="starsDropdown",
                ),
        ], ),
        html.Div(
            children=dcc.Graph(
                id="third-chart", config={"displayModeBar": False},
            ),
            className="wrapper", style={'display': 'block'}
        ),
        html.Div([
            dcc.Dropdown(
                    id='newsDropdown',
                    options=dropDownRestaurants,
                    value='Starbucks',
                    className="restaurantDropdown",
                ),
        ], ),
        html.Div(
            children=[dbc.Card(
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
            ),
            ], id='card',
        ),
    ],

    className="background"
)


# make the web-app responsive (so when you click something, it responds)
@app.callback(
    [Output("checkin-dates", "figure"),
     Output("checkin-days", "figure"),
     Output("checkin-months", "figure")],
    [Input("checklist", "value"),
     State("checkinToggle", "value"),
     State('radios', 'value')])
def update_bar_chart(state_chosen, checkin_value, visibility_state):
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

    checkinsVsDate = px.line(check, x=check.index, title="Product Usage All Time",
                             y=total_columns,
                             labels={"index": "Date", "variable": "State and Name", "value": "Total Checkins"})
    checkinsVsDate.update_layout(yaxis_title="Number of Checkins")

    checkinsVsDay = px.line(dayCheck, x=dayCheck.index, title="Product Usage Last Three Weeks",
                            y=total_columns,
                            labels={"index": "Date", "variable": "State and Name", "value": "Total Checkins"})
    checkinsVsDay.update_layout(yaxis_title="Number of Checkins")

    checkinsVsMonth = px.line(monthCheck, x=monthCheck.index, title="Product Usage Last Three Months",
                              y=total_columns,
                              labels={"index": "Date", "variable": "State and Name", "value": "Total Checkins"})
    checkinsVsMonth.update_layout(yaxis_title="Number of Checkins")

    # if visibility_state == 1 and checkin_value == 1 and fileButton.triggered and fileButton.triggered[0]['prop_id'] == 'fileButton.n_clicks':
    #     checkinsVsDate.write_image('images/checkinsVsDate.pdf')
    #     return checkinsVsDate, checkinsVsMonth, checkinsVsDay, downloadFile(visibility_state, 1)
    #
    # if visibility_state == 1 and checkin_value == 2 and fileButton.triggered and fileButton.triggered[0]['prop_id'] == 'fileButton.n_clicks':
    #     checkinsVsMonth.write_image('images/checkinsVsMonth.pdf')
    #     return checkinsVsDate, checkinsVsMonth, checkinsVsDay, downloadFile(visibility_state, 2)
    #
    # if visibility_state == 1 and checkin_value == 3 and fileButton.triggered and fileButton.triggered[0]['prop_id'] == 'fileButton.n_clicks':
    #     checkinsVsDay.write_image('images/checkinsVsDay.pdf')
    #     return checkinsVsDate, checkinsVsMonth, checkinsVsDay, downloadFile(visibility_state, 3)

    # return all the charts/maps
    return checkinsVsDate, checkinsVsMonth, checkinsVsDay


@app.callback(Output("ma", "style"), [Input("radios", "value")])
def display_value(value):
    if value == 2:
        return {'display': 'block'}
    else:
        return {'display': 'none'}


@app.callback(Output("second-chart", "style"), [Input("radios", "value")])
def display_value(value):
    if value == 3:
        return {'display': 'block'}
    else:
        return {'display': 'none'}


@app.callback(Output("bar-chart", "style"), [Input("radios", "value")])
def display_value(value):
    if value == 4:
        return {'display': 'block'}
    else:
        return {'display': 'none'}


@app.callback(Output("third-chart", "style"), [Input("radios", "value")])
def display_value(value):
    if value == 5:
        return {'display': 'block'}
    else:
        return {'display': 'none'}


# @app.callback(Output("numStarsRadio", "style"), [Input("radios", "value")])
# def display_value(value):
#     if value == 5:
#         return {'display': 'block'}
#     else:
#         return {'display': 'none'}


@app.callback(Output("checkinToggle", "style"), [Input("radios", "value")])
def display_value(value):
    if value == 1:
        return {'display': 'block'}
    else:
        return {'display': 'none'}


@app.callback(Output("checkin-dates", "style"), [Input("checkinToggle", "value"), Input("radios", "value")])
def display_value(checkinValue, radiosValue):
    if checkinValue == 1 and radiosValue == 1:
        return {'display': 'block'}
    else:
        return {'display': 'none'}


@app.callback(Output("checkin-months", "style"), [Input("checkinToggle", "value"), Input("radios", "value")])
def display_value(checkinValue, radiosValue):
    if checkinValue == 3 and radiosValue == 1:
        return {'display': 'block'}
    else:
        return {'display': 'none'}


@app.callback(Output("checkin-days", "style"), [Input("checkinToggle", "value"), Input("radios", "value")])
def display_value(checkinValue, radiosValue):
    if checkinValue == 2 and radiosValue == 1:
        return {'display': 'block'}
    else:
        return {'display': 'none'}

@app.callback(Output("fileButton", "style"), [Input("radios", "value")])
def display_value(value):
    if value!=2:
        return {'display': 'block'}
    else:
        return {'display': 'none'}

# @app.callback(Output("starsDropdown", "style"), [Input("radios", "value")])
# def display_value(value):
#     if value==5:
#         return {'display': 'block'}
#     else:
#         return {'display': 'none'}

@app.callback(Output("card", "style"), [Input("radios", "value")])
def display_value(value):
    if value!=5:
        return {'display': 'block'}
    else:
        return {'display': 'none'}


@app.callback(
    Output('bar-chart', 'figure'),
    [Input("checklist", "value"),
     State('radios', 'value')])
def makeNameVsReviewCount(state_chosen, visibility_state):
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
    # if visibility_state == 4 and fileButton.triggered and fileButton.triggered[0]['prop_id'] == 'fileButton.n_clicks':
    #     nameVsReviewCount.write_image('images/nameVsReviewCount.pdf')
    #     return nameVsReviewCount, downloadFile(visibility_state, -1)
    return nameVsReviewCount


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


@app.callback(
    Output('second-chart', 'figure'),
    [Input("checklist", "value"),
     State('radios', 'value')])
def makeNameVsStarsChart(state_chosen, visibility_state):
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
    # if visibility_state == 3 and fileButton.triggered and fileButton.triggered[0]['prop_id'] == 'fileButton.n_clicks':
    #     nameVsStars.write_image('images/nameVsStars.pdf')
    #     return nameVsStars, downloadFile(visibility_state, -1)
    return nameVsStars




# Radio buttons for changing stars in attribute graph
@app.callback(
    Output('third-chart', 'figure'),
    [Input('checklist', 'value'),
     State('radios', 'value')])
def update_attribute_chart(state_chosen, visibility_state):
    fileButton = dash.callback_context

    # if fileButton.triggered and fileButton.triggered[0]['prop_id'] != 'fileButton.n_clicks':
    a = AttributeData()
    a.updateStates(state_chosen)
    a.updateStar(1)
    labels1, attributesTrue1, attributesFalse1 = a.createAttributeGraphs(False)
    a.updateStar(2)
    labels2, attributesTrue2, attributesFalse2 = a.createAttributeGraphs(False)
    a.updateStar(3)
    labels3, attributesTrue3, attributesFalse3 = a.createAttributeGraphs(False)
    a.updateStar(4)
    labels4, attributesTrue4, attributesFalse4 = a.createAttributeGraphs(False)
    a.updateStar(5)
    labels5, attributesTrue5, attributesFalse5 = a.createAttributeGraphs(False)

    attributeCount = go.Figure()
    attributeCount.add_trace(go.Bar(name='True', x=labels1, y=attributesTrue1, marker_color='darkblue', visible=False))
    attributeCount.add_trace(go.Bar(name='False', x=labels1, y=attributesFalse1, marker_color='lightblue', visible=False))
    attributeCount.add_trace(go.Bar(name='True', x=labels2, y=attributesTrue2, marker_color='darkblue', visible=False))
    attributeCount.add_trace(go.Bar(name='False', x=labels2, y=attributesFalse2, marker_color='lightblue', visible=False))
    attributeCount.add_trace(go.Bar(name='True', x=labels3, y=attributesTrue3, marker_color='darkblue', visible=False))
    attributeCount.add_trace(go.Bar(name='False', x=labels3, y=attributesFalse3, marker_color='lightblue', visible=False))
    attributeCount.add_trace(go.Bar(name='True', x=labels4, y=attributesTrue4, marker_color='darkblue', visible=False))
    attributeCount.add_trace(go.Bar(name='False', x=labels4, y=attributesFalse4, marker_color='lightblue', visible=False))
    attributeCount.add_trace(go.Bar(name='True', x=labels5, y=attributesTrue5, marker_color='darkblue', visible=True))
    attributeCount.add_trace(go.Bar(name='False', x=labels5, y=attributesFalse5, marker_color='lightblue', visible=True))
    attributeCount.update_layout(title='Attributes of 5 Star Products')
    attributeCount.update_layout(barmode='group',
                                 yaxis_title="Number of Attributes",
                                 xaxis_title="Attributes",
                                 # execute=saveImagesOfCharts(attributeCount),
                                 clickmode='event',
                                 updatemenus=[dict(
                                        type = "dropdown",
                                        direction = 'down',
                                        active=4,
                                        buttons=list([
                                            dict(
                                                args=[{'visible': [True, True, False, False, False, False,
                                                                   False, False, False, False]},
                                                      {'title':'Attributes of 1 Star Products'}],
                                                label="1 Star",
                                                method="update"
                                            ),
                                            dict(
                                                args=[{'visible': [False, False, True, True, False, False,
                                                                   False, False, False, False]},
                                                      {'title': 'Attributes of 2 Star Products'}],
                                                label="2 Star",
                                                method="update"
                                            ),
                                            dict(
                                                args=[{'visible': [False, False, False, False, True, True,
                                                                   False, False, False, False]},
                                                      {'title': 'Attributes of 3 Star Products'}],
                                                label="3 Star",
                                                method="update"
                                            ),
                                            dict(
                                                args=[{'visible': [False, False, False, False, False, False,
                                                                   True, True, False, False]},
                                                      {'title': 'Attributes of 4 Star Products'}],
                                                label="4 Star",
                                                method="update"
                                            ),
                                            dict(
                                                args=[{'visible': [False, False, False, False, False, False,
                                                                   False, False, True, True]},
                                                      {'title':'Attributes of 5 Star Products'}],
                                                label="5 Star",
                                                method="update"
                                            )
                                        ]),
                                        pad={"r": 0, "t": 0},
                                        showactive=True,
                                        x=0.5,
                                        xanchor="left",
                                        y=1.5,
                                        yanchor="top"
                                    ),])
    print('ayyy')
    f = go.FigureWidget(attributeCount)
    # attributeCount.on('plotly_click', saveImagesOfCharts(attributeCount))
    # attributeCount.on_selection(print('now'))

    # attributeCount.
    # with open('attributeCount.pkl', 'wb') as output:
    #     pickle.dump(attributeCount, output, pickle.HIGHEST_PROTOCOL)
    # saveImagesOfCharts()
    # if visibility_state == 5 and fileButton.triggered and fileButton.triggered[0]['prop_id'] == 'fileButton.n_clicks':
    #     attributeCount.write_image('images/AttributeGraph.pdf')
    #     return attributeCount, downloadFile(visibility_state, -1)
    return attributeCount

# attributeCount = ''
# with open('attributeCount.pkl', 'rb') as input:
#     attributeCount = pickle.load(input)
# f = go.FigureWidget(attributeCount)
# print(f.data[0])
# f.data[0].on_click(print('brrrr'))

# @app.callback(Output('third-chart', 'figure'), [Input("oneStar", "value"), State('radios', 'value')])
# def display_value(value, visibility_state):
#     if visibility_state == 5:
#         print('inside')
#     return dash.no_update

def saveImagesOfCharts(figure):
    print('here')
    # print(figure)
    with open('attributeCount.pkl', 'wb') as output:
        pickle.dump(figure, output, pickle.HIGHEST_PROTOCOL)

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
            attributeCount.write_image('images/AttributeGraph.pdf')
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


# inputList = []
# for r in restaurantsList:
#     inputList.append(Input(r, "n_clicks"))



@app.callback([Output("card-text", "children"),
               Output("card-title", "children"),
               Output("img", "src")
               ],
              Input("newsDropdown", "value"))
def update_card_text(dropdown_value):
    article_list = newsDF[newsDF['restaurant'].str.contains(dropdown_value)]['title'].to_list()
    date_list = newsDF[newsDF['restaurant'].str.contains(dropdown_value)]['date'].to_list()
    source_list = newsDF[newsDF['restaurant'].str.contains(dropdown_value)]['source'].to_list()
    correct_img = newsDF[newsDF['restaurant'].str.contains(dropdown_value)]['imageUrl'].to_list()[0]
    all_titles = ""
    for i in range(len(article_list)):
        all_titles += str(i+1) + ": " + "Date: " + date_list[i] + ", Source: " + source_list[i] + ", Title: "+ article_list[i] + ". \n"
    return all_titles, dropdown_value, correct_img

# run the app at port 8080
if __name__ == "__main__":
    application.run(debug=True, port=8080)
