#!python3
# coding: utf-8

import appex, ui
import socket
import json
import requests as req
from buscreds import API_KEY, APP_ID

OC_API = 'https://api.octranspo1.com/v1.3/'

creds = {
	'appID': APP_ID,
	'apiKey': API_KEY,
	'format': 'JSON',
}


stop = 8615
data = {
	**creds,
	'stopNo': stop,
	'routeNo': 14,
	'format': 'JSON',
}

resp = req.post(f'{OC_API}GetNextTripsForStop', data=data)
d = resp.json()

arrival1 = d['GetNextTripsForStopResult']['Route']['RouteDirection']['Trips']['Trip'][0]['AdjustedScheduleTime']
arrival2 = d['GetNextTripsForStopResult']['Route']['RouteDirection']['Trips']['Trip'][1]['AdjustedScheduleTime']

	
def add_row(x, y):
	l = ui.Label(frame=(x, y, 320-44-8, 220))
	l.font = ('Menlo', 16)
	l.text = f'Next bus: {arrival1}, {arrival2}'
	v.add_subview(l)

v = ui.View(frame=(0, 0, 320, 220))

add_row(8, -90)
add_row(8, -40)

appex.set_widget_view(v)
# appex.set_widget_view(ui.load_view('widget'))

# ui.load_view('widget').present('sheet')
