var map;
var control;
OpenLayers.IMAGE_RELOAD_ATTEMPTS = 3;
OpenLayers.Util.onImageLoadErrorColor = "transparent";

// Juiste projectieparameters voor Rijksdriehoekstelsel (EPSG:28992):
Proj4js.defs["EPSG:28992"] = "+proj=sterea +lat_0=52.15616055555555 +lon_0=5.38763888888889 +k=0.9999079 +x_0=155000 +y_0=463000  +ellps=bessel  +towgs84=565.040,49.910,465.840,-0.40939,0.35971,-1.86849,4.0772 +units=m +no_defs";

window.onload = function() {
    map = new OpenLayers.Map ('map-canvas',{
        // Geldigheidsgebied van het tiling schema in RD-coördinaten:
        maxExtent: new OpenLayers.Bounds(-285401.92,22598.08,595401.9199999999,903401.9199999999),
        // Resoluties (pixels per meter) van de zoomniveaus:
        resolutions: [3440.64, 1720.32, 860.16, 430.08, 215.04, 107.52, 53.76, 26.88, 13.44, 6.72, 3.36, 1.68, 0.84, 0.42],
        units: 'm',
        projection: new OpenLayers.Projection("EPSG:28992")
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
        name: 'AHN2',
        visibility: false,
        url: 'http://geodata.nationaalgeoregister.nl/tiles/service/wmts/ahn2',
        layer: 'ahn2_05m_ruw',
        style: 'default',
        matrixSet: 'EPSG:28992',
        matrixIds: epsg28992matrixids,
        format: 'image/png8',
        isBaseLayer: false,
        // attribution: 'Kaartgegevens: &copy; <a href="http://www.cbs.nl">CBS</a>, <a href="http://www.kadaster.nl">Kadaster</a>, <a href="http://openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        transitionEffect: 'resize'
        }
    );
    var osm_nb_rd_tms_layer = new OpenLayers.Layer.TMS( "OSM",
        "http://www.openbasiskaart.nl/mapcache/tms/",
        { //attribution: 'Kaartgegevens: &copy; <a href="http://openstreetmap.org/copyright">OpenStreetMap</a> contributors',
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
    
    // var boxLayer = new OpenLayers.Layer.Vector("Box layer");

    control = new OpenLayers.Control();

    map.addControl(control)
    // map.addControl(new OpenLayers.Control.LayerSwitcher());
    map.addLayers([tiledLayer_lf, tiledLayer_brt, osm_nb_rd_tms_layer, tiledLayer_ahn2]);
    // map.addControl(new OpenLayers.Control.Attribution({div:document.getElementById('map-attribution')}));

    // Het kaartbeeld wordt gecentreerd op basis van een locatie die is gedefinieerd in lengte- en breedtegraden (WGS-84):
    var lonlat = new OpenLayers.LonLat(94194.0138,431587.71576609);
    // var wgs84 = new OpenLayers.Projection("EPSG:4326");
    // lonlat.transform(wgs84, map.baseLayer.projection);
    map.setCenter(lonlat,8);
}


function drawRectangle()
{
  box = new OpenLayers.Handler.Box( control,
    {
      "done": function RectangleDrawn(bounds) {
      var ll = map.getLonLatFromPixel(new OpenLayers.Pixel(bounds.left, bounds.bottom)); 
      var ur = map.getLonLatFromPixel(new OpenLayers.Pixel(bounds.right, bounds.top)); 
      
      $.getJSON($SCRIPT_ROOT + '/_getPointCountEstimate', {
        ll_x: ll.lon.toFixed(1),
        ll_y: ll.lat.toFixed(1),
        ur_x: ur.lon.toFixed(1),
        ur_y: ur.lat.toFixed(1)
      }, function(data) {
        $(".ptcountest").text(data.result);
      });

      box.deactivate()
      }
    }
  );
  box.activate();
}

$('#menuLink').click(function() {
  $('body').toggleClass( "open-menu" );
});

$('#overlay-button').click(function(){
  var visible = ! map.getLayersByName("AHN2")[0].getVisibility();
  map.getLayersByName("AHN2")[0].setVisibility(visible);
});

$('#baselayer-button').click(function(){
  var baseLayers = map.getLayersBy('isBaseLayer',true);
  var index;
  $.each(baseLayers, function(i){
    if (baseLayers[i].visibility == true) index = i;
  })
  if (index == baseLayers.length-1) index=0;
  else index+=1;

  map.setBaseLayer(baseLayers[index]);
});

