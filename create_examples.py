from matplotlib import pyplot as plt
from matplotlib.patches import Rectangle

# Create figure
plt.figure()

# Set width and height
W = 100
H = 100

# Set warehouse sizes
plt.xlim([0, W])
plt.ylim([-.1 * H, H])

# Get axis
ax = plt.gca()

# Remove ticks
plt.tick_params(axis='both', which='both', bottom=False, top=False, labelbottom=False, right=False, left=False,
                labelleft=False)


# Plot docking doors
docking_doors = Rectangle((0, -.1 * H), W, .1 * H, color="black", fill=True, alpha=1)

# Annotate
ax.add_artist(docking_doors)
rx, ry = docking_doors.get_xy()
cx = rx + docking_doors.get_width() / 2
cy = ry + docking_doors.get_height() / 2

# Place annotation
ax.annotate("Docking doors", (cx, cy), color="white", weight="bold", fontsize=10, ha='center', va='center')

ax.annotate(text='', xy=(0,90), xytext=(100,90), arrowprops=dict(arrowstyle='<->'))
ax.text(45, 92, "100", fontsize = 16)
ax.text(42, 82, "n = 10", fontsize = 16)



ax.annotate(text='', xy=(0,70), xytext=(50,70), arrowprops=dict(arrowstyle='<->'))
ax.text(22, 72, "50", fontsize = 16)
ax.plot([50, 50], [0, 70], 'r')
ax.text(18, 62, "n = 5", fontsize = 16)

ax.annotate(text='', xy=(50,70), xytext=(100,70), arrowprops=dict(arrowstyle='<->'))
#ax.text(72, 82, "50", fontsize = 16)
#ax.text(68, 72, "n = 5", fontsize = 16)



ax.annotate(text='', xy=(0,50), xytext=(20,50), arrowprops=dict(arrowstyle='<->'))
ax.text(7.5, 52, "20", fontsize = 16)
ax.plot([20, 20], [0, 50], 'b')
ax.text(3.5, 42, "n = 2", fontsize = 16)

ax.annotate(text='', xy=(20,50), xytext=(40,50), arrowprops=dict(arrowstyle='<->'))
#ax.text(27.5, 62, "20", fontsize = 16)
ax.plot([40, 40], [0, 50], 'b')
#ax.text(23.5, 52, "n = 2", fontsize = 16)

ax.annotate(text='', xy=(40,50), xytext=(60,50), arrowprops=dict(arrowstyle='<->'))

ax.annotate(text='', xy=(60,50), xytext=(80,50), arrowprops=dict(arrowstyle='<->'))
#ax.text(67.5, 62, "20", fontsize = 16)
ax.plot([60, 60], [0, 50], 'b')
#ax.text(63.5, 52, "n = 2", fontsize = 16)

ax.annotate(text='', xy=(80,50), xytext=(100,50), arrowprops=dict(arrowstyle='<->'))
#ax.text(87.5, 62, "20", fontsize = 16)
ax.plot([80, 80], [0, 50], 'b')
#ax.text(83.5, 52, "n = 2", fontsize = 16)


plt.savefig("data/feasible_solution_generator_example.png")
plt.show()