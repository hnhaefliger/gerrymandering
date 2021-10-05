import data
import map
import json

#geojson = data.get_state_geojson('pa')

with open('PA2018.geojson', 'r') as f:
    geojson = json.loads(f.read())

data = data.process_geojson(geojson)

display = map.Map(data, width=1700, height=800)
display.set_precinct('Warren County, cherry grove', 'red')
display.mainloop()
