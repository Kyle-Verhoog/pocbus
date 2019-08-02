#!python3
# coding: utf-8

import ui
import location
import time

import api
import lib


stops = []
with open('stops.txt', 'r', encoding='utf-8') as f:
	for l in f:
		if l.startswith('#'):
			continue
		l = l.split(',')
		stops.append((l[1], l[2], float(l[4]), float(l[5])))


class NearbyStopsViewDataSource:
	def tableview_number_of_rows(self, tableview, section):
		return 11

	def tableview_cell_for_row(self, tableview, section, row):
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
		self.routes = api.rfs(num)
		self.routes.sort(key=lambda x: int(x[0]))
		super().__init__(*args, **kwargs)

	def tableview_number_of_rows(self, tableview, section):
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
		b, h, s = kwargs.pop('bus')
		self.arrivals = api.baas(b, s)
		super().__init__(*args, **kwargs)

	def tableview_number_of_rows(self, tableview, section):
		return len(self.arrivals)

	def tableview_cell_for_row(self, tableview, section, row):
		t = self.arrivals[row]
		from datetime import datetime, timedelta
		import time
		if t != 'N/A':
			t = int(t)
			eta = datetime.now() + timedelta(minutes=t)
			eta = eta.strftime('(%H:%M:%S)')
		else:
			eta = ''
		cell = ui.TableViewCell()
		cell.text_label.text = f'⏱ {t} mins {eta}'
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

va = ui.load_view('arrivals')
arrivals = va['tableArrivals']
arrivals.scroll_enabled = False

nav = ui.NavigationView(vn)
nav.navigation_bar_hidden = True


location.start_updates()
time.sleep(0.5)
loc = location.get_location()
lat = loc['latitude']
lon = loc['longitude']
location.stop_updates()

stopsd = [(stop, name.strip('"'), lib.haversine(lat, lon, la, lo)) for stop, name, la, lo in stops]

# sort by dist
stopsd.sort(key=lambda x: x[2])


nav.present('portrait')
