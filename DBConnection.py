import datetime
import requests
import json

class DBConnection:
	query_string = None
	url = None
	
	def load_query(self, queryFile):
		with open(queryFile) as file:
			return file.read()
	
	def dateInRange(self, date, start, end):
		data = date.split('-')
		d = datetime.datetime(int(data[0]), int(data[1]), int(data[2]))
		s = datetime.datetime(start[0], start[1], start[2])
		e = datetime.datetime(end[0], end[1], end[2])
		return d >= s and d <= e
	
	def filter_fields(self, problem):
		new_prob = {}
		d = problem['date'].split('-')
		new_prob['difficulty'] = problem['question']['difficulty']
		new_prob['acRate'] = problem['question']['acRate']
		new_prob['day'] = datetime.datetime(int(d[0]), int(d[1]), int(d[2])).strftime('%w')
		return new_prob
		
	def query(self, variables):
		startD = int(variables['startD'])
		startM = int(variables['startM'])
		startY = int(variables['startY'])
		endD = int(variables['endD'])
		endM = int(variables['endM'])
		endY = int(variables['endY'])
		
		params = { "query": self.query_string, "variables": variables }
		response = requests.post(url=self.url, json=params)
		if response.status_code == 200:
			data = json.loads(response.content)['data']['dailyCodingChallengeV2']['challenges']
			
			output = []
			for p in data:
				if self.dateInRange(p['date'], (startY, startM, startD), (endY, endM, endD)):
					output.append(self.filter_fields(p))
			return output
		raise Exception("Query failed")
		
	def __init__(self, url, queryfile):
		self.url = url
		self.query_string = self.load_query(queryfile)