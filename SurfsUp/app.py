# Import the dependencies.
import numpy as np
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
#Define function to calculate one year from the most recent date in Measurement data
def prev_year():
    #Create session
    session = Session(engine)
    
    #Query the most recent date in the Measurement dataset
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    #Create variable to store the last date
    last_date = dt.datetime.strptime(most_recent_date[0], '%Y-%m-%d')
    #Determine one year by subtracting a year from the last date in the Measurement dataset
    one_year = dt.date(last_date.year-1, last_date.month, last_date.day)

    #Close session
    session.close()

    #Return the one year date
    return(one_year)

#Define what the user sees when reaching the homepage
@app.route("/")
def welcome():
    return (
        f"Welcome to the Hawaii Weather Station API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )

#Define what the user sees when reaching the preciptation api
@app.route("/api/v1.0/precipitation")
def precipitation():

    #Create session
    session = Session(engine)

    #Query the Measurement date and Measurement precipitation for one year
    prcp_results = session.query(Measurement.date, Measurement.prcp).\
                filter(Measurement.date >= prev_year()).all()
    
    #Close session
    session.close()

    #Create a dictionary from the query results and append to a precipitation list
    prcp_list = []
    for date, prcp in prcp_results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        prcp_list.append(prcp_dict)

    #Return the jsonified precipitation list
    return jsonify(prcp_list)

#Define what the user sees when reaching the stations api
@app.route("/api/v1.0/stations")
def stations():

    #Create session
    session = Session(engine)

    #Query all stations in Stations dataset
    station_results = session.query(Station.station).all()

    #Close session
    session.close()

    #Convert the station result tuples into a normal list
    station_list = list(np.ravel(station_results))

    #Return the jsonified station list
    return jsonify(station_list)

#Define what the user sees when reaching the tobs api
@app.route("/api/v1.0/tobs")
def tobs():

    #Create session
    session = Session(engine)

    #Query the Measurement date and Measurement Tobs for Station USC00519281 for one year
    tobs_results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == 'USC00519281').\
                    filter(Measurement.date >= prev_year()).all()
    
    #Close session
    session.close()

    #Create a dictionary from the query results and append to a tobs list
    tobs_list = []
    for date, tobs in tobs_results:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        tobs_list.append(tobs_dict)
    
    #Return the jsonified tobs list
    return jsonify(tobs_list)

#Define what the user sees when reaching the start and start/end api
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def calc_temps(start=None, end=None):

    #Create session
    session = Session(engine)

    #Create a list to query the min, max, and avg function of the Measurement tobs data
    sel = [func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)]

    #Check if there is an end date
    if end == None:
        
        #Query using the min, max, avg list and all data after start date
        start_date = session.query(*sel).filter(Measurement.date >= start).all()

        #Convert start date results into a normal list
        start_list = list(np.ravel(start_date))

        #Return jsonified start list
        return jsonify(start_list)
    
    else:

        #Query using the min, max, avg list and all dates between start and end dates
        start_end_date = session.query(*sel).filter(Measurement.date >= start).\
                            filter(Measurement.date <= end).all()
        
        #Convert the start and end date results into a normal list
        start_end_list = list(np.ravel(start_end_date))

        #Return jsonified start and end date list
        return jsonify(start_end_list)
    
    #Close session
    session.close()


if __name__ == '__main__':
    app.run(debug=True)