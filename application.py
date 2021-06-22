import dash
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input, State
from datetime import date, time
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

attributeGraph = ''

# formatting stuff
external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?"
                "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
        "href": 'https://codepen.io/chriddyp/pen/bWLwgP.css',
        "rel": "buttons",
    },
]
# how to run an app with dash/plotly
app = dash.Dash(__name__, external_stylesheets=external_stylesheets,
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
                     columns=['nameNStars', 'latitude', 'longitude', 'state', 'stars', 'name', 'business_id', 'review_count'])

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
        if date > startOfLastWeeks < endDate :
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

# the main meat of the display, all in this weird html/python hybrid (it's how dash works)
app.layout = html.Div(
    children=[
        html.Div(
            children=[
            #     html.Img(
            #         src='https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/344612c2-fb5b-4cea-8846-869ed27fe70a/da6ozar-bc9308b1-01ae-49e7-b497-d7acbfa0f3ce.jpg/v1/fill/w_1024,h_576,q_75,strp/forest_background_by_chantalwut_da6ozar-fullview.jpg?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1cm46YXBwOjdlMGQxODg5ODIyNjQzNzNhNWYwZDQxNWVhMGQyNmUwIiwiaXNzIjoidXJuOmFwcDo3ZTBkMTg4OTgyMjY0MzczYTVmMGQ0MTVlYTBkMjZlMCIsIm9iaiI6W1t7ImhlaWdodCI6Ijw9NTc2IiwicGF0aCI6IlwvZlwvMzQ0NjEyYzItZmI1Yi00Y2VhLTg4NDYtODY5ZWQyN2ZlNzBhXC9kYTZvemFyLWJjOTMwOGIxLTAxYWUtNDllNy1iNDk3LWQ3YWNiZmEwZjNjZS5qcGciLCJ3aWR0aCI6Ijw9MTAyNCJ9XV0sImF1ZCI6WyJ1cm46c2VydmljZTppbWFnZS5vcGVyYXRpb25zIl19.6rj3OZCxvz65h1KORRIxnfy9Wy6JqYH9x-j3_2JI_gs',
            #         sizes="small", className="gif", style="background-image",
            #     ),
                html.Img(
                    src='https://upload.wikimedia.org/wikipedia/commons/thumb/5/5f/NRO.svg/1200px-NRO.svg.png',
                    sizes="small", className="NRO", style={"clear": "right", "float": "right"}
                ),
                html.Img(src="static/logo.png", className='gif'
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
                        html.Div(children="Select a region and the specific metrics you want to view:", className="menu-title"),
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
        html.Div([
            # Create element to hide/show, in this case an 'Input Component'
            dcc.RadioItems(
            id = 'radio',
            options=[
                {'label': 'Product Usage Over Time', 'value': 'c'},
                {'label': 'Map', 'value': 'm'},
                {'label': 'Products vs. User Ratings', 'value': 'pa'},
                {'label': 'Products vs. Review Count', 'value': 'pt'},
                {'label': 'Summary Statistics', 'value':'s'},
            ],
                className="radioOptions",
                value="m"
            )
        ],
        ),
        html.Div([
             # Create element to hide/show, in this case an 'Input Component'
             dbc.Button('Download CSV Report', id='fileButton', n_clicks=0),
             html.Span(id='outputReport'),
             dcc.Download(id='nameVsStarsDownload-csv'),
             dcc.Download(id='nameVsReviewDownload-csv'),
             dcc.Download(id='attributeCountDownload-csv'),
             dcc.Download(id='productUsageDownload-csv'),
         ],),
        # html.Div([
        #     dcc.DatePickerRange(
        #         id='my-date-picker-range',
        #         min_date_allowed=date(2010, 1, 1),
        #         max_date_allowed=date(2020, 12, 1),
        #         initial_visible_month=date(2010, 1, 1),
        #     ),
        #     html.Div(id='output-container-date-picker-range')
        # ]),
        html.Div(children=dcc.Graph(
            id="checkin-dates", config={"displayModeBar": False},
        ),
            className="wrapper", style= {'display': 'block'}
        ),
        html.Div(children=dcc.Graph(
            id="checkin-days", config={"displayModeBar": False},
        ),
            className="wrapper", style= {'display': 'block'}
        ),
        html.Div(children=dcc.Graph(
            id="checkin-months", config={"displayModeBar": False},
        ),
            className="wrapper", style= {'display': 'block'}
        ),
        html.Div(children=dcc.Graph(
            id="bar-chart", config={"displayModeBar": False},
        ),
            className="wrapper", style= {'display': 'block'}
        ),
        html.Div(children=[html.Div(
            children=dcc.Graph(
                id='ma',
                figure=map,
            ),
            className="wrapper", style= {'display': 'block'}
        ),
        ],
        ),
        html.Div(
            children=dcc.Graph(
                id="second-chart", config={"displayModeBar": False},
            ),
            className="wrapper", style= {'display': 'block'}
        ),
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

        html.Div(
            children=dcc.Graph(
                id="third-chart", config={"displayModeBar": False},
            ),
            className="wrapper", style = {'display': 'block'}
        ),
    ],

    className="background"
)


# make the web-app responsive (so when you click something, it responds)
@app.callback(
    [Output("checkin-dates", "figure"),
     Output("checkin-days", "figure"),
     Output("checkin-months", "figure"),
     Output('productUsageDownload-csv', 'data')],
    [Input("checklist", "value"),
     Input('fileButton', 'n_clicks'),
     State('radio', 'value')])
def update_bar_chart(state_chosen, n_clicks, visibility_state):
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
                   y=total_columns, labels={"index": "Date", "variable": "State and Name", "value": "Total Checkins"} )
    checkinsVsDate.update_layout(yaxis_title="Number of Checkins")

    checkinsVsDay = px.line(dayCheck, x=dayCheck.index, title="Product Usage Last Three Weeks",
                             y=total_columns,
                             labels={"index": "Date", "variable": "State and Name", "value": "Total Checkins"})
    checkinsVsDay.update_layout(yaxis_title="Number of Checkins")

    checkinsVsMonth = px.line(monthCheck, x=monthCheck.index, title="Product Usage Last Three Months",
                            y=total_columns,
                            labels={"index": "Date", "variable": "State and Name", "value": "Total Checkins"})
    checkinsVsMonth.update_layout(yaxis_title="Number of Checkins")

    if visibility_state == 'c' and fileButton.triggered and fileButton.triggered[0]['prop_id'] == 'fileButton.n_clicks':
        checkinsVsMonth.write_image('images/checkinsVsMonth.pdf')
        checkinsVsDay.write_image('images/checkinsVsDay.pdf')
        checkinsVsDate.write_image('images/checkinsVsDate.pdf')
        return checkinsVsDate, checkinsVsMonth, checkinsVsDay, downloadFile(visibility_state)

    # return all the charts/maps
    return checkinsVsDate, checkinsVsMonth, checkinsVsDay, dash.no_update



@app.callback(
   Output(component_id='checkin-dates', component_property='style'),
   [Input(component_id='radio', component_property='value')])

def show_hide_element(visibility_state):
    if visibility_state == 'c':
        return {'display': 'block'}
    else:
        return {'display': 'none'}

@app.callback(
   Output(component_id='checkin-days', component_property='style'),
   [Input(component_id='radio', component_property='value')])

def show_hide_element(visibility_state):
    if visibility_state == 'c':
        return {'display': 'block'}
    else:
        return {'display': 'none'}

@app.callback(
   Output(component_id='checkin-months', component_property='style'),
   [Input(component_id='radio', component_property='value')])

def show_hide_element(visibility_state):
    if visibility_state == 'c':
        return {'display': 'block'}
    else:
        return {'display': 'none'}


@app.callback(
   Output(component_id='bar-chart', component_property='style'),
   [Input(component_id='radio', component_property='value')])

def show_hide_element(visibility_state):
    if visibility_state == 'pt':
        return {'display': 'block'}
    else:
        return {'display': 'none'}

@app.callback(
   Output(component_id='second-chart', component_property='style'),
   [Input(component_id='radio', component_property='value')])

def show_hide_element(visibility_state):
    if visibility_state == 'pa':
        return {'display': 'block'}
    else:
        return {'display': 'none'}

@app.callback(
   Output(component_id='ma', component_property='style'),
   [Input(component_id='radio', component_property='value')])

def show_hide_element(visibility_state):
    if visibility_state == 'm':
        return {'display': 'block'}
    else:
        return {'display': 'none'}

@app.callback(
   Output('bar-chart', 'figure'),
   Output('nameVsReviewDownload-csv', 'data'),
   [Input("checklist", "value"),
    Input('fileButton', 'n_clicks'),
    State('radio', 'value')])

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
    if visibility_state == 'pt' and fileButton.triggered and fileButton.triggered[0]['prop_id'] == 'fileButton.n_clicks':
        nameVsReviewCount.write_image('images/nameVsReviewCount.pdf')
        return nameVsReviewCount, downloadFile(visibility_state)
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

@app.callback(
   Output('second-chart', 'figure'),
   Output('nameVsStarsDownload-csv', 'data'),
   [Input("checklist", "value"),
    Input('fileButton', 'n_clicks'),
    State('radio', 'value')])

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
    if visibility_state == 'pa' and fileButton.triggered and fileButton.triggered[0]['prop_id'] == 'fileButton.n_clicks':
        nameVsStars.write_image('images/nameVsStars.pdf')
        return nameVsStars, downloadFile(visibility_state)
    return nameVsStars, dash.no_update


@app.callback(
   Output(component_id='third-chart', component_property='style'),
   [Input(component_id='radio', component_property='value')])

def show_hide_element(visibility_state):
    if visibility_state == 's':
        return {'display': 'block'}
    else:
        return {'display': 'none'}

@app.callback(
   Output(component_id='numStarsRadio', component_property='style'),
   [Input(component_id='radio', component_property='value')])

def show_hide_element(visibility_state):
    if visibility_state == 's':
        return {'display': 'block'}
    else:
        return {'display': 'none'}


# Radio buttons for changing stars in attribute graph
@app.callback(
   Output('third-chart', 'figure'),
   Output('attributeCountDownload-csv', 'data'),
   [Input('numStarsRadio', 'value'),
    Input('checklist', 'value'),
    Input('fileButton', 'n_clicks'),
    State('radio', 'value')])

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
    attributeCount.update_layout(barmode='group', title='Attributes of ' + str(a.getStar()) + ' Star Restaurants',
                                 yaxis_title="Number of Attributes",
                                 xaxis_title="Attributes")
    if visibility_state == 's' and fileButton.triggered and fileButton.triggered[0]['prop_id'] == 'fileButton.n_clicks':
        attributeCount.write_image('images/AttributeGraph.pdf')
        return attributeCount, downloadFile(visibility_state)
    # attributeCount.write_image('images/AttributeGraph.pdf')
    return attributeCount, dash.no_update

# hides download button for map
@app.callback(
   Output(component_id='fileButton', component_property='style'),
   [Input(component_id='radio', component_property='value')])

def show_hide_element(visibility_state):
    if visibility_state != 'm':
        return {'display': 'block'}
    else:
        return {'display': 'none'}

# download report into csv file
# @app.callback(
#    Output('download-csv', 'data'),
#    [Input('fileButton', 'n_clicks'),
#     State('radio', 'value')],
#     prevent_initial_call=True)

def downloadFile(visibility_state):
    if visibility_state == 's':
        return dcc.send_file('images/AttributeGraph.pdf')
    elif visibility_state == 'pt':
        return dcc.send_file('images/nameVsReviewCount.pdf')
    elif visibility_state == 'pa':
        # fig = copy.deepcopy(nameVsStars)
        # fig.write_image('images/nameVsStars.pdf')
        #time.sleep(3)
        return dcc.send_file('images/nameVsStars.pdf')
    else:
    #df = pd.DataFrame({"a": [1, 2, 3, 4], "b": [2, 1, 5, 6], "c": ["x", "x", "y", "y"]})
        return dcc.send_file('images/checkinsVsDate.pdf', 'images/checkinsVsMonth.pdf', 'images/checkinsVsDay.pdf')


# run the app at port 8080
if __name__ == "__main__":
    application.run(debug=True, port=8080)
