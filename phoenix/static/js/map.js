var map,  wmsLayer, animateLayer;
var start_time, end_time;
var layerList;
var selectedLayer;

function initMap() {
  if (map != null) {
    map.destroy();
  }

  //var mapOptions = { maxResolution: 256/512, numZoomLevels: 11, fractionalZoom: true};
  //map = new OpenLayers.Map('map',mapOptions);
  map = new OpenLayers.Map('map');
  map.addControl(new OpenLayers.Control.LayerSwitcher());
  //map.addControl(new OpenLayers.Control.Attribution());
  //map.addControl(new OpenLayers.Control.Animate());

  map.setupGlobe();

  // base layers
  var baseLayer = new OpenLayers.Layer.WMS("World Map",
                                   "http://www2.demis.nl/wms/wms.ashx?WMS=WorldMap",
                                   {layers: '*', format: 'image/png'},
                                   {singleTile: false}
                                  );
  map.addLayer(baseLayer);

  baseLayer = new OpenLayers.Layer.WMS( "OpenLayers WMS",
                                       "http://vmap0.tiles.osgeo.org/wms/vmap0", 
                                       {layers: 'basic'} );
  map.addLayer(baseLayer);
 
  map.finishGlobe();
  map.set3D(false);
  map.show2D();
 
  map.zoomToMaxExtent(); 

  initLayerList();
}

function initLayerList() {
  wps = new SimpleWPS({
    process: "org.malleefowl.wms.layer",
    onSuccess: function(result) {
      //console.log(result);
      var output = [];
      layerList = []
      $.each(result, function(index, layer) {
        //output.push('<optgroup label="' + layer.service_name + '">');
        title = layer.title + " (" + layer.service_name + ")";
        output.push('<option label="' + title + '" value="'+ index +'">' + title +'</option>'); 
        //output.push('</optgroup>');
        layerList.push(layer);
      });
      $('#select').html(output.join(''));

      $('#select').change(function() {
        selectedLayer = layerList[this.selectedIndex];
        showLayer(selectedLayer);
      });

      selectedLayer = layerList[0];
      showLayer(selectedLayer);
    },
  });
  wps.execute();
}

function showLayer(layer) {
  if (wmsLayer != null) {
    map.removeLayer(wmsLayer);
  }
  wmsLayer = new OpenLayers.Layer.WMS(layer.title,
                                      layer.service,
                                      {layers: layer.name,
                                       transparent: true,
                                       format:'image/png',
                                       time: layer.timesteps[0]});
  
  map.addLayer(wmsLayer);
  wmsLayer.events.register('loadend', wmsLayer, function(evt){
    //map.zoomToExtent(new OpenLayers.Bounds(wmsLayer.getExtent()));
  }); 
  initTimeSlider(layer, wmsLayer);
}

function dateLabel(timestep) {
  return timestep.substring(0,16);
}

function initTimeSlider(layer, wmsLayer) {
  var max = layer.timesteps.length - 1;

  // slider
  $("#slider").slider({
    value: 0,
    min: 0,
    max: max,
    step: 1,
    slide: function(e, ui) {
      var step = parseInt(ui.value);
      //console.log("sliding ...");
      $("#time").text(dateLabel(layer.timesteps[step]));
    },
    change: function(e, ui) {
      //tds_wms.setOpacity(ui.value / 10);
      var step = parseInt(ui.value);
      //console.log("step: " + step);
      $("#time").text(dateLabel(layer.timesteps[step]));
      wmsLayer.mergeNewParams({'time': layer.timesteps[step]});
    }
  });
  $("#time").text(dateLabel(layer.timesteps[0]));

  // prev button
  $("#prev").button({
    text: false,
  }).click(function( event ) {
    //console.log('prev button clicked');
    current = $("#slider").slider( "values", 0 );
    if (current > 0 ) {
      $("#slider").slider( "value", current - 1 );
    }
  });

  // next button
  $("#next").button({
    text: false,
  }).click(function( event ) {
    //console.log('next button clicked');
    current = $("#slider").slider( "values", 0 );
    if (current < max ) {
      $("#slider").slider( "value", current + 1 );
    }
  });

  // play button
  $("#play").button({
    text: false,
  }).click(function( event ) {
    $("#dialog-play").dialog({
      resizable: false,
      height: 300,
      modal: true,
      buttons: {
        Ok: function() {
          $( this ).dialog( "close" );
          animate(selectedLayer);
        },
        Cancel: function() {
         $( this ).dialog( "close" );
        }
      }
    });
  });
  
  // stop button
  $("#stop").button({
    text: false,
  }).click(function( event ) {
    if (animateLayer != null) {
      map.removeLayer(animateLayer);
    }
  });

  // slider range
  $("#slider-range").slider({
    range: true,
    values: [0, max],
    min: 0,
    max: max,
    step: 1,
    slide: function(e, ui) {
      var step0 = parseInt(ui.values[0]);
      var step1 = parseInt(ui.values[1]);
      
      $("#time-range").text( dateLabel(layer.timesteps[step0]) + " - " + dateLabel(layer.timesteps[step1]) );
      start_time = layer.timesteps[step0];
      end_time = layer.timesteps[step1];
    },
  });
  $("#time-range").text( dateLabel(layer.timesteps[step0]) + " - " + dateLabel(layer.timesteps[step1]) );
}

function animate(layer) {
  if (animateLayer != null) {
    map.removeLayer(animateLayer);
  }

  wps = new SimpleWPS({
    process: "org.malleefowl.wms.animate",
    raw: false,
    format: 'xml',
    onSuccess: function(xmlDoc) {
      //console.log(xmlDoc);
      var url = $(xmlDoc).find("wps\\:Reference, Reference").first().attr('href');
      console.log(url);

      animateLayer = new OpenLayers.Layer.Image(
        "Animation", url, map.getExtent(), map.getSize(), {
        isBaseLayer: false,
        alwaysInRange: true // Necessary to always draw the image
        });
      map.addLayer(animateLayer);
    },
  });
  wps.execute({
    service_url: layer.service,
    layer: layer.name,
    start: start_time,
    end: end_time,
    resolution: $("#select-resolution").val(),
    delay: $("#delay").val(),
    width: map.getSize().w,
    height: map.getSize().h,
    bbox: map.getExtent().toBBOX(),
  });  
}

/*
function animateSlow(step) {
  if (step < 10) {
    $("#slider").slider( "value", step );
    setTimeout(function() {animate(step+1);}, 500);
  }
}
*/
