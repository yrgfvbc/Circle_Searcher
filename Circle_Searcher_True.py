import Gmaps
import logger
import time
import json

circle_logger = logger.make_logger("circle_logger","Circle_logger.log")

class Circle():
    def __init__(self,center,radius,type = None):
        self.center = center
        self.radius = radius
        self.type = type
        self.Gmaps = Gmaps.Gmaps()
        self.my_places = self.find_all_places_in_circle()
        self.ammount_of_places = len(self.my_places["results"])
        circle_logger.debug("Found %i places arround %s at radius %s" %(self.ammount_of_places, self.center, self.radius))

    def find_all_places_in_circle(self):
        my_places = self.Gmaps.get_places_nearby(center = self.center,radius = self.radius,type = self.type)
        circle_logger.debug("Finding all places in circle around %s in radius %s" %(self.center,self.radius))
        if not isinstance(my_places, dict):
            raise(ValueError("Gmaps error - %s" %my_places))
        #maps api's nearby places function only returns up to 20 places in one request, but returns a "next page token" value if more than 20 places exist
        #This function will check if such a value exists and if so take the new results and append them to the dictionary
        #either way - the maximum ammount of places the api can return is 60 total
        #code is written to work even for more than 3 pages
        my_places = self.fetch_next_page(my_places)

        return my_places
        
    #recursivly checks if a next page token exists, if so appends the results of the next page to the first page results list
    def fetch_next_page(self,page):
       #print(page)
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
                self.all_circle_dictionary[center] = current_circle.my_places
        return self.all_circle_dictionary

#test = Circle_Searcher(["32.7796504,35.25440820000001","32.7796503,35.25440820000001", "37.7796504,35.25440820000001"],300)
test = Circle_Searcher(["32.7796504,35.25440820000001"],300)
#test_dictionary = {"1":"1","2":"2"}
#circle_logger.debug("test - {0}".format(test_dictionary,format('utf-8')))
#print(test.all_circle_dictionary)
#print(test.find_all_places_in_circle())
#gmaps_test = Gmaps.Gmaps()

