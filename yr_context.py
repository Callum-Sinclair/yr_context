# Libraries needed (pandas is not standard and must be installed in Python)
import requests
import datetime
import seaborn
import matplotlib.pyplot as plt


# Insert your own client ID here
# Initially hard-coded, removed to publish, replaced with external input in later commit
client_id = '<REDACTED>'

# Source
trondheim = 'SN68125'

today = datetime.date.today()
history_list = list(())
for years_ago in range(10, -1, -1):
    get_date = datetime.date(today.year - years_ago, today.month, today.day)
    print(get_date)

    # Define endpoint and parameters
    endpoint = 'https://frost.met.no/observations/v0.jsonld'
    parameters = {
        'sources': trondheim,
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
        print("ERROR")

print(history_list)

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
    if year_data['min']:
        min.append(year_data['min'])
        min_year.append(year_data['year'])
    if year_data['max']:
        max.append(year_data['max'])
        max_year.append(year_data['year'])

seaborn.set_theme(style="dark")
seaborn.set()
day_graph = plt.plot(mean_year, mean, 'go')
day_graph = plt.plot(min_year, min, 'bo')
day_graph = plt.plot(max_year, max, 'ro')
plt.show()
