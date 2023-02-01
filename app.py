from flask import Flask, render_template, request, jsonify
#import FlightSearch
from FlightSearch import *
import datetime as dt, gspread, pytz

#### Google Information
gc = gspread.service_account(filename="credentials.json")
sh = gc.open_by_key("1SzXaeiurXrmTVSqOf4sXY0Xca57Qe8hBbxOoDETJjqY")
worksheet = sh.sheet1
####

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
@app.route("/home", methods=['GET', 'POST'])
def home():
    #sendEmail("airover.business@gmail.com", request.remote_addr)
    LisbonTz = pytz.timezone("Europe/Lisbon") 
    currTime = dt.datetime.now(LisbonTz)
    currTimeStamp = currTime.strftime("%d/%m/%Y %H:%M:%S")
    user = [currTimeStamp, request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr), "landing"]
    worksheet.append_row(user)
    return render_template("index.html")

''''
@app.route("/result", methods = ["POST", "GET"])
def result():
    origin = request.form["origin"]
    destination = request.form["destination"]
    departDate = request.form["departDate"]
    layoverDuration = request.form["layoverDuration"]
    results = finalFlightSearch(origin, destination, dt.date(int(departDate[6:]), int(departDate[3:5]), int(departDate[0:2])), int(layoverDuration))
    return render_template("flightResults.html", flightResults = results)
'''

@app.route("/result", methods = ["POST", "GET"])
def result():
    # filename='second.png
    LisbonTz = pytz.timezone("Europe/Lisbon") 
    currTime = dt.datetime.now(LisbonTz)
    currTimeStamp = currTime.strftime("%d/%m/%Y %H:%M:%S")
    user = [currTimeStamp, request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr), "results"]
    worksheet.append_row(user)
    origin = request.form["origin"]
    destination = request.form["destination"]
    departDate = request.form["departDate"]
    layoverDuration = request.form["layoverDuration"]
    results = getResultsForWebsite(origin, destination, dt.date(int(departDate[6:]), int(departDate[3:5]), int(departDate[0:2])), int(layoverDuration))
    # Problem: Some trip combinations may have < 5 connections, in which case if we're trying to get 5 results, we will receive an error.
    # Example: OPO to GYE (Only 3 possible intermediary results!!!)
    return render_template("searchResults.html", 
                            firstLayoverAirport = getLayoverAirport(results[0]), 
                            firstLayoverDuration = layoverDuration,
                            firstAirlinePic = "static/logos/" + str(IATAToICAO(getFirstAirline(results[0]))) + ".png",
                            firstTotalCost = getTotalCost(results[0]),
                            firstAmountSaved = getAmountSaved(results[0], origin, destination, dt.date(int(departDate[6:]), int(departDate[3:5]), int(departDate[0:2]))),
                            
                            firstLayoverAirport2 = getLayoverAirport(results[1]), 
                            firstLayoverDuration2 = layoverDuration,
                            firstAirlinePic2 = "static/logos/" + str(IATAToICAO(getFirstAirline(results[1]))) + ".png",
                            firstTotalCost2 = getTotalCost(results[1]),
                            firstAmountSaved2 = getAmountSaved(results[1], origin, destination, dt.date(int(departDate[6:]), int(departDate[3:5]), int(departDate[0:2]))),

                            firstLayoverAirport3 = getLayoverAirport(results[2]), 
                            firstLayoverDuration3 = layoverDuration,
                            firstAirlinePic3 = "static/logos/" + str(IATAToICAO(getFirstAirline(results[2]))) + ".png",
                            firstTotalCost3 = getTotalCost(results[2]),
                            firstAmountSaved3 = getAmountSaved(results[2], origin, destination, dt.date(int(departDate[6:]), int(departDate[3:5]), int(departDate[0:2]))),

                            firstLayoverAirport4 = getLayoverAirport(results[3]), 
                            firstLayoverDuration4 = layoverDuration,
                            firstAirlinePic4 = "static/logos/" + str(IATAToICAO(getFirstAirline(results[3]))) + ".png",
                            firstTotalCost4 = getTotalCost(results[3]),
                            firstAmountSaved4 = getAmountSaved(results[3], origin, destination, dt.date(int(departDate[6:]), int(departDate[3:5]), int(departDate[0:2]))),

                            firstLayoverAirport5 = getLayoverAirport(results[4]), 
                            firstLayoverDuration5 = layoverDuration,
                            firstAirlinePic5 = "static/logos/" + str(IATAToICAO(getFirstAirline(results[4]))) + ".png",
                            firstTotalCost5 = getTotalCost(results[4]),
                            firstAmountSaved5 = getAmountSaved(results[4], origin, destination, dt.date(int(departDate[6:]), int(departDate[3:5]), int(departDate[0:2]))),
                            )


#app.run(host = "0.0.0.0", port = 5000)
if __name__ == "__main__":
    app.run()