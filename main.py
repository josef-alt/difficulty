from flask import Flask, render_template, request
from dotenv import load_dotenv
import os

import DBConnection
from graphing import graphFrequency


load_dotenv()
app = Flask(__name__)
db = DBConnection.DBConnection(os.getenv('URL'), os.getenv('QUERY_FILE'))

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
	variables = { 
		'startY': startY, 
		'startM': startM, 
		'startD': startD, 
		'endY': endY,
		'endM': endM,
		'endD': endD 
	}
	
	problems = []
	
	year = startY
	month = startM
	while year <= endY:
		while (month <= endM) or (year != endY):
			print('query', month, year)
			variables['year'] = year
			variables['month'] = month
			
			try:
				response = db.query(variables)
				if response:
					problems.extend(response)
			except Exception as e:
				print('Something went wrong', e)
				
			
			month += 1
			if month == 13:
				month = 1
				break
		year += 1
	
	return render_template('index.html', daily_difficulty=graphFrequency(problems))

if __name__ == "__main__":	
	app.run(host=os.getenv('HOST'), port=os.getenv('PORT'), debug=True)
	
	