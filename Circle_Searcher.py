import Gmaps
import logger
import time
import json

circle_logger = logger.make_logger("circle_logger","Circle_logger.log")

#add types if u finish!
class Circle():
    def __init__(self,center,radius,type = None):
        self.center = center
        self.radius = radius
        self.type = type

        #try to create a gmaps object - if failed raise a value error

        try:
            self.Gmaps = Gmaps.Gmaps()
        except(NameError):
            raise(ValueError("Gmaps authentication error - no key or credentials file"))

        #attempt to find all places in circle

        self.my_places = self.find_all_places_in_circle()
        #self.my_places = self.my_places["results"]

        #if function returns string - return the error

        if isinstance(self.my_places, dict):
            self.ammount_of_places = len(self.my_places["results"])
            circle_logger.debug("Found %i places arround %s at radius %s" %(self.ammount_of_places, self.center, self.radius))
        else:
            circle_logger.debug(self.my_places)

    #finds all places in a cirlce and return a dictionary with results
    def find_all_places_in_circle(self):
        my_places = self.Gmaps.get_places_nearby(center = self.center,radius = self.radius,type = self.type)
        circle_logger.debug("Finding all places in circle around %s in radius %s" %(self.center,self.radius))
        if not isinstance(my_places, dict):
            return("Gmaps error - %s" %my_places)
        #maps api's nearby places function only returns up to 20 places in one request, but returns a "next page token" value if more than 20 places exist
        #This function will check if such a value exists and if so take the new results and append them to the dictionary
        #either way - the maximum ammount of places the api can return is 60 total
        #code is written to work even for more than 3 pages
        my_places = self.fetch_next_page(my_places)

        return my_places
        
    #recursivly checks if a next page token exists, if so appends the results of the next page to the first page results list
    def fetch_next_page(self,page):
        if "next_page_token" in page:
            page_token = page.pop("next_page_token")
            time.sleep(2) #maps api takes a bit of time to create the page with the token so we have to wait a bit before accesing it
            next_page = self.Gmaps.get_places_nearby(next_page_token=page_token)
            circle_logger.debug("Looking at next page at token %s" % page_token)
            self.fetch_next_page(next_page)
            page["results"].extend(next_page["results"])
        return page

#checks all circles and their respective places
class Circle_Searcher():
    def __init__(self,coordinate_list,radius):
        self.coordinate_list = coordinate_list
        self.circle_radius = radius
        self.all_circle_dictionary = {}
        circle_logger.debug("Finding all places in circles arround %s at radius %s" % (self.coordinate_list, self.circle_radius))
        self.check_all_circles()

    #goes through the coordinate list and checks what places are around each coordinate in the radius range
    #puts all
    def check_all_circles(self):
        for center in self.coordinate_list:
            if not center in self.all_circle_dictionary: #checks if the coordinate was already checked - if so doesnt check it to reduce runtime
                current_circle = Circle(center,self.circle_radius,type = type)
                #save the results in a master dictionary in the following format - coordinate : results, discarding all other info in the payload
                self.all_circle_dictionary[center] = current_circle.my_places["results"]
        return self.all_circle_dictionary

