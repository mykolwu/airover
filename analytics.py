import pandas as pd
allResults = pd.read_csv("IP Address Logger - Sheet1.csv", usecols=[1, 2])
newDFLanding =  allResults[(allResults['Page:'] == "landing")]
newDFResults = allResults[(allResults["Page:"] == "results")]
landingDict = dict(newDFLanding.values)
resultsDict = dict(newDFResults.values)
print("There are " + str(len(landingDict)) + " unique people who have hit the landing page.")
print("There are " + str(len(resultsDict)) + " unique people who have hit the results page.")
