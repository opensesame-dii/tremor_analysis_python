import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
import pandas as pd
import time
dpi = 97
wide_figsize = (12, 3)
wide_figsize_dots = (wide_figsize[0] * dpi, wide_figsize[1] * dpi)
narrow_figsize = (4, 3)
narrow_figsize_dots = (narrow_figsize[0] * dpi, narrow_figsize[1] * dpi)

file_name = "./sample_data/Sample2_right.csv"
sampling_rate = 200
segment_duration_sec = 5


df1 = pd.read_csv(file_name, header=None, skiprows=10, index_col=0, encoding="shift jis")
npdata1=np.array(df1.values.flatten())
data = np.reshape(npdata1,(df1.shape[0],df1.shape[1])).T
data = data[:, 3:]

# plt.plot(data[0])
# plt.show()
# plt.close()
print(data.shape)
# a, f, t = spectrogram_analize(data1[:, j*3: j*3 + 3].T, sampling_rate, sampling_rate * segment_duration_sec, file_name, "sensor_name", start=0, end=-1)

nperseg = sampling_rate * segment_duration_sec
L = np.min((len(data[0]), nperseg))
nTimesSpectrogram = 500; 
noverlap = np.ceil(L - (len(data[0]) - L) / (nTimesSpectrogram - 1))
noverlap = int(np.max((1,noverlap)))
specs = []
for i in range(3):
    start = time.time()
    # spec, f, t = np.abs(stft(signal.detrend(data[i]), fs, int(nperseg)))
    # spec, f, t = np.abs(stft(signal.detrend(data[i]), fs, int(nperseg)))
    ### scipy
    # f, t, spec = signal.spectrogram(signal.detrend(data[i]), sampling_rate, nfft=1024, noverlap=noverlap, nperseg=nperseg)
    ### plt
    spec, f, t, _ = plt.specgram(data[i], NFFT=1024, Fs=sampling_rate, noverlap=noverlap, pad_to=nperseg)
    specs.append(spec)
    elapsed_time = time.time() - start
    print ("elapsed_time:\n{0}".format(elapsed_time))
# convert to 3-dimensional ndarray
specs = np.array(specs) #specs.shape: (3, 640, 527)
vmin = np.min(specs)
vmax = np.max(specs)
# add norm
specs = np.append(specs, [np.linalg.norm(specs, axis=0)], axis=0)
print(f.shape)
print(t.shape)
print(specs.shape)

### グラフ

for ax in range(3):
    plt.figure(dpi=dpi, figsize=narrow_figsize)
    plt.pcolormesh(t, f, specs[ax], cmap="jet")
    plt.ylabel("Frequency [Hz]")
    plt.xlabel("Time [sec]")
    cbar = plt.colorbar()
    cbar.ax.set_ylabel("Intensity [dB]")
    #cbar.set_clim(0, 1.1) #plt3.2まで
    #cbar.mappable.set_clim(0, 1.1) #plt3.3以降
    #plt.show()
    #plt.savefig("./test/" + str(ax) + "sp.png")
    plt.close()
    #print("saved: ", data_dir + "/" + remove_ext(filename) + str(ax) + sensor + "sp.png")

plt.figure(dpi=dpi, figsize=wide_figsize)
plt.pcolormesh(t, f, specs[3], cmap="jet")
plt.ylabel("Frequency [Hz]")
plt.xlabel("Time [sec]")
cbar = plt.colorbar()
cbar.ax.set_ylabel("Intensity [dB]")
#cbar.set_clim(0, 1.1) #plt3.2まで
#cbar.mappable.set_clim(0, 1.1) #plt3.3以降
#plt.show()
#plt.savefig("./test/norm_sp.png")
plt.close()

print("graph fin")

### いろいろ計算

recording = len(data[0]) / sampling_rate
f_offset = int(specs.shape[1] * 20 / 100)
print(f"f_offset: {f_offset}")
# print("s t {} {}".format(t[0], t[-1]))
peak_amp = np.max(specs[3, :, :])
peak_idx = np.where(specs[3] == peak_amp)
peak_freq = f[peak_idx[0][0]]
peak_time = t[peak_idx[1][0]]

i = np.unravel_index(np.argmax(specs[3, ]), specs[3].shape)
print(i)

print("=" * 20)

print("recording(s): {}".format(recording))
print("peak amplitude: {}  {}".format(peak_amp, peak_idx))
print("peak frequency(Hz): {}".format(peak_freq))
print("peaktime(s): {}".format(peak_time))

print("=" * 20)