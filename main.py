# File to test WebData
from WebData import LiveWebData
from WebData import WebData

print("1")
liveReporting = LiveWebData()
reporting = WebData()
print("2")

# Live Users
print("Live Users:")
print(liveReporting.active_users())
print()

# Live Locations
print("Users per Location (Country,Region,City):")
print(liveReporting.users_per_location())
print()

# Live Countries
print("Users per Country:")
print(liveReporting.users_per_countries())
print()

# Live Regions
print("Users per Region:")
print(liveReporting.users_per_region())
print()

# Live Cities
print("Users per City:")
print(liveReporting.users_per_city())
print()

# Live Lat Long
print("Users per Lat/Long:")
print(liveReporting.users_per_lat_long())
print()

# Live Pages
print("Users per Page:")
print(liveReporting.users_per_page())
print()

# Sessions last 7 days
print("Sessions last 7 days:")
print(reporting.get_results())
print()


# Generic Results Query (Past 30 Days,:
print("Sessions :")
print(reporting.print_results(
    start_date='30daysAgo',
    end_date='today',
    metrics='ga:users, ga:sessions',
    dimensions='ga:subContinent',
))
