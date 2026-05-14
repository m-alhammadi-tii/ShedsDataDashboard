# Shed Dashboard Refactored

Run the app from this folder:

```bash
streamlit run app.py
```

## File structure

- `app.py` - main Streamlit app only
- `config.py` - sensor groups, constants, delta formulas
- `data_io.py` - Excel loading and column grouping
- `filters.py` - date and time-window filters
- `cleaning.py` - temperature and solar cleaning
- `statistics.py` - summaries, deltas, processing pipeline
- `plotting.py` - plot functions
- `exports.py` - Excel export helpers
- `reporting.py` - Word report generation

## Fix included

The temperature cleaner now converts sensor data to numeric before filtering. This fixes errors like:

```text
TypeError: '<' not supported between instances of 'str' and 'float'
```

This happens when Excel contains repeated text/header rows such as `Value` inside sensor columns.

## Input file structure

Please always follow the ssame structure for the input files. this is very important. or the app will not work. This might require you checking format is correct in excel and simple pre-processing steps where you just coombine the data under the same columns and columnb names. 