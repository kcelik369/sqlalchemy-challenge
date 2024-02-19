# sqlalchemy-challenge
All relevant files are present in the SurfsUp directory. CSV and SQLite files are found at "EmployeeSQL/Resoureces".
1. The Jupyter notebook for part 1 of the assignment is called "climate_starter.ipynb"
1. The Flask application code can be found in "app.py", and is run with the command "python app.py"
    - When accessing routes of the Flask app with dates in the route, the format expected is "YYYY-MM-DD"
    - There is error checking on if the date is within the bounds of the relevant dataset, but not if the date itself is valid. If you pass an invalid date, expect an error.