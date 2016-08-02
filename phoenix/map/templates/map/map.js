var map = L.map('map', {
  zoom: 2,
  fullscreenControl: true,
% if dataset:
  timeDimension: true,
  timeDimensionOptions:{
        times: "${times}",
  },
  timeDimensionControl: true,
% endif    
  center: [20.0, 0.0],
});

var osmLayer = L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
  attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'    
});
osmLayer.addTo(map);

% if dataset:
var testWMS = "/ows/proxy/wms?DATASET=${dataset}"
var ncLayer = L.tileLayer.wms(testWMS, {
  layers: '${layers}',
  format: 'image/png',
  transparent: true,
  styles: '${styles}',
  attribution: '<a href="http://bird-house.github.io/">Birdhouse</a>'
});
var ncTimeLayer = L.timeDimension.layer.wms(ncLayer, {
  updateTimeDimension: false,
});
ncTimeLayer.addTo(map);
% endif

var baseMaps = {
  "OpenStreetMap": osmLayer,
};

var overlayMaps = {
  "${layers}": ncTimeLayer
};

L.control.layers(baseMaps, overlayMaps).addTo(map);

% if dataset:
var ncLegend = L.control({
    position: 'topright'
});
ncLegend.onAdd = function(map) {
    var src = testWMS + "&SERVICE=WMS&VERSION=1.3.0&REQUEST=GetLegendGraphic&LAYERS=${layers}&STYLES=${styles}&PALETTE=default&HEIGHT=300";
    var div = L.DomUtil.create('div', 'info legend');
    div.innerHTML +=
        '<img src="' + src + '" alt="legend">';
    return div;
};
ncLegend.addTo(map);
% endif

L.control.coordinates({
    position: "bottomright",
    decimals: 3,
    labelTemplateLat: "Latitude: {y}",
    labelTemplateLng: "Longitude: {x}",
    useDMS: true,
    enableUserInput: false
}).addTo(map);







