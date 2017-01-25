var map = L.map('map', {
  zoom: 2,
  fullscreenControl: true,
% if wms:
  timeDimension: true,
  timeDimensionOptions:{
        position: 'bottomleft',
        playerOptions: {
            transitionTime: 1000,
            startOver: true,
            minBufferReady: 2,
            buffer: 5,
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
  attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors',
});
osmLayer.addTo(map);

var baseMaps = {
  "OpenStreetMap": osmLayer,
};

% if wms:
var proxy = 'owsproxy';
var dsWMS = '${wms.url}';
<%
   wms_layers = [layer_id for layer_id in wms.contents if wms.contents[layer_id].queryable and layer_id.split('/')[-1] not in ['lat', 'lon']]
%>
% for layer_id in wms_layers:
var layer${loop.index} = L.tileLayer.wms(dsWMS, {
  layers: '${layer_id}',
  format: 'image/png',
  transparent: true,
  //styles: 'default',
  attribution: '<a href="http://bird-house.github.io/">Birdhouse</a>',
});
var timeLayer${loop.index} = L.timeDimension.layer.wms(layer${loop.index}, {
  proxy: proxy,
  updateTimeDimension: true,
% if dataset:
  getCapabilitiesParams: {
    DATASET: '${dataset}',
  },
% endif
});
timeLayer${loop.index}.addTo(map);

% endfor
var overlayMaps = {
% for layer_id in wms_layers:
    "${wms.contents[layer_id].title}": timeLayer${loop.index},
% endfor
};
% else:
var overlayMaps = {};
% endif

L.control.layers(baseMaps, overlayMaps).addTo(map);
