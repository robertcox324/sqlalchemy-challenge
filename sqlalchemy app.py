#import Flask and all the other dependencies
from flask import Flask, jsonify

import numpy as np
import pandas as pd
import datetime as dt
from dateutil.relativedelta import relativedelta

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
#Create an app
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

#Create homepage that lists all available routes and how to use them
@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    test = "/api/v1.0/<start>/<end>, "
    return (
        "Available webpages: <br>"
        "/api/v1.0/precipitation <br>"
        "/api/v1.0/stations <br> "
        "/api/v1.0/tobs <br> "
        "/api/v1.0/(start) <br> "
        "Usage - replace start with a date in yyyy-mm-dd format <br>"
        "/api/v1.0/(start)/(end) <br>"
        "Usage - replace start and end with a date in yyyy-mm-dd format <br>"
    )
#Convert the precipitation query's results to a dictionary, then return the JSON representation of the dictionary.
@app.route("/api/v1.0/precipitation")
def precipitation():
    print("Server received request for 'Precipitation' page...")
    
    session = Session(engine)

    precipQuery = session.query(Measurement.date, Measurement.prcp).order_by(Measurement.date.desc()).filter(Measurement.date > firstdate).all() 
    #how am I supposed to make a decent dictionary with this when we have multiple values for the same dates,
    #resulting in overwriting the values for each key?
    #I'm really not sure if this is the query the directions actually wanted, but it seems like the only precipitation related one we did
    return jsonify(dict(precipQuery))  

#return a JSON list of all the stations in the dataset
@app.route("/api/v1.0/stations")
def stations():
    print("Server received request for 'Stations' page...")
    session = Session(engine)
    
    #get the names of each station and return them as json
    stations = session.query(Station.name).all()
    return jsonify(stations)

#query temperature observations for the past year then return them in a JSON list
@app.route("/api/v1.0/tobs") 
def temperature():
    print("Server received request for 'Temperature' page...")
    session = Session(engine)

    #another query I'm not particularly sure of, since again we'll have multiple results per date (less of a problem since not a dictionary this time), but a specific station was never specified either
    tempQuery = session.query(Measurement.date, Measurement.tobs).order_by(Measurement.date.asc()).filter(Measurement.date > firstdate).all()
    return jsonify(tempQuery)

#return a JSON list of min, avg, and max temperature between a given start date and the last observed date
@app.route("/api/v1.0/<start>") 
def start(start):
    print("Server received request for 'Start Date' page...")
    session = Session(engine)
    #change the labels of 0, 1, and 2 to min, avg, and max. Can simply return jsonify(values) if these labels are unwanted
    keys = ("min", "avg", "max")
    values = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= lastdate).all()[0]
    result = {k:v for k,v in zip(keys,values)}
    return jsonify(result)

#return a JSON list of min, avg, and max temperature between a given start and end date
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