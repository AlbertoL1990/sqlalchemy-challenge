# Import the dependencies
import numpy as np
import pandas as pd
import datetime as dt
import re
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################

# Create engine to connect to hawaii.sqlite
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

# Reflect the existing database into a new model
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create a session to interact with the database
session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# Route 1: Homepage
@app.route("/")
def welcome():
    return (
        f"Welcome to the Hawaii Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start (enter as YYYY-MM-DD)<br/>"
        f"/api/v1.0/start/end (enter as YYYY-MM-DD/YYYY-MM-DD)"
    )

# Route 2: Precipitation data for the last year
@app.route("/api/v1.0/precipitation")
def precipitation():
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).\
        order_by(Measurement.date.desc()).all()

    precipitation_data = dict(results)
    print(f"Precipitation data: {precipitation_data}")
    return jsonify(precipitation_data)

# Route 3: List of stations
@app.route("/api/v1.0/stations")
def stations():
    query_result = session.query(Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).all()
    session.close()

    stations_list = []
    for station, name, latittude, longitude, elevation in query_result:
        station_info = {
            "Station": station,
            "Name": name,
            "Lat": latittude,
            "Lon": longitude,
            "Elevation": elevation
        }
        stations_list.append(station_info)

    return jsonify(stations_list)

# Route 4: Temperature observations for the most active station in the last year
@app.route("/api/v1.0/tobs")
def tobs():
    query_result = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= '2016-08-23').all()

    temperature_observations = []
    for date, tobs in query_result:
        temperature_observations.append({"Date": date, "Tobs": tobs})

    return jsonify(temperature_observations)

# Route 5: Temperature statistics for a specified start date or range
@app.route("/api/v1.0/<start>")
def get_temps_start(start):
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    session.close()

    temperatures = [{"Minimum Temperature": min_temp, "Average Temperature": avg_temp, "Maximum Temperature": max_temp} for min_temp, avg_temp, max_temp in results]
    return jsonify(temperatures)

@app.route("/api/v1.0/<start>/<end>")
def get_temps_start_end(start, end):
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    session.close()

    temperatures = [{"Minimum Temperature": min_temp, "Average Temperature": avg_temp, "Maximum Temperature": max_temp} for min_temp, avg_temp, max_temp in results]
    return jsonify(temperatures)

if __name__ == '__main__':
    app.run(debug=True)
