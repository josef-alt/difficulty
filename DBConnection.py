from datetime import datetime
import requests
import json

# my attempt to streamline the data access portion of the project
class DBConnection:
	query_string = None
	url = None
	
	# retrieve query string from file
	def load_query(self, queryFile):
		with open(queryFile) as file:
			return file.read()

	# compare a string date to the start and end dates
	def date_in_range(self, date, start, end):
		d = datetime.strptime(date, '%Y-%m-%d').date()
		return d >= start and d <= end
	
	# collate problem data
	def filter_fields(self, problem):
		new_prob = {}
		d = problem['date'].split('-')
		new_prob['date'] = datetime.strptime(problem['date'], '%Y-%m-%d').date() #problem['date']
		new_prob['difficulty'] = problem['question']['difficulty']
		new_prob['acRate'] = problem['question']['acRate']
		new_prob['day'] = datetime(int(d[0]), int(d[1]), int(d[2])).strftime('%w')
		return new_prob

	# graphql returns a deep collection
	# flattens the response for easier access
	def flatten_data(self, data):
		return data['data']['dailyCodingChallengeV2']['challenges']
	
	# handle all gql queries
	def query(self, variables, after, before):
		params = { "query": self.query_string, "variables": variables }
		response = requests.post(url=self.url, json=params)
		if response.status_code == 200:
			data = self.flatten_data(json.loads(response.content))
			
			output = []
			for p in data:
				# the api only provides month and year fields
				# here we need to implement our own checks for day
				if self.date_in_range(p['date'], after, before):
					output.append(self.filter_fields(p))
			return output
		
		# TODO - handle failed queries
		raise Exception("Query failed")
		
	def __init__(self, url, queryfile):
		self.url = url
		self.query_string = self.load_query(queryfile)