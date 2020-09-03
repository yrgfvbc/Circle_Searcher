import flask
import logger
from flask import request, jsonify
import Circle_Searcher
from flask.logging import default_handler

#configure the api servers logging to be named 'werkzeug' to log to a file
#this happens because flask's default logger (app.logger)
api_logger = logger.make_logger('werkzeug',"api_logger.log")

#A class for raising an exception for invalid paramaters

class InvalidParamaters(Exception):
    status_code = 401
    def __init__(self, message, status_code = None):
        self.message = message
        if status_code:
            self.status_code = status_code

    def error_message(self):
        payload = {"error":
                       {"status code": self.status_code,
                        "error_message": self.message}
                   }
        return payload

app = flask.Flask(__name__)
app.logger.removeHandler(default_handler)
app.logger = api_logger
app.logger.debug("test")

#checks if coordinate_list is valid - all items in list are pairs of numbers seperated by a ","
#if have time - will check if coordinate is in range

def check_list_validity(coordinate_list):
    validity = 1
    for coordinate in coordinate_list:
        message = None
        lat_lon = coordinate.split(",")
        if len(lat_lon) == 2:
            lat = lat_lon[0]
            lon = lat_lon[1]
            try:
                lat = float(lat)
                lon = float(lon)
            except(ValueError):
                message = "invalid coordinate"
                validity = 0
                break
        else:
            message = "list not in format"
            validity = 0
    return validity, message


@app.errorhandler(InvalidParamaters)
def handle_invalid_paramaters(error):
    response_message = jsonify(error.error_message())
    return response_message

@app.route('/', methods=['GET'])
def home():
    return '''<h1>Circle searcher Api</h1>
<p>Returns a list of places inside the circles you choose.</p>'''
#https://maps.googleapis.com/maps/api/place/nearbysearch/json

@app.route('/api/circlesearcher', methods=['GET'])
def circlesearcher_api():

    # check if coordinate_list or radius exist
    #if they do, check validity
    #if invalid - return errors acordingly

    if "coordinate_list" in request.args and "radius" in request.args:
        #api_logger.debug("recieved request - coordinate_list - %s , radius - %s"%())
        coordinate_list = request.args["coordinate_list"].split("/")
        radius = request.args["radius"]
        #check if radius is valid
        try:
            radius = float(radius)
            if radius < 0:
                raise(InvalidParamaters("Invalid radius - radius must be positive"))
        except(ValueError):
            raise (InvalidParamaters("Invalid radius - %s"%radius ))
        #check if coordinate list is valid
        list_validity, message = check_list_validity(coordinate_list)
        if not list_validity == 1:
            raise(InvalidParamaters("Invalid coordinates list - %s"%message))
        else:
            try:
                searcher = Circle_Searcher.Circle_Searcher(coordinate_list,radius)
                payload = searcher.all_circle_dictionary
                return payload
            except(ValueError):
                raise InvalidParamaters("Gmaps authentication error - no key or credentials file",403)

    #if center or radius missing - check wich and return error messege
    else:
        if "radius" in request.args:
            raise (InvalidParamaters("Missing coordinate list" ,402))
        else:
            raise (InvalidParamaters("Missing radius" , 402))



app.run(host= '0.0.0.0')
