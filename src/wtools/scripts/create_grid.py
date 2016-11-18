# -*- coding: utf-8 -*-
"""
Created on Wed Jul 08 16:12:29 2015

@author: winsemi

$Id: create_grid.py 1126 2015-11-18 16:28:37Z winsemi $
$Date: 2015-11-18 16:28:37 +0000 (Wed, 18 Nov 2015) $
$Author: winsemi $
$Revision: 1126 $
$HeadURL: https://repos.deltares.nl/repos/Hydrology/trunk/hydro-earth/wtools/scripts/create_grid.py $
$Keywords: $

"""

# import sys packages
from hydrotools import gis
import sys
import os
import shutil
# import admin packages
from optparse import OptionParser

# import general packages
import numpy as np
from osgeo import osr, gdal
from osgeo import ogr
from lxml import etree
import pyproj
# import specific packages
import wtools_lib
# import pdb

def main():
    ### Read input arguments #####
    logfilename = 'wtools_create_grid.log'
    parser = OptionParser()
    usage = "usage: %prog [options]"
    parser = OptionParser(usage=usage)
    parser.add_option('-q', '--quiet',
                      dest='verbose', default=True, action='store_false',
                      help='do not print status messages to stdout')
    parser.add_option('-f', '--file', dest='inputfile', nargs=1,
                      help='file of which extent will be read. Most logically the catchment layer\nformat: ESRI Shapefile or any gdal supported raster format (preferred GeoTiff)')
    parser.add_option('-e', '--extent',
                      nargs=4, dest='extent', type='float',
                      help='extent in WGS 1984 lat-lon (xmin, ymin, xmax, ymax)')
    parser.add_option('-l', '--logfile',
                      dest='logfilename', default='wtools_create_grid.log',
                      help='log file name')
    parser.add_option('-p', '--projection',
                      dest='projection', default='EPSG:4326',
                      help='Only used if no file is provided, either of type EPSG:<####> or +proj...')
    parser.add_option('-c', '--cellsize', type='float',
                      nargs=1, dest='cellsize', default=0.005,
                      help='extent')
    parser.add_option('-s', '--snap',
                      dest='snap', default=False, action='store_true',
                      help='Snaps grid extents to a multiple of the resolution')
    parser.add_option('-d', '--destination',
                      dest='destination', default='wflow',
                      help='Destination folder (default=./wflow)')
    
    (options, args) = parser.parse_args()
    
    ##### Preprocessing #####
    # check if either a file or an extent is provided. If not, sys.exit
    if not np.logical_or(os.path.isfile(options.inputfile), options.extent is not None):
        parser.error('No file or extent given')
        parser.print_help()
        sys.exit(1)

    # open a logger, dependent on verbose print to screen or not
    logger, ch = wtools_lib.setlogger(logfilename, 'WTOOLS', options.verbose)

    # delete old files
    if os.path.isdir(options.destination):
        shutil.rmtree(options.destination)
    os.makedirs(options.destination)

    ### Get information ####
    if options.inputfile is not None:
        # retrieve extent from input file. Check if projection is provided
        file_ext = os.path.splitext(os.path.basename(options.inputfile))[1]
        if file_ext == '.shp':
            file_att = os.path.splitext(os.path.basename(options.inputfile))[0]
            ds = ogr.Open(options.inputfile)
            # read the extent of the shapefile
            lyr = ds.GetLayerByName(file_att)
            extent = lyr.GetExtent()
            extent_in = [extent[0], extent[2], extent[1], extent[3]]
            # get spatial reference from shapefile
            srs = lyr.GetSpatialRef()
        else:
            # Read extent from a GDAL compatible file
            try:
                extent_in = wtools_lib.get_extent(options.inputfile)
            except:
                msg = 'Input file {:s} not a shape or gdal file'.format(options.inputfile)
                wtools_lib.close_with_error(logger, ch, msg)
                sys.exit(1)

#            # get spatial reference from grid file
            try:
                srs = wtools_lib.get_projection(options.inputfile)                
            except:
                logger.warning('No projection found, assuming WGS 1984 lat long')
                srs = osr.SpatialReference()
                srs.ImportFromEPSG(4326)

#            geotransform = ds.GetGeoTransform()
#            raster_cellsize = geotransform[1]
#            ncols = ds.RasterXSize
#            nrows = ds.RasterYSize
#            extent_in = [geotransform[0],
#                         geotransform[3]-nrows*raster_cellsize,
#                         geotransform[0]+ncols*raster_cellsize,
#                         geotransform[3]]
#            # get spatial reference from grid file
#            WktString = ds.GetProjection()
#            srs = osr.SpatialReference()
#            srs.ImportFromWkt(WktString)
    else:
        lonmin, latmin, lonmax, latmax = options.extent
        srs_4326 = osr.SpatialReference()
        srs_4326.ImportFromEPSG(4326)
        srs = osr.SpatialReference()
        if options.projection is not None:
            # import projection as an srs object
            if options.projection.lower()[0:4] == 'epsg':
                # make a proj4 string
                srs.ImportFromEPSG(int(options.projection[5:]))
            elif options.projection.lower()[0:5] == '+proj':
                srs.ImportFromProj4(options.projection)
            else:
                msg = 'Projection "{:s}" is not a valid projection'.format(options.projection)
                wtools_lib.close_with_error(logger, ch, msg)
        else:
            logger.warning('No projection found, assuming WGS 1984 lat long')
            srs.ImportFromEPSG(4326)
        xmin, ymin = pyproj.transform(pyproj.Proj(srs_4326.ExportToProj4()),
                                      pyproj.Proj(srs.ExportToProj4()), lonmin, latmin)
        xmax, ymax = pyproj.transform(pyproj.Proj(srs_4326.ExportToProj4()),
                                      pyproj.Proj(srs.ExportToProj4()), lonmax, latmax)
        # project the extent parameters to selected projection and snap to selected resolution
        extent_in = [xmin, ymin, xmax, ymax]

    # srs known, extent known, prepare UTM or WGS string for grid.xml
    logger.info('Projection "{:s}" used'.format(srs.ExportToProj4()))
    if srs.IsProjected():
        utm = srs.GetUTMZone()
        if utm < 0:
            hemisphere = 'S'
        else:
            hemisphere = 'N'
        geodatum = 'UTM{:d}{:s}'.format(np.abs(utm), hemisphere)
    else:
        geodatum = 'WGS 1984'

    if options.snap:
        logger.info('Snapping raster')
        snap = len(str(options.cellsize-np.floor(options.cellsize)))-2
        extent_out = wtools_lib.round_extent(extent_in, options.cellsize, snap)
    else:
        extent_out = extent_in
    cols = int((extent_out[2]-extent_out[0])/options.cellsize)  # +2)
    rows = int((extent_out[3]-extent_out[1])/options.cellsize)  # +2)
    cells = rows*cols
    xorg = extent_out[0]  # -options.cellsize
    yorg = extent_out[3]  # +options.cellsize

    # create clone raster
    print('rows: {0} cols: {1}'.format(rows, cols))

    dummy_raster = np.zeros((rows, cols))-9999.
    clone_file_map = os.path.abspath(os.path.join(options.destination, 'mask.map'))
    clone_file_tif = os.path.abspath(os.path.join(options.destination, 'mask.tif'))
    logger.info('Writing PCRaster clone to {:s}'.format(clone_file_map))
    gis.gdal_writemap(clone_file_map, 'PCRaster',
                      xorg, yorg, dummy_raster,
                      -9999., resolution=options.cellsize,
                      srs=srs)
    logger.info('Writing Geotiff clone to {:s}'.format(clone_file_tif))
    gis.gdal_writemap(clone_file_tif, 'GTiff',
                      xorg, yorg, dummy_raster,
                      -9999., resolution=options.cellsize,
                      zlib=True, srs=srs)

    # create grid.xml
    root = etree.Element('regular', locationId='wflow_mask')
    etree.SubElement(root, 'rows').text = str(rows)
    etree.SubElement(root, 'columns').text = str(cols)
    etree.SubElement(root, 'geoDatum').text = geodatum
    etree.SubElement(root, 'firstCellCenter')
    etree.SubElement(root[3], 'x').text = str(xorg+0.5*options.cellsize)
    etree.SubElement(root[3], 'y').text = str(yorg-0.5*options.cellsize)
    etree.SubElement(root, 'xCellSize').text = str(options.cellsize)
    etree.SubElement(root, 'yCellSize').text = str(options.cellsize)
    xml_file = os.path.abspath(os.path.join(options.destination, 'grid.xml'))
    logger.info('Writing FEWS grid definition to {:s}'.format(xml_file))
    gridxml = open(xml_file, 'w+')
    gridxml.write(etree.tostring(root, pretty_print=True))
    gridxml.close()

    # create shape file
    Driver = ogr.GetDriverByName("ESRI Shapefile")
    shp_file = os.path.abspath(os.path.join(options.destination, 'mask.shp'))
    logger.info('Writing shape of clone to {:s}'.format(shp_file))
    shp_att = os.path.splitext(os.path.basename(shp_file))[0]
    shp = Driver.CreateDataSource(shp_file)
    lyr = shp.CreateLayer(shp_att, srs, geom_type=ogr.wkbPolygon)
    fieldDef = ogr.FieldDefn('ID', ogr.OFTString)
    fieldDef.SetWidth(12)
    lyr.CreateField(fieldDef)
    ring = ogr.Geometry(ogr.wkbLinearRing)
    ring.AddPoint(xorg, yorg)
    ring.AddPoint(xorg + cols * options.cellsize,
                  yorg)
    ring.AddPoint(xorg + cols * options.cellsize,
                  yorg - rows * options.cellsize)
    ring.AddPoint(xorg, yorg - rows * options.cellsize)
    ring.AddPoint(xorg, yorg)
    ring.CloseRings
    polygon = ogr.Geometry(ogr.wkbPolygon)
    polygon.AddGeometry(ring)
    feat_out = ogr.Feature(lyr.GetLayerDefn())
    feat_out.SetGeometry(polygon)
    feat_out.SetField('ID', 'wflow_mask')
    lyr.CreateFeature(feat_out)
    shp.Destroy()
    logger.info('Model contains {:d} cells'.format(cells))
    if cells > 5000000:
        logger.warning('With this amount of cells your model will run VERY slow.\nConsider a larger cell-size.\nFast models run with < 1,000,000 cells')
    elif cells > 1000000:
        logger.warning('With this amount of cells your model will run slow.\nConsider a larger cell-size. Fast models run with < 1,000,000 cells')
    logger, ch = wtools_lib.closeLogger(logger, ch)
    del logger, ch
    sys.exit(1)

if __name__ == "__main__":
    main()

