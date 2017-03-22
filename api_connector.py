import requests

class APIConnector:
	def __init__(self, name="MainConnector", base_endpoint="https://gt-surveyor.firebaseio.com/"):
		self.name = name
		self.base_endpoint = base_endpoint

	def get(self, name):
		if ".json" not in name:
			name += ".json"

		r = requests.get(self.base_endpoint + name)

		assert r.status_code == 200, "Failed to reach " + self.base_endpoint + name + " server may be down."
		
		return r.json()



