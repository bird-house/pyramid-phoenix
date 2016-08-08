var map = L.map('map', {
  zoom: 8,
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
var dsWMS = "/ows/proxy/wms?DATASET=${dataset}"
var dsLayer = L.tileLayer.wms(dsWMS, {
  layers: '${layers}',
  format: 'image/png',
  transparent: true,
  styles: '${styles}',
  attribution: '<a href="http://bird-house.github.io/">Birdhouse</a>'
});
var dsTimeLayer = L.timeDimension.layer.wms(dsLayer, {
  updateTimeDimension: false,
});
dsTimeLayer.addTo(map);
% endif

var baseMaps = {
  "OpenStreetMap": osmLayer,
};

var overlayMaps = {
  "${layers}": dsTimeLayer
};

L.control.layers(baseMaps, overlayMaps).addTo(map);

% if dataset:
var dsLegend = L.control({
    position: 'topright'
});
dsLegend.onAdd = function(map) {
    var src = dsWMS + "&SERVICE=WMS&VERSION=1.3.0&REQUEST=GetLegendGraphic&LAYERS=${layers}&STYLES=${styles}&PALETTE=default&HEIGHT=300";
    var div = L.DomUtil.create('div', 'info legend');
    div.innerHTML +=
        '<img src="' + src + '" alt="legend">';
    return div;
};
dsLegend.addTo(map);
% endif

L.control.coordinates({
    position: "bottomright",
    decimals: 3,
    labelTemplateLat: "Latitude: {y}",
    labelTemplateLng: "Longitude: {x}",
    useDMS: true,
    enableUserInput: false
}).addTo(map);







