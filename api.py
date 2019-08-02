import requests as req
from buscreds import API_KEY, APP_ID


OC_API = 'https://api.octranspo1.com/v1.3/'


creds = {
	'appID': APP_ID,
	'apiKey': API_KEY,
	'format': 'JSON',
}


def _arrival(d, n):
	routes = d.get('GetNextTripsForStopResult', {}).get('Route', {}).get('RouteDirection')
	if not isinstance(routes, list):
		routes = [routes]
	
	for r in routes:
		trips = r.get('Trips', {})
		# TODO this is bug but works
		trip = trips.get('Trip', [{}, {}, {}, {}])
	if not isinstance(trip, list):
		trip = [trip]
	if n > len(trip) - 1:
		return 'N/A'
		
	t = trip[n].get('AdjustedScheduleTime', 'N/A')
	return t


def baas(bus, stop):
	# bus arrivals at stop
	# Get the 3 nearest arrival times for bus at stop
	data = {
		**creds,
		'stopNo': stop,
		'routeNo': bus,
	}
	resp = req.post(f'{OC_API}GetNextTripsForStop', data=data)
	d = resp.json()
	return [_arrival(d, i) for i in range(0, 3)]
	
	
	
def rfs(stop):
	# routes for stop
	data = { **creds, 'stopNo': stop, }
	resp = req.post(f'{OC_API}GetRouteSummaryForStop', data=data)
	d = resp.json()
	rs = d.get('GetRouteSummaryForStopResult', {}).get('Routes', {}).get('Route', [])
	
	if not isinstance(rs, list):
		rs = [rs]
		
	rs = [(r.get('RouteNo'), r.get('DirectionID'), r.get('Direction'), r.get('RouteHeading')) for r in rs]
	return rs
