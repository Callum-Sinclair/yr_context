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
for years_ago in range(6, 0, -1):
    get_date = datetime.date(today.year - years_ago, today.month, today.day)
    print(years_ago)
    print(get_date)

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
    if r.status_code == 200:
        data = json['data']
        print('Data retrieved from frost.met.no!')
    else:
        print('Error! Returned status code %s' % r.status_code)
        print('Message: %s' % json['error']['message'])
        print('Reason: %s' % json['error']['reason'])

    # This will return a Dataframe with all of the observations in a table format
    df = pd.DataFrame()
    for i in range(len(data)):
        row = pd.DataFrame(data[i]['observations'])
        row['referenceTime'] = data[i]['referenceTime']
        row['sourceId'] = data[i]['sourceId']
        df = df.append(row)

    df = df.reset_index()
    print(df.head())
