// This file is part of MATAHN.

// MATAHN is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.

// MATAHN is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.

// You should have received a copy of the GNU General Public License
// along with MATAHN.  If not, see <http://www.gnu.org/licenses/>.

// Copyright 2014 Ravi Peters, Hugo Ledoux

var map;
var boxControl;
var boxLayer;
OpenLayers.IMAGE_RELOAD_ATTEMPTS = 3;
OpenLayers.Util.onImageLoadErrorColor = "transparent";

// Juiste projectieparameters voor Rijksdriehoekstelsel (EPSG:28992):
proj4.defs["EPSG:28992"] = "+proj=sterea +lat_0=52.15616055555555 +lon_0=5.38763888888889 +k=0.9999079 +x_0=155000 +y_0=463000  +ellps=bessel  +towgs84=565.040,49.910,465.840,-0.40939,0.35971,-1.86849,4.0772 +units=m +no_defs";

var getSelectedClasses = function(){
  var classString = "";
  $('input[type="checkbox"].class-code').each(function(i) {
    if (this.checked){
      if (classString.length!=0)
        classString += ',';
      classString += this.id;
    }
  });
  return classString;
}

window.onload = function() {
    map = new OpenLayers.Map ('map-canvas',{
        theme: null,
	// Geldigheidsgebied van het tiling schema in RD-coördinaten:
        maxExtent: new OpenLayers.Bounds(-285401.92,22598.08,595401.9199999999,903401.9199999999),
        // Resoluties (pixels per meter) van de zoomniveaus:
        resolutions: [3440.64, 1720.32, 860.16, 430.08, 215.04, 107.52, 53.76, 26.88, 13.44, 6.72, 3.36, 1.68, 0.84, 0.42],
        units: 'm',
        projection: new OpenLayers.Projection("EPSG:28992"),
        controls: [ new OpenLayers.Control.Navigation(), new OpenLayers.Control.Zoom(),  new OpenLayers.Control.Attribution({div:document.getElementById('map-attribution')} ) ]
    });

    // Er zijn 15 (0 tot 14) zoomniveaus beschikbaar van de WMTS-service voor de BRT-Achtergrondkaart:

    var epsg28992matrixids = [];
    for (var i=0; i<14; ++i) {
        epsg28992matrixids[i] = 'EPSG:28992:' + i;
    }
    
    var tiledLayer_brt = new OpenLayers.Layer.WMTS({
        name: 'BRT',
        url: 'http://geodata.nationaalgeoregister.nl/wmts/',
        layer: 'brtachtergrondkaart',
        style: 'default',
        matrixSet: 'EPSG:28992',
        matrixIds: epsg28992matrixids,
        format: 'image/png8',
        isBaseLayer: true,
        // attribution: 'Kaartgegevens: &copy; <a href="http://www.cbs.nl">CBS</a>, <a href="http://www.kadaster.nl">Kadaster</a>, <a href="http://openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        transitionEffect: 'resize'
        }
    );
    var tiledLayer_ahn2 = new OpenLayers.Layer.WMTS({
        attribution: 'Map layer: <a href="http://www.nationaalgeoregister.nl/geonetwork/srv/search/?uuid=3ffbf101-75f9-479f-8d45-5d87ac61b2ce">AHN2 WMTS</a>',
        name: 'AHN2',
        visibility: false,
        url: 'http://geodata.nationaalgeoregister.nl/tiles/service/wmts/ahn2',
        layer: 'ahn2_05m_ruw',
        style: 'default',
        matrixSet: 'EPSG:28992',
        matrixIds: epsg28992matrixids,
        format: 'image/png8',
        isBaseLayer: true,
        transitionEffect: 'resize'
        }
    );
    var osm_nb_rd_tms_layer = new OpenLayers.Layer.TMS( "OSM",
        "http://www.openbasiskaart.nl/mapcache/tms/",
        { attribution: 'Map layer: <a href="http://www.openbasiskaart.nl">Openbasiskaart</a>',
          layername: 'osm@rd', type: "png", serviceVersion:"1.0.0",
          gutter:0,buffer:0,isBaseLayer:true,transitionEffect:'resize',
          tileOrigin: new OpenLayers.LonLat(-285401.920000,22598.080000),
          resolutions:[3440.64, 1720.32, 860.16, 430.08, 215.04, 107.52, 53.76, 26.88, 13.44, 6.72, 3.36, 1.68, 0.84, 0.42],
          zoomOffset:0,
          units:"m",
          maxExtent: new OpenLayers.Bounds(-285401.920000,22598.080000,595401.920000,903401.920000),
          projection: new OpenLayers.Projection("EPSG:28992".toUpperCase()),
          sphericalMercator: false
        }
    );
    var tiledLayer_lf = new OpenLayers.Layer.TMS( "Luchtfoto",
        "http://geodata1.nationaalgeoregister.nl/luchtfoto/tms/",
        {
          attribution: 'Map layer: <a href="http://www.nationaalgeoregister.nl/geonetwork/srv/search/?uuid=5bda5b66-ae22-4a12-9236-13ad2c4d0730">PDOK-achtergrond luchtfoto</a>',
          layername: 'luchtfoto_EPSG28992', type: "jpeg",
          gutter:0,buffer:0,isBaseLayer:true,transitionEffect:'resize',
          tileOrigin: new OpenLayers.LonLat(-285401.920000,22598.080000),
          resolutions:[3440.64, 1720.32, 860.16, 430.08, 215.04, 107.52, 53.76, 26.88, 13.44, 6.72, 3.36, 1.68, 0.84, 0.42],
          zoomOffset:0,
          units:"m",
          maxExtent: new OpenLayers.Bounds(-285401.920000,22598.080000,595401.920000,903401.920000),
          projection: new OpenLayers.Projection("EPSG:28992".toUpperCase()),
          sphericalMercator: false
        }
    );

  //-- for the layer that shows the download area
    var myStyle = new OpenLayers.StyleMap(
    {
      "default": new OpenLayers.Style(
      {
        fillColor: "#0078e7",
        strokeColor: "#0078e7",
        fillOpacity: 0.05,
        strokeWidth: 1 
      }
      )
    });
    var geojson_format = new OpenLayers.Format.GeoJSON();
    var downloadarea = new OpenLayers.Layer.Vector("downloadarea", {styleMap: myStyle}); 
    map.addLayer(downloadarea);

    var getArea = '/_getDownloadArea';
    var submit_data = {dataset_id: $ACTIVE_DATASET_ID};
    if (!($TASK_ID === undefined)){
      getArea = '/_getTaskArea';
      submit_data = {task_id: $TASK_ID};
    }
    $.getJSON($SCRIPT_ROOT + getArea, submit_data, 
      function(data) {
        var features = geojson_format.read(data.result);
        downloadarea.addFeatures( features );
        map.zoomToExtent(downloadarea.getDataExtent(), false);
    });
    
  //-- layer download area

    boxLayer = new OpenLayers.Layer.Vector("Box layer");
    boxControl =  new OpenLayers.Control.DrawFeature(boxLayer,
                        OpenLayers.Handler.RegularPolygon, {
                            handlerOptions: {
                                sides: 4,
                                irregular: true
                            },
                            featureAdded: boxDrawn
                        }
                    )
    map.addControl(boxControl);

    // map.addControl(new OpenLayers.Control.LayerSwitcher());
    map.addLayers([osm_nb_rd_tms_layer, tiledLayer_lf, tiledLayer_ahn2, boxLayer]);
  }

var showPointcountEstimate = function(left, bottom, right, top) {
  $.getJSON($SCRIPT_ROOT + '/_getPointCountEstimate', {
    left: left,
    bottom: bottom,
    right: right,
    top: top,
    dataset_id: $ACTIVE_DATASET_ID
  }, function(data) {
    $(".ptcountest").text(data.result);
  });
};

$('#draw-rectangle').click(function(event){
  event.preventDefault();
  if (!boxControl.active) {
    boxLayer.removeAllFeatures();
    $(this).toggleClass('pure-button-active');
    $('body').removeClass('open-menu');
    $('.menu-link i').addClass("fa-chevron-right")
    $('.menu-link i').removeClass("fa-chevron-left")
    boxControl.activate();
  } else {
    deactivateBox()
  }
});

function boxDrawn(box) {
  showPointcountEstimate(box.geometry.bounds.left,box.geometry.bounds.bottom,box.geometry.bounds.right,box.geometry.bounds.top);
  deactivateBox()
}

function deactivateBox() {
  boxControl.deactivate();
  $('#draw-rectangle').removeClass('pure-button-active');
  $('body').addClass('open-menu');
  $('.menu-link i').removeClass("fa-chevron-right");
  $('.menu-link i').addClass("fa-chevron-left");
  $(".noselection").text("");
  $('#submit-button').removeAttr("disabled")
  $('#submit-button').removeClass('pure-button-disabled');
}

$('#menuLink').click(function(event) {
  event.preventDefault();
  $('body').toggleClass( "open-menu" );
  $('.menu-link i').toggleClass("fa-chevron-right");
  $('.menu-link i').toggleClass("fa-chevron-left");
});

$('#overlay-button').click(function(){
  var visible = ! map.getLayersByName("AHN2")[0].getVisibility();
  map.getLayersByName("AHN2")[0].setVisibility(visible);
});


$('#submit-task').submit(function(event){
  event.preventDefault();
  var okay = 1;
  var fs = boxLayer.features;

  var classes = getSelectedClasses();
  if (classes.length == 0) {
    $("#errorBox").show();
    $(".wronginput").text("At least one class should be selected.");
    okay = 0;
  }
  if (fs.length == 0) {
    $("#errorBox").show();
    $(".wronginput").text("An area on the map must be selected.");
    okay = 0;
  }

  if (okay == 1) {
    var f = fs[0];
    $.getJSON($SCRIPT_ROOT + '/_submit', {
      left:    f.geometry.bounds.left,
      bottom:  f.geometry.bounds.bottom,
      right:   f.geometry.bounds.right,
      top:     f.geometry.bounds.top,
      classification: classes, 
      email: $('input[name="useremail"]').val(),
      dataset_id: $ACTIVE_DATASET_ID
    }, function(data) {
      if(data.hasOwnProperty('wronginput')) {
        $("#errorBox").show();
        $(".wronginput").text(data["wronginput"]);
        okay = 0;
      }
      else {
        window.location.href = data.result;
      }
    });
  }
});


$('#baselayer-button').click(function(event){
  event.preventDefault();
  var baseLayers = map.getLayersBy('isBaseLayer',true);
  var index;
  $.each(baseLayers, function(i){
    if (baseLayers[i].visibility == true) index = i;
  })
  if (index == baseLayers.length-1) index=0;
  else index+=1;

  map.setBaseLayer(baseLayers[index]);
});

// prevent ios rubberband scrolling of main page
$('body').on('touchmove', function(e) {
    // this is the node the touchmove event fired on
    // in this example it would be the </p> element
    target = e.target;

    // we need to find the parent container
    // we get it like so; assumes div as parent
    parent = $(e.target).closest('div');

    // check if the parent is a scroll window by class //
    if ($(parent).hasClass('scroll')){
        // ignore as we want the scroll to happen
    } else {
        e.preventDefault();
    }
});

