# tremor analysis

## how to use

### conda instllation 
This program needs conda, which is environment for python.  

1. Download the installer from [here](https://www.anaconda.com/products/individual)
1. Launch the installer and follow the instructions. I recommend eneble `Add Anaconda3 to my PATH environment variable` and `Resister Anaconda3 as my default Python X.X` in `Advanced Options` section if you are using Windows.


### seting up
1. Download this repository by `git clone` or clicking `"Code" button > Download ZIP` in this page. If you get program the latter, unzip the file.
1. Launch terminal(Windows: command prompt, Mac: Terminal)
1. Set "current directory" to the directory containing "app.py", "tremor.yml", and so on. Operation hints are here. [for Windows](https://www.howtogeek.com/659411/how-to-change-directories-in-command-prompt-on-windows-10/), [for Mac](https://www.earthdatascience.org/courses/intro-to-earth-data-science/open-reproducible-science/bash/bash-commands-to-manage-directories-files/)
1. Enter following commands.
```
conda env create -n tremor -f tremor.yml
```


### conda activation
Enter following command after setup. This command is needed every time you open a terminal.
```
conda activate trenor
```

### launch program
After set "current directory" to this repository by using "cd" command, enter following command.
```
python app.py
```

## supported file format
csv, xlms, xlsx files are supported. Files must follow these rules.
- data series along with collumn
- 3-dimensional data
- data cell starts with 1A(not yet implemented)