import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation

# A more classique and romantique poem for Naval Ando,
# who is a girl and an engineer
poem_lines = [
    "To Naval Ando, brilliant and bright,",
    "Engineer of dreams, a guiding light.",
    "Upon the sea, your visions flow,",
    "In golden beams, your talents grow.",
    "",
    "Your gentle gaze, serene and deep,",
    "In circuits, code, and midnight sleep.",
    "O Muse! Your laughter, soft and clear,",
    "Is music every heart holds dear.",
    "",
    "Your presence, like a summer breeze,",
    "Brings hope and strength with perfect ease.",
    "In every star, your eyes I find,",
    "A universe by you designed.",
    "",
    "Naval, beloved, ever thine,",
    "My heart, my soul, with yours entwine.",
    "Let time stand still, let tempests cease,",
    "Within your arms, I dwell in peace."
]

fig, ax = plt.subplots(figsize=(8, 6))
ax.axis('off')
text_obj = ax.text(0.5, 0.5, "", ha='center', va='center', fontsize=20, wrap=True, color='indigo', fontname='Times New Roman')

# For a more classique and romantique animation, let's add floating roses and hearts
heart_x = []
heart_y = []
heart_objs = []
rose_x = []
rose_y = []
rose_objs = []

def heart_shape(t, x0, y0, size=1):
    x = 16 * np.sin(t)**3
    y = 13 * np.cos(t) - 5 * np.cos(2*t) - 2 * np.cos(3*t) - np.cos(4*t)
    return x0 + size * x / 20, y0 + size * y / 20

def rose_shape(t, x0, y0, size=1, k=4):
    # A polar rose curve: r = size * cos(k * t)
    r = size * np.cos(k * t)
    x = x0 + r * np.cos(t)
    y = y0 + r * np.sin(t)
    return x, y

num_hearts = 5
num_roses = 3
np.random.seed(42)
for i in range(num_hearts):
    t = np.linspace(0, 2*np.pi, 100)
    x0 = np.random.uniform(0.15, 0.85)
    y0 = np.random.uniform(0.25, 0.75)
    size = np.random.uniform(0.06, 0.12)
    x, y = heart_shape(t, x0, y0, size)
    heart, = ax.plot(x, y, color='crimson', lw=2, alpha=0.7)
    heart_x.append(x0)
    heart_y.append(y0)
    heart_objs.append(heart)

for i in range(num_roses):
    t = np.linspace(0, 2*np.pi, 200)
    x0 = np.random.uniform(0.2, 0.8)
    y0 = np.random.uniform(0.3, 0.7)
    size = np.random.uniform(0.08, 0.13)
    k = np.random.choice([3,4,5])
    x, y = rose_shape(t, x0, y0, size, k)
    rose, = ax.plot(x, y, color='darkmagenta', lw=2, alpha=0.6)
    rose_x.append(x0)
    rose_y.append(y0)
    rose_objs.append(rose)

def animate(i):
    # Animate poem lines
    if i < len(poem_lines):
        text_obj.set_text('\n'.join(poem_lines[:i+1]))
    # Animate hearts floating up and gently swaying
    for idx, heart in enumerate(heart_objs):
        new_y = heart_y[idx] + 0.002 * i
        new_x = heart_x[idx] + 0.01 * np.sin(0.18 * i + idx)
        t = np.linspace(0, 2*np.pi, 100)
        size = 0.09 + 0.02 * np.sin(0.09 * i + idx)
        x, y = heart_shape(t, new_x, new_y, size)
        heart.set_data(x, y)
    # Animate roses gently rotating and floating
    for idx, rose in enumerate(rose_objs):
        new_y = rose_y[idx] + 0.0015 * i
        new_x = rose_x[idx] + 0.008 * np.cos(0.13 * i + idx)
        t = np.linspace(0, 2*np.pi, 200)
        size = 0.11 + 0.015 * np.cos(0.07 * i + idx)
        k = 4 + int(1 * np.sin(0.05 * i + idx))
        x, y = rose_shape(t + 0.03 * i, new_x, new_y, size, k)
        rose.set_data(x, y)
    return [text_obj] + heart_objs + rose_objs

ani = animation.FuncAnimation(
    fig, animate, frames=len(poem_lines)+70, interval=650, blit=True, repeat=False
)

plt.show()
