# Downloads bladindex file from nationaalgeoregister and stores geometries in dict with bladnr as key, then export dict to json file

import json, requests

BLADINDEX_JSON_URL = "http://geodata.nationaalgeoregister.nl/ahn2/wfs?&REQUEST=GetFeature&SERVICE=WFS&VERSION=1.1.0&TYPENAME=ahn2_bladindex&BBOX=648.8692338359542,305797.13988315896,288160.09461884724,620773.0085768757&SRSNAME=EPSG:28992&OUTPUTFORMAT=json"
OUTFILE = 'tiles.json'

original_bladindex = requests.get(BLADINDEX_JSON_URL).json()

my_bladindex = {}
for f in original_bladindex['features']:
	f['properties']['bladnr']
	my_bladindex[ f['properties']['bladnr'] ] = f['geometry']['coordinates'][0][0]


with open(OUTFILE, 'w') as f:
	json.dump(my_bladindex, f)
