from flask import Flask, render_template, request
from dotenv import load_dotenv
import datetime
import requests
import json
import os

def dateInRange(date, start, end):
	data = date.split('-')
	d = datetime.datetime(int(data[0]), int(data[1]), int(data[2]))
	s = datetime.datetime(start[0], start[1], start[2])
	e = datetime.datetime(end[0], end[1], end[2])
	return d >= s and d <= e

def load_query():
	with open(os.getenv('QUERY_FILE')) as file:
		return file.read()

load_dotenv()
Q = load_query()
url = os.getenv('URL')

app = Flask(__name__)

@app.route("/", methods=['GET'])
def index():
	return render_template('index.html')

@app.route("/query/", methods=['POST'])
def query():
	startDate = request.form.get('start').split('-')
	endDate = request.form.get('end').split('-')
	print('\n')
	print(startDate, endDate)
	startY = int(startDate[0])
	startM = int(startDate[1])
	startD = int(startDate[2])
	endY = int(endDate[0])
	endM = int(endDate[1])
	endD = int(endDate[2])
	
	problems = []
	
	year = startY
	month = startM
	while year <= endY:
		print(year, " <= ", endY, "m=", month)
		while (month <= endM) or (year != endY):
			print("query", month, year)
			variables = { "year": year, "month": month }
			params = { "query": Q, "variables": variables }
			response = requests.post(url=url, json=params)
			if response.status_code == 200:
				data = json.loads(response.content)['data']['dailyCodingChallengeV2']['challenges']
				for p in data:
					if dateInRange(p['date'], (startY, startM, startD), (endY, endM, endD)):
						problems.append(p)
				
			month += 1
			if month == 13:
				month = 1
				break
		year += 1
	
	opt = []
	for prob in problems:
		opt.append(prob['date'] + " " + prob['question']['title'])
	return render_template('index.html', test_str=opt, start_date=startDate, end_date=endDate)

if __name__ == "__main__":
	app.run(host=os.getenv('HOST'), port=os.getenv('PORT'), debug=True)
	
	