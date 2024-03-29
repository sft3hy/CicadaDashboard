import dash
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Output, Input
from datetime import date
import re
import json

# pd print settings
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

# reads in the json
data = pd.read_json("finalBusinessData.json")

# with open("finalBusinessData.json", encoding="UTF-8") as f:
#     sData = json.load(f)
#
# for business in sData:
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
nams = data.name.to_list()
tars = data.stars.to_list()
la = data.latitude.to_list()
lo = data.longitude.to_list()
sta = data.state.to_list()
id = data.business_id.to_list()

i = 0
namsNStarsList = []
for n in nams:
    namsNStarsList.append(n + ": " + str(tars[i]) + " Star Average")
    i += 1

mapDF = pd.DataFrame(list(zip(namsNStarsList, la, lo, sta, tars, nams, id)),
                     columns=['nameNStars', 'latitude', 'longitude', 'state', 'stars', 'name', 'business_id'])

# format a table to match check ins to business name using business_id
checkins = pd.read_json("finalCheckin.json")
goodIDs = mapDF.business_id.to_list()

goodCheckins = checkins[checkins.business_id.isin(goodIDs)]
nameAndCheckin = mapDF.merge(goodCheckins, on="business_id")

finalCheckins = nameAndCheckin[['name_x', 'date', 'state_x']]
finalCheckins = finalCheckins[finalCheckins["date"] != "None"]
finalCheckins = finalCheckins.dropna()
finalCheckins = finalCheckins.groupby(['state_x', 'name_x'])['date'].apply(', '.join).reset_index()

datesList = finalCheckins.date.to_list()

overallDates = []
for l in datesList:
    tempList = l.replace(' ', '').split(',')
    dateList = []
    for date in tempList:
        date = date[0:7]
        dateList.append(date)
    overallDates.append(dateList)

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

# the main meat of the display, all in this weird html/python hybrid (it's how dash works)
app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.Img(
                    src='https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/344612c2-fb5b-4cea-8846-869ed27fe70a/da6ozar-bc9308b1-01ae-49e7-b497-d7acbfa0f3ce.jpg/v1/fill/w_1024,h_576,q_75,strp/forest_background_by_chantalwut_da6ozar-fullview.jpg?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1cm46YXBwOjdlMGQxODg5ODIyNjQzNzNhNWYwZDQxNWVhMGQyNmUwIiwiaXNzIjoidXJuOmFwcDo3ZTBkMTg4OTgyMjY0MzczYTVmMGQ0MTVlYTBkMjZlMCIsIm9iaiI6W1t7ImhlaWdodCI6Ijw9NTc2IiwicGF0aCI6IlwvZlwvMzQ0NjEyYzItZmI1Yi00Y2VhLTg4NDYtODY5ZWQyN2ZlNzBhXC9kYTZvemFyLWJjOTMwOGIxLTAxYWUtNDllNy1iNDk3LWQ3YWNiZmEwZjNjZS5qcGciLCJ3aWR0aCI6Ijw9MTAyNCJ9XV0sImF1ZCI6WyJ1cm46c2VydmljZTppbWFnZS5vcGVyYXRpb25zIl19.6rj3OZCxvz65h1KORRIxnfy9Wy6JqYH9x-j3_2JI_gs',
                    sizes="small", className="header", style="background-image",
                ),
                html.Img(src='https://i.giphy.com/media/KAGO5fYDEnJ3VFqtWN/200w.gif', className='gif'),
                html.P(children="🦟 CICADA", className="header-title"),
                html.P(
                    children="Analyze the behavior of your product's users",
                    className="header-description",
                ),
            ],
            className="header",
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(children="Region", className="menu-title"),
                        dcc.Checklist(
                            id="checklist",
                            options=[
                                {"label": state, "value": state}
                                for state in np.sort(data.state.unique())
                            ],
                            value=["BC"],
                            className="body",
                        ),
                    ],
                    style={'textalign': 'center'}
                ),
            ],
            className="menu",
        ),

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
            className="wrapper",
        ),
        html.Div(children=dcc.Graph(
            id="bar-chart", config={"displayModeBar": False},
        ),
            className="wrapper",
        ),
        html.Div(children=[html.Div(
            children=dcc.Graph(
                id='map',
                figure=map,
                className="wrapper",
            ),
        ),
        ],
        ),
        html.Div(
            children=dcc.Graph(
                id="second-chart", config={"displayModeBar": False},
            ),
            className="wrapper",
        ),
    ],

    className="background"
)


# make the web-app responsive (so when you click something, it responds)
@app.callback(
    [Output("checkin-dates", "figure"),
     Output("bar-chart", "figure"),
     Output("second-chart", "figure"),
     Output("map", "figure")],
    [Input("checklist", "value")])
def update_bar_chart(options_chosen):
    # make dataframes that the buttons can update according to user requests
    dff = data[data["state"].isin(options_chosen)]
    m = mapDF[mapDF["state"].isin(options_chosen)]
    st = formattedStars[formattedStars["state"].isin(options_chosen)]

    total_columns = []
    for option in options_chosen:
        for col in frequencies.columns:
            if option in col:
                total_columns.append(col)


    check = frequencies[[state for state in total_columns]]

    # plotly bar charts
    fig1 = px.bar(st, x="stars", y="name", orientation='h',
                  color="state", barmode='group',
                  title="Products vs. User Ratings",
                  labels={
                      "stars": "Average Stars",
                      "name": "Product Name",
                      "state": "State"
                  }
                  )
    fig2 = px.bar(dff, x="review_count", y="name", orientation='h', color="state",
                  title="Products vs. Review Count",
                  labels={
                      "review_count": "Review Count",
                      "name": "Product Name",
                      "state": "State"
                  }
                  )
    fig3 = go.Figure(data=go.Scattergeo(
        lon=m['longitude'],
        lat=m['latitude'],
        mode='markers',
        marker_color=m['stars'],
        text=m['nameNStars'],
    ))
    fig3.update_layout(
        geo_scope='usa'
    )

    fig4 = px.line(check, x=check.index, title="Restaurants' Checkins Over Time",
                   y=total_columns, labels={"index": "Date", }, )
    fig4.update_layout(yaxis_title="Number of Checkins")


    # return all the charts/maps
    return fig4, fig2, fig3, fig1


# run the app at port 8080
if __name__ == "__main__":
    application.run(debug=True, port=8080)
