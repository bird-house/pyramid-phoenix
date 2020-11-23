class BboxMapSelector {

    /*
     * HTML elements
     */

    // The map
    viewport;

    // coordinates
    bboxNorthElement;
    bboxEastElement;
    bboxSouthElement;
    bboxWestElement;

    areaRestriction;

    mapMessage;

    /*
     * Other variables
     */

    // this will hold the ol.interaction.Draw
    draw;

    /*
     * Sources, vectors and overlays
     */

    // the source to draw on
    sourceDrawing;

    // define the view
    view;

    // the openlayer map
    map;

    // A categorisation of the map coverage
    mapArea;

    constructor(initialExtentValues, oid) {
        /*
         * HTML elements
         */

        // The map
        this.viewport = document.getElementById(oid + "-map");

        // bbox coordinates
        this.bboxNorthElement = document.getElementById(oid + "-maxy");
        this.bboxEastElement = document.getElementById(oid + "-maxx");
        this.bboxSouthElement = document.getElementById(oid + "-miny");
        this.bboxWestElement = document.getElementById(oid + "-minx");

        // zoom buttons
        let zoomIn = document.getElementById(oid + "-zoom-in");
        let zoomOut = document.getElementById(oid + "-zoom-out");
        let zoomReset = document.getElementById(oid + "-reset-zoom");

        // message
        this.mapMessage = document.getElementById(oid + "-map_message");

        // help text
        let helpText = document.getElementById(oid + "-help_text");

        // End of html


        if (initialExtentValues[1] < -85 || initialExtentValues[3] > 85) {
            this.mapArea = "global"
            this.areaRestriction = initialExtentValues;
        } else {
            this.mapArea = "custom"
            this.areaRestriction = BboxMapSelector.transformLatLongTo3857(initialExtentValues);
        }

        if (this.mapArea === "global") {
            this.view = new ol.View({
                projection: 'EPSG:4326',
                zoom: 1,
                extent: this.areaRestriction
            });
        } else {
            this.view = new ol.View({
                zoom: 1,
                extent: this.areaRestriction
            });
        }

        this.setExtentAndZoom();

        // define the source and vector to draw on
        this.sourceDrawing = new ol.source.Vector({
            wrapX: false
        });
        let vectorDrawing = new ol.layer.Vector({
            extent: this.areaRestriction,
            source: this.sourceDrawing
        });

        // define the OSM base layer
        let osmLayer = new ol.layer.Tile({
            source: new ol.source.OSM()
        });
        let layers = [osmLayer, vectorDrawing];

        // define the controller for the scale line
        let scaleLineControl = new ol.control.ScaleLine({
            units: "degrees"
        });

        /* generate the map */
        this.map = new ol.Map({
            controls: ol.control.defaults({
                attributionOptions: /** @type {olx.control.AttributionOptions} */ ({
                    collapsible: false
                })
            }).extend([scaleLineControl]),
            layers: layers,
            target: oid + "-map",
            view: this.view
        });

        // add the interactive layer
        let areaRestrictionAsString = BboxMapSelector.areaRestrictionAsString(initialExtentValues)
        this.addBBoxInteraction(helpText, areaRestrictionAsString);

        /*
         *
         * Listeners and on change
         *
         */

        /*
         * Form fields
         */
        let updateMapFromTextInputsCallback = (function() {
            this.updateMapFromTextInputs();
        }).bind(this);

        this.bboxNorthElement.addEventListener("change", updateMapFromTextInputsCallback);
        this.bboxEastElement.addEventListener("change", updateMapFromTextInputsCallback);
        this.bboxSouthElement.addEventListener("change", updateMapFromTextInputsCallback);
        this.bboxWestElement.addEventListener("change", updateMapFromTextInputsCallback);

        /*
         * Buttons
         */

        /* submit button */
        let submitCallback = (function() {
            return this.validate();
        }).bind(this);
        $("form").bind("submit", submitCallback);

        /* zoom out button */
        let zoomOutCallback = (function() {
            let zoom = this.view.getZoom();
            this.view.setZoom(zoom - 1);
        }).bind(this);
        zoomOut.addEventListener("click", zoomOutCallback);

        /* zoom in button */
        let zoomInCallback = (function() {
            let zoom = this.view.getZoom();
            this.view.setZoom(zoom + 1);
        }).bind(this);
        zoomIn.addEventListener("click", zoomInCallback);

        /* zoom reset button */
        let zoomResetCallback = (function() {
            this.view.fit(this.areaRestriction);
        }).bind(this);
        zoomReset.addEventListener("click", zoomResetCallback, false);

        /*
         * Other listeners
         */

        /* adjust zoom on resize */
        let resizeCallback = (function() {
            let minZoom = this.getMinZoom();
            if (minZoom !== this.view.getMinZoom()) {
                this.view.setMinZoom(minZoom);
            }
        }).bind(this);
        window.addEventListener("resize", resizeCallback);

    }

    /*
     *
     * Methods
     *
     */

    setExtentAndZoom() {
        // set the initial zoom
        this.view.setMinZoom(this.getMinZoom());

        // set the initial fit
        this.view.fit(this.areaRestriction);
    }

    // Clear out the html fields
    cleanHtml() {
        this.bboxEastElement.value = "";
        this.bboxNorthElement.value = "";
        this.bboxWestElement.value = "";
        this.bboxSouthElement.value = "";
        this.mapMessage.innerHTML = "";
    }

    // Get the minimum zoom
    getMinZoom() {
        let width = this.viewport.clientWidth;
        let zoom = Math.ceil(Math.LOG2E * Math.log(width / 256));
        zoom = zoom - 0.8;
        return zoom;
    }

    // ensure there are valid values set
    validate() {
        let mapUpdate = this.updateMapFromTextInputs();
        if (mapUpdate === false) {
            this.viewport.focus();
            this.viewport.dataset.container = "body";
            this.viewport.dataset.toggle = "popover";
            this.viewport.dataset.trigger = "manual";
            this.viewport.dataset.content = "Please select an area on the map";
            $("#" + this.viewport.id).popover("show");
            let setTimeoutCallback = (function() {
                $("#" + this.viewport.id).popover("hide");
            }).bind(this);
            setTimeout(setTimeoutCallback, 5000);
            return false;
        } else {
            return mapUpdate;
        }
    }

    /*
     * Drawing boxes
     */

    // Create a box interaction
    addBBoxInteraction(helpText, areaRestrictionAsString) {
        let geometryFunction = ol.interaction.Draw.createBox();
        this.draw = new ol.interaction.Draw({
            source: this.sourceDrawing,
            type: /** @type {ol.geom.GeometryType} */ "Circle",
            geometryFunction: geometryFunction
        });
        helpText.innerHTML = "Please select a valid bounding box within the following geographical boundaries: " +
            areaRestrictionAsString + "."

        // On draw start we need to remove the previous feature so
        // that it doesn't show.
        let drawstartCallback = (function(e) {
            this.sourceDrawing.clear(); // implicit remove of last feature.
        }).bind(this);

        this.draw.on("drawstart", drawstartCallback);

        // When a drawing ends update the html
        let drawendCallback = (function(e) {
            let selectedExtent = e.feature.getGeometry().getExtent();
            this.processBBox(selectedExtent, false)
        }).bind(this);

        this.draw.on("drawend", drawendCallback);

        if (this.userBboxDefined()) {
            this.updateMapFromTextInputs()
        } else {
            this.processBBox(this.areaRestriction, true)
        }
        this.map.addInteraction(this.draw);
    }

    // Read in the input boxes and then updates the selection based on
    // the values provided by the form text boxes for west, south, east and
    // north. Some basic validation is done
    updateMapFromTextInputs() {
        // Some basic validation is done here, as in the next step the if one
        // of the coordinates is off the map and there is an intersection, an
        // error of no intersection is reported

        var area
        if (this.mapArea === "global") {
            area = this.areaRestriction;
        } else {
            area = BboxMapSelector.transformExtentTo4326(this.areaRestriction);
        }

        let mapMessage = "";
        let trimMessage = "Bounding box trimmed to fit geographical boundaries.";

        let west = BboxMapSelector.getNumValue(this.bboxWestElement);
        if (west < area[0]) {
            mapMessage = trimMessage;
            west = area[0];
        }

        let south = BboxMapSelector.getNumValue(this.bboxSouthElement);
        if (south < area[1]) {
            mapMessage = trimMessage;
            south = area[1];
        }

        let east = BboxMapSelector.getNumValue(this.bboxEastElement);
        if (east > area[2]) {
            mapMessage = trimMessage;
            east = area[2];
        }
        if (east < area[0]) {
            mapMessage = trimMessage;
            east = area[0];
        }

        let north = BboxMapSelector.getNumValue(this.bboxNorthElement);
        if (north > area[3]) {
            mapMessage = trimMessage;
            north = area[3];
        }
        if (north < area[1]) {
            mapMessage = trimMessage;
            north = area[1];
        }

        if (south > north) {
            mapMessage = trimMessage;
            south = north;
        }

        if (west > east) {
            mapMessage = trimMessage;
            west = east;
        }

        var selectedExtent
        if (this.mapArea === "global") {
            selectedExtent = [west, south, east, north];
        } else {
            selectedExtent = BboxMapSelector.transformLatLongTo3857([west, south, east, north]);
        }

        return this.processBBox(selectedExtent, true, mapMessage)
    }

    // Check that all the bbox values are present in the form
    userBboxDefined() {
        if (this.bboxWestElement.value === "" || this.bboxSouthElement.value === "" ||
            this.bboxEastElement.value === "" || this.bboxNorthElement.value === "") {
            return false;
        }
        return true
    }

    // Validate the selected extent. If it extends beyond the area restriction
    // then
    // trim it. If it is outside the area restriction then remove it.
    // If the drawBox flag is set the draw the box.
    processBBox(selectedExtent, drawBox, mapMessage = "") {
        if (ol.extent.containsExtent(this.areaRestriction, selectedExtent)) {
            // good to go
            this.displayBBoxCoordinates(selectedExtent);
            if (drawBox) {
                this.drawBBox(selectedExtent);
            }
            this.view.fit(selectedExtent);
            this.mapMessage.innerHTML = mapMessage;
            return true;

        } else if (ol.extent.intersects(this.areaRestriction, selectedExtent)) {
            // need to trim extent
            let trimmedExtent = ol.extent.getIntersection(this.areaRestriction,
                selectedExtent);
            this.displayBBoxCoordinates(trimmedExtent)
            // draw the trimmed box
            this.drawBBox(trimmedExtent);
            this.view.fit(trimmedExtent);
            this.mapMessage.innerHTML = "Bounding box trimmed to fit geographical boundaries.";
            return true;

        } else {
            // extent totally out of areaRestriction, lets get rid of it
            this.sourceDrawing.clear();
            this.cleanHtml();
            this.mapMessage.innerHTML = "Bounding box is outside of geographical boundaries.";
            return false;
        }
    }

    // Add the coordinates of the box to the html
    displayBBoxCoordinates(extent) {
        var area
        if (this.mapArea === "global") {
            area = extent;
        } else {
            area = BboxMapSelector.transformExtentTo4326(extent);
        }

        let en = ol.coordinate.toStringXY(ol.extent.getTopRight(area), 2)
            .split(",");
        this.bboxEastElement.value = en[0].trim();
        this.bboxNorthElement.value = en[1].trim();
        let ws = ol.coordinate.toStringXY(ol.extent.getBottomLeft(area), 2)
            .split(",");
        this.bboxWestElement.value = ws[0].trim();
        this.bboxSouthElement.value = ws[1].trim();
    }

    // Draw a bounding box on the drawing vector layer.
    drawBBox(extent) {
        this.sourceDrawing.clear();
        let boundingPoly = new ol.geom.Polygon.fromExtent(extent)
        this.sourceDrawing.addFeature(new ol.Feature({
            geometry: boundingPoly
        }));
    }

    // Get the areaRestriction as a string
    static areaRestrictionAsString(extentValues) {
        let areaRestrictionString = "northern extent: " + extentValues[3] + ", southern extent: " +
            extentValues[1] + ", eastern extent: " + extentValues[0] + ", western extent: " +
            extentValues[2];
        return areaRestrictionString;
    }

    // Parse a numerical value from an HTML element.
    static getNumValue(element) {
        return parseFloat(element.value);
    }

    // Transform an extent from EPSG:4326 to EPSG:3857
    static transformLatLongTo3857(extent) {
        return ol.proj.transformExtent(extent, 'EPSG:4326', 'EPSG:3857');
    }

    // Transform an extent from EPSG:3857 to EPSG:4326
    static transformExtentTo4326(extent) {
        return ol.proj.transformExtent(extent, 'EPSG:3857', 'EPSG:4326')
    }

}