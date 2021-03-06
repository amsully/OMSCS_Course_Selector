import printer as p
import api_connector as api
import textwrap
import random
import operator
import json
import os
import time
from os import listdir
from os.path import isfile, join

from util import *

class UserSelection:
	def __init__(self, name="UserSelection", save_directory = "tmp"):
		self.courses = {} # Empty == All Courses
		self.metrics = [] # Empty == All metrics
		self.include_grades = False
		self.weights = [] # Weights of each metrics (sums to 1)
		self.results = {}
		self.save_directory = "tmp"

	def reset(self):
		self.courses = {} # Empty == All Courses
		self.metrics = [] # Empty == All metrics
		self.include_grades = False
		self.weights = [] # Weights of each metrics (sums to 1)
		self.results = {}

	def save_results(self):
		if not os.path.exists(self.save_directory):
		    os.makedirs(self.save_directory)


		data = {
			"courses":self.courses,
			"metrics":self.metrics,
			"includes_grades":self.include_grades,
			"weights":self.weights,
			"results":self.results
		}

		timestr = time.strftime("%Y-%m-%d-%H%M%S")
		filename = self.save_directory +"/" + "results_" + timestr

		with open(filename, 'w') as outfile:
			json.dump(data, outfile)

	def get_average_metrics(self):

		tot_results = [0. for i in range(0, len(self.metrics))]
		cnt_results = [0  for i in range(0, len(self.metrics))]

		for course in self.results:

			for i in range(0, len(self.metrics)):
				rew = self.results[course][i]

				if(rew == None):
					continue
				else:
					tot_results[i] += rew
					cnt_results[i] += 1


		return [tot_results[i]/cnt_results[i] for i in range(0, len(tot_results))]



	def sort_totals(self):

		total_res = {}

		# get average of each metric
		average_metrics = self.get_average_metrics()

		# sum metrics and add average to none metrics
		result_totals = {}
		for course in self.results:
			course_total = 0
			for i in range(0, len(self.metrics)):
				rew = self.results[course][i]

				# None, add average of this metric
				if(rew == None):
					course_total += average_metrics[i]
				else:
					course_total += rew

			result_totals[course] = course_total

		sorted_totals = sorted(result_totals.items(), key=operator.itemgetter(1), reverse = True)

		return sorted_totals

	def print_results(self):

		sorted_totals = self.sort_totals()

		column_names = []
		for i in range(0, len(self.metrics)):
			column_names.append(self.metrics[i] + " (" + str(self.weights[i]) + ")")
		columns = column_names

		columns.append("TOTAL")

		r_format = "{:>25}" * (len(columns) + 1)
		print( r_format.format("", *columns))

		for course,score in sorted_totals:
			row_results = self.results[course]
			row_results.append(score)
			row = [ "None (avg)" if res == None else str(round(res,2)) for res in row_results]

			print( r_format.format(self.courses[course][0:15] + ":" + course, *row) )

	def load_results(self, file):
		# 		data = {
		# 	"courses":self.courses,
		# 	"metrics":self.metrics,
		# 	"includes_grades":self.include_grades,
		# 	"weights":self.weights,
		# 	"results":self.results
		# }

		path = self.save_directory + "/" + file
		with open(path) as infile:
			data = json.load(infile)
			self.courses = data["courses"]
			self.metrics = data["metrics"]
			self.includes_grades = data["includes_grades"]
			self.weights = data["weights"]
			self.results = data["results"]

class Selector:

	def __init__(self, name="MainSelector", max_value_range = 5):
		self.api = api.APIConnector()
		self.name = name
		self.course_CRS = None
		self.course_AGG = None
		self.course_GRD = None
		self.user_selection = UserSelection()
		self.scores = None
		self.max_course_workload = None
		self.max_value_range = max_value_range
		self.grade_map = {"a":95,"b":85,"c":75,"d":65,"f":55}

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

		selected_courses = []
		user_happy = False
		while not user_happy:
			print ("What courses do you want to select from? Use course numbers or first column numbers. Space to separate (eg. 6035 2 3 8803-BDHI 8803-GA). (Enter: All)")
			course_numbers = parse_input(input())

			selected_courses = self.convert_to_courses(course_numbers, course_index)

			print("You selected: ")
			if(len(selected_courses) == 0):
				print("All")
				selected_courses = list(self.course_CRS.keys())
			else:
				for course in selected_courses:
					print(course + " " + self.course_CRS[course]["name"])
				
			user_happy = prompt_correct()

		# Include names
		user_selection_courses = {}
		for course in selected_courses:
			user_selection_courses[course] = self.course_CRS[course]["name"]

		self.user_selection.courses = user_selection_courses


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
			choice = input("Would you like to include grade information? (Courses with higher average grades score better). [y]/n:").lower()

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

			tot = round(tot,3) # handle floating points
			if(tot == 1. and len(weights) == len(metrics)):
				print("You selected:" )
				for i in range(0, len(metrics)):
					print(metrics[i] + ": " + str(weights[i]))

				correct = prompt_correct()

				if correct:
					self.user_selection.weights = weights
					valid_weights = True				

	def get_metric_values(self, c, metrics):
		if(self.course_AGG == None):
			self.course_AGG == self.api.get("AGG")

		values = []

		course_agg = {}
		avg = {}
		try:
			course_agg = self.course_AGG[c]
			avg =  course_agg["average"].copy() # Value Copy
		except KeyError:
			print(c + " does not have any aggregate information. Assigning 'None'.")
			for m in metrics:
				avg[m] = None
	


		if("grades" in metrics):
			try:
				avg["grades"] = self.course_GRD[c]
			except KeyError:
				print(c + " does not have any grade information. Assigning 'None'.")
				avg["grades"] = None


		for m in metrics:
			values.append(avg[m])

		return values

	def max_workload(self):
		if(self.course_AGG == None):
			self.course_AGG = self.api.get("AGG")

		if(self.max_course_workload == None):
			max_workload = 0
			for c in self.course_AGG:
				workload = self.course_AGG[c]["average"]["workload"]
				if( workload > max_workload):
					max_workload = workload
			self.max_course_workload = max_workload

		return self.max_course_workload

	def workload_scale(self):
		if(self.course_AGG == None):
			self.course_AGG = self.api.get("AGG")

		if(self.max_course_workload == None):
			self.max_course_workload = self.max_workload()

		return self.max_value_range / self.max_course_workload


	def grade_mean(self, grades):
		total_grade = 0.
		grade_count = 0.

		for term in grades: # Each term
			term_grades = grades[term]
			for g in term_grades: # Each grade
				if g in self.grade_map:
					grade_count += term_grades[g]
					total_grade += (term_grades[g] * self.grade_map[g])

		return total_grade/grade_count


	def get_metric_function(self, metric):

		def grades(weight, value):

			return (1.*self.max_value_range / self.grade_map['a']) * self.grade_mean(value) * weight

		# Higher difficulty is bad!
		def difficulty(weight, value):
			return weight * (self.max_value_range - value)

		def workload(weight, value):
			return 1. * weight * (self.max_value_range - value * self.workload_scale())

		# Higher ratings are good!
		def rating(weight, value):
			return ( 1. * weight * value )

		def wt_times_val(weight, value):
			return 1. * weight * value

		if(metric == "grades"):
			return grades
		elif(metric == "difficulty"):
			return difficulty
		elif(metric == "workload"):
			return workload
		elif(metric == "rating"):
			return rating
		else:
			print("Unknown metric: " + metric + ". Using 'weight * value'")
			return wt_times_val


	def score(self, metrics, weights, values):
		assert(len(metrics) == len(weights))
		assert(len(weights) == len(values))

		results = []

		for i in range(0, len(metrics)):
			metric = metrics[i]
			value  = values[i]
			wt     = weights[i]

			if(value == None):
				print("    Metric " + metric + " is not available for this class. Assigning 'None'.")
				results.append(None)
			else:
				metric_eval = self.get_metric_function(metric)
				results.append(metric_eval(wt,value))

		return results



	def generate_results(self):
		results = {} # course: score

		metrics = self.user_selection.metrics
		weights = self.user_selection.weights
		courses = self.user_selection.courses

		assert(len(weights) == len(metrics))

		for c in courses:
			print("Scoring: " + c)
			values = self.get_metric_values(c, metrics)

			results[c] = self.score(metrics, weights, values)

		self.user_selection.results = results

	def view_results(self, path="tmp/"):

		onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]
		for i in range(0, len(onlyfiles)):
			print(str(i) + ": " +onlyfiles[i])

		file_index = input("Select number representing file:")

		try:
			file_index = int(file_index)
			self.user_selection.load_results(onlyfiles[file_index])
			# self.generate_results() # TODO: ERROR. Dependency here between load results and print results.
			self.user_selection.print_results()
		except ValueError:
			print("Invalid choice")
		except IndexError:
			print("Invalid choice. Value not in range.")

	def run(self):

		p.print_break()
		print ("Feel free to contribute at: https://github.com/amsully/OMSCS_Course_Selector")
		print ("All data is pulled from here: https://omscentral.com/")
		p.print_break()

		yes = set(['yes','y', 'ye'])
		no = set(['no','n', ''])

		while(1):
			self.user_selection.reset()

			view_prev_results = input("Do you want to view previous results? [n]/y (Ctrl-C to exit):")

			if(view_prev_results in yes):
				self.view_results()
				p.print_break()

			elif(view_prev_results in no):
				self.course_selection()
				p.print_break()
				self.metric_selection()
				p.print_break()
				self.grade_selection()
				p.print_break()
				self.weight_selection()
				p.print_break()
				self.generate_results()
				self.user_selection.print_results()
				self.user_selection.save_results()
				p.print_break()
			else:
				print("Select yes or no")

