
def parse_input(input_):

	result = input_.split(" ")

	return result

def prompt_correct():
	yes = set(['yes','y', 'ye', ''])
	no = set(['no','n'])

	while(1):
		choice = input("Is this correct? [y]/n: ").lower()

		if choice in yes:
			return True
		elif choice in no:
			return False
		else:
			print("Please respond with 'yes' or 'no'")