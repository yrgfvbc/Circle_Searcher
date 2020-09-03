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
            #checks if a key was passed in a credentials file or a value
            #if it wasnt - raises an error
            try:
                self.api_key = credentials.api_key
            except(NameError):
                gmaps_logger.debug("Authontication error - No credentials file and no key passed")
                raise
        else:
            self.api_key = key


    #return all places in a circle around the center coordinate with the "radius" radius, optionally only return a single type of place
    def get_places_nearby(self,center = None ,radius = None , type = None, next_page_token = None):
        if not center and not next_page_token:
            return ("Either a coordinate or a next_page_token arg is required")
        elif center and not radius:
            return ("Radius missing")
        params = {"location":center,"radius":radius,"key":self.api_key, "type":type,"pagetoken":next_page_token}
        gmaps_logger.debug("Requesting nearby places - params %s" %params)
        nearby_places = requests.get("https://maps.googleapis.com/maps/api/place/nearbysearch/json",params)
        places_dictionary = nearby_places.json()
        status = places_dictionary["status"]
        if status == "OK" or status == "ZERO_RESULTS":
            ammount_of_places = len(places_dictionary["results"])
            gmaps_logger.debug("Found %i places in circle" % ammount_of_places)
            return places_dictionary
        else:
            status_message = self.handle_status(status)
            return status_message

    #if the request status is not equal to "OK" return a message with the correct error
    def handle_status(self,status):
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




