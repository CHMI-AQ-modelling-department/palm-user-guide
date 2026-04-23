import geopandas as gpd
from shapely.geometry import box

# Define extent: 512x512 (parent domain)
grid_size = 512
dx = dy = 4  # grid spacing in meters

x_center = 459220.0
y_center = 5546850.0  

extent_half = (grid_size * dx) / 2  # 1024.0

xmin = x_center - extent_half  # 458196.0
xmax = x_center + extent_half  # 460244.0
ymin = y_center - extent_half  # 5545826.0
ymax = y_center + extent_half  # 5547874.0

geometry = box(xmin, ymin, xmax, ymax)

# Create GeoDataFrame with empty placeholder values
gdf = gpd.GeoDataFrame({
    'URAU_CODE': [''],     # String (max length 8)
    'FIRST_URAU': [''],    # String (max length 80)
    'FIRST_CNTR': [''],    # String (max length 2)
    'SUM_POPL_2': [0.0],   # Float
    'geometry': [geometry]
}, crs='EPSG:32633')

# Define schema with field lengths
schema = {
    'geometry': 'Polygon',
    'properties': {
        'URAU_CODE': 'str:8',
        'FIRST_URAU': 'str:80',
        'FIRST_CNTR': 'str:2',
        'SUM_POPL_2': 'float:23.15'
    }
}

# Save to shapefile using Fiona-compatible schema
gdf.to_file('/storage/home/gunes/data/palm/palm_gem/data_acquisition/inputs_praha/src/shp/CZ2025_LEGEROVA_PARENT_512_4.shp', driver='ESRI Shapefile')
