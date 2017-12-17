import matplotlib.pyplot as plt

def draw_plot(data, edge_color, fill_color):
	bp = ax.boxplot(data, patch_artist=True)

	for element in ['boxes', 'whiskers', 'fliers', 'means', 'medians', 'caps']:
		plt.setp(bp[element], color=edge_color)

	for patch in bp['boxes']:
		patch.set(facecolor=fill_color)

example_data1 = [[1,2,0.8], [0.5,2,2], [3,2,1]]
example_data2 = [[5,3, 4], [6,4,3,8], [6,4,9]]

fig, ax = plt.subplots()
draw_plot(example_data1, 'red', 'tan')
draw_plot(example_data2, 'blue', 'cyan')
ax.set_ylim(0, 10)
plt.show()