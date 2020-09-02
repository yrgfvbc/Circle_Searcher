import logger
gmaps_logger = logger.make_logger("gmaps_logger","Gmaps_logger.log")
import requests
try:
    import credentials
except(ModuleNotFoundError):
    gmaps_logger.debug("Wrapper startup - no credentials file")
import logging
import datetime
import json

#wrapper for making requests to the google maps developer api
#can pass the api key in a "credentials.py" file or as a value
class Gmaps():
    def __init__(self, key = None):
        if not key:
            try:
                self.api_key = credentials.api_key
            except(NameError):
                gmaps_logger.debug("Authontication error - No credentials file and no key passed")
                raise
        else:
            self.api_key = key


    #return all places in a circle around the center coordinate withe the "radius" radius, optionally only return a single type of place
    def get_places_nearby(self,center = None ,radius = None , type = None, next_page_token = None):
        if not center and not next_page_token:
            raise ValueError("Either a coordinate or a next_page_token arg is required")
        elif center and not radius:
            raise ValueError("Radius missing")
        params = {"location":center,"radius":radius,"key":self.api_key, "type":type,"pagetoken":next_page_token}
        gmaps_logger.debug("Requesting nearby places - params %s" %params)
        nearby_places = requests.get("https://maps.googleapis.com/maps/api/place/nearbysearch/json",params)
        places_dictionary = nearby_places.json()
        status = places_dictionary["status"]
        if status == "OK" or "ZERO_RESULTS":
            ammount_of_places = len(places_dictionary["results"])
            gmaps_logger.debug("Found %i places in circle" % ammount_of_places)
            return places_dictionary
        else:
            status_message = self.handle_status(status)
            return status_message

    #if the request status is not equal to "OK" return a message with the correct error
    def handle_status(self,status):
        #if status == "ZERO_RESULTS":
        #    status_message = "No places found in circle"
        if status == "OVER_QUERY_LIMIT":
            status_message = "Over query limit"
        elif status == "REQUEST_DENIED ":
            status_message = "Request denied - check key validity"
        elif status == "INVALID_REQUEST":
            status_message = "invalid denied - one or more params missing or invalid"
        elif status == "UNKNOWN_ERROR":
            status_message = "Unknown serverside error - please try again"
        gmaps_logger.debug("Attempted to get places nearby - %s" %status_message)
        return status_message


test = Gmaps()
#test_dict = test.get_places_nearby(center = "32.7796504,35.25440820000001",radius = 1000)
#print(type(test_dict))
#file = open("json_test.txt","a")
#file.write("\n")
#json.dump(test_dict,file)
#file.close()

#test_dict = {"html_attributions": [], "results": [{"business_status": "OPERATIONAL", "geometry": {"location": {"lat": 32.7796504, "lng": 35.25440820000001}, "viewport": {"northeast": {"lat": 32.7810941802915, "lng": 35.2557629302915}, "southwest": {"lat": 32.7783962197085, "lng": 35.2530649697085}}}, "icon": "https://maps.gstatic.com/mapfiles/place_api/icons/civic_building-71.png", "name": "\u05de\u05e7\u05d5\u05e8\u05d5\u05ea", "photos": [{"height": 1960, "html_attributions": ["<a href=\"https://maps.google.com/maps/contrib/106418128719130584870\">Shuki Vigodney</a>"], "photo_reference": "CkQ0AAAAt4qLQGsZ53RsRxuP412YEbuTdSDmvaNsL2laN4ByrCfLFUjDdOLnvpkNEiPxkqjtPmtweO_kptgDmK-MNn_YqxIQJSTdaJu-VnZsQTOp9M69GxoUDyQBkr393FLnY0oVts5y25Uqlkk", "width": 4032}], "place_id": "ChIJ6yeAghFLHBURmFULcvtK_Wo", "plus_code": {"compound_code": "Q7H3+VQ Hanaton, Israel", "global_code": "8G4QQ7H3+VQ"}, "rating": 4, "reference": "ChIJ6yeAghFLHBURmFULcvtK_Wo", "scope": "GOOGLE", "types": ["travel_agency", "point_of_interest", "establishment"], "user_ratings_total": 6, "vicinity": "Israel"}, {"business_status": "OPERATIONAL", "geometry": {"location": {"lat": 32.78572919999999, "lng": 35.2564939}, "viewport": {"northeast": {"lat": 32.78873145000001, "lng": 35.25815208029149}, "southwest": {"lat": 32.78472845, "lng": 35.2554541197085}}}, "icon": "https://maps.gstatic.com/mapfiles/place_api/icons/generic_business-71.png", "name": "\u05ea\u05dc \u05d7\u05e0\u05ea\u05d5\u05df", "photos": [{"height": 1536, "html_attributions": ["<a href=\"https://maps.google.com/maps/contrib/105763963868964852097\">\u05d9\u05d5\u05e1\u05e3 \u05d0\u05d1\u05df \u05db\u05e1\u05e3</a>"], "photo_reference": "CkQ0AAAAY_PP7qdgZzP74xjPi9KmJvo4SoA1rOYQT3a18BfkO3SAmBTCyymxyJN4UYbYqT-RphN_xkAfC2aJk7lFJRVjbRIQz_H_V30X1eaAV_1Re0kpUBoUSOQLKDZj6Gm0F1UCdu9ATVoxSUU", "width": 2048}], "place_id": "ChIJZwwirgdLHBURQGkmvp5mwYA", "plus_code": {"compound_code": "Q7P4+7H Kafr Manda, Israel", "global_code": "8G4QQ7P4+7H"}, "rating": 3.7, "reference": "ChIJZwwirgdLHBURQGkmvp5mwYA", "scope": "GOOGLE", "types": ["point_of_interest", "establishment"], "user_ratings_total": 27, "vicinity": "Israel"}], "status": "OK"}
#for i in test_dict["results"]:
#    print(i["name"])
#file.write(str(x))
#file.close()
#try:
#    mystring.decode('utf-8')
#except UnicodeDecodeError:
#    pass


