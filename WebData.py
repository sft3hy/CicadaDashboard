"""
Last Update: 7/6/2021

IMPORTANT: make sure you have 'client_secrets.json' in the same location as this file

Install Packages:
>pip install oauth2client
>pip install --upgrade google-api-python-client
>
"""

from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

"""
METHODS LiveWebData:
    
    Retrieves JSON of _____ from Google Analytics API:
        query_active_users()
        
        query_users_per_location()  
        
            query_users_per_countries() 
            
            query_users_per_region()
        
            query_users_per_city()
        
        query_users_per_lat_long()
            
        query_users_per_page()
    
    Retrieves JSON of _____ and scrubs for important info from returns:
        active_users()
        
        users_per_location()    
        
            users_per_countries()
            
            users_per_region()
        
            users_per_city()
        
        users_per_lat_long()
            
        users_per_page()
"""

"""
METHODS WebData:

WIP

"""


class LiveWebData:

    def __init__(self):
        # Scope and Access key
        self.scopes = ['https://www.googleapis.com/auth/analytics.readonly']
        self.key_file_location = 'client_secrets.json'

        # Fetch credentials
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            self.key_file_location, scopes=self.scopes)

        #
        self.service = build('analytics', 'v3', credentials=credentials)

        self.profile_id = query_first_profile(self.service)

    """
    Inputs: https://developers.google.com/analytics/devguides/reporting/realtime/v3/reference/data/realtime/get
    Metrics and Dimensions: https://developers.google.com/analytics/devguides/reporting/realtime/dimsmets
    
    Default: Print the current number of users, separated by mobile device model
    
    Notes: Not all fields are required, only required field is Metrics
            Format for multiple Dimensions, Metrics, etc. is: 'rt:____, rt:____'
    
    More Complex Example:
    Returns the number of active users, separated into Countries and Page titles, with 1 max result...
    
            print(reporting.print_live_data(
                dimensions='rt:pageTitle, rt:country',
                metrics='rt:activeUsers',
                max_results = 1,
            ))
    """

    # User Defined searches:
    def get_live_data(self, dimensions='rt:browser', metrics='rt:activeUsers', sort=None, filters=None, max_results=None):
        return self.service.data().realtime().get(
            ids='ga:' + self.profile_id,
            metrics=metrics,
            dimensions=dimensions,
            sort=sort,
            filters=filters,
            max_results=max_results,
        ).execute()

    def print_live_data(self, dimensions='ga:source', metrics='ga:sessions', sort=None, filters=None, max_results=None):
        result = self.get_live_data(
            dimensions=dimensions,
            metrics=metrics,
            sort=sort,
            filters=filters,
            max_results=max_results,
        )
        return result.get('rows')

    # Pre-defined searches:
    # Returns the Google Analytics JSON for active users.
    def query_active_users(self):
        return self.service.data().realtime().get(
            ids='ga:' + self.profile_id,
            metrics='rt:activeUsers',).execute()

    # Returns an integer number of active users
    def active_users(self):
        result = self.query_active_users()
        if result.get('totalsForAllResults').get('rt:activeUsers') == '0':
            return None
        else:
            return int(result.get('rows')[0][0])

    # Returns the JSON for location
    def query_users_per_location(self):
        return self.service.data().realtime().get(
            ids='ga:' + self.profile_id,
            metrics='rt:activeUsers',
            dimensions='rt:country, rt:region, rt:city',).execute()

    # Returns a list of locations
    def users_per_location(self):
        result = self.query_users_per_location()
        if result.get('totalsForAllResults').get('rt:activeUsers') == '0':
            return None
        else:
            return result.get('rows')

    # Returns the JSON for countries
    def query_users_per_countries(self):
        return self.service.data().realtime().get(
            ids='ga:' + self.profile_id,
            metrics='rt:activeUsers',
            dimensions='rt:country',).execute()

    # Returns a list of countries
    def users_per_countries(self):
        result = self.query_users_per_countries()
        if result.get('totalsForAllResults').get('rt:activeUsers') == '0':
            return None
        else:
            return result.get('rows')

    # Returns the JSON for Regions
    def query_users_per_region(self):
        return self.service.data().realtime().get(
            ids='ga:' + self.profile_id,
            metrics='rt:activeUsers',
            dimensions='rt:region',).execute()

    # Returns a list of Regions
    def users_per_region(self):
        result = self.query_users_per_region()
        if result.get('totalsForAllResults').get('rt:activeUsers') == '0':
            return None
        else:
            return result.get('rows')

    # Returns the JSON for cities
    def query_users_per_city(self):
        return self.service.data().realtime().get(
            ids='ga:' + self.profile_id,
            metrics='rt:activeUsers',
            dimensions='rt:city',).execute()

    # Returns a list of cities
    def users_per_city(self):
        result = self.query_users_per_city()
        if result.get('totalsForAllResults').get('rt:activeUsers') == '0':
            return None
        else:
            return result.get('rows')

    # Returns the JSON for lat and lon
    def query_users_per_lat_long(self):
        return self.service.data().realtime().get(
            ids='ga:' + self.profile_id,
            metrics='rt:activeUsers',
            dimensions='rt:latitude, rt:longitude',).execute()

    # Returns a list of lat and lon
    def users_per_lat_long(self):
        result = self.query_users_per_lat_long()
        if result.get('totalsForAllResults').get('rt:activeUsers') == '0':
            return None
        else:
            return result.get('rows')

    # Returns the JSON for countries
    def query_users_per_page(self):
        return self.service.data().realtime().get(
            ids='ga:' + self.profile_id,
            metrics='rt:activeUsers',
            dimensions='rt:pagePath',).execute()

    # Returns a list of countries
    def users_per_page(self):
        result = self.query_users_per_page()
        if result.get('totalsForAllResults').get('rt:activeUsers') == '0':
            return None
        else:
            return result.get('rows')


class WebData:

    def __init__(self):
        # Scope and Access key
        self.scopes = ['https://www.googleapis.com/auth/analytics.readonly']
        self.key_file_location = 'client_secrets.json'

        # Fetch credentials
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            self.key_file_location, scopes=self.scopes)

        #
        self.service = build('analytics', 'v3', credentials=credentials)

        self.profile_id = query_first_profile(self.service)

    """
    Inputs: https://developers.google.com/analytics/devguides/reporting/core/v3/reference#filters
    Metrics and Dimensions: https://ga-dev-tools.web.app/dimensions-metrics-explorer/
    
    Default: Print the number of users, and the countries they come from, over the last week
    
    Notes: Not all fields are required, only required fields are Dates and Metrics
            Format for multiple Dimensions, Metrics, etc. is: 'ga:____, ga:____'
    
    More Complex Example:
    Returns the number of Users and Sessions, divided into Sub Continents and Continents, over the past 30 days...
    
            print(reporting.print_results(
                start_date='30daysAgo',
                end_date='today',
                metrics='ga:users, ga:sessions',
                dimensions='ga:continent, ga:subContinent',
            ))
    """
    def get_results(self, start_date='7daysAgo', end_date='today', dimensions='ga:country', metrics='ga:users',
                    sort=None, filters=None, segment=None):
        return self.service.data().ga().get(
            ids='ga:' + self.profile_id,
            start_date=start_date,
            end_date=end_date,
            metrics=metrics,
            dimensions=dimensions,
            sort=sort,
            filters=filters,
            segment=segment,
        ).execute()

    def print_results(self, start_date='7daysAgo', end_date='today', dimensions='ga:country', metrics='ga:users',
                      sort=None, filters=None, segment=None):
        result = self.get_results(start_date, end_date, dimensions, metrics, sort, filters, segment)
        return result.get('rows')


def query_first_profile(service):
    # Use the Analytics service object to get the first profile id.

    # Get a list of all Google Analytics accounts for this user
    accounts = service.management().accounts().list().execute()

    if accounts.get('items'):
        # Get the first Google Analytics account.
        account = accounts.get('items')[0].get('id')

        # Get a list of all the properties for the first account.
        properties = service.management().webproperties().list(
            accountId=account).execute()

        if properties.get('items'):
            # Get the first property id.
            property = properties.get('items')[0].get('id')

            # Get a list of all views (profiles) for the first property.
            profiles = service.management().profiles().list(
                accountId=account,
                webPropertyId=property).execute()

            if profiles.get('items'):
                # return the first view (profile) id.
                return profiles.get('items')[0].get('id')
    return None

