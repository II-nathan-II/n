import sys; sys.path.insert(0, '/home/user/n/pipeline'); sys.path.insert(0, '/home/user/n/pipeline/dev')
from sheet import sheet
from layers_base import *
from layers_space import *
S = [
 ('planet_cobalt', Composite([SpaceBG(1, 'blue'), Planet('cobalt', 820, atmo=(90,150,255))])),
 ('earth', Composite([SpaceBG(2, 'deep'), Planet('earth', 760, clouds=True)])),
 ('sun', Composite([SpaceBG(3, 'orange', 0.5), Star(560)])),
 ('blackhole', Composite([SpaceBG(4, 'purple', 0.6), BlackHole()])),
 ('galaxy', Composite([SpaceBG(5, 'deep'), Galaxy(size=1000, incl=1.0)])),
 ('web', Composite([Solid((1,1,4)), CosmicWeb(highlight_void=0.8)])),
 ('rain', Composite([CloudLayers('cobalt'), GlassRain()])),
 ('venus', Composite([SpaceBG(6, 'orange', 0.4), Planet('venus', 800, atmo=(255,210,140))])),
 ('venus_surf', Composite([VenusSurface(sun=((150,700),(150,500)), labels=True)])),
 ('vent', Composite([Vent()])),
 ('cloudsea', Composite([CloudSea(), Airship()])),
 ('gw', Composite([SpaceBG(7, 'deep'), GWMerger()])),
]
sheet(S, sys.argv[1])
