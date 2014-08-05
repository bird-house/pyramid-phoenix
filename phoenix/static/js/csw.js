var map = null;

function initMap() {
  map = L.map('div-map').setView([10, 0], 1);
  basemap = L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
  })
  map.addLayer(basemap);
  map_layers_control = L.control.layers({"basemap": basemap}, {}, {'collapsed': true}).addTo(map);
}