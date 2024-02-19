# Import dependencies
import numpy as np
import datetime as dt
from pathlib import Path
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
db_path = Path("./Resources/hawaii.sqlite")
engine = create_engine(f"sqlite:///{db_path}")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# general use setup
#################################################
# these are used for queries based on the latest year in the dataset
oldest_date = session.query(Measurement.date).order_by(Measurement.date.asc()).first()[0]
latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]

prev_yr = str(int(latest_date[3]) - 1)
if prev_yr == -1: prev_yr = 9 # base 10 check
one_yr_prior = latest_date[:3] + prev_yr + latest_date[4:]

oldest_datetime = dt.date(int(oldest_date[:4]), int(oldest_date[5:7]), int(oldest_date[8:]))
latest_datetime = dt.date(int(latest_date[:4]), int(latest_date[5:7]), int(latest_date[8:]))

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/2016-01-01<br/>"
        f"/api/v1.0/2015-06-01/2015-12-31<br/>"
    )

@app.route("/api/v1.0/precipitation")
def yearly_precipitation():
    # Perform a query to retrieve the data and precipitation scores
    # order_by allows sorting by date
    relevant_dates = session.query(Measurement.date, Measurement.prcp).\
        filter(func.strftime("%Y-%m-%d", Measurement.date) <= latest_date).\
        filter(func.strftime("%Y-%m-%d", Measurement.date) >= one_yr_prior).\
        order_by(Measurement.date.asc()).all()
    dates_dict = {}
    # transform results into dict with dates as keys and precipitation amts as values
    for date in relevant_dates:
        dates_dict[date.date] = date.prcp

    return jsonify(dates_dict)

@app.route("/api/v1.0/stations")
def get_stations():
    # get list of station "names"
    stations = session.query(Station.station).distinct().all()
    return jsonify([s.station for s in stations])

@app.route("/api/v1.0/tobs")
def yearly_temps_most_active():
    station_cts = session.query(Measurement.station, func.count(Measurement.date)).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.date).desc()).all()
    most_active_station = station_cts[0][0]
    tobs_data = session.query(Measurement.tobs).\
        filter(func.strftime("%Y-%m-%d", Measurement.date) <= latest_date).\
        filter(func.strftime("%Y-%m-%d", Measurement.date) >= one_yr_prior).\
        filter(Measurement.station == most_active_station).\
        order_by(Measurement.date.asc()).all()
    return jsonify([t.tobs for t in tobs_data])

# for the routes below, we assume dates passed to start/end are formatted as:
# YYYY-MM-DD, eight characters that are all numbers and represent a date

@app.route("/api/v1.0/<start>")
def x(start):
    start_dt = dt.date(int(start[:4]), int(start[5:7]), int(start[8:]))

    if start_dt < oldest_datetime or start_dt > latest_datetime:
        error_msg = "ERROR: start date out of dataset date bounds"
        print(error_msg)
        return jsonify(error_msg)

    tobs_data = session.query(Measurement.tobs).\
        filter(func.strftime("%Y-%m-%d", Measurement.date) >= start_dt).\
        order_by(Measurement.date.asc()).all()
    tobs_dict = {
        "TMIN": np.min(tobs_data),
        "TMAX": np.max(tobs_data),
        "TAVG": np.average(tobs_data)
    }
    return jsonify(tobs_dict)

@app.route("/api/v1.0/<start>/<end>")
def y(start, end):
    start_dt = dt.date(start[:4], start[5:7], start[:8])
    end_dt = dt.date(end[:4], end[5:7], end[:8])

    if end_dt < start_dt:
        error_msg = "ERROR: end date before start"
        print(error_msg)
        return jsonify(error_msg)
    if start_dt < oldest_datetime or start_dt > latest_datetime:
        error_msg = "ERROR: start date out of dataset date bounds"
        print(error_msg)
        return jsonify(error_msg)
    if end_dt < oldest_datetime or end_dt > latest_datetime:
        error_msg = "ERROR: end date out of dataset date bounds"
        print(error_msg)
        return jsonify(error_msg)

    tobs_data = session.query(Measurement.tobs).\
        filter(func.strftime("%Y-%m-%d", Measurement.date) <= end_dt).\
        filter(func.strftime("%Y-%m-%d", Measurement.date) >= start_dt).\
        order_by(Measurement.date.asc()).all()
    tobs_dict = {
        "TMIN": np.min(tobs_data),
        "TMAX": np.max(tobs_data),
        "TAVG": np.average(tobs_data)
    }
    return jsonify(tobs_dict)

if __name__ == "__main__":
    app.run(debug=True)
