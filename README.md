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
- --row_start : enter the first row
- --column_start: enter the first column
- --sensors_num: enter the number of sensors used in the experiment.
- --encoding: enter the encoding of the file you want to analyze.  

For example, in this file, the data starts with 11 rows and 2 columns, has 3 sensors, and the encoding is Shift_jis, so please enter the following command.  

```
python app.py --row_start 11 --column_start 2 --sensors_num 3 --encoding shift_jis
```

### Operation  
1.  Press the browser button in Data I and select the file to be analyzed.
1. After a few moments, the graph and numbers will appear in a window.
1. You can also press the browser button on Data2 to load the other data.  

Switch between Data1 and Data2 in now-showing.  
Select the mode of analysis in the Analysis section and the sensor to be displayed in the Sensor section.For more information about modes, click here.


## Supported file format
csv, xlms, xlsx files are supported. Files must follow these rules.
- data series along with collumn
- 3-dimensional data
- data cell starts with 1A(not yet implemented)