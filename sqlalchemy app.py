# 1. import Flask and all the other dependencies
from flask import Flask, jsonify

import numpy as np
import pandas as pd
import datetime as dt
from dateutil.relativedelta import relativedelta

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
# 2. Create an app, being sure to pass __name__
app = Flask(__name__)

#Create an engine etc
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)
#get firstdate and lastdate to use later in the program
lastdate = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
lastdate = dt.datetime.strptime(lastdate,'%Y-%m-%d').date()

firstdate = lastdate
delta = relativedelta(months = 12)
firstdate = firstdate - delta

#Calc_temps function to call alter
# def calc_temps(start_date, end_date):  #can't use this because it will try to call a session outside of where it was created,
#which results in a crash when using flask like this 
#     return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

# * `/`

  # * Home page.

  # * List all routes that are available.






@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    test = "/api/v1.0/<start>/<end>, "
    return (
        "Available webpages: <br>"
        "/api/v1.0/precipitation <br>"
        "/api/v1.0/stations <br> "
        "/api/v1.0/tobs <br> "
        "/api/v1.0/(start) <br> " #replace <start> and <end> with specific dates!
        "Usage - replace start with a date in yyyy-mm-dd format <br>"
        "/api/v1.0/(start)/(end) <br>"
        "Usage - replace start and end with a date in yyyy-mm-dd format <br>"
        "(start) and (start)/(end) return min temperature as 0, avg as 1, max as 2"
    )
# "Available webpages: "
        # "/api/v1.0/precipitation, "
        # "/api/v1.0/stations, "
        # "/api/v1.0/tobs, "
        # "/api/v1.0/<start>, "
        # "/api/v1.0/<start>/<end>, "

        # * `/api/v1.0/precipitation`

  # * Convert the query results to a Dictionary using `date` as the key and `prcp` as the value.

  # * Return the JSON representation of your dictionary.
@app.route("/api/v1.0/precipitation")
def precipitation():
    print("Server received request for 'Precipitation' page...")
    
    session = Session(engine)

    precipQuery = session.query(Measurement.date, Measurement.prcp).order_by(Measurement.date.desc()).filter(Measurement.date > firstdate).all() 
    #how am I supposed to make a decent dictionary with this when we have multiple values for the same dates,
    #resulting in overwriting the values for each key?
    #I'm really not sure if this is the query the directions actually wanted, but it seems like the only precipitation related one we did
    
    #return dt.datetime.strftime(lastdate,'%Y-%m-%d') + "<br>" + str(firstdate)
    return dict(precipQuery)
   #precipQuery = session.query(Measurement.date, Measurement.prcp).order_by(Measurement.date.desc()).filter(Measurement.date > firstdate).all()
    
# * `/api/v1.0/stations`

  # * Return a JSON list of stations from the dataset.

@app.route("/api/v1.0/stations")
def stations():
    print("Server received request for 'Stations' page...")
    session = Session(engine)
    #session.query(func.count(Station.id)).all()[0][0]
    
    #get the names of each station and return them as json
    stations = session.query(Station.name).all()
    return jsonify(stations)

# * `/api/v1.0/tobs`
  # * query for the dates and temperature observations from a year from the last data point.
  # * Return a JSON list of Temperature Observations (tobs) for the previous year.
@app.route("/api/v1.0/tobs") 
def temperature():
    print("Server received request for 'Temperature' page...")
    session = Session(engine)
    
    #tempteratures = session.query().filter(Measurement.date > firstdate).all()
    
    #Return a JSON list of temperuatre observations for the previous year
    #another query I'm not particularly sure of, since again we'll have multiple results per date, but a specific station was never specified either
    tempQuery = session.query(Measurement.date, Measurement.tobs).order_by(Measurement.date.asc()).filter(Measurement.date > firstdate).all()
    return jsonify(tempQuery)

# * `/api/v1.0/<start>` and `/api/v1.0/<start>/<end>`

  # * Return a JSON list of the minimum temperature, the average temperature,
  #and the max temperature for a given start or start-end range.

  # * When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all 
  #dates greater than and equal to the start date.

  # * When given the start and the end date, calculate the `TMIN`, `TAVG`, and 
  #`TMAX` for dates between the start and end date inclusive.
@app.route("/api/v1.0/<start>") #figure out the actual route to put here
def start(start):
    print("Server received request for 'Start Date' page...")
    session = Session(engine)
    #values = calc_temps(start, lastdate) - doesn't seem like it likes access of the session coming from a function accessed outside of this function
    #change the labels of 0, 1, and 2 to min, avg, and max. Can simply return jsonify(values) if these labels are unwanted
    keys = ("min", "avg", "max")
    values = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= lastdate).all()[0]
    result = {k:v for k,v in zip(keys,values)}
    return jsonify(result)
    
@app.route("/api/v1.0/<start>/<end>")
def startend(start,end):
    print("Server received request for 'Start/End Date' page...")
    session = Session(engine)
    keys = ("min", "avg", "max")
    values = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()[0]
    result = {k:v for k,v in zip(keys,values)}
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)