# Libraries needed (pandas is not standard and must be installed in Python)
import requests
import pandas as pd
import datetime

# Insert your own client ID here
# Initially hard-coded, removed to publish, replaced with external input in later commit
client_id = '<REDACTED>'

# Source
trondheim = 'SN68125'

today = datetime.date.today()
for years_ago in range(11, 0, -1):
    get_date = datetime.date(today.year - years_ago, today.month, today.day)

    # Define endpoint and parameters
    endpoint = 'https://frost.met.no/observations/v0.jsonld'
    parameters = {
        'sources': trondheim,
        'elements': 'max(air_temperature P1D),min(air_temperature P1D)',
        'referencetime': get_date,
        'timeoffsets': 'default',
        'levels': 'default',
    }
    # Issue an HTTP GET request
    r = requests.get(endpoint, parameters, auth=(client_id,''))
    # Extract JSON data
    json = r.json()

    # Check if the request worked, print out any errors
    try:
        data = json['data']
        print("{}: {}'C to {}'C".format(get_date, data[0]['observations'][1]['value'], data[0]['observations'][0]['value']))
    except KeyError:
        print(get_date)

    # This will return a Dataframe with all of the observations in a table format
    # df = pd.DataFrame()
    # for i in range(len(data)):
    #     row = pd.DataFrame(data[i]['observations'])
    #     row['referenceTime'] = data[i]['referenceTime']
    #     row['sourceId'] = data[i]['sourceId']
    #     df = df.append(row)
    #
    # df = df.reset_index()
    # print(df.head())
