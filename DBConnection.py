from datetime import datetime
import requests
import json

class DBConnection:
	query_string = None
	url = None
	
	def load_query(self, queryFile):
		with open(queryFile) as file:
			return file.read()

	def dateInRange(self, date, start, end):
		d = datetime.strptime(date, '%Y-%m-%d').date()
		return d >= start and d <= end
	
	def filter_fields(self, problem):
		new_prob = {}
		d = problem['date'].split('-')
		new_prob['date'] = datetime.strptime(problem['date'], '%Y-%m-%d').date() #problem['date']
		new_prob['difficulty'] = problem['question']['difficulty']
		new_prob['acRate'] = problem['question']['acRate']
		new_prob['day'] = datetime(int(d[0]), int(d[1]), int(d[2])).strftime('%w')
		return new_prob
		
	def query(self, variables, after, before):
		params = { "query": self.query_string, "variables": variables }
		response = requests.post(url=self.url, json=params)
		if response.status_code == 200:
			data = json.loads(response.content)['data']['dailyCodingChallengeV2']['challenges']
			
			output = []
			for p in data:
				if self.dateInRange(p['date'], after, before):
					output.append(self.filter_fields(p))
			return output
		raise Exception("Query failed")
		
	def __init__(self, url, queryfile):
		self.url = url
		self.query_string = self.load_query(queryfile)