# Load in all the Airports and IDs and Make a dictionary out of it
# airportDict: Key = ID, Value = Airport Code
import datetime as dt, pandas as pd, requests, geopy.distance, smtplib, ssl, time
airports = pd.read_csv("air-routes-latest-nodes.csv", usecols=[0, 3], header=0)
airports = airports.drop(airports.index[0])
airports = airports.drop(airports.index[3504:])
airportsDict = dict(airports.values)

# Load in all the Routes and Make a dictionary out of it
routes = pd.read_csv("air-routes-latest-edges.csv", usecols=[1, 2], header=0)
routes = routes.drop(routes.index[50547:])
routesDict = {}
for route in routes.values:
    originAirportCode = airportsDict[route[0]]
    destinationAirportCode = airportsDict[route[1]]
    if originAirportCode not in routesDict:
        routesDict[originAirportCode] = [destinationAirportCode]
    else:
        routesDict[originAirportCode].append(destinationAirportCode)

inverseRoutesDict = {}
for route in routes.values:
    originAirportCode = airportsDict[route[0]]
    destinationAirportCode = airportsDict[route[1]]
    if destinationAirportCode not in inverseRoutesDict:
        inverseRoutesDict[destinationAirportCode] = [originAirportCode]
    else:
        inverseRoutesDict[destinationAirportCode].append(originAirportCode)

# Store the coordinates of airports in a dictionary. Format is {Airport Code: (Lat, Long)}
airportsDF = pd.read_csv("air-routes-latest-nodes.csv", usecols=[3, 12, 13], header=0)
airportsDF = airportsDF.drop(airportsDF.index[0])
airportsDF = airportsDF.drop(airportsDF.index[3504:])
coordsList = tuple(zip(airportsDF["lat:double"], airportsDF["lon:double"]))
airportCoordsDict = dict(zip(airportsDF["code:string"], coordsList))

def getDestinations(originAirportCode):
    return routesDict[originAirportCode]

def getArrivals(airportCode):
    return inverseRoutesDict[airportCode]

# Direct Flight Search Functionality
directSearchURLEndpoint = "https://tequila-api.kiwi.com/v2/search"
directSearchAPIKey = "ae8gGCDltiv8QqPxW1ATEhOh5W1a9wsj"
directSearchHeader = {
    "apikey": directSearchAPIKey
}

# Multi-City Flight Search Functionality
URLEndpoint = "https://tequila-api.kiwi.com/v2/flights_multi"
APIKey = "07vgjolPoSrF7AuOwyH8A192EeUofoJZ"
header = headers = {
            "apikey": APIKey
        }

def findLayoverAirports(origin, destination):
    return set(getDestinations(origin)) & set(getArrivals(destination))

def getDistance(origin, destination):
    originCoords = airportCoordsDict[origin]
    destinationCoords = airportCoordsDict[destination]
    return geopy.distance.distance(originCoords, destinationCoords).mi

def getDistanceWithLayover(origin, layover, destination):
    return getDistance(origin, layover) + getDistance(layover, destination)

# datetime object to DD/MM/YYYY conversion
def convertDate(dateTime):
    return dateTime.strftime("%d/%m/%Y")

# Direct Flight Search
def directFlightSearch(origin, destination, departureDate):
    searchData = {
        "to": destination,
        "flyFrom": origin,
        "dateFrom": convertDate(departureDate),
        "dateTo": convertDate(departureDate),
        "limit": 20
    }
    response = requests.get(directSearchURLEndpoint, headers=directSearchHeader, params=searchData)
    if not response.json():
        return
    minPrice = response.json()["data"][0]["price"]
    bestItinerary = response.json()["data"][0]
    for itinerary in response.json()["data"]:
        if itinerary["price"] < minPrice:
            minPrice = itinerary["price"]
            bestItinerary = itinerary
    return bestItinerary

# Multi-City Flight Search
def flightSearch(origin, destination, firstDepartureDate, layoverAirport, layoverDuration):
    # Note: Date must be in the format "DD/MM/YYYY"
    # Constraint: Need someway to account for flights that take multiple days, for instance some flights may be +2 days, which would break this booking functionality
    searchData = {
    "requests": [
        {
        "to": layoverAirport,
        "flyFrom": origin,
        "dateFrom": convertDate(firstDepartureDate),
        "dateTo": convertDate(firstDepartureDate)
        },
        {
        "to": destination,
        "flyFrom": layoverAirport,
        "dateFrom": convertDate(firstDepartureDate + dt.timedelta(days = layoverDuration)),
        "dateTo": convertDate(firstDepartureDate + dt.timedelta(days = layoverDuration))
        }
    ]
    }
    response = requests.post(URLEndpoint, headers = header, json = searchData)
    if not response.json():
        return
    minPrice = response.json()[0]["price"]
    bestItinerary = response.json()[0]
    for itinerary in response.json():
        if itinerary["price"] < minPrice:
            minPrice = itinerary["price"]
            bestItinerary = itinerary
    return bestItinerary

def bigFlightSearch(origin, destination, firstDepartureDate, layoverDuration):
    results = []
    possibleLayovers = list(findLayoverAirports(origin, destination))
    possibleLayovers = sorted(possibleLayovers, key = lambda layover: getDistanceWithLayover(origin, layover, destination))
    possibleLayovers = possibleLayovers[0:min(10, len(possibleLayovers))]
    for possibleLayover in possibleLayovers:
        itinerary = flightSearch(origin, destination, firstDepartureDate, possibleLayover, layoverDuration)
        if itinerary:
            results.append(itinerary)
    return sorted(results, key = lambda trip: trip["price"])

def extractRelevantData(itinerary):
    toReturn = ""
    for tripLeg in itinerary["route"]:
        toReturn += "This is your itenerary from: " + tripLeg["cityFrom"] + " to " + tripLeg["cityTo"] + "\n"
        for legRouting in tripLeg["route"]:
            toReturn += legRouting["airline"] + str(legRouting["flight_no"]) + " " + legRouting["flyFrom"] + " " + legRouting["flyTo"] + " " + "Departs: " + legRouting["local_departure"] + " " + "Arrives: " + legRouting["local_arrival"] + "\n"
    toReturn += "The price for this itinerary is: " + str(itinerary["price"]) + "\n"
    return toReturn

# Extracts the Data for the direct flight.
def extractDataDirect(itinerary):
    toReturn = ""
    toReturn += "This is your itinerary from: " + itinerary["flyFrom"] + " to " + itinerary["flyTo"] + "\n"
    for tripLeg in itinerary["route"]:
        # Changed from operating_carrier and operating_flight_no
        toReturn += tripLeg["airline"] + str(tripLeg["flight_no"]) + " " + tripLeg["flyFrom"] + " " + tripLeg["flyTo"] + " " + "Departs: " + tripLeg["local_departure"] + " " + "Arrives: " + tripLeg["local_arrival"] + "\n"
    toReturn += "The price for this itinerary is: " + str(itinerary["price"])
    return toReturn

def finalFlightSearch(origin, destination, date, layoverDuration):
    toReturn = ""
    toReturn += "Direct Itinerary: \n"
    toReturn += extractDataDirect(directFlightSearch(origin, destination, date)) + "\n"
    toReturn += "Itineraries with layovers: \n"
    for itinerary in bigFlightSearch(origin, destination, date, layoverDuration):
        toReturn += extractRelevantData(itinerary) + "\n"
    return toReturn

def getResultsForWebsite(origin, destination, date, layoverDuration):
    resultsList = []
    for itinerary in bigFlightSearch(origin, destination, date, layoverDuration):
        # Changed from extractRelevantData(itinerary) to just itinerary
        resultsList.append(itinerary)
    return resultsList

def sendEmail(receiverEmail, flightResultsMessage):
    port = 465
    smtp_server = "smtp.gmail.com"
    sender_email = "airover.business@gmail.com"
    receiver_email = receiverEmail
    password = "rxbhwxlgdsjowbeo"
    message = """From: From Person <from@fromdomain.com>
    To: To Person <to@todomain.com>
    Subject: Your Airover Flight Search Result

    
    """ + flightResultsMessage
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)

def IATAToICAO(IATACode):
    airlineCodes = pd.read_csv("IATAToICAOTable.csv", usecols=[0, 1], header=0)
    airlineCodeDict = dict(airlineCodes.values)
    return airlineCodeDict[IATACode]

# Returns the Layover City, not the layover Airport
def getLayoverAirport(itinerary):
    return itinerary["route"][0]["cityTo"]

def getFirstAirline(itinerary):
    return itinerary["route"][0]["route"][0]["airline"]

def getTotalCost(itinerary):
    return itinerary["price"]

def getAmountSaved(itinerary, origin, destination, departureDate):
    return directFlightSearch(origin, destination, departureDate)["price"] - getTotalCost(itinerary)


#start = time.time()
#print(finalFlightSearch("ORY", "LIS", dt.date(2022, 8, 9), 1))
#myResults = getResultsForWebsite("ORD", "DEL", dt.date(2022, 12, 25), 3)
#print(myResults[0]["route"])
#print(myResults[0]["route"][0])
#print(getLayoverAirport(myResults[1]))
#end = time.time()
#print("The time that this search took was: ", end - start)

#print(getFirstAirline(getResultsForWebsite("ORD", "LIS", dt.date(2022, 8, 20), 5)[0]))
#print(finalFlightSearch("ORD", "LIS", dt.date(2022, 8, 20), 5))
#flightResultsString = finalFlightSearch("LAX", "CDG", dt.date(2022, 8, 8), 5)
#sendEmail("joseluu11tower@gmail.com", flightResultsString)

""" To-Do List:
1) Filter out travel restricted countries (using spreadsheet) to save on API Calls **REVIEW: This point with group**
2) Make a determination on whether to use best quality, lowest price, or some combination of the two.
3) Determine what currency the results should be displayed in. Should it be Euro or Dollars or based on the starting point of the route.
"""