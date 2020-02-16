import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from dateutil.relativedelta import relativedelta
import datetime as dt

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitations<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )

@app.route("/api/v1.0/precipitations")
def precipitations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of past 12 months precip"""
    # Query the precip for the past 12 months
    
    result = session.query(func.max(Measurement.date)).one()
    for row in result:
        start_date=row
    
    sub_months = dt.datetime.strptime(start_date, '%Y-%m-%d') + relativedelta(days=-366)

    last_12 = pd.read_sql(session.query(Measurement.date,Measurement.prcp,\
        func.extract('year',Measurement.date).label('year'),\
            func.extract('week',Measurement.date).label('week')).\
                filter(Measurement.date >= sub_months).\
                    order_by(Measurement.date.asc()).statement,engine)

    session.close()

    # Convert list of tuples into normal list
    all_precip = list(np.ravel(last_12))

    return jsonify(all_precip)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of weather stations"""
    # Query the weather stations
    
    station_measurements = pd.read_sql(session.query(Measurement.station.\
        distinct()).\
                statement, engine)

    session.close()

    # Convert list of tuples into normal list
    stations = list(np.ravel(station_measurements))

    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    result = session.query(func.max(Measurement.date)).one()
    for row in result:
        start_date=row
    
    sub_months = dt.datetime.strptime(start_date, '%Y-%m-%d') + relativedelta(days=-366)    

    """Return a list of temperature observations"""
    # Query the weather stations
    last_12 = pd.read_sql(session.query(Measurement.station,\
        Measurement.date,Measurement.prcp).\
               filter(Measurement.date >= sub_months).\
                   filter(Measurement.station == 'USC00519281').\
                   order_by(Measurement.date.asc()).statement, engine)

    session.close()

    # Convert list of tuples into normal list
    tobs = list(np.ravel(last_12))

    return jsonify(tobs)

@app.route("/api/v1.0/<start_date>")
def start(start_date):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return the min max and avg temp from given start date"""
    # Query the weather stations
    start_temp = pd.read_sql(session.query(Measurement.station,\
        func.min(Measurement.tobs).label('min_temperature'),\
            func.max(Measurement.tobs).label('max_temperature'),\
                func.avg(Measurement.tobs).label('avg_temperature')).\
                    filter(Measurement.date >= start_date).\
                        group_by(Measurement.station).\
                            statement, engine)

    session.close()

    # Convert list of tuples into normal list
    start = list(np.ravel(start_temp))

    return jsonify(start)

@app.route("/api/v1.0/<start_date>/<end_date>")
def start_end(start_date,end_date):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return the min max and avg temp from given start date"""
    # Query the weather stations
    start_end_temp = pd.read_sql(session.query(Measurement.station,\
        func.min(Measurement.tobs).label('min_temperature'),\
            func.max(Measurement.tobs).label('max_temperature'),\
                func.avg(Measurement.tobs).label('avg_temperature')).\
                    filter(Measurement.date >= start_date).\
                        filter(Measurement.date <= end_date).\
                            group_by(Measurement.station).\
                            statement, engine)

    session.close()

    # Convert list of tuples into normal list
    start_end = list(np.ravel(start_end_temp))

    return jsonify(start_end)

if __name__ == '__main__':
    app.run(debug=True)