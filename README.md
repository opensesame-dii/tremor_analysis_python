# Tremor Analysis

## About this  
There are two programs, app.py and multiple.py. app.py works on one file or pair of files, while multiple.py works on all files at once and exports the results. The following is mainly an explanation of app.py, so if you are using multiple.py, please refer to README.md in the multiple_analysis directory after you are done with `conda activation`.

## How to use

### Conda instllation 
This program needs conda, which is environment for python.  

1. Download the installer from [here](https://www.anaconda.com/products/individual)
1. Launch the installer and follow the instructions. I recommend eneble `Add Anaconda3 to my PATH environment variable` and `Resister Anaconda3 as my default Python X.X` in `Advanced Options` section if you are using Windows.


### Setting up of conda environment for tremor analysis
1. Download this repository by `git clone` or clicking `"Code" button > Download ZIP` in this page. If you get program the latter, unzip the file.
1. Launch terminal(Windows: command prompt, Mac: Terminal)
1. Set "current directory" to the directory containing "app.py", "tremor.yml", and so on. Operation hints are here. [for Windows](https://www.howtogeek.com/659411/how-to-change-directories-in-command-prompt-on-windows-10/), [for Mac](https://www.earthdatascience.org/courses/intro-to-earth-data-science/open-reproducible-science/bash/bash-commands-to-manage-directories-files/)
1. Enter the following command(replace {YOUR_OPERATING_SYSTEM} with mac, windows or ubuntu). For example, if you use windows, `conda env create -n tremor -f tremor_windows.yml`
```
conda env create -n tremor -f tremor_{YOUR_OPERATING_SYSTEM}.yml
```
If this process finished successfully, below will be displayed.
```
done
#
# To activate this environment, use
#
#     $ conda activate tremor
#
# To deactivate an active environment, use
#
#     $ conda deactivate
```


If errors occur or your operating system is not in above list, enter the following commands line by line.
You may need to wait for a few seconds before executing the next step.


```
conda create -n tremor python=3.7
conda activate tremor
conda install matplotlib=3.1.3
conda install numpy=1.21.2
conda install pandas=1.3.5
conda install tk=8.6.11
conda install scipy=1.7.3 
```

Hints
- If `Proceed ([y]/n)?` is displayed, enter "y".

- If `WARNING: A newer conda version exists.` is displayed, enter `conda update -n base -c defaults conda` then enter install command again.

### Confirm
Enter the following command.
```
conda info -e
```
Then you may see the following outputs on your terminal. The outputs might differ slightly based on your environment. If you see a row starting with "tremor", setting up was finished successfully.

```
# conda environments:
#
base                  *  C:\Users\Alice\anaconda3
tremor                   C:\Users\Alice\anaconda3\envs\tremor
```

### Conda activation
Enter following command after setup. This command is needed every time you open a terminal. 
```
conda activate tremor
```

The new row starting with "(tremor)" will appear. The name of the environment will be displayed in parentheses. Here is example.
```
(tremor) C:\Users\Alice>    <- windows
(tremor) /home/Alice    <- mac
```

### Launch program
After set "current directory" to this repository by using "cd" command, enter the following command. 
```
python app.py --row_start xx --column_start xx --sensors_num xx --encoding xx
```  
Please fill in the "xx" according to the format of your file according to the following rules.  
- `--row_start` : enter the first row
- `--column_start` : enter the first column
- `--sensors_num` : enter the number of sensors used in the experiment.
- `--encoding` : enter the encoding of the file you want to analyze.  

For example, [in this file](./analysis_samples), the data starts with 11 rows and 2 columns, has 3 sensors, and the encoding is Shift_jis, so please enter the following command.  

```
python app.py --row_start 11 --column_start 2 --sensors_num 3 --encoding shift_jis
```  
You can also start it with `python app.py` without any configuration. In this case, it will automatically be set to `python app.py--row_start 1 --column_start 1 --sensors_num 3 --encoding utf-8`.


### Operation  
1.  Press the browser button in Data I and select the file to be analyzed.
1. After a few moments, the graph and numbers will appear in a window.
1. You can also press the `Browse` button on Data2 to load the other data.  

Switch between Data1 and Data2 in now-showing.  
Select the mode of analysis in the Analysis section and the sensor to be displayed in the Sensor section.
For more information about modes, [click here](##Modes).


## Supported file format
csv, xlms, xlsx files are supported. Files must follow these rules.
- data series along with column.
- data from 3-dimensional sensor. any number of sensors can be used. (column number must be a multiple of 3)

## Modes
This program provides two modes of graph export.

- Spectral Amplitude   
This is based on Fourier Transform using [scipy.signal.spectrogram(complex mode)](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.spectrogram.html).  
Fourier Transform is a major method of frequency analysis.
Below is Fourier Transform equation.  
![](https://latex.codecogs.com/gif.image?%5Cdpi%7B110%7D%20%5Cbg_white%20X_%7B%5Comega%7D%20=%20%5Cint_%7B-%20%5Cinfty%7D%5E%7B%5Cinfty%7D%20x(t)%20e%5E%7B-i%5Comega%20t%7D%20dt)  
Omega is a normalized frequency, so multiplying by sampling rate, we can obtain the spectra in each frequency.
We focused on the difference in time axis, so we use STFT(short-time Fourier Transform).
In this method, segment the data series and perform a Fourier transform on each of them.  
Data series are passed to scipy.signal.spectrogram linearly detrended.
Hamming Window is used as window function, `nperseg`(points in Short-Time Fourier Transform segment) is the product of `segment duration` and `sampling rate`, `noverlap` is 75% of `nperseg`, and `nfft` is 2^12.
Then, Spectral Amplitude is calculated as shown below where `n` is the number of samples in the time axis and `X` is complex spectrum.
This means that Spectral Amplitude is average of the amplitude of each frequency on the time axis.  
![](https://latex.codecogs.com/gif.image?%5Cdpi%7B110%7D%20%5Cbg_white%20Spectral%20Amplitude_%7Bf%7D%20=%20%5Cfrac%7B%5Csum_%7Bt%7D%5E%7B%7D%20abs(X_%7Bt,%20f%7D)%7D%7Bn%7D)



- Spectrogram  
This is based on Fourier Transform using [scipy.signal.spectrogram(magnitude mode)](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.spectrogram.html).
Data series are passed to scipy.signal.spectrogram linearly detrended.
Hamming Window is used as window function, `nperseg`(points in Short-Time Fourier Transform segment) is the product of `segment duration` and `sampling rate`, and other parameters (`noverlap, nfft`) are determined in accordance with Elble & McNames [1].
`noverlap, nfft` are obtained by the following equation(N: number of data points).  
![](https://latex.codecogs.com/gif.image?%5Cbg_white%20%5C%5CL%20=%20min(N,%20nperseg)%20%5C%5CnTimes%20Spectrogram%20=%20500%20%5C%5Cnoverlap%20=%20max(1,%20ceil(%5Cfrac%7B2L%20-%20N%7D%7BnTimesSpectrogram%20-%201%7D))%20%5C%5Cnfft%20=%202%5E%7B12%7D)  
Then, Spectral Amplitude is calculated by time avarage of spectrogram in each frequency.  



## Calculated values

-  Spectrogram Peak Amplitude(sp_peak_amp)  
Maximum value in `Spectrogram` mode.


- Spectrogram Peak Frequency(sp_peak_freq)  
Frequency at which the amplitude is maximum in `Spectrogram` mode.


- Spectrogram Peak Time(sp_peak_time)  
Time at which the amplitude is maximum in `Spectrogram` mode.


- Whole Peak Amplitude(sa_peak_amp)  
Maximum value in `Spectral Amplitude` mode.


- Whole Peak Frequency(sa_peak_freq)  
Frequency at which the amplitude is maximum in `Spectral Amplitude` mode.


- Full-width Half Maximum(sa_fwhm)  
Frequency range at which frequency exceed half of the maximum value.
Linear interpolation is used.


- Half-width Power(sa_hwp)  
Integral value at which frequency exceed half of the maximum value.


- Tremor Stability Index(sa_tsi)  
Quartile range of difference in frequency for each tremor.
Each frequency is reciprocal of the period of each oscillation.


- FT(Fourier Transforms) coherence integral  
Coherence is the ratio of auto spectra and cross spectra.
Coherence of each frequency is calculated by [matplotlib.mlab.cohere](https://matplotlib.org/stable/api/mlab_api.html#matplotlib.mlab.cohere).
In this program, `nfft` is 2^10 and `noverlap` is 50% of `nfft`(2^9).  
![](https://latex.codecogs.com/gif.image?%5Cdpi%7B110%7D%20%5Cbg_white%20Coherence(f)%20=%20%5Cfrac%7B%7C(X_%7Bf%7D%20Y_%7Bf%7D%5E%7B*%7D)%7C%5E2%7D%7B(X_%7Bf%7D%20X_%7Bf%7D%5E%7B*%7D)(Y_%7Bf%7D%20Y_%7Bf%7D%5E%7B*%7D)%7D)  
FT coherence is the integral value at the frequency at which the coherence exceeds a thresold.
We use 95% confidence interval(CI) as a thresold. [2, 3]  
![](https://latex.codecogs.com/gif.image?%5Cdpi%7B110%7D%20%5Cbg_white%20%5C%5C%20CI%20=%201%20-%200.05%5E%7B%5Cfrac%7B1%7D%7B(N%20-%20noverlap)/(nfft-noverlap)-1%7D%7D%20%5C%5C%20FT%20%20coherence%5C;%20integral%20=%20%5Cint_%7Bf%5Cin%20coherence(f)%3ECI%7D%5E%7B%7D%20coherence%20%5C;%20df)  
This value will only be calculated when data are imported in pairs.

# References
1. Rodger J. Elble & James McNames. Using Portable Transducers to Measure Tremor Severity https://tremorjournal.org/article/10.5334/tohm.320/
1. Anne Sofie Bøgh Malling, Bo Mohr Morberg, Lene Wermuth, Ole Gredal, Per Bech & Bente Rona Jensen. The effect of 8 weeks of treatment with transcranial pulsed electromagnetic fields on hand tremor and inter-hand coherence in persons with Parkinson’s disease https://jneuroengrehab.biomedcentral.com/articles/10.1186/s12984-019-0491-2
1. K Terry & L Griffin. How computational technique and spike train properties affect coherence detection https://pubmed.ncbi.nlm.nih.gov/17976736/