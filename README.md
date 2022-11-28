# yr_context - Norwegian weather graphing

A quick script to get historic weather data from the Norwegian meteorological
institute on a given date or date range for the last decade, and present it as a graph.

Default weather type to analyse is temperature, but tailored options are available for
wind speed and snow depth, and arbirary data types from frost.met.no can be queeried.

Can graph data from any weather station in Norway.  See `yr_context -h` for all options.

Example output:

`$ python yr_context.py --location røros --day 18 --month 11 --num_days 2`

![Røros 2-day](samples/roros.png)

`$ python yr_context.py --location høvringen --day 31 --month 12 --num_days 15`

![Høvringen 15-day](samples/hovringen.png)

Uses data from https://frost.met.no/

Requires a free client-id from frost.met.no to function.
Request this at https://frost.met.no/auth/requestCredentials.html

Place the client-id in a file called client_id.txt in this directory.

Not all data types are available for all weather stations or dates.  The script will run but may
produce a graph with no or limited data.  See print output for which dates recieved zero data
for your request.
