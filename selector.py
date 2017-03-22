import printer as p
import api_connector as api
import textwrap
from util import *

class UserSelection:
	def __init__(self, name="UserSelection"):
		self.courses = [] # Empty == All Courses
		self.metrics = [] # Empty == All metrics
		self.weights = [] # Weights of each metrics (sums to 1)

class Selector:

	def __init__(self, name="MainSelector"):
		self.api = api.APIConnector()
		self.name = name
		self.course_CRS = None
		self.course_AGG = None
		self.course_GRD = None
		self.user_selection = UserSelection()

	def api_get(self, name):
		if(self.course_CRS == None):
			self.course_CRS = self.api.get("CRS")

		return self.course_CRS

	def prompt_course_input(self):

		course_numbers = []
		user_happy = False
		while not user_happy:
			print ("What courses do you want to select from? Use space to separate (eg.: 321 123 320) (Nothing: All)")
			course_numbers = parse_input(input())

			print("You selected: " + str(course_numbers))
			user_happy = prompt_correct()

		self.user_selection.courses = course_numbers

	def course_selection(self):

		courses = self.api_get("CRS")
		courses = " ".join(list(courses.keys()))
		textwrap.wrap(courses)
		
		print(courses)

		self.prompt_course_input()


	def run(self):
		selector = Selector()

		p.print_break()
		print ("Feel free to contribute at: https://github.com/amsully/OMSCS_Course_Selector")
		print ("All data is pulled from here: https://omscentral.com/")
		p.print_break()

		self.course_selection()
