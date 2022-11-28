import requests
import datetime
import seaborn
import matplotlib.pyplot as plt
import argparse

# Sources available by name
sources = {
    'trondheim': 'SN68125',
    'høvringen': 'SN16271',
    'røros': 'SN10380',
    'oslo': 'SN18210',
    'bergen': 'SN50540',
    'tromsø': 'SN90450',
    'oppdal': 'SN63705',
    'skistua': 'SN68110',
}

parser = argparse.ArgumentParser(description="Weather data for Trondheim",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-d", "--day", default=0, help="day of month")
parser.add_argument("-m", "--month", default=0, help="number of month")
parser.add_argument("-l", "--location", default='Trondheim', help="Location for temparatures, ignored if location_id given", choices=sources.keys())
parser.add_argument("-i", "--location_id", default=0, help="Weather station ID to use, overrides --location")
parser.add_argument("-n", "--num_days", default=1, help="The number of days to fetch for each year (requested day and (n-1) days previous)")
parser.add_argument("-a", "--average_only", action='store_true', help="Only display the average temperatures, not max and min")
parser.add_argument("-w", "--wind", action='store_true', help="Get wind speed (max gust, daily average, minimum hourly average) instead of temperature")
parser.add_argument("-s", "--snow", action='store_true', help="Get snow depth graph instead of temperature")
parser.add_argument("-W", "--weather", default=0, help="Weather type to fetch instead of temperature (see frost.met.no/elementtable)")
parser.add_argument("-q", "--quiet", action='store_true', help="Silence most print output")

args = parser.parse_args()
config = vars(args)

# Set location details
if config['location_id'] != 0:
    location = config['location_id']
    location_name = config['location_id']
else:
    location = sources[config['location'].lower()]
    location_name = config['location']

print('Location: {}'.format(location_name))
print('Using weather station ID {}'.format(location))

# Set start date
requested_day = datetime.date.today().day
requested_month = datetime.date.today().month
if config['day']:
    requested_day = int(config['day'])
if config['month']:
    requested_month = int(config['month'])

try:
    requested_date = datetime.date(datetime.date.today().year, requested_month, requested_day)
except ValueError:
    print('Invalid date requested')
    raise

if not config['quiet']:
    print('\nRequesting data from {}\n'.format(requested_date))
    print('Fetching data for...')

# Read client id from client_id file
with open('client_id.txt') as f:
    client_id = f.readline().strip()

# Prepare graph
seaborn.set_theme(style="dark")
seaborn.set()

# Gather and plot data
for days_back in range(0, int(config['num_days'])):
    history_list = list(())
    for years_ago in range(10, -1, -1):
        get_date = datetime.date(requested_date.year - years_ago,
                                 requested_date.month,
                                 requested_date.day) - datetime.timedelta(days=days_back)
        if not config['quiet']:
            print(get_date)

        # Define endpoint and parameters
        endpoint = 'https://frost.met.no/observations/v0.jsonld'

        if config['weather']:
            elements = 'max({0} P1D),min({0} P1D),mean({0} P1D)'.format(config['weather'])
        elif config['wind']:
            elements = 'max(wind_speed_of_gust P1D),min(wind_speed P1D),mean(wind_speed P1D)'
        elif config['snow']:
            elements = 'surface_snow_thickness'
        else:
            elements = 'max(air_temperature P1D),min(air_temperature P1D),mean(air_temperature P1D)'
        parameters = {
            'sources': location,
            'elements': elements,
            'referencetime': get_date,
            'timeoffsets': 'default',
            'levels': 'default',
        }
        # Issue an HTTP GET request
        r = requests.get(endpoint, parameters, auth=(client_id,''))
        # Extract JSON data
        json = r.json()

        try:
            data = json['data']
            air_temp_dict = {'year': get_date.year, 'min': False, 'mean': False, 'max': False }
            for observation in data[0]['observations']:
                if observation['elementId'].startswith('min'):
                    air_temp_dict['min'] = observation['value']
                if observation['elementId'].startswith('mean'):
                    air_temp_dict['mean'] = observation['value']
                if observation['elementId'].startswith('max'):
                    air_temp_dict['max'] = observation['value']
                if config['snow']:
                    if observation['timeResolution'] == 'P1D':
                        air_temp_dict['mean'] = observation['value']
            history_list.append(air_temp_dict)
            units = observation['unit']

        except KeyError:
            print("No data recieved for {}".format(get_date))

    # reformat data for day graph
    mean = list(())
    mean_year = list(())
    min = list(())
    min_year = list(())
    max = list(())
    max_year = list(())
    for year_data in history_list:
        if year_data['mean']:
            mean.append(year_data['mean'])
            mean_year.append(year_data['year'])
        if not config['average_only']:
            if year_data['min']:
                min.append(year_data['min'])
                min_year.append(year_data['year'])
            if year_data['max']:
                max.append(year_data['max'])
                max_year.append(year_data['year'])

    # Plot data for this date
    mean_plot, = plt.plot(mean_year, mean, 'go', label='Daily mean')
    min_plot, = plt.plot(min_year, min, 'bo', label='Daily minimum')
    max_plot, = plt.plot(max_year, max, 'ro', label='Daily maximum')

# Add zero 'C line
plt.axhline(y=0, color='b', linestyle='-')

# Create Chart title
if config['weather']:
    weather_type = config['weather']
elif config['wind']:
    weather_type = 'Wind speed'
elif config['snow']:
    weather_type = 'Snow depth'
else:
    weather_type = 'Temperature'
title_string = '{} in {} on '.format(weather_type, location_name.capitalize())
if int(config['num_days']) > 1:
    start_date = requested_date - datetime.timedelta(days=(int(config['num_days']) - 1))
    title_string = title_string + ('{}/{} to '.format(start_date.day, start_date.month))
title_string = title_string + ('{}/{} by Year'.format(requested_date.day, requested_date.month))
plt.title(title_string, size='x-large')

# Add legends
plt.subplots_adjust(bottom=0.2)
plt.legend(handles=[max_plot, mean_plot, min_plot], bbox_to_anchor=(0.5, -0.15), loc='upper center', ncol=3)

if config['weather']:
    plt.ylabel("Recorded {} ({})".format(config['weather'], units))
if config['snow']:
    plt.ylabel("Recorded snow depth ({})".format(units))
elif config['wind']:
    plt.ylabel("Recorded wind speed (m/s)")
else:
    plt.ylabel("Recorded temperatures ('C)")

# Show graph
plt.plot()
plt.show()
