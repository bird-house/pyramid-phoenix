var mymap = L.map('mapid', {
  zoom: 2,
  fullscreenControl: true,
  timeDimension: true,
  timeDimensionOptions:{
    timeInterval: "2001-01-16T12:00:00Z/2005-12-16T12:00:00Z",
    period: "P1M"
  },
  timeDimensionControl: true,
  timeDimensionControlOptions:{
    timeSteps: 12
  },    
  center: [20.0, 0.0],
});

L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
  attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'    
}).addTo(mymap);

var testWMS = "http://localhost:8080/ncWMS2/wms?DATASET=outputs/hummingbird/output-3d059bc0-5033-11e6-9fa2-af0ebe9e921e.nc"
//var testWMS = "https://localhost:8443/ows/proxy/wms?DATASET=outputs/hummingbird/output-3d059bc0-5033-11e6-9fa2-af0ebe9e921e.nc"
var testLayer = L.tileLayer.wms(testWMS, {
  layers: 'tasmax',
  format: 'image/png',
  transparent: true,
  styles: 'default-scalar/x-Rainbow',
  attribution: '<a href="http://bird-house.github.io/">Birdhouse</a>'
});
var testTimeLayer = L.timeDimension.layer.wms(testLayer);
testTimeLayer.addTo(mymap);







