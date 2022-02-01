# continuous analysis tool

## about this

app.py works for a file or a pair of files. On the other hand, this program, continuous.py works for all files at once and exports the results.

## how to use

### launch program
After doing `conda activation` and setting "current directory" to here, enter following command.
```
python continuous.py
```

### set files
After program launched, `data-YYYYMMDDhhmm` directory is created.
Create directiries per file pair in this directory, and place files in them.
csv, xlms, xlsx, are supported.
One or two file(s) must be placed in each directory.
Here is example.
```
├── sample01
│   ├── sample01-left.csv
│   └── sample01-right.csv
├── sample02
│   └── sample02.csv
└── sample03
    ├── sample03-left.xlms
    └── sample03-right.xlms
```

### run
Click "run" button.
You can check files which will be analized by clicking "scan" button.

If there are file placement errors, Dialog shows details.