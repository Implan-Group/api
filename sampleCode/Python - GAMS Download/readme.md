# Regional GAMS File Exporter

## Auth

You must create a `.env` file in the root of this project (in the same folder as `main.py`) that contains your IMPLAN credentials.
e.g.:
```env
# Development Settings
IMPLAN_USERNAME="{USERNAME}"
IMPLAN_PASSWORD="{PASSWORD}"
```
Where you should replace `{USERNAME}` and `{PASSWORD}` with your IMPLAN username and password.


## Usage
- There is a header section in `main.py` that must have some variables defined before execution:
  - `Aggregation Scheme Id` and `Dataset Id` for filtering to the correct data
  - An override to where the output report `.csv` files will be stored (defaults to the same directory as `main.py`)
- One those have been filled out, simply execute `main.py` as a script


## Links
### IMPLAN
- [Impact API Readme](https://github.com/Implan-Group/api/blob/main/impact/readme.md)
- [Other Python Workflow Examples](https://github.com/Implan-Group/api/tree/main/sampleCode/Python)
- [IMPLAN Support Site](https://support.implan.com)
- [Combined Regions Builder Template](https://support.implan.com/hc/en-us/articles/1260805784110-Combining-Regions)

### Python
#### Libraries used in this project
- [logging](https://docs.python.org/3/library/logging.html)
- [os](https://docs.python.org/3/library/os.html)
- [sys](https://docs.python.org/3/library/sys.html)
- [time](https://docs.python.org/3/library/time.html)
- [pathvalidate](https://pypi.org/project/pathvalidate/)
- [requests](https://pypi.org/project/requests/)
- [openpyxl](https://openpyxl.readthedocs.io/en/stable/)

- [Python Type Hints Cheat Sheet](https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html)
- [OpenPyxl - Reading + Writing Excel with Python](https://openpyxl.readthedocs.io/en/stable/)