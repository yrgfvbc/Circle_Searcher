import flask
import logger
from flask import request , jsonify
from flask.logging import default_handler
import circle_searcher

# Configure the api servers logging to be named 'werkzeug' so i can log to a file
# This is needed because flask's default logger (app.logger) uses the 'werkzeug' logger with the logger name
api_logger = logger.make_logger('werkzeug',display_name="api_server")

# A class for raising an exception for invalid paramaters
class InvalidParamaters(Exception):
    status_code = 400

    def __init__(self, message, status_code = None):
        self.message = message

        if not status_code == None:
            self.status_code = status_code

        app.logger.debug("error - %s" %self.message + "statuscode = %s"%self.status_code)

    def error_message(self):
        payload = {"error":
                       {"status code": self.status_code,
                        "error_message": self.message}
                   }
        return payload

app = flask.Flask(__name__)
app.logger.removeHandler(default_handler)
app.logger = api_logger

# Checks if coordinate_list is valid - all items in list are pairs of numbers seperated by a ","
# Also checks if the coordinates are in range
def check_list_validity(coordinate_list):
    validity = True

    for coordinate in coordinate_list:
        message = None
        lat_lon = coordinate.split(",")

        if len(lat_lon) == 2:
            lat = lat_lon[0]
            lon = lat_lon[1]

            try:
                lat = float(lat)
                lon = float(lon)

                if not(-90 <= lat <= 90 and -180 <= lon <= 180):
                    message = "Coordinate out of range - lat must be between -90 ~ 90, lon must be between -180 ~ 180"
                    validity = False

            except ValueError:
                message = "invalid coordinate"
                validity = False

        else:
            message = "list not in format"
            validity = False

    return validity, message

# Add error handler to api server that handles my custom error
@app.errorhandler(InvalidParamaters)
def handle_invalid_paramaters(error):
    response_message = jsonify(error.error_message())
    return response_message, error.status_code

@app.route('/', methods=['GET'])
def home():
    return '''<h1>circle searcher Api</h1>
<p>Returns a list of places inside the circles you choose.</p>'''

@app.route('/api/circlesearcher', methods=['GET'])
def circlesearcher_api():

    # Check if coordinate_list or radius exist
    # If they do, check validity
    # If invalid - return errors accordingly
    if "coordinate_list" in request.args and "radius" in request.args:
        api_logger.debug("recieved request - coordinate_list - %s , radius - %s"%(request.args["coordinate_list"],request.args["radius"]))
        coordinate_list = request.args["coordinate_list"].split("/")
        radius = request.args["radius"]
        # Check if radius is valid
        try:
            radius = float(radius)
            if radius < 0:
                error_message = "Invalid radius - radius must be positive"
                raise InvalidParamaters(error_message)
        except ValueError:
            raise InvalidParamaters("Invalid radius - %s"%radius )

        # Check if coordinate list is valid
        list_validity, message = check_list_validity(coordinate_list)
        if list_validity == False:
            raise InvalidParamaters("Invalid coordinates list - %s"%message)
        else:
            try:
                if "gmaps_key" in request.args:
                    key = request.args["gmaps_key"]
                else:
                    key = None
                payload = circle_searcher.circle_searcher(coordinate_list,radius, key)
                return payload

            except ConnectionError as error:
                raise InvalidParamaters(error.args,500)

    # If center or radius missing - check which and return error messege
    else:
        if "radius" in request.args:
            raise InvalidParamaters("Missing coordinate list")
        else:
            raise InvalidParamaters("Missing radius")


# Run server on current public ip address
if __name__ == "__main__":
    app.run(host= '0.0.0.0')
