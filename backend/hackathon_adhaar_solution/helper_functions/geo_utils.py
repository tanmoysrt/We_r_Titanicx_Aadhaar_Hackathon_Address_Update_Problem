import requests
from geopy.distance import geodesic

from hackathon_adhaar_solution.settings import GOOGLE_MAPS_API_KEY

# GOOGLE_MAPS_API_KEY = "AIzaSyA-oks9HUwdY5TDmGhAe53PvU_keXGyK7Y"


def get_coordinate_by_address(address):
    url = f"https://maps.googleapis.com/maps/api/geocode/json?key={GOOGLE_MAPS_API_KEY}&address={address}"
    payload = {}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    response_json = response.json()

    try:
        return True, response_json['results'][0]["geometry"]["location"]['lat'], \
               response_json['results'][0]["geometry"]["location"]['lng']
    except:
        return False, "-1", "-1"


# print(get_coordinate_by_address("palitpara taherpur road,ward no 9, birnagar, nadia, west bengal, pincode 741127"))
# print(get_coordinate_by_address("birnagar high school, birnagar, nadia, west bengal"))

def get_distance_between_coordinates_meter(lat1, lon1, lat2, lon2):
    return geodesic((lat1, lon1), (lat2, lon2)).meters
