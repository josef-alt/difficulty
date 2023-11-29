import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from numpy import linspace
import io
import base64

COLOR_E = '#46c6c2'
COLOR_M = '#fac31d'
COLOR_H = '#f8615c'

def fig_to_base64(fig):
	png_image = io.BytesIO()
	FigureCanvas(fig).print_png(png_image)
	png_b64 = 'data:image/png;base64,'
	png_b64 += base64.b64encode(png_image.getvalue()).decode('utf8')
	return png_b64

def partition(probs):
	diff = { 'Easy': [], 'Medium': [], 'Hard': []}
	for prob in probs:
		diff[prob['difficulty']].append(prob)    
	return diff

def plot(ax, x, y, color, label, mark=False):
	if mark:
		return ax.plot(x, y, marker='o', markersize=4, color=color, label=label)
	return ax.plot(x, y, color=color, label=label)

def graph_ac(problems):
	plt.switch_backend('agg')
	fig, ax = plt.subplots(figsize=(5, 4))
	plt.title('AC Rate')
	plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
	plt.gca().xaxis.set_major_locator(mdates.DayLocator())
	
	data = partition(problems)	
	dh = data['Hard']
	dm = data['Medium']
	de = data['Easy']
	hard, = plot(ax, [prob['date'] for prob in dh], [prob['acRate'] for prob in dh], COLOR_H, 'Hard', True)
	medium, = plot(ax, [prob['date'] for prob in dm], [prob['acRate'] for prob in dm], COLOR_M, 'Medium', True)
	easy, = plot(ax, [prob['date'] for prob in de], [prob['acRate'] for prob in de], COLOR_E, 'Easy', True)
	ax.legend(handles=[hard, medium, easy])
	
	ticks = ax.xaxis.get_major_ticks()
	n_ticks = len(ticks)
	if n_ticks > 10:
		keep = linspace(0, n_ticks - 1, 10, dtype='int').astype(int)
		for i in range(n_ticks):
			if i not in keep:
				ticks[i].set_visible(False)
	plt.gcf().autofmt_xdate()

	return fig_to_base64(fig)

def graph_frequency(problems):
	data = partition(problems)
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
	plt.title('Daily Difficulty')
	hard, = plot(ax, range(7), freq['Hard'], COLOR_H, 'Hard')
	medium, = plot(ax, range(7), freq['Medium'], COLOR_M, 'Medium')
	easy, = plot(ax, range(7), freq['Easy'], COLOR_E, 'Easy')
	ax.legend(handles=[hard, medium, easy])
    
	return fig_to_base64(fig)