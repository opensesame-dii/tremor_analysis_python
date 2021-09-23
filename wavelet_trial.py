from scipy import signal
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

fname = "sample_data/Sample1_left.csv"
fs = 200

df = pd.read_csv(fname, header=None, skiprows=10, index_col=0, encoding="shift jis")
npdata = np.array(df.values.flatten())
data = np.reshape(npdata,(df.shape[0],df.shape[1]))

sig = data[:,4]

t, dt = np.linspace(0, len(sig) // fs, len(sig), retstep=True)

#t, dt = np.linspace(0, 1, 200, retstep=True)
fs = 1/dt
w = 6.
#sig = np.cos(2*np.pi*(50 + 10*t)*t) + np.sin(40*np.pi*t)
freq = np.linspace(0, fs/2/5, 100 + 1)[1:] # /5 : 20Hzまでを取り出すため
widths = w*fs / (2*freq*np.pi)

print(f"dt: {dt}\nfs: {fs}\nw: {w}")

cwtm = signal.cwt(sig, signal.morlet2, widths, w=w)
print(f"cwt shape: {cwtm.shape}\n")
fig, ax = plt.subplots()
ax.set_xlabel("Time [sec]")
ax.set_ylabel("Frequency [Hz]")
im = ax.pcolormesh(t, freq, np.abs(cwtm), cmap='jet', shading='gouraud')
cbar = fig.colorbar(im,ax=ax)
cbar.set_label("Amplitude")
plt.show()