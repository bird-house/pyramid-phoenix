/**
 * Class: OpenLayers.Control.Animate
 *
 */
OpenLayers.Control.Animate = OpenLayers.Class(OpenLayers.Control, {
  start: "2006-01-01T12:00:00Z",
  end: "2006-01-03T12:00:00Z",

  initialize: function(options) { 
    console.log("init animate control");

    if(!options) { 
      options = {}; 
    } 
    OpenLayers.Control.prototype.initialize.apply(this, [options]); 
  },
  
  draw: function(options) {
    var div = OpenLayers.Control.prototype.draw.apply(this);
    return div;
  },

  onClick: function (event) { 
  },
})
