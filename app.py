import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
import numpy as np
from flask import Flask, jsonify

###Create and connect to databases

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

###Setup Flask

app = Flask(__name__)

### Routes 
### Homepage

@app.route("/")
def homepage():
   return (
        f"<h1>sqlalchemy challenge<h1/>"
        f"<h3>Routes:<h3/>"
        f"Precipitation data for most recent year of data: /api/v1.0/precipitation<br/>"
        f"Stations: /api/v1.0/stations<br/>"
        f"Dated temperature observations for most active station for most recent year in data: /api/v1.0/tobs<br/>"
        f"Temperature normals for the given date range: /api/v1.0/YYYY-MM-DD and /api/v1.0/YYYY-MM-DD/YYYY-MM-DD<br/>"
    )

#Precipitation
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create session
    session = Session(engine)

    # query for last date in data

    max_dateq = session.query(Measurement).order_by(Measurement.date.desc()).first()
    max_date = dt.datetime.strptime(max_dateq.date, '%Y-%m-%d')
    
    # Calculate the date 1 year ago from the last data point in the database
    min_date = max_date - dt.timedelta(days=365)

    min_date

    #query for last year of data

    sel = [func.avg(Measurement.prcp), Measurement.date]

    prcp_avg = session.query(*sel).\
        filter(Measurement.date >= min_date).\
        group_by(Measurement.date).all()
    prcp_avg

    session.close()

    prcp_list = []

    for date, prcp in prcp_avg:
        prcp_dict = {}
        #prcp_dict[date] = prcp
        prcp_list.append({f"{date}": prcp})

    session.close()

    return (
        jsonify(prcp_list)
    )
    
### Stations

@app.route("/api/v1.0/stations")
def stations():
    # Create  session
    session = Session(engine)

    # Query stations
    stations = session.query(Station.station).all()

    session.close()

    return jsonify(stations)

### TOBS

@app.route("/api/v1.0/tobs")
def tobs():
    #create session
    session = Session(engine)

    # Design a query that lists all stations with their corresponding observation count in descending order.


    station_obv = session.query(Measurement.station, func.count(Measurement.tobs)).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).all()

    print(station_obv)

    # Choose the station with the highest number of temperature observations.

    most_active = "USC00519281"

    print("----------------------------------------")
    print(f"The most active station is {most_active}.")

    min_date = dt.datetime(2016, 8, 23)

    tobs = session.query(Measurement.tobs).\
    filter(Measurement.station == most_active).\
    filter(Measurement.date >= min_date).all()

    session.close()

    total_tobs = []

    for t in tobs:
        total_tobs.append(t[0])
    total_tobs
    
    return jsonify(total_tobs)

### Start and end date queries

@app.route("/api/v1.0/<start>")
def first_date(start):
    session = Session(engine)
    
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()

    session.close()

    tobs_info = list(np.ravel(results))

    return jsonify(tobs_info)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    
    session = Session(engine)

    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    session.close()

    tobs_info = list(np.ravel(results))

    return jsonify(tobs_info)

if __name__ == '__main__':
    app.run(debug=True)