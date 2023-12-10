import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from numpy import linspace, average
import io
import base64

# color constants pulled from site's css
COLOR_E = '#46c6c2'
COLOR_M = '#fac31d'
COLOR_H = '#f8615c'

# convert plot to base 64 string to pass to frontend
def fig_to_base64(fig):
	png_image = io.BytesIO()
	FigureCanvas(fig).print_png(png_image)
	png_b64 = 'data:image/png;base64,'
	png_b64 += base64.b64encode(png_image.getvalue()).decode('utf8')
	return png_b64

# used to group problems by difficulty
def partition(probs):
	diff = { 'Easy': [], 'Medium': [], 'Hard': []}
	for prob in probs:
		diff[prob['difficulty']].append(prob)    
	return diff

# simple plotting function to reduce on rewritten code
def plot(ax, x, y, color, label, mark=False, solid=True):
	style = 'solid' if solid else 'dashed'
	if mark:
		return ax.plot(x, y, marker='o', markersize=4, color=color, label=label, linestyle=style)
	return ax.plot(x, y, color=color, label=label, linestyle=style)

# add additional lines to plot for ac rate
def ac_plot_helper(data, key, ax, color, ac_running_average):
	dk = data[key]
	plt, = plot(ax, [p['date'] for p in dk], [p['acRate'] for p in dk], color, key, True)
	if ac_running_average:
		running_average = [p['acRate'] for p in dk]
		running_average = [average(running_average[:i]) for i in range(1, len(running_average) + 1)]
		avg_plt, = plot(ax, [p['date'] for p in dk], running_average, color, (key + ' avg'), mark=True, solid=False)
	return plt

# graph the accepted rate over time
# plots_data used for
#  - filter by problem difficulty
#  - plotting running average
def graph_ac(problems, plots_data):
	plt.switch_backend('agg')
	fig, ax = plt.subplots(figsize=(5, 4))
	plt.title('AC Rate')
	plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
	plt.gca().xaxis.set_major_locator(mdates.DayLocator())
	
	data = partition(problems)
	handles = []
	if plots_data['Hard']:
		handles.append(ac_plot_helper(data, 'Hard', ax, COLOR_H, plots_data['ac_running_average']))
	if plots_data['Medium']:
		handles.append(ac_plot_helper(data, 'Medium', ax, COLOR_M, plots_data['ac_running_average']))
	if plots_data['Easy']:
		handles.append(ac_plot_helper(data, 'Easy', ax, COLOR_E, plots_data['ac_running_average']))
	ax.legend(handles=handles)	
	
	# prevent x axis crowding, limit to 10 ticks
	ticks = ax.xaxis.get_major_ticks()
	n_ticks = len(ticks)
	if n_ticks > 10:
		keep = linspace(0, n_ticks - 1, 10, dtype='int').astype(int)
		for i in range(n_ticks):
			if i not in keep:
				ticks[i].set_visible(False)
	plt.gcf().autofmt_xdate()

	return fig_to_base64(fig)

# difficulty frequency over the weekdays
def graph_frequency(problems, plots_data):
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
	
	handles = []
	if plots_data['Hard']:
		hard, = plot(ax, range(7), freq['Hard'], COLOR_H, 'Hard')
		handles.append(hard)
	if plots_data['Medium']:
		medium, = plot(ax, range(7), freq['Medium'], COLOR_M, 'Medium')
		handles.append(medium)
	if plots_data['Easy']:
		easy, = plot(ax, range(7), freq['Easy'], COLOR_E, 'Easy')
		handles.append(easy)
	ax.legend(handles=handles)
    
	return fig_to_base64(fig)