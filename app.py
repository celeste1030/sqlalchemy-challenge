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
        f"Stations: /api/v1.0/stations</<br/>"
        f"Dated temperature observations for most active station for most recent year in data: /api/v1.0/tobs<br/>"
        f"Temperature normals from the given date: /api/v1.0/yyyy-mm-dd<br/>"
        f"Temperature normals for the given date range: /api/v1.0/<start> and /api/v1.0/<start>/<end><br/>"
    )

#Precipitation
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
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
        prcp_dict[date] = prcp
        prcp_list.append({f"{date}": number})

    return (
        jsonify(prcp_list)
    )
### Return a JSON list of stations from the dataset.

@app.route("/api/v1.0/stations")
def stations():
    # Create  session
    session = Session(engine)

    # Query stations
    stations = session.query(Station.station).all()

    session.close()

    return jsonify(stations)

