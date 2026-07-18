


import ee
import geemap
import config

# Initialize Earth Engine
try:
    ee.Initialize()
except Exception:
    ee.Authenticate()
    ee.Initialize()

def add_metrics(feature):
    """Calculates feature geometry metrics and elevation."""
    geom = feature.geometry()
    # Get bounding box coordinates
    bounds = geom.bounds().coordinates().get(0)
    xs = ee.List(bounds).map(lambda pt: ee.List(pt).get(0))
    ys = ee.List(bounds).map(lambda pt: ee.List(pt).get(1))
    
    # Calculate dimensions
    min_x, max_x = ee.Number(xs.reduce(ee.Reducer.min())), ee.Number(xs.reduce(ee.Reducer.max()))
    min_y, max_y = ee.Number(ys.reduce(ee.Reducer.min())), ee.Number(ys.reduce(ee.Reducer.max()))
    
    width_m = ee.Geometry.Point([min_x, min_y]).distance(ee.Geometry.Point([max_x, min_y]))
    length_m = ee.Geometry.Point([min_x, min_y]).distance(ee.Geometry.Point([min_x, max_y]))
    
    # Get elevation from SRTM
    dem = ee.Image("USGS/SRTMGL1_003")
    elevation = dem.reduceRegion(ee.Reducer.mean(), geom.centroid(10), 30, bestEffort=True).get('elevation')
    
    return feature.set({
        'length_m': length_m.max(width_m), 
        'width_m': length_m.min(width_m),
        'elevation': ee.Algorithms.If(elevation, elevation, 0)
    })

# 1. Define Area of Interest
kenai_aoi = ee.Geometry.Rectangle(config.AOI)

# 2. Get Sentinel-2 Data
s2 = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED") \
    .filterBounds(kenai_aoi) \
    .filterDate('2025-06-01', '2025-09-01') \
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 10)) \
    .median() \
    .clip(kenai_aoi)

# 3. Process Water Mask
water_mask = s2.normalizedDifference(['B3', 'B8']).gt(0.2)
lake_vectors = water_mask.selfMask().reduceToVectors(
    geometry=kenai_aoi, crs=s2.projection(), scale=30, geometryType='polygon', eightConnected=False
)

# 4. Filter by Pilot Criteria (using config)
navigable_water = lake_vectors.map(add_metrics) \
    .filter(ee.Filter.gt('length_m', config.MIN_LENGTH)) \
    .filter(ee.Filter.gt('width_m', config.MIN_WIDTH)) \
    .filter(ee.Filter.lt('elevation', config.MAX_ELEVATION))

# 5. Visualize
# 5. Visualize
m = geemap.Map()
m.centerObject(kenai_aoi, 9)

# Add a hybrid satellite basemap for context
m.add_basemap('HYBRID')

# Draw the features with transparency so you can see the terrain
style = {'color': '00FFFF', 'fillColor': '00FFFF33', 'width': 2}
m.addLayer(navigable_water.style(**style), {}, 'Floatplane Accessible Lakes')

# Save the map as an interactive page
output_map = "kenai_water_map.html"
# Quick & dirty export
geemap.ee_export_vector(navigable_water, filename="kenai_lakes_log.csv")
m.save(output_map)
print(f"\n[Success] Analysis complete. Found {navigable_water.size().getInfo()} navigable lakes.")
print(f"[Map] Interactive map saved to: {output_map}")

# 6. Extract the Data Table to print the list
print("\nRetrieving flight logs from Google Earth Engine...")
lake_features = navigable_water.getInfo()['features']

# Print a structured text list directly in the terminal
print("\n" + "="*60)
print(f"{'LAKE ID':<10} | {'LENGTH (m)':<12} | {'WIDTH (m)':<12} | {'ELEVATION (m)':<12}")
print("="*60)

for idx, feat in enumerate(lake_features):
    props = feat['properties']
    print(f"{idx+1:<10} | {int(props['length_m']):<12} | {int(props['width_m']):<12} | {int(props['elevation']):<12}")

print("="*60)
print(f"Total Logged Landable Zones: {len(lake_features)}")


# *** do this to display map 
# Save the map as an HTML file and open it automatically
output_file = "kenai_water_map.html"
m.save(output_file)
print(f"Map saved to {output_file}. Opening in browser...")

# Optional: Automatically open the file in your default web browser
import webbrowser
import os
webbrowser.open('file://' + os.path.realpath(output_file))