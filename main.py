from flask import Flask, render_template, request
from dotenv import load_dotenv
from datetime import datetime
import os

import DBConnection
from graphing import graphFrequency, graphAC

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

	strt = datetime.strptime(request.form.get('start'), '%Y-%m-%d').date()
	endd = datetime.strptime(request.form.get('end'), '%Y-%m-%d').date()
		
	variables = {}
	problems = []
	
	year = strt.year
	month = strt.month
	while year <= endd.year:
		while (month <= endd.month) or (year != endd.year):
			print('query', month, year)
			variables['year'] = year
			variables['month'] = month
			
			try:
				response = db.query(variables, strt, endd)
				if response:
					problems.extend(response)
			except Exception as e:
				print('Something went wrong', e)
				
			month += 1
			if month == 13:
				month = 1
				break
		year += 1
	
	return render_template('index.html', daily_difficulty=graphFrequency(problems), ac_rate=graphAC(problems))

if __name__ == "__main__":	
	app.run(host=os.getenv('HOST'), port=os.getenv('PORT'), debug=True)
	
	