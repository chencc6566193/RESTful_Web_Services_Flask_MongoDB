Implement an API endpoint that returns a filtered set of listings from the .csv data provided:

data example:

id,street,status,price,bedrooms,bathrooms,sq_ft,lat,lng
0,545 2nd Pl,pending,299727,4,1,1608,33.36944420834164,-112.11971469843907
1,320 Blake St,active,123081,5,3,3125,33.476759305937215,-112.11512153436901
2,740 2nd Pl,pending,172219,5,2,1208,33.468811357715914,-112.22879647183072

API:
GET /listings?min_price=100000&max_price=200000&min_bed=2&max_bed=2&min_bath=2&max_bath=2

min_price: The minimum listing price in dollars.
max_price: The maximum listing price in dollars.
min_bed: The minimum number of bedrooms.
max_bed: The maximum number of bedrooms.
min_bath: The minimum number of bathrooms.
max_bath: The maximum number of bathrooms.

The expected response is a GeoJSON FeatureCollection of listings:

{
 "type": "FeatureCollection",
 "features": [
   {
     "type": "Feature",
     "geometry": {"type": "Point", "coordinates": [-112.1,33.4]},
     "properties": {
 "id": "123ABC", # CSV id
 "price": 200000, # Price in Dollars
 "street": "123 Walnut St",
       "bedrooms": 3, # Bedrooms
       "bathrooms": 2, # Bathrooms
       "sq_ft": 1500 # Square Footage
   },
   ...
 ]
}

This implementation also provide: Pagination via web linking (http://tools.ietf.org/html/rfc5988)

