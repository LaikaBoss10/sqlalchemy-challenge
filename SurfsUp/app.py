# Import the dependencies.
from flask import Flask, jsonify

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import numpy as np
import pandas as pd
import datetime as dt
from datetime import datetime
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
# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Find the most recent date in the data set.
    most_recent_date = session.query(func.strftime(Measurement.date)).order_by(Measurement.date.desc()).first()
    # Print Statement for most recent date as a row object
    print(most_recent_date)
    # Convert date to format to determine the date 12 months ago
    most_recent_date_string = str(most_recent_date)
    most_recent_date_string = most_recent_date_string.strip("(),'")
    ### Find the date twelve months ago
    twelve_months_ago = datetime.strftime(datetime.strptime(most_recent_date_string, '%Y-%m-%d') - dt.timedelta(days=365), '%Y-%m-%d')
    # Perform a query to retrieve the data and precipitation scores
    last_12_months_data = session.query(func.strftime(Measurement.date),Measurement.prcp).filter(Measurement.date >= twelve_months_ago).order_by(Measurement.date.desc()).all()
    # close session
    session.close()
    # make a data frame
    last_12_months_data_df = pd.DataFrame(last_12_months_data, columns=['Date', 'Precipitation'])
    # sort data frame in ascending order
    last_12_months_data_df_asc = last_12_months_data_df.sort_values(by='Date')
    # convert data frame to a list of dictionaries
    dict_data = last_12_months_data_df_asc.to_dict(orient='records')
    # iterate through the list and make a single dictionary containing Dates and Precipitation
    result_dict = {item['Date']: item['Precipitation'] for item in dict_data}
    # return dictionary as json.
    return jsonify(result_dict)
    
@app.route("/api/v1.0/stations")
def stations():
    # query the unique station Ids from measurement table
    stations_query = session.query(Measurement.station).distinct()
    # close session
    session.close()
    # put station ids in a row
    unique_ids = [name[0] for name in stations_query]
    # return list as json.
    return jsonify(unique_ids)
    
    
@app.route("/api/v1.0/tobs")
def tobs():
    # Find the most recent date in the data set.
    most_recent_date = session.query(func.strftime(Measurement.date)).order_by(Measurement.date.desc()).first()
    # Convert date to format to determine the date 12 months ago
    most_recent_date_string = str(most_recent_date)
    most_recent_date_string = most_recent_date_string.strip("(),'")

    ### Find the date twelve months ago
    twelve_months_ago = datetime.strftime(datetime.strptime(most_recent_date_string, '%Y-%m-%d') - dt.timedelta(days=365), '%Y-%m-%d')
    # List the stations and their counts in descending order.
    most_active_stations = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    # Using the most active station id from the previous query, calculate the lowest, highest, and average temperature.
    most_active_station = most_active_stations[0][0]
    # makes a list of temp tuples
    temp_list_12_months = session.query(Measurement.tobs).filter(Measurement.station == most_active_station, Measurement.date >= twelve_months_ago).all()
    # close session
    session.close()
    # converts list to a real python list that can be jsonified.
    temp_list = [temp[0] for temp in temp_list_12_months]
    return jsonify(temp_list)
    
    
@app.route("/api/v1.0/<start>")
def temp_data_start(start):
    # List the stations and their counts in descending order.
    most_active_stations = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    # Using the most active station id from the previous query, calculate the lowest, highest, and average temperature.
    most_active_station = most_active_stations[0][0]
    # makes a list of temp tuples after the entered date.
    temp_list_after_start_date = session.query(Measurement.tobs).filter(Measurement.station == most_active_station, Measurement.date >= start).all()
    temp_list = [temp[0] for temp in temp_list_after_start_date]
    # close session
    session.close()
    # list of min max and average
    temp_stats = {"Min" : min(temp_list), "Max" : max(temp_list), "Average": sum(temp_list) / len(temp_list)}
    # return temp stats
    return jsonify(temp_stats)

@app.route("/api/v1.0/<start>/<end>")
def temp_data_start_end(start, end):
    # List the stations and their counts in descending order.
    most_active_stations = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    # Using the most active station id from the previous query, calculate the lowest, highest, and average temperature.
    most_active_station = most_active_stations[0][0]
    # makes a list of temp tuples after the entered started date but before the entered end date.
    temp_list_after_start_date = session.query(Measurement.tobs).filter(Measurement.station == most_active_station, Measurement.date >= start, Measurement.date <= end).all()
    temp_list = [temp[0] for temp in temp_list_after_start_date]
    # close session
    session.close()
    # list of min max and average
    temp_stats = {"Min" : min(temp_list), "Max" : max(temp_list), "Average": sum(temp_list) / len(temp_list)}
    # return temp stats
    return jsonify(temp_stats)


@app.route("/")
def welcome():
    return (
        f"Welcome to the Climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"enter start date:"
        f"/api/v1.0/yyyy-mm-dd<br/>"
        f"enter start and end date:"
        f"/api/v1.0/yyyy-mm-dd/yyyy-mm-dd<br/>"

    )


if __name__ == "__main__":
    app.run(debug=True)
