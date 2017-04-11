"use strict"
//"Cedar+Falls+IA+50613&Decorah+IA+52101"
var map;
var markerList = [];
var directionsService;
var directionsDisplay;

function startEngine() {
    //takes input from html file and makes it readable by server
    let serverOrigin = document.getElementById("startCity").value.concat("+").concat(document.getElementById("startState").value.concat("&"));
    let serverDestination = document.getElementById("endCity").value.concat("+").concat(document.getElementById("endState").value);
    let car = serverOrigin.concat(serverDestination).replace(" ","+");
    deleteMarkers();
    startTrip(car);
    //takes same input from html file but makes it readable by googleMaps.
    let googleOrigin = document.getElementById("startCity").value.concat(",").concat(document.getElementById("startState").value).toLowerCase();
    let googleDestination = document.getElementById("endCity").value.concat(",").concat(document.getElementById("endState").value).toLowerCase();
    calculateAndDisplayRoute(directionsService, directionsDisplay, googleOrigin, googleDestination);
}

function deleteMarkers() {
    for (let i = 0; i < markerList.length; i++) {
        markerList[i].setMap(null);
    }
    markerList = []
}

function startTrip(car) {
    let self = this;
    let dfd = new $.Deferred();

    $.ajax({
        url: `http://localhost:5000/readySetGo/${car}`,
        method: "GET"
    }).done(function(data) {
        pinWheel(data)
    dfd.resolve()
    });

    return dfd;

}

function addPin(latitude,longitude,iconNumber,iconPhrase) {
    let latLng = {"lat": latitude, "lng": longitude};

    let marker = new google.maps.Marker({
        animation: google.maps.Animation.DROP,
        icon: `./WeatherIcons/${iconNumber}-s.png`,
        title: iconPhrase,
        position: latLng,
        map: map
    });

    markerList.push(marker);
    marker.setMap(map);
}

function pinWheel(jsonData) {

    // receives an array of arrays containing, in order, the lat float; long float; and weather object
    let f = JSON.parse(jsonData);
    //console.log(f);
    for (let i of f) {
        if ("WeatherIcon" in i[2]) {
            addPin(i[0],i[1],i[2]["WeatherIcon"],i[2]["IconPhrase"])
        } else {
            addPin(i[0],i[1],i[2]["Icon"],i[2]["IconPhrase"])
        }
    }

}
function initMap() {
        // Create a map object and specify the DOM element for display.
        directionsService = new google.maps.DirectionsService;
        directionsDisplay = new google.maps.DirectionsRenderer;
        map = new google.maps.Map(document.getElementById('map'), {
          center: {lat: 40, lng: -95.7129},
          scrollwheel: false,
          zoom: 4
        });
        directionsDisplay.setMap(map);
}

function calculateAndDisplayRoute(directionsService, directionsDisplay, origin, destination) {
  directionsService.route({
    origin: origin,
    destination: destination,
    travelMode: 'DRIVING'
  }, function(response, status) {
    if (status === 'OK') {
      directionsDisplay.setDirections(response);
    } else {
      window.alert('Directions request failed due to ' + status);
    }
  })
}
