import datetime as dt
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

# Database Setup
engine = create_engine("sqlite:///hawaii.sqlite", connect_args={'check_same_thread': False})
# Reflect an existing database into a new model
Base = automap_base()
# Reflect the tables
Base.prepare(engine, reflect=True)
# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station
# Create our session (link) from Python to the DB
session = Session(engine)
# Flask Setup
app = Flask(__name__)

# Flask Routes
@app.route("/")
def home():
    return (
        f"Welcome to the Hawaii Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/startdate/enddate"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the precipitation data for the last year"""
    # Date 1 year ago from last date in database
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    # Query for the date and precipitation for the last year
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= prev_year).all()
    # Dict with date as the key and prcp as the value
    precip = {date: prcp for date, prcp in precipitation}
    # Results
    return jsonify(precipitation=precip)

@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations."""
    # Unravel results into a 1D array and convert to a list
    results = session.query(Station.station).all()
    stations = list(np.ravel(results))
    # Results 
    return jsonify(stations=stations)

@app.route("/api/v1.0/tobs")
def temp():
    """Return the temperature observations(tobs) for previous year."""
    # Date 1 year ago from last date in database
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    # Query the primary station for all tobs from the last year
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= prev_year).all()
    # Unravel results into a 1D array and convert to a list
    temps = list(np.ravel(results))
    # Results
    return jsonify(temps=temps)

@app.route("/api/v1.0/temp/<startdate>") 
@app.route("/api/v1.0/temp/<startdate>/<enddate>")
def stats(startdate=None, enddate=None):
    """Return TMIN, TAVG, TMAX."""
    # Select statement
    sql = [func.min(Measurement.tobs), func.avg(
        Measurement.tobs), func.max(Measurement.tobs)]
    if not enddate:
        # Calculate TMIN, TAVG, TMAX for dates greater than start
        results = session.query(*sql).\
            filter(Measurement.date >= startdate).all()
    else:
        # Calculate TMIN, TAVG, TMAX with start and stop
        results = session.query(*sql).\
            filter(Measurement.date >= startdate).\
            filter(Measurement.date <= enddate).all()
    # Unravel results into a 1D array and convert to a list
    temps = list(np.ravel(results))
    # Results
    return jsonify(temps=temps)

if __name__ == '__main__':
    app.run(debug=True)