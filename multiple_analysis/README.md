# Continuous analysis tool

## About this

app.py works for a file or a pair of files. On the other hand, this program, multiple.py works for all files at once and exports the results.

## How to use

### Launch program
After doing `Conda activation` and setting "current directory" to here "continuous_analize", enter the following command.
```
python multiple.py
```

### Set files
After the program was launched, `data-YYYYMMDDhhmm` (YYYY: year, MM: month, DD: date, hh: hour, mm: minute) directory is created in the folder, "multiple_analysis".
Create directiries per file pair in this directory, and place files in them.
csv, xlms, xlsx, are supported.
One or two file(s) must be placed in each directory.
Here is example.
```
data-YYYYMMDDhhmm
├── sample01
│   ├── sample01-left.csv
│   └── sample01-right.csv
├── sample02
│   └── sample02.csv
└── sample03
    ├── sample03-left.xlms
    └── sample03-right.xlms
```

### Scan and Run
You can check files which will be analized by clicking "scan" button. 
Click "run" button.
When finished, result.csv is created in `data-YYYYMMDDhhmm` and preview picutures are created in each directory.

If there are file placement errors, Dialog shows details.