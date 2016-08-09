var map = L.map('map', {
  zoom: 2,
  fullscreenControl: true,
% if dataset:
  timeDimension: true,
  timeDimensionOptions:{
        position: 'bottomleft',
        playerOptions: {
            transitionTime: 1000,
        },
  },
  timeDimensionControl: true,
% endif    
  center: [20.0, 0.0],
});

L.control.coordinates({
    position: "bottomright",
    decimals: 3,
    labelTemplateLat: "Latitude: {y}",
    labelTemplateLng: "Longitude: {x}",
    useDMS: true,
    enableUserInput: false
}).addTo(map);

var osmLayer = L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
  attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'    
});
osmLayer.addTo(map);

var baseMaps = {
  "OpenStreetMap": osmLayer,
};

% if dataset:
var dsWMS = "/ows/proxy/wms"
var dsLayer = L.tileLayer.wms(dsWMS, {
  layers: '${layers}',
  format: 'image/png',
  transparent: true,
  styles: '${styles}',
  attribution: '<a href="http://bird-house.github.io/">Birdhouse</a>',
});
var dsTimeLayer = L.timeDimension.layer.wms(dsLayer, {
  updateTimeDimension: true,
  getCapabilitiesParams: {
    DATASET: '${dataset}',
  },
});
dsTimeLayer.addTo(map);

var dsLegend = L.control({
    position: 'bottomright'
});
dsLegend.onAdd = function(map) {
    var src = dsWMS + "?DATASET=${dataset}&SERVICE=WMS&VERSION=1.1.1&REQUEST=GetLegendGraphic&LAYERS=${layers}&STYLES=${styles}&PALETTE=default&HEIGHT=300";
    var div = L.DomUtil.create('div', 'info legend');
    div.innerHTML +=
        '<img src="' + src + '" alt="legend">';
    return div;
};
dsLegend.addTo(map);

var overlayMaps = {
  "${layers}": dsTimeLayer
};
% else:
var overlayMaps = {}
% endif

L.control.layers(baseMaps, overlayMaps).addTo(map);










