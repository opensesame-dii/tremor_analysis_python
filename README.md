# tremor analysis

## setup (conda env creation)
Enter following commands (conda needed). Replace `ENV_NAME` with something.
```
conda env create -n ENV_NAME -f tremor.yml
pip install -r requirements.txt
```

## how to use

### conda activate  
Enter following command after setup. This command is needed every time you open a terminal.
```
conda activate ENV_NAME
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