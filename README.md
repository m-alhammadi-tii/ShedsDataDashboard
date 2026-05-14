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

## Input file structure

Please always follow the same structure for the input files. This is very important, or the app will not work. This might require you checking format is correct in excel and simple pre-processing steps where you just coombine the data under the same columns and column names. 
