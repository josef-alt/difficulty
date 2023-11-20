from flask import Flask, render_template, request
from dotenv import load_dotenv
import datetime
import requests
import json
import os

import io
import base64
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure


def dateInRange(date, start, end):
	data = date.split('-')
	d = datetime.datetime(int(data[0]), int(data[1]), int(data[2]))
	s = datetime.datetime(start[0], start[1], start[2])
	e = datetime.datetime(end[0], end[1], end[2])
	return d >= s and d <= e

def load_query():
	with open(os.getenv('QUERY_FILE')) as file:
		return file.read()

def filter_fields(problem):
	new_prob = {}
	d = problem['date'].split('-')
	new_prob['difficulty'] = problem['question']['difficulty']
	new_prob['acRate'] = problem['question']['acRate']
	new_prob['day'] = datetime.datetime(int(d[0]), int(d[1]), int(d[2])).strftime('%w')
	return new_prob
	
def process(probs):
	diff = { 'Easy': [], 'Medium': [], 'Hard': []}
	for prob in probs:
		diff[prob['difficulty']].append(prob)    
	return diff

def graphFrequency(problems):
	data = process(problems)
	freq = { 'Hard': [], 'Medium': [], 'Easy': []}
	for diff in freq.keys():
		for day in range(7):
			freq[diff].append(0)
		for prob in data[diff]:
			freq[prob['difficulty']][int(prob['day'])] = freq[prob['difficulty']][int(prob['day'])] + 1
		total = sum(freq[diff])
		freq[diff] = [0 if total == 0 else f / total * 100 for f in freq[diff]]
    
	plt.switch_backend('agg')
	fig, ax = plt.subplots(figsize=(5, 4))
	x_ticks_labels = ['Sun','Mon','Tue','Wed', 'Thu', 'Fri', 'Sat']
	plt.xticks(range(7), x_ticks_labels)
	plt.title("Daily Difficulty")
	ax.plot(range(7), freq['Hard'], color='#f8615c')
	ax.plot(range(7), freq['Medium'], color='#fac31d')
	ax.plot(range(7), freq['Easy'], color='#46c6c2')
    
	pngImage = io.BytesIO()
	FigureCanvas(fig).print_png(pngImage)
	pngImageB64String = "data:image/png;base64,"
	pngImageB64String += base64.b64encode(pngImage.getvalue()).decode('utf8')
	return pngImageB64String

load_dotenv()
Q = load_query()
url = os.getenv('URL')

app = Flask(__name__)

@app.route("/", methods=['GET'])
def index():
	return render_template('index.html')

@app.route("/query/", methods=['POST'])
def query():
	if not request.form.get('start') or not request.form.get('end'):
		return render_template('index.html')
		
	startDate = request.form.get('start').split('-')
	endDate = request.form.get('end').split('-')
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
		while (month <= endM) or (year != endY):
			print("query", month, year)
			variables = { "year": year, "month": month }
			params = { "query": Q, "variables": variables }
			response = requests.post(url=url, json=params)
			if response.status_code == 200:
				data = json.loads(response.content)['data']['dailyCodingChallengeV2']['challenges']
				for p in data:
					if dateInRange(p['date'], (startY, startM, startD), (endY, endM, endD)):
						problems.append(filter_fields(p))
			month += 1
			if month == 13:
				month = 1
				break
		year += 1
	
	return render_template('index.html', daily_difficulty=graphFrequency(problems))

if __name__ == "__main__":
	app.run(host=os.getenv('HOST'), port=os.getenv('PORT'), debug=True)
	
	