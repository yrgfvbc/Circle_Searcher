import gmaps
import logger
import time
import json

circle_logger = logger.make_logger("circle_logger")

#add types if u finish!
class circle():
    def __init__(self,center,radius, gmaps_wrapper, type = None):
        self.center = center
        self.radius = radius
        self.type = type
        self.gmaps = gmaps_wrapper
        #try to create a gmaps object - if failed raise a value error

        #attempt to find all places in circle

        self.my_places = self.find_all_places_in_circle()
        self.ammount_of_places = len(self.my_places["results"])
        circle_logger.debug(
            "Found %i places arround %s at radius %s" % (self.ammount_of_places, self.center, self.radius))
        #self.my_places = self.my_places["results"]

        #if function returns string - return the error

    #finds all places in a cirlce and return a dictionary with results
    def find_all_places_in_circle(self):
        circle_logger.debug("Finding all places in circle around %s in radius %s" %(self.center,self.radius))
        try:
            my_places = self.gmaps.get_places_nearby(center = self.center,radius = self.radius,type = self.type)
        except ValueError or ConnectionError as error:
            error_message = "gmaps error - %s" %error.args
            circle_logger.debug(error_message)
            raise ConnectionError(error_message)
        #Maps api's nearby places function only returns up to 20 places in one request, 
        # but returns a "next page token" value if more than 20 places exist.
        #This function will check if such a value exists and if so take the new results and append them to the dictionary
        #either way - the maximum ammount of places the api can return is 60 total
        #code is written to work even for more than 3 pages
        if "next_page_token" in my_places:
            my_places = self.fetch_next_pages(my_places)
        return my_places
        
    #recursivly checks if a next page token exists, if so appends the results of the next page to the first page results list
    def fetch_next_pages(self,page):
        if "next_page_token" in page:
            page_token = page.pop("next_page_token")
            #Maps api takes a bit of time to create the page with the token so we have to wait a bit before accesing it
            #If retries more than 5 times - timeout
            retries = 0
            while True:
                try:
                    time.sleep(1)
                    next_page = self.gmaps.get_places_nearby(next_page_token=page_token)
                    break
                except (ValueError,ConnectionError) as error:
                    circle_logger.debug("Failed to fetch next page - %s retry %s" %(error.args,retries))
                    retries += 1
                if retries > 5:
                    error_message = ("Timeout - failed to fetch next pages")
                    circle_logger.debug(error_message)
                    raise ConnectionError(error_message)
            circle_logger.debug("Looking at next page at token %s" % page_token)
            self.fetch_next_pages(next_page)
            page["results"].extend(next_page["results"])
        return page

#checks all circles and their respective places
def circle_Searcher(coordinate_list, radius, key = None):
    try:
        gmaps_wrapper = gmaps.gmaps(key)
    except ConnectionError as error:
        raise ConnectionError("Gmaps error - %s" %error.args)
    circle_logger.debug("Finding all places in circles arround %s at radius %s" % (coordinate_list, radius))
    all_circles = check_all_circles(coordinate_list,radius,gmaps_wrapper)
    return all_circles

#goes through the coordinate list and checks what places are around each coordinate in the radius range
#puts all
def check_all_circles(coordinate_list, circle_radius, gmaps_wrapper):
    all_circle_dictionary = {}
    for center in coordinate_list:
        if not center in all_circle_dictionary: #checks if the coordinate was already checked - if so doesnt check it to reduce runtime
            current_circle = circle(center,circle_radius,gmaps_wrapper, type = type)
            #save the results in a master dictionary in the following format - coordinate : results, discarding all other info in the payload
            if not isinstance(current_circle.my_places, dict):
                return "Error - %s" %current_circle
            else:
                all_circle_dictionary[center] = current_circle.my_places["results"]
    return all_circle_dictionary

test = circle_Searcher(["32.058895,34.805781"],300)
#print(test)