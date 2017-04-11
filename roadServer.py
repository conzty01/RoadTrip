from flask import Flask, request, make_response
import requests as req
import json
import math

app = Flask(__name__)

@app.route("/readySetGo/<string:se>")
def readySetGo(se):
    start = se.split("&")[0]
    end = se.split("&")[-1]
    print(start,end)

    #print(start,end)

    r = json.loads(getRoute(start,end))                 # creates a JSON-like dictionary object of the text returned from Google
    #print(r)

    pinList = pinLocations(r)
    wList = getWeather(pinList)

    weathPins = parseWeather(wList,pinList)
    #print(weathPins)

    return json.dumps(weathPins)

def getRoute(s,e):
    resp = req.get("https://maps.googleapis.com/maps/api/directions/json?"
                    "origin={}&destination={}&key=AIzaSyCrwRulIzknvLKB_ZX9baK0Ao4B3245LAA".format(s,e))
    return resp.text

def getWeather(locList):

    weathList = []

    locKeyList = []
    for locat in locList:
        resp1 = req.get("http://dataservice.accuweather.com/locations/v1/cities/geoposition/search?apikey=XJdSipw5Kq9HU44GHfsTGHrypV6WQAN8&q={}%2C{}".format(locat[0],locat[1]))
        resp1JSON = json.loads(resp1.text)
        #print(resp1.text)
        locKeyList.append(resp1JSON["Key"])

    for i, locKey in enumerate(locKeyList):
        if locList[i][-1] > 720:
            resp2 = req.get("http://dataservice.accuweather.com/forecasts/v1/daily/5day/{}?apikey=XJdSipw5Kq9HU44GHfsTGHrypV6WQAN8&details=true".format(locKey))
            weathList.append(json.loads(resp2.text))

        else:
            resp2 = req.get("http://dataservice.accuweather.com/forecasts/v1/hourly/12hour/{}?apikey=XJdSipw5Kq9HU44GHfsTGHrypV6WQAN8&details=true".format(locKey))
            weathList.append(json.loads(resp2.text))

    #print(weathList)
    return weathList

def parseWeather(wList,locList):

    pinList = []

    for i,locTuple in enumerate(locList):

        if isinstance(wList[i],list):
            weath = wList[i][locTuple[-1] // 60]
            locWeath = (locTuple[0],locTuple[1],weath)

        elif isinstance(wList[i],dict):
            dayDict = wList[i]["DailyForecasts"][locTuple[-1] // 1440]
            weath = dayDict["Day"]
            locWeath = (locTuple[0],locTuple[1],weath)

        pinList.append(locWeath)

    return pinList

def pinLocations(dictRoute):
    locList = []
    startLocDict = dictRoute["routes"][0]["legs"][0]["start_location"]
    endLocDict = dictRoute["routes"][0]["legs"][0]["end_location"]
    locList.append((startLocDict["lat"],startLocDict["lng"],0))                 # Latitude then Longitude then duration

    prev = locList[0]                                                           # Start with beginning location
    time = 0
    for stage in dictRoute["routes"][0]["legs"][0]["steps"]:
        s = stage["duration"]["text"]

        if "hour" in s:                                                         # Parse for hour in result
            c = s.split("hour")

            time += 60 * int(c[0])

            if "min" in c[1]:                                                   # Then parse for minute
                d = c[1].split("min")
                timeStr = d[0]
                time += int(timeStr.replace("s",""))

        elif "min" in s:                                                        # Otherwise parse for minute
            b = s.split("min")
            time += int(b[0])

        # if the overall difference between lat and long is greater than about 30 miles, then add the point to the locatList
        if math.fabs(prev[0]-stage["end_location"]["lat"])+math.fabs(prev[-1]-stage["end_location"]["lng"]) >= .4:
            locList.append((stage["end_location"]["lat"],stage["end_location"]["lng"],time))
            prev = (stage["end_location"]["lat"],stage["end_location"]["lng"])

    locList.append((endLocDict["lat"],endLocDict["lng"],time))

    if len(locList) > 10:
        newList = [locList[0]]

        indexValue = len(locList) // 8

        for pos in range(indexValue,len(locList),indexValue):
            newList.append(locList[pos])
            if len(newList) == 9:
                break

        newList.append(locList[-1])

        locList = newList

    return locList

app.run(debug=True)
