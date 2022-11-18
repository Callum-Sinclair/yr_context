# Libraries needed (pandas is not standard and must be installed in Python)
import requests
import datetime
import seaborn
import matplotlib.pyplot as plt
import argparse

# Source
sources = {
    'trondheim': 'SN68125',
    'høvringen': 'SN16271',
    'røros': 'SN10380',
    'oslo': 'SN18210',
    'bergen': 'SN50540',
    'tromsø': 'SN90450',
    'oppdal': 'SN63705',
}

with open('client_id.txt') as f:
    client_id = f.readline().strip()

parser = argparse.ArgumentParser(description="Weather data for Trondheim",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-d", "--day", default=0, help="day of month")
parser.add_argument("-m", "--month", default=0, help="number of month")
parser.add_argument("-l", "--location", default='Trondheim', help="Location for temparatures, ignored if location_id given", choices=sources.keys())
parser.add_argument("-i", "--location_id", default=0, help="Weather station ID to use, overrides --location")
parser.add_argument("-n", "--num_days", default=1, help="The number of days to fetch for each year (requested day and (n-1) days previous)")
parser.add_argument("-a", "--average_only", action='store_true', help="Only display the average temperatures, not max and min")
parser.add_argument("-q", "--quiet", action='store_true', help="Silence most print output")

args = parser.parse_args()
config = vars(args)

if config['location_id'] != 0:
    location = config['location_id']
    location_name = config['location_id']
else:
    location = sources[config['location'].lower()]
    location_name = config['location']

print('Location: {}'.format(location_name))
print('Using weather station ID {}'.format(location))

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

seaborn.set_theme(style="dark")
seaborn.set()

if not config['quiet']:
    print('\nRequesting data from {}\n'.format(requested_date))
    print('Fetching data for...')

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
        parameters = {
            'sources': location,
            'elements': 'max(air_temperature P1D),min(air_temperature P1D),mean(air_temperature P1D)',
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
            history_list.append(air_temp_dict)
            # print(air_temp_dict)

        except KeyError:
            print("No data recieved for {}".format(get_date))

    # print(history_list)

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

    mean_plot, = plt.plot(mean_year, mean, 'go', label='Daily mean')
    min_plot, = plt.plot(min_year, min, 'bo', label='Daily minimum')
    max_plot, = plt.plot(max_year, max, 'ro', label='Daily maximum')

# Add zero 'C line
plt.axhline(y=0, color='b', linestyle='-')

# Create Chart title
title_string = 'Temperature in {} on '.format(location_name.capitalize())
if int(config['num_days']) > 1:
    start_date = requested_date - datetime.timedelta(days=(int(config['num_days']) - 1))
    title_string = title_string + ('{}/{} to '.format(start_date.day, start_date.month))
title_string = title_string + ('{}/{} by Year'.format(requested_date.day, requested_date.month))
plt.title(title_string, size='x-large')

# Add legends
plt.subplots_adjust(bottom=0.2)
plt.legend(handles=[max_plot, mean_plot, min_plot], bbox_to_anchor=(0.5, -0.15), loc='upper center', ncol=3)
plt.ylabel("Recorded temperatures ('C)")

# Show graph
plt.plot()
plt.show()
