import gerrymandering

gerrymander = gerrymandering.Gerrymander(path='PA2018.geojson')
gerrymander.init_districts(9)
gerrymander.loop(10)
gerrymander.start()
