from flask import Flask, render_template, request
from dotenv import load_dotenv
from datetime import datetime
import os

import DBConnection
from graphing import graph_frequency, graph_ac

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

	start_date = datetime.strptime(request.form.get('start'), '%Y-%m-%d').date()
	end_date = datetime.strptime(request.form.get('end'), '%Y-%m-%d').date()
	
	print(request.form)
	plots_data = { 
		'Easy': request.form.get('plot_easy') == 'on', 
		'Medium': request.form.get('plot_medium') == 'on', 
		'Hard': request.form.get('plot_hard') == 'on',
		'ac_running_average': request.form.get('ac_running_average') == 'on'
	}
	
	variables = {}
	problems = []
	
	year = start_date.year
	month = start_date.month
	while year <= end_date.year:
		while (month <= end_date.month) or (year != end_date.year):
			print('query', month, year)
			variables['year'] = year
			variables['month'] = month
			
			try:
				response = db.query(variables, start_date, end_date)
				if response:
					problems.extend(response)
			except Exception as e:
				print('Something went wrong', e)
				
			month += 1
			if month == 13:
				month = 1
				break
		year += 1
	
	return render_template('index.html', daily_difficulty=graph_frequency(problems, plots_data), ac_rate=graph_ac(problems, plots_data))

if __name__ == "__main__":	
	app.run(host=os.getenv('HOST'), port=os.getenv('PORT'), debug=True)
	
	