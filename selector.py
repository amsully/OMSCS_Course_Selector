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

	def convert_to_courses(self, course_numbers, course_index_to_number):
		courses = []
		for cn in course_numbers:
			try:
				if cn in self.course_CRS:
					courses.append(cn)
				elif int(cn) < len(self.course_CRS):
					c_num = course_index_to_number[int(cn)]
					courses.append(c_num)
				else:
					raise(ValueError)
			except ValueError:
				print("Invalid course: " + str(cn) + ". Will not include in selection.")

		return courses


	def prompt_course_input(self, course_index):

		course_numbers = []
		user_happy = False
		while not user_happy:
			print ("What courses do you want to select from? Use course numbers or first column numbers. Space to separate (eg.: 6035 2 3 8803-BDHI 8803-GA). (Nothing: All)")
			course_numbers = parse_input(input())

			selected_courses = self.convert_to_courses(course_numbers, course_index)

			print("You selected: ")
			for course in selected_courses:
				print(course + " " + self.course_CRS[course]["name"])
			
			user_happy = prompt_correct()

		self.user_selection.courses = course_numbers

	def course_selection(self):

		courses = self.api_get("CRS")

		i = 0
		course_index = [] # used for easier selection

		for course in courses:
			course_index.append(course)
			print(str(i) + ": " + course + " " + courses[course]["name"])
			i+=1

		self.prompt_course_input(course_index)

	def metric_selection(self):
		return 0

	def run(self):
		selector = Selector()

		p.print_break()
		print ("Feel free to contribute at: https://github.com/amsully/OMSCS_Course_Selector")
		print ("All data is pulled from here: https://omscentral.com/")
		p.print_break()

		self.course_selection()

		p.print_break()
		self.metric_selection()
