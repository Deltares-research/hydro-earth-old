var featureTable = args[1];
var hybasId = parseInt(args[2]);
var filePrefix = args[3];

var basins = ee.FeatureCollection('ft:' + featureTable);
print('Feature table:' + featureTable)
print('Basin id:' + hybasId)
                                      
var buffer_size = 0
//var buffer_size = 2000

var aoi = basins.filter(ee.Filter.eq('HYBAS_ID', ee.Number(hybasId)));

if(buffer_size !== 0) {
  var accuracy = 10 // m
  aoi = ee.FeatureCollection(ee.Feature(aoi.first()).simplify(accuracy).buffer(buffer_size, accuracy))
}

var aoiRegion = aoi.geometry(1e-2).bounds(1e-2).coordinates().getInfo()[0];

//var dem = ee.Image('USGS/SRTMGL1_003');
var dem = ee.Image('CGIAR/SRTM90_V4');
//var dem = ee.Image('WWF/HydroSHEDS/03CONDEM').clip(aoi);
//var dem = ee.Image('WWF/HydroSHEDS/03VFDEM').clip(aoi);

var crsTransform = dem.getInfo().bands[0].crs_transform; // see http://en.wikipedia.org/wiki/World_file
var crs = dem.getInfo().bands[0].crs;

var w = Math.round((aoiRegion[1][0] - aoiRegion[0][0])/-crsTransform[4]);
var h = Math.round((aoiRegion[2][1] - aoiRegion[1][1])/crsTransform[0]);

var dimensions = w + 'x' + h;
print(dimensions)

var maskAndFill = function(image, aoi) {
  var mask = ee.Image(0).byte().paint(aoi, 1);
  var fill = mask.not().multiply(-9999);

  var result = image.unmask().multiply(mask);
  result = result.add(fill);
  
  return result;
}

var image = maskAndFill(dem, aoi);

var fileName = 'SRTM' // filePrefix + hybasId.toString()
var fileNameZip = fileName + '.zip';
var url = image.getDownloadURL({
  name: fileName,
  //scale: 30,
  crs: crs,
  crs_transform: JSON.stringify(crsTransform),
  region: JSON.stringify(aoiRegion),
});

download(url, fileNameZip)
validate_zip(fileNameZip)
