#!python3
# coding: utf-8
import dialogs
from math import radians, cos, sin, asin, sqrt
import ui
import socket
import json
import location
from pprint import pprint
import requests as req
from buscreds import API_KEY, APP_ID

OC_API = 'https://api.octranspo1.com/v1.3/'

creds = {
	'appID': APP_ID,
	'apiKey': API_KEY,
	'format': 'JSON',
}


def arrivalsforstop(bus, stop):
	data = {
		**creds,
		'stopNo': stop,
		'routeNo': bus,
	}
	resp = req.post(f'{OC_API}GetNextTripsForStop', data=data)
	d = resp.json()
	return [_arrival(d, i) for i in range(0, 3)]

def routesforstop(stop):
	data = {
		**creds,
		'stopNo': stop,
	}
	resp = req.post(f'{OC_API}GetRouteSummaryForStop', data=data)
	d = resp.json()
	rs = d.get('GetRouteSummaryForStopResult', {}).get('Routes', {}).get('Route', [])
	
	if not isinstance(rs, list):
		rs = [rs]
		
	rs = [(r.get('RouteNo'), r.get('DirectionID'), r.get('Direction'), r.get('RouteHeading')) for r in rs]
	return rs


def _arrival(d, n):
	routes = d.get('GetNextTripsForStopResult', {}).get('Route', {}).get('RouteDirection')
	print(routes)
	if not isinstance(routes, list):
		routes = [routes]
	
	for r in routes:
		trips = r.get('Trips', {})
	
		trip = trips.get('Trip', [{}, {}, {}, {}])
	if not isinstance(trip, list):
		trip = [trip]
	if n > len(trip) - 1:
		return 'N/A'
		
	t = trip[n].get('AdjustedScheduleTime', 'N/A')
	return t
	

def haversine(lat1, lon1, lat2, lon2):
	R = 6372.8
	dLat = radians(lat2 - lat1)
	dLon = radians(lon2 - lon1)
	lat1 = radians(lat1)
	lat2 = radians(lat2)
	a = sin(dLat/2)**2 + cos(lat1)*cos(lat2)*sin(dLon/2)**2
	c = 2*asin(sqrt(a))
	return R * c

location.start_updates()

stops = []
with open('stops.txt', 'r', encoding='utf-8') as f:
	for l in f:
		if l.startswith('#'):
			continue
		l = l.split(',')
		stops.append((l[1], l[2], float(l[4]), float(l[5])))

'''
loc = location.get_location()
lat = loc['latitude']
lon = loc['longitude']

location.stop_updates()

stopsd = [(stop, name.strip('"'), haversine(lat, lon, la, lo)) for stop, name, la, lo in stops]

# sort by dist
stopsd.sort(key=lambda x: x[2])
'''
	

class NearbyStopsViewDataSource:
	def tableview_number_of_rows(self, tableview, section):
		# Return the number of rows in the section
		return 11

	def tableview_cell_for_row(self, tableview, section, row):
		# Create and return a cell for the given section/row
		stop, name, dist = stopsd[row]
		dist = int(dist*1000)
		cell = ui.TableViewCell()
		cell.accessory_type = 'disclosure_indicator'
		cell.text_label.text = f'{name} ({dist}m)'
		return cell


class NearbyStopsDelegate:
	curstop = None
	def tableview_did_select(self, tableview, section, row):
		nav.push_view(vs)
		curstop = stopsd[row]
		stop, name, dist = curstop
		nav.navigation_bar_hidden = False
		buses.data_source = StopBusesViewDataSource(stop=curstop)


class StopBusesViewDataSource:
	def __init__(self, *args, **kwargs):
		self.stop = kwargs.pop('stop')
		num, name, dist = self.stop
		self.num = num
		stopsubtitle.text = name
		self.routes = routesforstop(num)
		self.routes.sort(key=lambda x: int(x[0]))
		super().__init__(*args, **kwargs)

	def tableview_number_of_rows(self, tableview, section):
		# Return the number of rows in the section
		return len(self.routes)

	def tableview_cell_for_row(self, tableview, section, row):
		bus, did, dir, head = self.routes[row]
		cell = ui.TableViewCell()
		cell.accessory_type = 'disclosure_indicator'
		cell.text_label.text = f'{bus}-{head}'
		return cell
		
def load_arrivals(r=None, s=[]):
	# lol
	if r is not None:
		s.append(r)
	else:
		r = s[-1]
	ds = buses.data_source
	bus, _, _, h = ds.routes[r]
	arrivals.data_source = ArrivalsViewDataSource(bus=(bus, h, ds.num))
	arrivals.reload_data()

class StopBusesDelegate:
	def tableview_did_select(self, tableview, section, row):
		nav.push_view(va)
		load_arrivals(r=row)


class ArrivalsViewDataSource:
	def __init__(self, *args, **kwargs):
		bus, header, stop = kwargs.pop('bus')
		self.arrivals = arrivalsforstop(bus, stop)
		super().__init__(*args, **kwargs)

	def tableview_number_of_rows(self, tableview, section):
		# Return the number of rows in the section
		return len(self.arrivals)

	def tableview_cell_for_row(self, tableview, section, row):
		t = self.arrivals[row]
		from datetime import datetime, timedelta
		import time
		if t != 'N/A':
			t = int(t)
			eta = datetime.now() + timedelta(minutes=t)
			eta = eta.strftime('%H:%M:%S')
		else:
			eta = ''
		cell = ui.TableViewCell()
		cell.text_label.text = f'⏱ {t} mins ({eta})'
		return cell


def btn_refresh_click(e):
	load_arrivals()
	
		
	
vn = ui.load_view('app')
nearby = vn['tableNearby']
nearby.scroll_enabled = False
nearby.data_source = NearbyStopsViewDataSource()
nearby.delegate = NearbyStopsDelegate()

vs = ui.load_view('stop')
stopsubtitle = vs['labelSubtitle']
stopsubtitle.text = ''
buses = vs['tableBuses']
buses.scroll_enabled = False
buses.delegate = StopBusesDelegate()
# buses.data_source = StopBusesViewDataSource()


va = ui.load_view('arrivals')
arrivals = va['tableArrivals']
arrivals.scroll_enabled = False

nav = ui.NavigationView(vn)
nav.navigation_bar_hidden = True


loc = location.get_location()
lat = loc['latitude']
lon = loc['longitude']

location.stop_updates()

stopsd = [(stop, name.strip('"'), haversine(lat, lon, la, lo)) for stop, name, la, lo in stops]

# sort by dist
stopsd.sort(key=lambda x: x[2])


nav.present('portrait')


# vn.present(orientations=['portrait'])


