from kivy.base import runTouchApp
from kivy.lang import Builder
from kivy.graphics import Color, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image


if __name__ == '__main__' and __package__ is None:
	from os import sys, path

	sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

	root = Builder.load_string(
	"""
#:import MapSource kivy_garden.mapview.MapSource

<Toolbar@BoxLayout>:
	size_hint_y: None
	height: '48dp'
	padding: '4dp'
	spacing: '4dp'

	canvas:
		Color:
			rgba: .2, .2, .2, .6
		Rectangle:
			pos: self.pos
			size: self.size

<ShadedLabel@Label>:
	size: self.texture_size
	canvas.before:
		Color:
			rgba: .2, .2, .2, .6
		Rectangle:
			pos: self.pos
			size: self.size


MapView:
	id: mapview
	lat: 50.6394
	lon: 3.057
	zoom: 8
	
	
	Image:
		id: pic1
	
		canvas:
			Color:
				rgba: 1, 1, 0.5, 1
	
	
	Toolbar:
		Button:
			text: "France"
			on_release: mapview.center_on(50.6394, 3.057)
		Button:
			text: "Australia"
			on_release: mapview.center_on(-33.867, 151.206)
		Spinner:
			text: "mapnik"
			values: MapSource.providers.keys()
			on_text: mapview.map_source = self.text
	
	Toolbar:
		Label:
			text: "Lon: {}".format(mapview.lon)
		Label:
			text: "Lat: {}".format(mapview.lat)
		
	"""
	)

# Create a list to store image objects
images = []

# Create a function to update the canvas with images
def update_canvas(x):
	# Clear the canvas
	x.canvas.clear()

	#for img in images:
	#	pics.canvas.add(Color(1, 1, 1))
	#	pics.canvas.add(Rectangle(pos=img.pos, size=img.size, source=img.source))

def on_map_relocated(obj, pos, zoom):
	print((obj, pos, zoom))
	# Add an image at the new map location
	images.append(Image(source='/home/koom/Downloads/wallpapertip_vector-wallpaper_159196.jpg', pos=(0,0), size=(100, 100)))
	# Update the canvas to draw the new images
	update_canvas(root.ids.pic1)



root.bind(on_map_relocated=on_map_relocated)

runTouchApp(root)
