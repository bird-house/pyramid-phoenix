var map = null;

function initMap() {
  map = L.map('div-map').setView([10, 0], 1);
  basemap = L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
  })
  map.addLayer(basemap);
  map_layers_control = L.control.layers({"basemap": basemap}, {}, {'collapsed': true}).addTo(map);
}

$(function() {
  // select item
  $(".select").button({
    text: false,
  }).click(function( event ) {
    event.preventDefault();
    var recordid = $(this).attr('data-value');
    $.getJSON(
      '/wizard/csw/'+recordid+'/select.json',
      {},
      function(json) {
        location.reload();
      }
    );
  });

});