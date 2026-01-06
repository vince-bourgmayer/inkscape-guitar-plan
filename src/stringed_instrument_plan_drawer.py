# -----------------------------------------------------------------------------
# stringed_instrument_plan_drawer.py
# Copyright (c) 2025-2026 Vincent Bourgmayer
# License: GNU GPL V3
# -----------------------------------------------------------------------------

# conversion constant
inch_to_mm = 25.4

# to use or not to use..
class Point:
	def __init__(self, x, y):
		self.x = x
		self.y = y

class Nut:
	def __init__(self, start_point, length, width, bass_margin, treble_margin):
		self.start_point = start_point
		self.length = length
		self.width = width
		self.bass_margin = bass_margin
		self.treble_margin = treble_margin
		self.drawing = None

	def draw(self):
		print("Drawing nut...")
		A = (self.start_point.x, self.start_point.y)
		B = (self.start_point.x + self.width, self.start_point.y)
		C = (self.start_point.x, self.start_point.y + self.length)
		D = (self.start_point.x + self.width, self.start_point.y + self.length)

		fretboard_edge = line(A, C).to_path()
		head_edge = line(B, D).to_path()
		bass_edge = line(A, B).to_path()
		treble_edge = line(C, D).to_path()

		self.drawing = apply_path_operation('combine', [fretboard_edge, head_edge, bass_edge, treble_edge])


class Bridge:
	def __init__(self, start_point, string_spread):
		self.start_point = start_point
		self.string_spread = string_spread
		self.drawing = None

	def draw(self):
		print("Drawing bridge center line...")
		self.drawing = line((self.start_point.x, self.start_point.y), (self.start_point.x, self.start_point.y + self.string_spread)).to_path()

class Scale:
	def __init__(self, length, x, y):
		self.length = length
		self.x = x
		self.y = y
		self.drawing = None

	def draw(self):
		print("Drawing scale...")
		scale_length = line((self.x, self.y), (self.x+self.length, self.y)).to_path()
		scale_rear = line((self.x, self.y-25), (self.x, self.y+25)).to_path()
		scale_nut = line((self.x+self.length, self.y-25), (self.x+self.length, self.y+25)).to_path()
		self.drawing = apply_path_operation('combine', [scale_length, scale_rear, scale_nut])


class Fretboard:
	def __init__(self, nut, bridge, frets_count):
		self.bass_margin = nut.bass_margin
		self.treble_margin = nut.treble_margin
		self.nut_length = nut.length
		self.bridge_string_spread = bridge.string_spread
		self.drawing = None
		self.frets = group()
		self.frets_count = frets_count

	def draw(self, scale):
		print("Drawng fretboard...")
		bridge_spread = line((scale.x, scale.y-self.bridge_string_spread/2), (scale.x, scale.y+self.bridge_string_spread/2)).to_path()
		nut_x = scale.x + scale.length
		half_nut_length = self.nut_length/2
		half_brige_spread = self.bridge_string_spread/2

		nut_length_line = line((nut_x, scale.y-half_nut_length), (nut_x, scale.y+half_nut_length)).to_path()

		bass_margin = line((scale.x, scale.y- half_brige_spread- self.bass_margin), (scale.x, scale.y-half_brige_spread)).to_path()
		treble_margin = line((scale.x, scale.y+half_brige_spread + self.treble_margin), (scale.x, scale.y+half_brige_spread)).to_path()
		low_edge = line((scale.x, scale.y-half_brige_spread-self.bass_margin), (nut_x, scale.y-half_nut_length)).to_path()
		high_edge = line((scale.x, scale.y+half_brige_spread+self.treble_margin), (nut_x, scale.y+half_nut_length)).to_path()

		self.drawing = apply_path_operation('combine', [bridge_spread, bass_margin, treble_margin, nut_length_line, low_edge, high_edge])

	def draw_frets(self, scale):
		print("Drawing frets...")
		for position in self.compute_frets_pos_from_nut(scale.length):
			fret_pos = scale.x+scale.length - position
			fret = line((fret_pos, scale.y-20), (fret_pos, scale.y+20))
			self.frets.append(fret)

	# could decline this method to let use other calculation like rules of 18, etc.
	def compute_frets_pos_from_nut(self, scale_length):
		frets_dist_from_nut=[]
		for i in range(1, self.frets_count):
			# Formula from https://ghettoluthier.blogspot.com/2013/07/guitar-fret-position-calculator.html
			frets_dist_from_nut.append(round(scale_length-(scale_length/pow(2, i/12)), 2))
		return frets_dist_from_nut


class Strings:
	# You need to provide gauge from thinnest to thickest
	def __init__(self, strings_gauge):
		self.strings_gauge_in_mm = []
		self.string_count = len(string_gauge)
		self.strings = group()
		for gauge in strings_gauge[::-1]:
			self.strings_gauge_in_mm.append(self.gauge_to_mm(gauge))
		print(self.strings_gauge_in_mm)

	# Convert string gauge printed on package to mm (e.g  13 => 0.013 => 0.3302)
	def gauge_to_mm(self, gauge):
		print(gauge)
		return round((gauge/1000 * inch_to_mm), 4)
	
	# method from "Build your Own electric guitars" of Martin Oakham
	# from what I understand, the idea is to get the dividable length of the nut:
	# so you need to remove all the string thickness & margin from the nut length 
	# then just divide by string count -1
	def compute_MN_nut_formula(self, nut_length, bass_margin, treble_margin):
		margin_and_strings_gauge = (bass_margin + treble_margin) + sum(self.strings_gauge_in_mm) 
		free_surface = nut_length - margin_and_strings_gauge
		return free_surface / (self.string_count -1)

	def compute_MN_bridge_formula(self, string_spread):
		print("string count: " + str(len(self.strings_gauge_in_mm)))
		strings_thickness = sum(self.strings_gauge_in_mm) - (self.strings_gauge_in_mm[0]+ self.strings_gauge_in_mm[self.string_count-1])/2
		return (string_spread - strings_thickness) / (self.string_count -1)

	# center of a given string is equal to bass margin + for each of thicker string: (string thickness + MN formula) + half thickness of the given string 
	# String index start at 0!
	def get_string_pos_at_nut(self, nut_y, bass_margin, string_index, mn):
		start_point = nut_y + bass_margin
		previous_strings_thickness = sum(self.strings_gauge_in_mm[:string_index])
		mn_sum = string_index * mn
		half_string = self.strings_gauge_in_mm[string_index]/2
		
		return round((start_point + previous_strings_thickness + mn_sum + half_string), 4)


	def get_string_pos_at_bridge(self, bridge_y, string_index, mn):
		if (string_index == 0):
			return bridge_y

		previous_strings_thickness = sum(self.strings_gauge_in_mm[1:string_index]) + self.strings_gauge_in_mm[0]/2
		mn_sum = string_index * mn
		half_string = self.strings_gauge_in_mm[string_index]/2

		return round(bridge_y + previous_strings_thickness + mn_sum + half_string, 4)
		
	def draw(self, nut, bridge):
		print("Drawing strings...")
		nut_MN = self.compute_MN_nut_formula(nut.length, nut.bass_margin, nut.treble_margin)

		bridge_MN = self.compute_MN_bridge_formula(bridge.string_spread)

		#print(nut_MN)
		for index, value in enumerate(self.strings_gauge_in_mm):
			string_end_point = Point(nut.start_point.x, self.get_string_pos_at_nut(nut.start_point.y, nut.bass_margin, index, nut_MN))
			print("String gauge(mm): "+ str(value) + ", x: " + str(string_end_point.x) + ", y: " + str(string_end_point.y))

			# start_point = Point(bridge.start_point.x, self.get_string_pos_at_nut(bridge.start_point.y, 0, index, bridge_MN))
			start_point = Point(bridge.start_point.x, self.get_string_pos_at_bridge(bridge.start_point.y, index, bridge_MN))
			string = line((start_point.x, start_point.y), (string_end_point.x, string_end_point.y), stroke='#FF0000', stroke_width=value).to_path()
			self.strings.append(string)



# General inputs
symetric_y = 200 #value represent position on y axis
bridge_x = 215

# guitar's value
# /!\ Update to fit you own requirement

scale_length = 25.5*inch_to_mm
bridge_string_spread = 51.5
fingerboard_bass_margin = 4
fingerboard_treble_margin = 4
nut_length = 44.45 #with margin integrated

string_gauge = (10, 13, 17, 30, 42, 52)

#string_gauge = (10, 13, 17, 26, 36, 46)
#nut_length = 41 #with set_back integrated
#nut = Nut(Point(0, 0), nut_length, 5, fingerboard_bass_margin, fingerboard_treble_margin)


# Drawing part
# Here: just comment the "*.draw()" of what you don't want to be drawn
style(stroke_width=0.1)
symetric_axis = line((0, symetric_y),(1000,symetric_y))

nut = Nut(Point(bridge_x+scale_length, symetric_y-nut_length/2), nut_length, 5, fingerboard_bass_margin, fingerboard_treble_margin)
nut.draw()

bridge = Bridge(Point(bridge_x, symetric_y-bridge_string_spread/2), bridge_string_spread)
bridge.draw()

scale = Scale(scale_length, bridge_x, symetric_y)
scale.draw()

fretboard = Fretboard(nut, bridge, 22)
fretboard.draw(scale)
fretboard.draw_frets(scale)

strings = Strings(string_gauge)
strings.draw(nut, bridge)
