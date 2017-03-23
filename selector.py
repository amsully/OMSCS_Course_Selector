import printer as p
import api_connector as api
import ranker
import textwrap
import random
from util import *

class UserSelection:
	def __init__(self, name="UserSelection"):
		self.courses = [] # Empty == All Courses
		self.metrics = [] # Empty == All metrics
		self.include_grades = False
		self.weights = [] # Weights of each metrics (sums to 1)

class Selector:

	def __init__(self, name="MainSelector"):
		self.api = api.APIConnector()
		self.name = name
		self.course_CRS = None
		self.course_AGG = None
		self.course_GRD = None
		self.user_selection = UserSelection()
		self.ranker = ranker.Ranker()

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
			print ("What courses do you want to select from? Use course numbers or first column numbers. Space to separate (eg. 6035 2 3 8803-BDHI 8803-GA). (Enter: All)")
			course_numbers = parse_input(input())

			selected_courses = self.convert_to_courses(course_numbers, course_index)

			print("You selected: ")
			if(len(selected_courses) == 0):
				print("All")
				course_numbers = list(self.course_CRS.keys())
			else:
				for course in selected_courses:
					print(course + " " + self.course_CRS[course]["name"])
				
			user_happy = prompt_correct()

		self.user_selection.courses = course_numbers

	def course_selection(self):
		if(self.course_CRS == None):
			self.course_CRS = self.api.get("CRS")

		i = 0
		course_index = [] # used for easier selection

		for course in self.course_CRS:
			course_index.append(course)
			print(str(i) + ": " + course + " " + self.course_CRS[course]["name"])
			i+=1

		self.prompt_course_input(course_index)

	def get_metrics(self):
		if(self.course_AGG == None):
			self.course_AGG = self.api.get("AGG")

		metrics = []

		key = random.choice(list(self.course_AGG.keys()))

		metric_map = self.course_AGG[key]

		return list( metric_map["average"].keys() )

	def prompt_metric_input(self, metrics):
		user_happy = False
		metric_choice = []
		while not user_happy:
			metric_choice = []
			print("What metrics would you like to use as a score? Use numbers separated by spaces to selected (eg. 0 3 4). (Enter: All)")
			metrics_nums = parse_input(input())


			print("You selected:")
			if(len(metrics_nums) == 0 or metrics_nums[0] == ''):
				print("All")
				metric_choice = self.get_metrics()
			else:
				for m_num in metrics_nums:
					try:
						print(m_num + ": " + metrics[int(m_num)])
						metric_choice.append(metrics[int(m_num)])
					except ValueError:
						print(m_num + " is not a valid entry and will not be selected.")

			user_happy = prompt_correct()

		self.user_selection.metrics = metric_choice

	def metric_selection(self):
		metrics = self.get_metrics()

		i = 0
		for metric in metrics:
			print(str(i) + ": " + metric)
			i+=1


		self.prompt_metric_input(metrics)

	def grade_selection(self):
		yes = set(['yes','y', 'ye', ''])
		no = set(['no','n'])

		while(1):
			choice = input("Would you like to include grade information? (Courses with higher average grades score better). [y]/n").lower()

			if choice in no:
				return
			elif choice in yes:
				if(self.course_GRD == None):
					self.course_GRD = self.api.get("GRD")
				self.user_selection.include_grades = True

				return
			else:
				print("Enter yes or no.")

	def weight_selection_metrics_helper(self):
		metrics = self.user_selection.metrics

		if self.user_selection.include_grades:
			metrics.append("grades")

		return metrics

	def weight_selection(self):

		valid_weights = False
		metrics = self.weight_selection_metrics_helper() 

		while(not valid_weights):
			tot = 0.0

			print("Now select your weights for each metric!")
			print("Weights must sum to 1! (eg. 0.1,0.2,0.7)")
			print("Upcoming choices: " + str(metrics))
			
			weights = []			

			for m in metrics:
				try:
					wt = float(input("Weight of " + m + " (total = " + str("{0:.3f}".format(tot)) + "):"))
					tot += wt
					weights.append(wt)
					if(tot > 1.):
						break
				except ValueError:
					print("Not a valid number")
					break

			if(tot == 1. and len(weights) == len(metrics)):
				print("You selected:" )
				for i in range(0, len(metrics)):
					print(metrics[i] + ": " + str(weights[i]))

				correct = prompt_correct()

				if correct:
					self.user_selection.weights = weights
					valid_weights = True				

	def generate_results(self):
		ranker = self.ranker

		metrics = self.user_selection.metrics
		weights = self.user_selection.weights
		courses = self.user_selection.courses

		


	def run(self):
		selector = Selector()

		p.print_break()
		print ("Feel free to contribute at: https://github.com/amsully/OMSCS_Course_Selector")
		print ("All data is pulled from here: https://omscentral.com/")
		p.print_break()

		self.course_selection()
		p.print_break()
		self.metric_selection()
		p.print_break()
		self.grade_selection()
		p.print_break()
		self.weight_selection()
		p.print_break()
		self.generate_results()
