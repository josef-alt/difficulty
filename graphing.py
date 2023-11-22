import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import io
import base64

def partition(probs):
	diff = { 'Easy': [], 'Medium': [], 'Hard': []}
	for prob in probs:
		diff[prob['difficulty']].append(prob)    
	return diff

def graphFrequency(problems):
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
	hard, = ax.plot(range(7), freq['Hard'], color='#f8615c', label='Hard')
	medium, = ax.plot(range(7), freq['Medium'], color='#fac31d', label='Medium')
	easy, = ax.plot(range(7), freq['Easy'], color='#46c6c2', label='Easy')
	ax.legend(handles=[hard, medium, easy])
    
	pngImage = io.BytesIO()
	FigureCanvas(fig).print_png(pngImage)
	pngImageB64String = 'data:image/png;base64,'
	pngImageB64String += base64.b64encode(pngImage.getvalue()).decode('utf8')
	return pngImageB64String