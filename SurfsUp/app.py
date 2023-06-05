# Import the dependencies.
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import os
from flask import Flask, jsonify, request
import datetime as dt

#################################################
# Database Setup
#################################################
#engine = create_engine("sqlite:///"+os_file_path)
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
#Dictionary of routes
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    return (
        f'Welcome to the Climate API!<br/>'
        f'Available Routes:<br/>'
        f'/api/v1.0/precipitation<br/>'
        f'/api/v1.0/stations<br/>'
        f'/api/v1.0/tobs<br/>'
        f'/api/v1.0/start<br/>'
        f'/api/v1.0/start/end<br/>'
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    
    # Starting from the most recent data point in the database. 
    most_recent_date = session.query(func.max(Measurement.date)).one()
    date_ = dt.date.fromisoformat(most_recent_date[0])

    # Calculate the date one year from the last date in data set.
    one_year_date = date_ - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    rec = session.query(Measurement.date, Measurement.prcp) \
                 .filter(Measurement.date >= str(one_year_date)) \
                 .all()
    
    session.close()
    return jsonify(dict(rec))
    
@app.route("/api/v1.0/stations")
def stations():
    rec = session.query(Station.station, Station.name) \
                                    .order_by(Station.station) \
                                    .all() 

    session.close()
    return jsonify(dict(rec))

@app.route("/api/v1.0/tobs")
def tobs():
    most_active_station = session.query(Measurement.station) \
                              .group_by(Measurement.station) \
                              .order_by(func.count(Measurement.station).desc()) \
                              .first() 
    
    most_recent_date = session.query(func.max(Measurement.date)) \
                              .filter(Measurement.station == most_active_station[0]) \
                              .one()
    
    date_ = dt.date.fromisoformat(most_recent_date[0])
    one_year_date = date_ - dt.timedelta(days=365)

    tobs = session.query(Measurement.date, Measurement.tobs) \
                  .filter(Measurement.station == most_active_station[0]
                         ,Measurement.date >= str(one_year_date)) \
                  .order_by(Measurement.date) \
                  .all() 

    session.close()
    
    return jsonify(dict(tobs))
    
@app.route("/api/v1.0/start/<start>")
def start(start):
       
    rec = session.query(func.min(Measurement.tobs) \
                       ,func.avg(Measurement.tobs)\
                       ,func.max(Measurement.tobs)) \
                 .filter(Measurement.date >= start) \
                 .one() 

    session.close()
    results = {'startDate':start, 'min': str(rec[0]), 'avg': str(rec[1]), 'max': str(rec[2])}
    return jsonify(results)

@app.route("/api/v1.0/start/end/<start>/<end>")
def start_end(start, end):
    
    rec = session.query(func.min(Measurement.tobs) \
                       ,func.avg(Measurement.tobs) \
                       ,func.max(Measurement.tobs)) \
              .filter(Measurement.date >= start
                     ,Measurement.date <= end) \
              .one() 

    session.close()
    results = {'startDate':start,'endDate':end, 'min': str(rec[0]), 'avg': str(rec[1]), 'max': str(rec[2])}
    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)
